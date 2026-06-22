import numpy as np

FEATURE_COLUMNS = [
    'bpm1', 'bpm2', 'bpm3',
    'vata_balance', 'pitta_balance', 'kapha_balance',
    'bpm1_bpm2_ratio', 'bpm2_bpm3_ratio', 'bpm1_bpm3_ratio',
    'bpm1_bpm2_diff', 'bpm2_bpm3_diff', 'bpm1_bpm3_diff',
    'mean_bpm', 'bpm_range', 'bpm_cv'
]


def build_feature_vector(avg_bpm1, avg_bpm2, avg_bpm3):
    total = avg_bpm1 + avg_bpm2 + avg_bpm3
    vata_balance = (avg_bpm1 / total) * 100 if total > 0 else 33.33
    pitta_balance = (avg_bpm2 / total) * 100 if total > 0 else 33.33
    kapha_balance = (avg_bpm3 / total) * 100 if total > 0 else 33.33

    bpm1_bpm2_ratio = avg_bpm1 / (avg_bpm2 + 1e-6)
    bpm2_bpm3_ratio = avg_bpm2 / (avg_bpm3 + 1e-6)
    bpm1_bpm3_ratio = avg_bpm1 / (avg_bpm3 + 1e-6)

    bpm1_bpm2_diff = abs(avg_bpm1 - avg_bpm2)
    bpm2_bpm3_diff = abs(avg_bpm2 - avg_bpm3)
    bpm1_bpm3_diff = abs(avg_bpm1 - avg_bpm3)

    mean_bpm = (avg_bpm1 + avg_bpm2 + avg_bpm3) / 3
    bpm_range = max(avg_bpm1, avg_bpm2, avg_bpm3) - min(avg_bpm1, avg_bpm2, avg_bpm3)
    bpm_std = np.std([avg_bpm1, avg_bpm2, avg_bpm3])
    bpm_cv = bpm_std / (mean_bpm + 1e-6)

    return np.array([[
        avg_bpm1, avg_bpm2, avg_bpm3,
        vata_balance, pitta_balance, kapha_balance,
        bpm1_bpm2_ratio, bpm2_bpm3_ratio, bpm1_bpm3_ratio,
        bpm1_bpm2_diff, bpm2_bpm3_diff, bpm1_bpm3_diff,
        mean_bpm, bpm_range, bpm_cv
    ]], dtype=float)
