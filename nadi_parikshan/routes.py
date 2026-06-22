from flask import Blueprint, render_template, request, jsonify
from .database import get_db
from .models import load_model_artifacts
from .prediction import build_feature_vector
from .analysis import (
    validate_bpm,
    analyze_graph_pattern,
    determine_dosha_from_graphs,
    get_dosha_interpretation,
    calculate_dosha_balance,
    calculate_statistical_features,
    get_dosha_interpretation_from_graphs
)

import time

main_bp = Blueprint('main', __name__)
model, scaler, label_encoder = load_model_artifacts()

latest_data = {
    'bpm1': 0,
    'bpm2': 0,
    'bpm3': 0,
    'prediction': 'Waiting for data...',
    'accuracy': 0.0,
    'timestamp': time.time()
}

READING_BUFFER_SIZE = 30
reading_buffer = {'bpm1': [], 'bpm2': [], 'bpm3': [], 'timestamps': []}


def get_enhanced_prediction(bpm1, bpm2, bpm3):
    if not all([validate_bpm(bpm1), validate_bpm(bpm2), validate_bpm(bpm3)]):
        return {
            'prediction': 'Invalid Reading',
            'accuracy': 0.0,
            'confidence': 'low',
            'message': 'BPM values outside normal range (40-200)'
        }

    dosha_balance = calculate_dosha_balance(bpm1, bpm2, bpm3)
    dosha_info = get_dosha_interpretation(dosha_balance)
    stats1 = calculate_statistical_features(reading_buffer['bpm1'])
    stats2 = calculate_statistical_features(reading_buffer['bpm2'])
    stats3 = calculate_statistical_features(reading_buffer['bpm3'])

    if len(reading_buffer['bpm1']) >= 5:
        avg_bpm1 = sum(reading_buffer['bpm1'][-5:]) / 5
        avg_bpm2 = sum(reading_buffer['bpm2'][-5:]) / 5
        avg_bpm3 = sum(reading_buffer['bpm3'][-5:]) / 5
    else:
        avg_bpm1, avg_bpm2, avg_bpm3 = bpm1, bpm2, bpm3

    if model is not None and scaler is not None and label_encoder is not None:
        try:
            X = build_feature_vector(avg_bpm1, avg_bpm2, avg_bpm3)
            X_scaled = scaler.transform(X)
            pred = model.predict(X_scaled)[0]
            proba = model.predict_proba(X_scaled)[0]
            prob = float(max(proba) * 100)
            label = label_encoder.inverse_transform([pred])[0]
        except Exception as e:
            return {
                'prediction': 'Prediction Error',
                'accuracy': 0.0,
                'confidence': 'none',
                'dosha_balance': dosha_balance,
                'dosha_info': dosha_info,
                'error': str(e)
            }

        confidence = 'high' if prob >= 80 else 'medium' if prob >= 60 else 'low'

        return {
            'prediction': label,
            'accuracy': round(prob, 2),
            'confidence': confidence,
            'dosha_balance': dosha_balance,
            'dosha_info': dosha_info,
            'statistics': {'vata': stats1, 'pitta': stats2, 'kapha': stats3},
            'readings_count': len(reading_buffer['bpm1']),
            'data_quality': 'good' if len(reading_buffer['bpm1']) >= 10 else 'building'
        }

    return {
        'prediction': 'Model Not Loaded',
        'accuracy': 0.0,
        'confidence': 'none',
        'dosha_balance': dosha_balance,
        'dosha_info': dosha_info
    }


