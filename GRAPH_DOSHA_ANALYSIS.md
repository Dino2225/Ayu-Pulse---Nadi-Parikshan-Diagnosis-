# Graph-Based Dosha Type Analysis

## Overview
The system now analyzes pulse graph patterns from the observed charts to determine dosha types (Vata, Pitta, Kapha) based on traditional Nadi Parikshan principles.

## Traditional Nadi Parikshan Patterns

### 1. **Vata (Snake-like / Sarpa)**
- **Characteristics**: Fast, irregular, erratic pulse
- **Graph Pattern**: High variability, low regularity, irregular waveform
- **BPM Range**: Typically >75 bpm
- **Variability**: High (>12% coefficient of variation)
- **Indications**: Anxiety, restlessness, nervous system issues

### 2. **Pitta (Frog-like / Manduka)**
- **Characteristics**: Moderate speed, strong, regular pulse
- **Graph Pattern**: Moderate variability, balanced regularity, consistent waveform
- **BPM Range**: 60-85 bpm
- **Variability**: Moderate (5-12% coefficient of variation)
- **Indications**: Good metabolism, watch for excess heat

### 3. **Kapha (Swan-like / Hamsa)**
- **Characteristics**: Slow, steady, smooth pulse
- **Graph Pattern**: Low variability, high regularity, smooth waveform
- **BPM Range**: Typically <70 bpm
- **Variability**: Low (<8% coefficient of variation)
- **Indications**: Stability, but watch for sluggishness

## Analysis Algorithm

### Pattern Analysis Features:
1. **Speed Score**: Based on mean BPM
   - Slow (<60): 0.2 (Kapha)
   - Moderate (60-80): 0.5 (Pitta)
   - Fast (>80): 0.8 (Vata)

2. **Variability**: Coefficient of variation (std/mean)
   - High variability → Vata pattern
   - Moderate variability → Pitta pattern
   - Low variability → Kapha pattern

3. **Regularity**: Inverse of variability
   - Low regularity → Vata (irregular)
   - Moderate regularity → Pitta (balanced)
   - High regularity → Kapha (steady)

4. **Smoothness**: Based on rate of change
   - Low smoothness → Vata (erratic)
   - Moderate smoothness → Pitta (balanced)
   - High smoothness → Kapha (smooth)

### Scoring System:
Each dosha is scored based on:
- Pattern type match: +3 points
- Variability match: +2 points
- Regularity match: +2 points
- Speed match: +1 point

**Total possible: 8 points per dosha**

The dosha with the highest score is determined as the dominant type.

## API Endpoints

### 1. Automatic Analysis (Built-in)
The `/update_bpm` endpoint now automatically analyzes graph patterns from the reading buffer and includes results in the response:

```json
{
  "graph_dosha_analysis": {
    "dosha_type": "Vata",
    "confidence": 75.5,
    "scores": {
      "Vata": 6,
      "Pitta": 2,
      "Kapha": 0
    },
    "interpretation": {
      "pattern_name": "Snake-like (Sarpa)",
      "characteristics": "Fast, irregular, erratic pulse pattern",
      "indications": "...",
      "recommendation": "..."
    },
    "patterns": {
      "vata": {...},
      "pitta": {...},
      "kapha": {...}
    }
  }
}
```

### 2. Manual Analysis Endpoint
`POST /analyze_graph_patterns`

Send chart data points:
```json
{
  "vata_data": [75, 78, 72, 80, 76],
  "pitta_data": [82, 81, 83, 82, 81],
  "kapha_data": [68, 69, 67, 68, 69]
}
```

Returns detailed pattern analysis.

## Frontend Display

The dashboard now shows:
1. **Dosha Type Card**: Displays the determined dosha type from graph analysis
2. **Pattern Name**: Shows traditional pattern name (Snake/Frog/Swan)
3. **Confidence Level**: Percentage confidence in the determination
4. **Pattern Details**: Individual sensor analysis with:
   - Mean BPM
   - Variability percentage
   - Pattern type

## Data Requirements

- **Minimum**: 3 data points per sensor
- **Optimal**: 10+ data points for accurate analysis
- **Best**: 30 data points (full buffer)

## Accuracy Factors

1. **Data Quality**: More readings = better accuracy
2. **Pattern Clarity**: Clear patterns = higher confidence
3. **Sensor Stability**: Consistent readings improve analysis
4. **Time Window**: Longer observation period = better pattern recognition

## Example Scenarios

### Scenario 1: Vata Dominant
- Vata sensor: High variability (15%), irregular pattern, fast (78 bpm)
- Pitta sensor: Moderate (82 bpm, 8% variability)
- Kapha sensor: Low variability (5%, 68 bpm)
- **Result**: Vata type with high confidence

### Scenario 2: Pitta Dominant
- All sensors: Moderate variability (6-10%), balanced patterns
- BPM ranges: 70-85 across sensors
- **Result**: Pitta type with moderate confidence

### Scenario 3: Kapha Dominant
- All sensors: Low variability (<8%), smooth patterns
- BPM ranges: 60-70, slow and steady
- **Result**: Kapha type with high confidence

## Integration

The graph analysis runs automatically:
1. Every time new BPM data is received
2. Analyzes the last 30 readings from the buffer
3. Updates the display in real-time
4. Provides confidence scores and interpretations

## Benefits

1. **Traditional Accuracy**: Based on authentic Nadi Parikshan principles
2. **Real-time Analysis**: Continuous pattern monitoring
3. **Visual Confirmation**: Graph patterns match dosha characteristics
4. **Detailed Insights**: Provides specific recommendations
5. **Confidence Scoring**: Shows reliability of determination

