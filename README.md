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

## Deploying (and auto-deploy on push) — Azure Web App

This repo deploys to an [Azure Web App](https://learn.microsoft.com/azure/app-service/)
(Linux, Python runtime) whenever you push to `main`, via
`.github/workflows/deploy.yml`.

### One-time Azure setup

1. Create a Web App in the Azure Portal: **App Service** → **Create** →
   pick **Linux** and the **Python 3.11** runtime stack.
2. Set the startup command so Azure knows how to launch Streamlit:
   **Configuration → General settings → Startup Command**:
   ```
   python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0
   ```
3. Download the app's publish profile: **Overview → Get publish profile**.
4. In this GitHub repo, add that file's contents as a secret named
   `AZURE_WEBAPP_PUBLISH_PROFILE` (Settings → Secrets and variables →
   Actions).
5. In `.github/workflows/deploy.yml`, set `AZURE_WEBAPP_NAME` to your Web
   App's name.

### What the included GitHub Action does

`.github/workflows/deploy.yml` runs on every push to `main`:

1. **Smoke test** — installs dependencies, boots the app headlessly, and
   confirms it responds on its health endpoint. This catches broken code
   *before* it reaches your live app.
2. **Deploy** — if the smoke test passes, deploys the repo to the Azure
   Web App named above using the publish profile secret.

## Important limitation: storage on Azure Web App

Azure Web App's filesystem is **not guaranteed to persist** across restarts,
scaling events, or redeploys unless you enable persistent storage, which
means CSV/JSON files written by the app (`data/entries.csv`,
`data/baseline.json`) can be lost. This is fine for running locally, but if
you want your logged data to survive on the hosted version, either turn on
Azure's persistent storage for the app (`WEBSITES_ENABLE_APP_SERVICE_STORAGE`)
and point `DATA_DIR` at the persisted `/home` path, or swap the storage layer
for something external — e.g. Azure Table Storage, a hosted Postgres
(Azure Database for PostgreSQL, Supabase, Neon), or a Google Sheet. Happy to
build one of those in if you want durable cloud storage.

## Project structure

```
health-tracker-python/
├── app.py                        # the Streamlit app
├── requirements.txt
├── .streamlit/config.toml        # theme
├── .github/workflows/deploy.yml  # CI smoke test + Azure Web App deploy
├── data/                         # created at runtime, git-ignored
└── README.md
```
