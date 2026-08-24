# Health ledger (Python / Streamlit)

A personal health tracker built with [Streamlit](https://streamlit.io). Set a
baseline (weight, height, age), log daily calorie intake, activities, and
weight, and see trends over time.

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).

Data is stored locally in `data/baseline.json` and `data/entries.csv`,
created automatically the first time you save something. That folder is
git-ignored so your personal data never gets committed.

## Push to your repository

```bash
git init
git add .
git commit -m "Initial commit: health tracker app"
git branch -M main
git remote add origin https://github.com/Neal-ubc/Health-Tracker.git
git push -u origin main
```

If the repo already has commits (e.g. an auto-created README), pull first:

```bash
git remote add origin https://github.com/Neal-ubc/Health-Tracker.git
git pull origin main --allow-unrelated-histories
git push -u origin main
```

## Deploying (and auto-deploy on push)

Streamlit Community Cloud is the simplest free host for a Streamlit app, and
it redeploys automatically whenever you push to `main` — that part doesn't
need a GitHub Action, it's built into how Streamlit Cloud watches your repo:

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with
   GitHub.
2. Click **New app**, pick this repo, branch `main`, and set the main file
   path to `app.py`.
3. Deploy. From then on, every push to `main` updates the live app.

### What the included GitHub Action does

`.github/workflows/deploy.yml` runs on every push to `main`:

1. **Smoke test** — installs dependencies, boots the app headlessly, and
   confirms it responds on its health endpoint. This catches broken code
   *before* it reaches your live app.
2. **Optional deploy trigger** — if you add a repository secret named
   `STREAMLIT_DEPLOY_HOOK` (Settings → Secrets and variables → Actions),
   the workflow will `curl` it after a passing smoke test. This is only
   useful if you're using a host with a webhook-based redeploy URL (for
   example a container host or a custom server) — Streamlit Community Cloud
   itself doesn't need this, since it already redeploys on push.

## Important limitation: storage on Streamlit Community Cloud

Streamlit Community Cloud's filesystem is **ephemeral** — it resets whenever
the app reboots or redeploys, which means CSV/JSON files written by the app
(`data/entries.csv`, `data/baseline.json`) will **not** persist across
redeploys on the free tier. This is fine for running locally, but if you
want your logged data to survive on the hosted version, you'll eventually
want to swap the storage layer for something external — e.g. a Google Sheet,
a hosted SQLite/Postgres database (Supabase, Turso, Neon), or committing
the CSV back to the repo via a scheduled Action. Happy to build one of those
in if you want durable cloud storage.

## Project structure

```
health-tracker-python/
├── app.py                        # the Streamlit app
├── requirements.txt
├── .streamlit/config.toml        # theme
├── .github/workflows/deploy.yml  # CI smoke test + optional deploy trigger
├── data/                         # created at runtime, git-ignored
└── README.md
```
