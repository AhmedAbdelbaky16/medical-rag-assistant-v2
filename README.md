# Medical RAG Assistant — Build Log

A step-by-step RAG (Retrieval-Augmented Generation) project answering
questions about FDA drug labels, built from scratch to learn the full
pipeline: data ingestion → SQL → embeddings → hybrid retrieval →
generation → evaluation → deployment.

**Repo:** https://github.com/AhmedAbdelbaky16/rag-medical-assistant-v2

**⚠️ Educational project only.** This is not medical advice and should
never be used for real clinical decisions.

## Clone this repo

```bash
git clone https://github.com/AhmedAbdelbaky16/rag-medical-assistant-v2.git
cd medical-rag-assistant
```

## Status
- [x] Phase 0  — Project setup
- [x] Phase 1  — Data ingestion & cleaning
- [ ] Phase 2  — Database setup (Docker + Postgres)
- [ ] Phase 3  — SQL schema & structured data
- [ ] Phase 4  — Tokenization & chunking
- [ ] Phase 5  — Embeddings
- [ ] Phase 6  — Hybrid retrieval
- [ ] Phase 7  — Generation
- [ ] Phase 8  — Backend API
- [ ] Phase 9  — Frontend
- [ ] Phase 10 — Docker Compose (full stack)
- [ ] Phase 11 — Evaluation


## Phase 0/1 — Setup instructions (run these on your own machine)
This project calls the public DailyMed API, which isn't reachable from
a sandboxed dev environment — run these steps locally:

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download the drug labels (~500 drugs, a few MB total)
cd src
python download_labels.py

# 4. Parse and clean them into structured JSON
python parse_labels.py
```

After step 3, check `data/raw/` — one `.xml` file per drug. After step
4, check `data/processed/` — one clean `.json` file per drug, each
broken into labeled sections (e.g. `WARNINGS`, `DOSAGE AND
ADMINISTRATION`).