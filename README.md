# Health Tracker

A lightweight personal health tracker that runs entirely in the browser.

## Features

- Baseline profile: date, age, height, weight, BMI and optional calorie target
- Daily logging: calorie intake, exercise minutes, activity calories, steps, weight, activity type and notes
- 7-day calorie and weight trend charts
- Daily history with search, edit and delete
- JSON export/import for backups
- Local browser storage; no backend or account required
- Responsive layout for desktop and mobile

## Run locally

No build step is required.

Open `index.html` directly in a browser, or serve the folder with any static web server:

```bash
python -m http.server 8000
```

Then visit `http://localhost:8000`.

## GitHub Pages

This project can be published directly with GitHub Pages because it is a static site.

1. Push the files to the repository's `main` branch.
2. In GitHub, open **Settings → Pages**.
3. Select **Deploy from a branch**.
4. Choose `main` and `/ (root)`.
5. Save and open the generated Pages URL.

## Data model

The app stores one `baseline` object and an array of daily `logs` in `localStorage` under the key `healthTrackerV1`.

Daily entries are keyed by date, so saving a date again updates that day's entry.

## Notes

BMI is calculated as weight (kg) / height (m)². The BMI category shown in the UI is informational and should not be treated as a medical diagnosis.
