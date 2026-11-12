import json
import logging
from pathlib import Path
import pg8000
from config import DB_CONFIG, PROCESSED_DIR, PROJECT_ROOT

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"

def get_connection():
    return pg8000.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
    )


def apply_schema(conn):

    raw_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    code_lines = [
        line for line in raw_sql.splitlines() if not line.strip().startswith("--")
    ]
    sql = "\n".join(code_lines)
    statements = [s.strip() for s in sql.split(";") if s.strip()]

    with conn.cursor() as cur:
        for statement in statements:
            cur.execute(statement)
    conn.commit()
    log.info(f"Schema applied ({len(statements)} statements).")



def load_drug(conn, drug_json: dict) -> int:

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO drugs (drug_name, generic_name, setid, source_file)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (setid) DO UPDATE
                SET drug_name    = EXCLUDED.drug_name,
                    generic_name = EXCLUDED.generic_name,
                    source_file  = EXCLUDED.source_file
            RETURNING drug_id;
            """,
            (drug_json["drug_name"], drug_json.get("generic_name"),
            drug_json["setid"], drug_json["source_file"]),
        )
        drug_id = cur.fetchone()[0]
    return drug_id


def load_sections(conn, drug_id: int, sections: list[dict]):

    with conn.cursor() as cur:
        cur.execute("DELETE FROM sections WHERE drug_id = %s;", (drug_id,))

        for order, section in enumerate(sections, start=1):
            cur.execute(
                """
                INSERT INTO sections (drug_id, section_order, section_title, section_text)
                VALUES (%s, %s, %s, %s);
                """,
                (drug_id, order, section["section_title"], section["text"]),
            )



def load_all_drugs():
    json_files = sorted(PROCESSED_DIR.glob("*.json")) #search all JSON files in the PROCESSED_DIR directory
    if not json_files:
        log.warning(f"No JSON files found in {PROCESSED_DIR}. Run parse_labels.py first.")
        return
    conn = get_connection()
    try:
        apply_schema(conn)
        loaded = 0
        for json_path in json_files:
            drug_json = json.loads(json_path.read_text(encoding="utf-8"))
            drug_id = load_drug(conn, drug_json)
            load_sections(conn, drug_id, drug_json["sections"])
            conn.commit()

            log.info(
                f"Loaded {drug_json['drug_name']} "
                f"(drug_id={drug_id}, {len(drug_json['sections'])} sections)"
            )
            loaded += 1

        log.info(f"Done. Loaded {loaded}/{len(json_files)} drugs.")

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()



if __name__ == "__main__":
    load_all_drugs()