def format_graph_patterns():
    if len(reading_buffer['bpm1']) < 3:
        return {'dosha_type': 'Insufficient Data', 'confidence': 0, 'message': 'Need at least 3 readings to analyze graph patterns'}

    vata_pattern = analyze_graph_pattern(reading_buffer['bpm1'])
    pitta_pattern = analyze_graph_pattern(reading_buffer['bpm2'])
    kapha_pattern = analyze_graph_pattern(reading_buffer['bpm3'])
    dosha_from_graphs = determine_dosha_from_graphs(vata_pattern, pitta_pattern, kapha_pattern)
    graph_interpretation = get_dosha_interpretation_from_graphs(dosha_from_graphs)

    return {
        'dosha_type': dosha_from_graphs['dosha_type'],
        'confidence': dosha_from_graphs['confidence'],
        'scores': dosha_from_graphs['scores'],
        'interpretation': graph_interpretation,
        'patterns': {'vata': vata_pattern, 'pitta': pitta_pattern, 'kapha': kapha_pattern}
    }


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@main_bp.route('/update_bpm', methods=['POST'])
def update_bpm():
    global latest_data, reading_buffer
    try:
        data = request.get_json(force=True)
        bpm1 = float(data.get('bpm1', 0))
        bpm2 = float(data.get('bpm2', 0))
        bpm3 = float(data.get('bpm3', 0))

        if not all([validate_bpm(bpm1), validate_bpm(bpm2), validate_bpm(bpm3)]):
            return jsonify({'status': 'warning', 'message': 'Invalid BPM readings detected. Please check sensors.', 'prediction': latest_data.get('prediction', 'Invalid Data'), 'accuracy': latest_data.get('accuracy', 0.0)})

        reading_buffer['bpm1'].append(bpm1)
        reading_buffer['bpm2'].append(bpm2)
        reading_buffer['bpm3'].append(bpm3)
        reading_buffer['timestamps'].append(time.time())

        if len(reading_buffer['bpm1']) > READING_BUFFER_SIZE:
            reading_buffer['bpm1'] = reading_buffer['bpm1'][-READING_BUFFER_SIZE:]
            reading_buffer['bpm2'] = reading_buffer['bpm2'][-READING_BUFFER_SIZE:]
            reading_buffer['bpm3'] = reading_buffer['bpm3'][-READING_BUFFER_SIZE:]
            reading_buffer['timestamps'] = reading_buffer['timestamps'][-READING_BUFFER_SIZE:]

        latest_data.update({'bpm1': bpm1, 'bpm2': bpm2, 'bpm3': bpm3, 'timestamp': time.time()})
        enhanced_result = get_enhanced_prediction(bpm1, bpm2, bpm3)
        latest_data.update({'prediction': enhanced_result['prediction'], 'accuracy': enhanced_result['accuracy'], 'confidence': enhanced_result.get('confidence', 'medium'), 'dosha_balance': enhanced_result.get('dosha_balance', {}), 'dosha_info': enhanced_result.get('dosha_info', {}), 'statistics': enhanced_result.get('statistics', {}), 'readings_count': enhanced_result.get('readings_count', 0), 'data_quality': enhanced_result.get('data_quality', 'building')})
        latest_data['graph_dosha_analysis'] = format_graph_patterns()

        return jsonify({
            'status': 'ok',
            'prediction': enhanced_result['prediction'],
            'accuracy': enhanced_result['accuracy'],
            'confidence': enhanced_result.get('confidence', 'medium'),
            'dosha_balance': enhanced_result.get('dosha_balance', {}),
            'dosha_info': enhanced_result.get('dosha_info', {}),
            'statistics': enhanced_result.get('statistics', {}),
            'readings_count': enhanced_result.get('readings_count', 0),
            'data_quality': enhanced_result.get('data_quality', 'building')
        })
    except Exception as e:
        print("Error in /update_bpm:", str(e))
        return jsonify({'status': 'error', 'message': str(e)})


@main_bp.route('/get_bpm')
def get_bpm():
    return jsonify(latest_data)


