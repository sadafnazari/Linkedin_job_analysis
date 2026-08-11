# CLAUDE.md

## Documentation

The READMEs are the source of truth for what this project is and how to run it. Read
`README.md` first, then `src/linkedin_job_search/README.md` or `src/dashboard/README.md`
for the half you are working on. Don't restate their contents here.

Keep them accurate: if a change alters a command, a config key, or documented behaviour,
update the relevant README in the same commit.

## Project shape

Two independent parts that share only `configs/` and `resources/`:

- `src/linkedin_job_search/` — Scrapy project; scrapes job posts and writes them to Postgres.
- `src/dashboard/` — Streamlit app; reads that Postgres and renders the analytics.

## Environment

- Dependencies come from `requirements.txt`, installed into the project env (`lja`).
- Run `pytest` and `scrapy` from inside the sub-project directory. Resource and config
  paths are resolved relative to it, so both fail from the repo root.
- Run `pre-commit run --all-files` before proposing a commit.

## Conventions

- Configuration decides *what* data is shown; code owns *how* it looks. Keep one source of
  truth per value and validate it at startup — raise on a bad value rather than falling
  back silently.
- Per-country behaviour is data-driven through `resources/<country>/*.json`. Never branch
  on a country name in code.
- Credentials live in `configs/.env` and `.streamlit/secrets.toml`, both untracked. Never
  read, print, or copy their contents.
