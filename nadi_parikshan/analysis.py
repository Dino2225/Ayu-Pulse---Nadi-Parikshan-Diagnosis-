import numpy as np


def validate_bpm(bpm):
    return 40 <= bpm <= 200


def analyze_graph_pattern(data_points):
    if len(data_points) < 3:
        return {
            'speed': 0,
            'variability': 0,
            'regularity': 0,
            'smoothness': 0,
            'pattern_type': 'insufficient_data'
        }

    data_array = np.array(data_points)
    mean_val = float(np.mean(data_array))
    std_val = float(np.std(data_array))
    variability = std_val / mean_val if mean_val > 0 else 0
    regularity = max(0, 1 - (variability * 2))

    if len(data_array) > 1:
        differences = np.diff(data_array)
        avg_change = np.mean(np.abs(differences))
        smoothness = max(0, 1 - (avg_change / mean_val)) if mean_val > 0 else 0
    else:
        smoothness = 0

    if mean_val < 60:
        speed_score = 0.2
    elif mean_val < 80:
        speed_score = 0.5
    else:
        speed_score = 0.8

    if variability > 0.15 or regularity < 0.5:
        pattern_type = 'vata'
    elif smoothness > 0.7 and variability < 0.08:
        pattern_type = 'kapha'
    else:
        pattern_type = 'pitta'

    return {
        'speed': round(speed_score, 3),
        'variability': round(variability, 3),
        'regularity': round(regularity, 3),
        'smoothness': round(smoothness, 3),
        'mean_bpm': round(mean_val, 2),
        'std_bpm': round(std_val, 2),
        'pattern_type': pattern_type
    }


def determine_dosha_from_graphs(vata_pattern, pitta_pattern, kapha_pattern):
    if not all([vata_pattern, pitta_pattern, kapha_pattern]):
        return {'dosha_type': 'Unknown', 'confidence': 0, 'analysis': {}}

    vata_score = 0
    pitta_score = 0
    kapha_score = 0

    if vata_pattern['pattern_type'] == 'vata':
        vata_score += 3
    if vata_pattern['variability'] > 0.12:
        vata_score += 2
    if vata_pattern['regularity'] < 0.6:
        vata_score += 2
    if vata_pattern['mean_bpm'] > 75:
        vata_score += 1

    if pitta_pattern['pattern_type'] == 'pitta':
        pitta_score += 3
    if 0.05 < pitta_pattern['variability'] < 0.12:
        pitta_score += 2
    if 0.6 < pitta_pattern['regularity'] < 0.85:
        pitta_score += 2
    if 60 < pitta_pattern['mean_bpm'] < 85:
        pitta_score += 1

    if kapha_pattern['pattern_type'] == 'kapha':
        kapha_score += 3
    if kapha_pattern['variability'] < 0.08:
        kapha_score += 2
    if kapha_pattern['smoothness'] > 0.7:
        kapha_score += 2
    if kapha_pattern['mean_bpm'] < 70:
        kapha_score += 1

    scores = {'Vata': vata_score, 'Pitta': pitta_score, 'Kapha': kapha_score}
    dominant_dosha = max(scores, key=scores.get)
    max_score = scores[dominant_dosha]
    total_score = sum(scores.values())
    confidence = (max_score / total_score * 100) if total_score > 0 else 0

    return {
        'dosha_type': dominant_dosha,
        'confidence': round(confidence, 2),
        'scores': scores,
        'analysis': {
            'vata_pattern': vata_pattern,
            'pitta_pattern': pitta_pattern,
            'kapha_pattern': kapha_pattern
        }
    }


def calculate_dosha_balance(bpm1, bpm2, bpm3):
    total = bpm1 + bpm2 + bpm3
    if total == 0:
        return {'vata': 0, 'pitta': 0, 'kapha': 0}

    return {
        'vata': round((bpm1 / total) * 100, 2),
        'pitta': round((bpm2 / total) * 100, 2),
        'kapha': round((bpm3 / total) * 100, 2)
    }


