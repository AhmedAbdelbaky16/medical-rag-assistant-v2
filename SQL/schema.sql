--   Two tables (chunks will be added later):
--   drugs    — one row per drug (the structured facts)
--   sections — one row per section of a drug's label (the text content)

CREATE TABLE IF NOT EXISTS drugs (
    drug_id      SERIAL PRIMARY KEY,
    drug_name    TEXT NOT NULL CHECK (drug_name <> ''),
    generic_name TEXT,
    setid        TEXT UNIQUE,
    source_file  TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sections (
    section_id     SERIAL PRIMARY KEY,
    drug_id        INTEGER NOT NULL REFERENCES drugs(drug_id) ON DELETE CASCADE,
    section_title  TEXT NOT NULL,
    section_text   TEXT NOT NULL,
    section_order  INTEGER NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sections_drug_id ON sections(drug_id);




