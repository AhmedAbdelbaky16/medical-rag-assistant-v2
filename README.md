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
- [x] Phase 2  — Database setup (Docker + Postgres)
- [x] Phase 3  — SQL schema & structured data
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

## Phase 2 — Database setup

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/)
(with WSL2 backend on Windows) installed and running.

```bash
docker compose up -d
```

This starts a PostgreSQL 16 container with the `pgvector` extension
pre-installed, on `localhost:5432`. Credentials (local dev only, not
used anywhere public) are set in `docker-compose.yml`.

Verify it's running:
```bash
docker ps
docker exec -it medical-rag-db psql -U raguser -d medical_rag -c "CREATE EXTENSION IF NOT EXISTS vector; SELECT extname FROM pg_extension;"
```
You should see `vector` and `plpgsql` listed.

To stop the database:
```bash
docker compose down
```
(Data persists in a Docker volume — `docker compose down` does not
delete it. `docker compose down -v` would, if you ever want a clean
slate.)

## Phase 3 — SQL schema & structured data

Two core tables: `drugs` (one row per drug) and `sections` (one row
per label section, linked to its drug via a foreign key). See
`sql/schema.sql` for the full definitions and inline comments
explaining each design choice.

Load all parsed JSON into the database:
```bash
cd src
python load_to_db.py
```

This applies the schema (safe to re-run) and loads every file in
`data/processed/`. Re-running is idempotent — existing drugs are
updated rather than duplicated, and each drug's sections are fully
replaced from the current JSON rather than appended to.

Verify:
```bash
docker exec -it medical-rag-db psql -U raguser -d medical_rag -c "SELECT COUNT(*) FROM drugs;"
docker exec -it medical-rag-db psql -U raguser -d medical_rag -c "SELECT COUNT(*) FROM sections;"
docker exec -it medical-rag-db-v2 psql -U raguser -d medical_rag_v2 -c "SELECT d.drug_name, COUNT(s.section_id) FROM drugs d JOIN sections s ON s.drug_id = d.drug_id GROUP BY d.drug_name;"
```

**Browsing the data:** either `psql` directly via the `docker exec`
commands above, or a GUI client like [DBeaver](https://dbeaver.io/)
(free) connecting to `localhost:5433`, database `medical_rag_v2`, using
the credentials in `docker-compose.yml`.