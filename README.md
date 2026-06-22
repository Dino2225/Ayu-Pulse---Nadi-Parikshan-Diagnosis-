# Nadi Parikshan — Intelligent IoT Pulse Analysis

A prototype Flask application for real-time multi-sensor pulse monitoring, Ayurveda-inspired Nadi analysis, and machine learning classification.

## Project overview

This project demonstrates an end-to-end prototype that:
- receives BPM readings from three sensors (Vata, Pitta, Kapha) via a Flask REST API,
- computes dosha balance and feature-engineered pulse statistics,
- performs ML inference using saved `joblib` models,
- displays live charts and prediction results in a browser dashboard,
- stores patient registration and prediction records in SQLite.

## Key features

- Real-time pulse ingestion at `/update_bpm`
- Live dashboard at `/dashboard`
- ML model loading with fallback to enhanced artifacts
- Dosha interpretation and graph-based pattern analysis
- Patient registration, history storage, and prediction persistence
- Device integration guidance for NodeMCU / ESP8266 / ESP32

## Current results

- Model type: RandomForest/XGBoost-based classifier
- Data used: `nadiparikshan_3sensor.csv`
- Classes: `Healthy`, `Fatigue`, `Hypertension`, `Stress`, `Arrhythmia`
- Current multiclass accuracy: ~50–55% on the available dataset
- Most reliable results: `Fatigue`
- Known challenge: `Arrhythmia` and `Hypertension` are difficult to distinguish with only three summary BPM values

## Limitations

This is a research/prototype repository, not a production system.
- Accuracy is low because the current dataset and features are summary BPM values rather than raw ECG/PPG waveforms.
- Better accuracy requires beat-to-beat HRV features, frequency-domain analysis, and more labeled training data.
- The model is suitable as an exploratory prototype; do not use it for clinical diagnosis.

## Installation

```powershell
cd "Ayu Pulse/Nadiparikshan_ Project"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the app

```powershell
.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000/ in your browser.

## Device integration

Send JSON POST requests to `/update_bpm`:

```json
{
  "bpm1": 72,
  "bpm2": 68,
  "bpm3": 75
}
```

Example curl command:

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"bpm1":72,"bpm2":68,"bpm3":75}' \
  http://127.0.0.1:5000/update_bpm
```

For NodeMCU/ESP integration, see `device_integration.md`.

## Demo GIF / screenshot

To create a short demo GIF:
1. Open the dashboard at http://127.0.0.1:5000/.
2. Use a screen recorder like ShareX, OBS, or a browser extension.
3. Capture a few seconds of the dashboard updating.
4. Save the file as `demo.gif` in the project root.
5. Add the GIF to the README using:

```md
![Demo](demo.gif)
```

## Screenshots

## Dashboard

![Dashboard](screenshots/dashboard.png)

## Dosha Analysis

![Dosha Analysis](screenshots/dosha_analysis.png)

## Training and artifacts

If you want to retrain the models, run:

```powershell
.venv\Scripts\python.exe train_enhanced.py
```

Required artifacts:
- `rf_nadi_model.joblib` or `rf_nadi_model_enhanced.joblib`
- `scaler.joblib` or `scaler_enhanced.joblib`
- `label_encoder.joblib` or `label_encoder_enhanced.joblib`

## Publish to GitHub

```bash
git init
git add .
git commit -m "Initial Nadi Parikshan prototype"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

If the repository already exists:

```bash
git add .
git commit -m "Update project README and docs"
git push
```

## Recommended GitHub topics

`flask`, `python`, `machine-learning`, `iot`, `health-tech`, `data-science`

## Project structure

- `app.py` — Flask backend and REST API
- `train.py` / `train_enhanced.py` — model training scripts
- `static/` — CSS, JS, video assets
- `templates/` — HTML templates
- `README.md` — project documentation
- `requirements.txt` — dependencies
- `device_integration.md` — NodeMCU/ESP payload guide
- `research_paper_plan.md` — paper improvement plan

## How to describe this on a resume

- Built an end-to-end IoT pulse analysis prototype with Flask backend, multi-sensor BPM input, and ML-powered prediction dashboard.
- Documented model performance, limitations, and a clear research roadmap for future HRV and raw waveform improvements.

## Notes

This repository is best used as a proof-of-concept and research demonstration. Accurate clinical use requires additional sensor data, larger datasets, and validation.
