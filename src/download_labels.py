
import time 
import logging 
import requests 
import re
from config import DRUG_LIST, RAW_DIR, DAILYMED_BASE_URL

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s") 
log = logging.getLogger(__name__)


def safe_filename(drug_name):
    return drug_name.lower().replace(" ", "_") + ".xml"

def is_single_ingredient(title: str, drug_name: str) -> bool:
    """Check if a DailyMed title is for the drug alone, not a combination."""
    title = title.upper()
    drug = drug_name.upper()

    match = re.search(r"\(([^)]*)\)", title)   
    generic = match.group(1) if match else title.split("[")[0]
    generic = generic.strip()

    if not generic.startswith(drug):
        return False
    rest = generic[len(drug):]
    return " AND " not in rest and "," not in rest




def search_setid(drug_name: str) -> str | None:
    url = f"{DAILYMED_BASE_URL}/spls.json"
    params = {"drug_name": drug_name, "pagesize": 50} 
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("data", [])
    if not results: 
        log.warning(f"No results found for '{drug_name}'") 
        return None
    for item in results:
        if is_single_ingredient(item["title"], drug_name):
            log.info(f"Selected for '{drug_name}': {item['title']}")
            return item["setid"]

    log.warning(f"No single-ingredient label for '{drug_name}', using first result: {results[0]['title']}")
    return results[0]["setid"]

def download_label_xml(setid) -> bytes:
    url = f"{DAILYMED_BASE_URL}/spls/{setid}.xml"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.content
    
def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True) 
    downloaded, skipped, failed = 0, 0, 0
    for drug_name in DRUG_LIST:
        out_path = RAW_DIR / safe_filename(drug_name)
        if out_path.exists():
            log.info(f"Skipping '{drug_name}' (already downloaded)") 
            skipped += 1 
            continue
        try:
            setid = search_setid(drug_name)
            if setid is None:
                failed += 1
                continue
            xml_bytes = download_label_xml(setid)
            out_path.write_bytes(xml_bytes)
            log.info(f"Saved {drug_name} -> {out_path.name} ({len(xml_bytes)} bytes)")
            downloaded += 1



        except requests.RequestException as e:
            log.error(f"Failed to fetch '{drug_name}': {e}")
            failed += 1

        time.sleep(0.5)

    log.info(f"Done. Downloaded={downloaded}, Skipped={skipped}, Failed={failed}")



if __name__ == "__main__":
    main()