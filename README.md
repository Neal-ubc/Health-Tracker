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
   Click **Save** at the top of the page (not just Enter in the field), and
   wait for the "Successfully updated configuration" notification. Refresh
   the page afterward and confirm the field still shows the command —
   Azure Portal's Configuration blade can silently fail to persist a value
   if you navigate away before the save notification appears.
3. Also on the **Configuration** page, switch to the **Application
   settings** tab → **New application setting**:
   - Name: `SCM_DO_BUILD_DURING_DEPLOYMENT`
   - Value: `true`

   **Save**, and again confirm it's still listed after a page refresh. This
   is what makes Azure actually run `pip install -r requirements.txt`
   during deploy — without it the app starts with no dependencies
   installed.
4. Download the app's publish profile: **Overview → Get publish profile**.
5. In this GitHub repo, add that file's contents as a secret named
   `AZURE_WEBAPP_PUBLISH_PROFILE` (Settings → Secrets and variables →
   Actions).
6. In `.github/workflows/deploy.yml`, set `AZURE_WEBAPP_NAME` to your Web
   App's name.

(An earlier version of this workflow tried to set steps 2–3 automatically
via a service principal on every deploy, so there was nothing to remember
in the Portal. That needs Azure AD "register an application" permission,
which is commonly locked down on university-managed tenants — if you hit
`Insufficient privileges to complete the operation` creating one, that's
why. The manual Portal steps above don't need that permission.)

### What the included GitHub Action does

`.github/workflows/deploy.yml` runs on every push to `main`:

1. **Smoke test** — installs dependencies, boots the app headlessly, and
   confirms it responds on its health endpoint. This catches broken code
   *before* it reaches your live app.
2. **Deploy** — if the smoke test passes, deploys the repo to the Azure
   Web App named above using the publish profile secret.

## Important limitation: storage on Azure Web App

By default the app stores data in a `data/` folder relative to `app.py`
(`data/entries.csv`, `data/baseline.json`). That's fine locally, but on
Azure Web App the repo's working directory (`/home/site/wwwroot`) gets
replaced on every deploy, which would silently wipe that folder each time
`main` is pushed — separately from Azure's usual filesystem-persistence
caveats around restarts and scaling.

The app reads its storage location from the `DATA_DIR` environment
variable (defaults to `data`), so point it somewhere outside the deployed
code instead: in the Web App's **Environment variables** (App settings),
add `DATA_DIR` = `/home/data`. Everything under `/home` other than
`/home/site/wwwroot` persists across both restarts and redeploys, so this
keeps your logged entries intact. For anything beyond a single-instance
hobby deployment, an external store (Azure Table Storage, a hosted
Postgres, a Google Sheet) would still be more robust — happy to build one
of those in if you want it.

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