def get_dosha_interpretation(dosha_balance):
    vata = dosha_balance['vata']
    pitta = dosha_balance['pitta']
    kapha = dosha_balance['kapha']
    dominant = max(vata, pitta, kapha)
    dominant_dosha = 'Vata' if dominant == vata else ('Pitta' if dominant == pitta else 'Kapha')

    interpretations = {
        'Vata': {
            'description': 'Vata dosha is dominant. Associated with movement, creativity, and nervous system.',
            'imbalance': 'High Vata may indicate anxiety, restlessness, or digestive issues.',
            'recommendation': 'Focus on grounding practices, warm foods, and regular routine.'
        },
        'Pitta': {
            'description': 'Pitta dosha is dominant. Associated with metabolism, digestion, and transformation.',
            'imbalance': 'High Pitta may indicate inflammation, acidity, or excessive heat.',
            'recommendation': 'Cooling foods, moderation, and stress management recommended.'
        },
        'Kapha': {
            'description': 'Kapha dosha is dominant. Associated with structure, stability, and lubrication.',
            'imbalance': 'High Kapha may indicate sluggishness, congestion, or weight issues.',
            'recommendation': 'Light foods, regular exercise, and stimulation recommended.'
        }
    }

    return {
        'dominant_dosha': dominant_dosha,
        'balance': dosha_balance,
        'interpretation': interpretations[dominant_dosha]
    }


def get_dosha_interpretation_from_graphs(dosha_analysis):
    dosha_type = dosha_analysis['dosha_type']
    analysis = dosha_analysis['analysis']
    interpretations = {
        'Vata': {
            'pattern_name': 'Snake-like (Sarpa)',
            'characteristics': 'Fast, irregular, erratic pulse pattern',
            'indications': 'High variability indicates Vata imbalance - may suggest anxiety, restlessness, or nervous system issues',
            'recommendation': 'Focus on grounding practices, warm foods, regular routine, and stress reduction'
        },
        'Pitta': {
            'pattern_name': 'Frog-like (Manduka)',
            'characteristics': 'Moderate speed, strong, regular pulse pattern',
            'indications': 'Balanced pattern with moderate variability suggests Pitta dominance - may indicate good metabolism but watch for excess heat',
            'recommendation': 'Maintain balanced diet, cooling foods, moderate exercise, and stress management'
        },
        'Kapha': {
            'pattern_name': 'Swan-like (Hamsa)',
            'characteristics': 'Slow, steady, smooth pulse pattern',
            'indications': 'Low variability and smooth pattern indicates Kapha dominance - may suggest stability but watch for sluggishness',
            'recommendation': 'Light foods, regular exercise, stimulation, and avoid excessive rest'
        }
    }

    base_interpretation = interpretations.get(dosha_type, {
        'pattern_name': 'Unknown',
        'characteristics': 'Insufficient data for pattern analysis',
        'indications': 'Need more readings to determine pattern',
        'recommendation': 'Continue monitoring to gather sufficient data'
    })

    if analysis:
        vata_pat = analysis.get('vata_pattern', {})
        pitta_pat = analysis.get('pitta_pattern', {})
        kapha_pat = analysis.get('kapha_pattern', {})

        base_interpretation['detailed_analysis'] = {
            'vata_sensor': {
                'mean_bpm': vata_pat.get('mean_bpm', 0),
                'variability': vata_pat.get('variability', 0),
                'pattern': vata_pat.get('pattern_type', 'unknown')
            },
            'pitta_sensor': {
                'mean_bpm': pitta_pat.get('mean_bpm', 0),
                'variability': pitta_pat.get('variability', 0),
                'pattern': pitta_pat.get('pattern_type', 'unknown')
            },
            'kapha_sensor': {
                'mean_bpm': kapha_pat.get('mean_bpm', 0),
                'variability': kapha_pat.get('variability', 0),
                'pattern': kapha_pat.get('pattern_type', 'unknown')
            }
        }

    return base_interpretation


def calculate_statistical_features(readings):
    if len(readings) < 2:
        return {
            'mean': readings[0] if readings else 0,
            'std': 0,
            'min': readings[0] if readings else 0,
            'max': readings[0] if readings else 0,
            'range': 0,
            'stability': 100.0
        }

    readings_array = np.array(readings)
    mean_val = float(np.mean(readings_array))
    std_val = float(np.std(readings_array))
    min_val = float(np.min(readings_array))
    max_val = float(np.max(readings_array))
    range_val = max_val - min_val
    stability = max(0, 100 - (std_val / 20 * 100))

    return {
        'mean': round(mean_val, 2),
        'std': round(std_val, 2),
        'min': round(min_val, 2),
        'max': round(max_val, 2),
        'range': round(range_val, 2),
        'stability': round(stability, 2)
    }
