from flask import Flask, render_template, request, jsonify, send_from_directory
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'krishimitra-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Load AI model
model = tf.keras.models.load_model('plant_disease_model.h5')
class_names = [
    'Pepper Bacterial Spot', 'Pepper Healthy', 'Potato Early Blight',
    'Potato Late Blight', 'Potato Healthy', 'Tomato Bacterial Spot',
    'Tomato Early Blight', 'Tomato Late Blight', 'Tomato Leaf Mold',
    'Tomato Septoria Leaf Spot', 'Tomato Spider Mites', 
    'Tomato Target Spot', 'Tomato Yellow Leaf Curl Virus',
    'Tomato Mosaic Virus', 'Tomato Healthy'
]

# COMPLETE Treatment advice database for all 15 diseases
TREATMENT_ADVICE = {
    'Pepper Bacterial Spot': {
        'urgency': 'high',
        'steps': [
            'Apply copper-based bactericides every 7-10 days',
            'Remove and destroy severely infected plants',
            'Avoid overhead watering to prevent spread',
            'Use disease-free seeds and transplants',
            'Practice 2-3 year crop rotation'
        ],
        'prevention': 'Use resistant varieties and avoid working with plants when wet'
    },
    'Pepper Healthy': {
        'urgency': 'none',
        'message': 'Your pepper plants are healthy! Maintain good spacing and watering practices.'
    },
    'Potato Early Blight': {
        'urgency': 'medium',
        'steps': [
            'Apply fungicides containing chlorothalonil or mancozeb',
            'Remove infected lower leaves',
            'Water at base of plants (avoid wetting foliage)',
            'Apply mulch to prevent soil splashing',
            'Ensure proper plant spacing for air circulation'
        ],
        'prevention': 'Use certified disease-free seed potatoes'
    },
    'Potato Late Blight': {
        'urgency': 'high',
        'steps': [
            'Apply copper-based fungicides immediately',
            'Remove and destroy all infected plants',
            'Do not compost infected plant material',
            'Avoid overhead irrigation',
            'Harvest potatoes carefully to avoid bruising'
        ],
        'prevention': 'Plant resistant varieties and practice crop rotation'
    },
    'Potato Healthy': {
        'urgency': 'none', 
        'message': 'Your potato plants are healthy! Continue proper hilling and watering practices.'
    },
    'Tomato Bacterial Spot': {
        'urgency': 'high',
        'steps': [
            'Apply copper sprays every 7-10 days',
            'Remove severely infected plants',
            'Avoid working with plants when wet',
            'Use drip irrigation instead of overhead watering',
            'Sterilize tools between plants'
        ],
        'prevention': 'Use disease-free seeds and resistant varieties'
    },
    'Tomato Early Blight': {
        'urgency': 'medium',
        'steps': [
            'Apply fungicides containing chlorothalonil',
            'Remove lower infected leaves',
            'Water at base of plants (avoid wetting leaves)',
            'Apply organic mulch around plants',
            'Improve air circulation through proper spacing'
        ],
        'prevention': 'Rotate crops and remove plant debris after harvest'
    },
    'Tomato Late Blight': {
        'urgency': 'high',
        'steps': [
            'Apply copper-based fungicides immediately',
            'Remove and destroy all infected plants',
            'Avoid overhead watering',
            'Improve air circulation around plants',
            'Do not compost infected plant material'
        ],
        'prevention': 'Use resistant varieties and practice crop rotation'
    },
    'Tomato Leaf Mold': {
        'urgency': 'medium',
        'steps': [
            'Apply fungicides containing chlorothalonil',
            'Remove infected leaves promptly',
            'Reduce humidity in greenhouse environments',
            'Improve air circulation around plants',
            'Water plants in the morning only'
        ],
        'prevention': 'Use resistant varieties and avoid overcrowding'
    },
    'Tomato Septoria Leaf Spot': {
        'urgency': 'medium',
        'steps': [
            'Apply copper-based fungicides',
            'Remove infected lower leaves',
            'Avoid overhead watering',
            'Apply mulch to prevent soil splashing',
            'Sterilize tools between plants'
        ],
        'prevention': 'Practice crop rotation and remove plant debris'
    },
    'Tomato Spider Mites': {
        'urgency': 'medium',
        'steps': [
            'Apply insecticidal soap or neem oil',
            'Spray plants with strong water jet to dislodge mites',
            'Introduce predatory mites for biological control',
            'Remove severely infested leaves',
            'Increase humidity around plants'
        ],
        'prevention': 'Monitor plants regularly and maintain plant health'
    },
    'Tomato Target Spot': {
        'urgency': 'medium',
        'steps': [
            'Apply fungicides containing chlorothalonil',
            'Remove infected leaves and fruits',
            'Improve air circulation',
            'Avoid overhead watering',
            'Practice proper sanitation'
        ],
        'prevention': 'Use resistant varieties and rotate crops'
    },
    'Tomato Yellow Leaf Curl Virus': {
        'urgency': 'high',
        'steps': [
            'Remove and destroy infected plants immediately',
            'Control whitefly populations with insecticides',
            'Use yellow sticky traps to monitor whiteflies',
            'Plant virus-free transplants',
            'Use reflective mulches to deter whiteflies'
        ],
        'prevention': 'Use resistant varieties and practice good sanitation'
    },
    'Tomato Mosaic Virus': {
        'urgency': 'high',
        'steps': [
            'Remove and destroy infected plants',
            'Wash hands thoroughly after handling plants',
            'Sterilize tools with bleach solution',
            'Control aphid populations',
            'Do not smoke around tomato plants'
        ],
        'prevention': 'Use virus-free seeds and resistant varieties'
    },
    'Tomato Healthy': {
        'urgency': 'none',
        'message': 'Your tomato plants are healthy! Continue good practices like regular watering, proper spacing, and balanced fertilization.'
    }
}

def predict_disease(img_path):
    """Predict plant disease from image"""
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    
    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions[0])
    confidence = float(predictions[0][predicted_class])
    
    return class_names[predicted_class], confidence

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Make prediction
        disease, confidence = predict_disease(filepath)
        
        # Get treatment advice - SPECIFIC FOR EACH DISEASE
        advice = TREATMENT_ADVICE.get(disease)
        
        # Safety check - should never be needed with complete database
        if not advice:
            advice = {
                'urgency': 'medium',
                'steps': ['Consult agricultural expert for specific treatment'],
                'prevention': 'Practice crop rotation and maintain field hygiene'
            }
        
        return jsonify({
            'success': True,
            'disease': disease,
            'confidence': confidence,
            'image_url': f'/uploads/{filename}',
            'advice': advice
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Simple chatbot API"""
    data = request.json
    question = data.get('question', '').lower()
    
    # Simple response system
    responses = {
        'fertilizer': 'For balanced nutrition, use NPK 10:10:10. Adjust based on soil test results.',
        'watering': 'Water deeply 2-3 times per week. Avoid overwatering to prevent root rot.',
        'pesticide': 'Use neem oil as organic pesticide. For severe infections, consult local experts.',
        'weather': 'Check local weather forecasts. Protect plants during extreme conditions.',
        'default': 'I recommend consulting with local agricultural experts for specific advice tailored to your farm.'
    }
    
    for key in responses:
        if key in question:
            return jsonify({'response': responses[key]})
    
    return jsonify({'response': responses['default']})

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)