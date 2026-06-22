import os
import joblib

PREFERRED_MODELS = [
    ('rf_nadi_model_enhanced.joblib', 'scaler_enhanced.joblib', 'label_encoder_enhanced.joblib'),
    ('rf_nadi_model.joblib', 'scaler.joblib', 'label_encoder.joblib')
]


def load_model_artifacts():
    model = None
    scaler = None
    label_encoder = None

    for mpath, spath, epath in PREFERRED_MODELS:
        if os.path.exists(mpath) and os.path.exists(spath) and os.path.exists(epath):
            try:
                model = joblib.load(mpath)
                scaler = joblib.load(spath)
                label_encoder = joblib.load(epath)
                print(f"Loaded model set: {mpath}, {spath}, {epath}")
                break
            except Exception as ex:
                print(f"Error loading model files ({mpath}, {spath}, {epath}):", ex)

    if model is None or scaler is None or label_encoder is None:
        print("No valid model/scaler/encoder found. Predictions will be disabled until artifacts are available.")

    return model, scaler, label_encoder