@main_bp.route('/analyze_graph_patterns', methods=['POST'])
def analyze_graph_patterns():
    try:
        data = request.get_json(force=True)
        vata_data = data.get('vata_data', [])
        pitta_data = data.get('pitta_data', [])
        kapha_data = data.get('kapha_data', [])

        if not all([vata_data, pitta_data, kapha_data]):
            return jsonify({'status': 'error', 'message': 'Insufficient data. Need at least 3 data points for each sensor.'}), 400

        vata_pattern = analyze_graph_pattern(vata_data)
        pitta_pattern = analyze_graph_pattern(pitta_data)
        kapha_pattern = analyze_graph_pattern(kapha_data)
        dosha_analysis = determine_dosha_from_graphs(vata_pattern, pitta_pattern, kapha_pattern)

        return jsonify({
            'status': 'ok',
            'dosha_type': dosha_analysis['dosha_type'],
            'confidence': dosha_analysis['confidence'],
            'scores': dosha_analysis['scores'],
            'pattern_analysis': {
                'vata': {
                    'pattern': vata_pattern['pattern_type'],
                    'speed': vata_pattern['speed'],
                    'variability': vata_pattern['variability'],
                    'regularity': vata_pattern['regularity'],
                    'smoothness': vata_pattern['smoothness'],
                    'mean_bpm': vata_pattern['mean_bpm']
                },
                'pitta': {
                    'pattern': pitta_pattern['pattern_type'],
                    'speed': pitta_pattern['speed'],
                    'variability': pitta_pattern['variability'],
                    'regularity': pitta_pattern['regularity'],
                    'smoothness': pitta_pattern['smoothness'],
                    'mean_bpm': pitta_pattern['mean_bpm']
                },
                'kapha': {
                    'pattern': kapha_pattern['pattern_type'],
                    'speed': kapha_pattern['speed'],
                    'variability': kapha_pattern['variability'],
                    'regularity': kapha_pattern['regularity'],
                    'smoothness': kapha_pattern['smoothness'],
                    'mean_bpm': kapha_pattern['mean_bpm']
                }
            },
            'interpretation': get_dosha_interpretation_from_graphs(dosha_analysis)
        })
    except Exception as e:
        print("Error in /analyze_graph_patterns:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500


@main_bp.route('/register_patient', methods=['POST'])
def register_patient():
    try:
        data = request.get_json(force=True)
        name = data.get('name', '').strip()
        gender = data.get('gender', '').strip()
        age = data.get('age', '').strip()

        if not name or not gender or not age:
            return jsonify({'status': 'error', 'message': 'All fields are required'}), 400

        try:
            age = int(age)
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Age must be a number'}), 400

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO patients (name, gender, age) VALUES (?, ?, ?)', (name, gender, age))
        patient_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({'status': 'ok', 'message': 'Patient registered successfully', 'patient_id': patient_id})
    except Exception as e:
        print("Error in /register_patient:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500


@main_bp.route('/save_prediction', methods=['POST'])
def save_prediction():
    try:
        data = request.get_json(force=True)
        patient_id = data.get('patient_id')
        prediction = data.get('prediction', '')
        accuracy = data.get('accuracy', 0.0)
        bpm1 = data.get('bpm1', 0)
        bpm2 = data.get('bpm2', 0)
        bpm3 = data.get('bpm3', 0)

        if not patient_id:
            return jsonify({'status': 'error', 'message': 'Patient ID is required'}), 400

        dosha_balance = latest_data.get('dosha_balance', {})
        dosha_info = latest_data.get('dosha_info', {})
        statistics = latest_data.get('statistics', {})

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE patients SET prediction = ?, accuracy = ?, bpm1 = ?, bpm2 = ?, bpm3 = ?, vata_balance = ?, pitta_balance = ?, kapha_balance = ?, dominant_dosha = ?, statistics = ? WHERE id = ?',
            (
                prediction, accuracy, bpm1, bpm2, bpm3,
                dosha_balance.get('vata', 0),
                dosha_balance.get('pitta', 0),
                dosha_balance.get('kapha', 0),
                dosha_info.get('dominant_dosha', 'Unknown') if dosha_info else 'Unknown',
                str(statistics), patient_id
            )
        )
        conn.commit()
        conn.close()

        return jsonify({'status': 'ok', 'message': 'Prediction saved successfully'})
    except Exception as e:
        print("Error in /save_prediction:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500


@main_bp.route('/get_patients', methods=['GET'])
def get_patients():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, gender, age, prediction, accuracy, bpm1, bpm2, bpm3, vata_balance, pitta_balance, kapha_balance, dominant_dosha, created_at FROM patients ORDER BY created_at DESC LIMIT 100')
        rows = cursor.fetchall()
        conn.close()

        patients = [
            {
                'id': row[0],
                'name': row[1],
                'gender': row[2],
                'age': row[3],
                'prediction': row[4] or 'N/A',
                'accuracy': row[5] or 0.0,
                'bpm1': row[6] or 0,
                'bpm2': row[7] or 0,
                'bpm3': row[8] or 0,
                'vata_balance': row[9] or 0,
                'pitta_balance': row[10] or 0,
                'kapha_balance': row[11] or 0,
                'dominant_dosha': row[12] or 'Unknown',
                'time': row[13] if row[13] else 'N/A'
            }
            for row in rows
        ]

        return jsonify({'status': 'ok', 'patients': patients})
    except Exception as e:
        print("Error in /get_patients:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500
