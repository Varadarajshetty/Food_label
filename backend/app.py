"""
Flask Backend API for AI Food Label Decoder
Provides prediction endpoints for nutrition analysis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from pathlib import Path
from werkzeug.utils import secure_filename

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from health_classifier import HealthClassifier, NutritionScorer
from disease_warnings import DiseaseWarningSystem, ExplanationGenerator
from ocr_processor import NutritionLabelOCR # Keeping for fallback if needed
from openai_ocr import OpenAIOCR
from openai_ocr import OpenAIOCR
from product_lookup import ProductSearch
from food_alternatives import AlternativeSuggester

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Enable CORS for frontend

# Configure upload folder
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

@app.route('/')
def serve_frontend():
    return app.send_static_file('index.html')

import logging

# Configure logging
logging.basicConfig(
    filename='backend.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize models
classifier = HealthClassifier()
scorer = NutritionScorer()
warning_system = DiseaseWarningSystem()
explainer = ExplanationGenerator()
ocr_processor = NutritionLabelOCR()
openai_ocr = OpenAIOCR()
ocr_processor = NutritionLabelOCR()
openai_ocr = OpenAIOCR()
product_searcher = ProductSearch()
suggester = AlternativeSuggester()

# Feature mapping
FEATURE_MAP = {
    'calories': 'calories',
    'protein': 'protein',
    'carbs': 'carbs',
    'fat': 'fat',
    'fiber': 'fiber',
    'sugar': 'sugar',
    'sodium': 'sodium',
    'cholesterol': 'cholesterol',
    'saturated_fat': 'saturated_fat',
}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'service': 'AI Food Label Decoder API',
        'version': '1.0.0',
        'features': ['text_input', 'image_upload']
    })


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint
    
    Expected JSON:
    {
        "calories": 250,
        "protein": 10,
        "carbs": 30,
        "fat": 8,
        "fiber": 3,
        "sugar": 12,
        "sodium": 400,
        "cholesterol": 50,
        "saturated_fat": 3
    }
    """
    try:
        # Get nutrition values from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['calories', 'protein', 'carbs', 'fat', 'sodium']
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Extract nutrition values
        nutrition_values = {
            'calories': float(data.get('calories', 0)),
            'protein': float(data.get('protein', 0)),
            'carbs': float(data.get('carbs', 0)),
            'fat': float(data.get('fat', 0)),
            'fiber': float(data.get('fiber', 0)),
            'sugar': float(data.get('sugar', 0)),
            'sodium': float(data.get('sodium', 0)),
            'cholesterol': float(data.get('cholesterol', 0)),
            'saturated_fat': float(data.get('saturated_fat', 0)),
        }
        
        # Classify food
        print(f"\n[DEBUG] Classification Input: {nutrition_values}")
        classification = classifier.classify_food(nutrition_values, FEATURE_MAP)
        print(f"[DEBUG] Result: {classification}")
        
        # Calculate nutrition score
        nutrition_score = scorer.calculate_score(nutrition_values, FEATURE_MAP)
        
        # Generate warnings
        warnings = warning_system.generate_warnings(nutrition_values)
        
        # Generate explanation
        explanation = explainer.generate_explanation(
            classification,
            nutrition_score,
            nutrition_values,
            warnings
        )
        
        # NEW: Detailed Scores & Traffic Lights
        detailed_score = scorer.calculate_detailed_score(nutrition_values, FEATURE_MAP)
        
        traffic_lights = {}
        for nutrient, value in nutrition_values.items():
            color = classifier.get_traffic_light(value, nutrient)
            if color != 'neutral':
                traffic_lights[nutrient] = color
                
        # NEW: Alternatives
        alternatives = []
        # Need product name for suggestions. In /predict, we might not have it unless sent.
        # User usually sends just numbers here. If 'name' is in body, use it.
        product_name = data.get('product_name', '')
        if classification == 'Avoid' and product_name:
            alternatives = suggester.suggest_alternatives(product_name)
        
        # Build response
        response = {
            'success': True,
            'classification': classification,
            'nutrition_score': nutrition_score,
            'detailed_score': detailed_score,
            'traffic_lights': traffic_lights,
            'alternatives': alternatives,
            'warnings': warnings,
            'explanation': explanation,
            'input_values': nutrition_values
        }
        
        return jsonify(response), 200
    
    except ValueError as e:
        return jsonify({'error': f'Invalid input values: {str(e)}'}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/batch-predict', methods=['POST'])
def batch_predict():
    """
    Batch prediction endpoint for multiple foods
    
    Expected JSON:
    {
        "foods": [
            {"name": "Food 1", "calories": 250, ...},
            {"name": "Food 2", "calories": 150, ...}
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'foods' not in data:
            return jsonify({'error': 'No foods provided'}), 400
        
        foods = data['foods']
        results = []
        
        for food in foods:
            food_name = food.get('name', 'Unknown')
            
            # Extract nutrition values
            nutrition_values = {
                'calories': float(food.get('calories', 0)),
                'protein': float(food.get('protein', 0)),
                'carbs': float(food.get('carbs', 0)),
                'fat': float(food.get('fat', 0)),
                'fiber': float(food.get('fiber', 0)),
                'sugar': float(food.get('sugar', 0)),
                'sodium': float(food.get('sodium', 0)),
                'cholesterol': float(food.get('cholesterol', 0)),
                'saturated_fat': float(food.get('saturated_fat', 0)),
            }
            
            # Classify
            classification = classifier.classify_food(nutrition_values, FEATURE_MAP)
            nutrition_score = scorer.calculate_score(nutrition_values, FEATURE_MAP)
            warnings = warning_system.generate_warnings(nutrition_values)
            
            results.append({
                'name': food_name,
                'classification': classification,
                'nutrition_score': nutrition_score,
                'warning_count': len(warnings)
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_foods': len(results)
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """
    Image upload endpoint for OCR processing
    
    Accepts image file and extracts nutrition values
    """
    try:
        logging.info("Received image upload request")
        
        # Check if file is present
        if 'image' not in request.files:
            logging.warning("No image file in request")
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            logging.warning("No filename selected")
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            logging.warning(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, bmp'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logging.info(f"File saved to {filepath}")
        print(f"\n[DEBUG] === STARTED PROCESSING IMAGE: {filename} ===")
        print(f"[DEBUG] File Path: {filepath}")
        
        # Process with OpenAI OCR
        try:
            # 1. Detect Label Type
            print("[DEBUG] Step 1: Detecting Label Type...")
            label_type = openai_ocr.detect_label_type(filepath)
            
            logging.info(f"Detected label type (OpenAI): {label_type}")
            print(f"[DEBUG] Step 1 Result: Detected label type: {label_type}")
            
            nutrition_values = None
            product_name = "Unknown Product"
            
            if label_type == 'nutrition_label':
                # Use OpenAI to extract nutrition values
                print("[DEBUG] Step 2: Extracting Nutrition (Table Mode)...")
                nutrition_values = openai_ocr.extract_nutrition(filepath)
                print(f"[DEBUG] Step 2 (Table) Result: {nutrition_values}")
                
                # Also attempt to get product name from nutrition label (often at the top)
                openai_name = openai_ocr.extract_product_name(filepath)
                if openai_name and openai_name.lower() != 'unknown':
                    product_name = openai_name
                else:
                    # Fallback to Tesseract if OpenAI doesn't find a name
                    tesseract_candidates = ocr_processor.extract_product_name(filepath)
                    if tesseract_candidates:
                        product_name = tesseract_candidates[0] # Take the top candidate

                print(f"DEBUG: Final Product Name: {product_name}")
                
                if not nutrition_values:
                    logging.warning("OpenAI OCR failed, falling back to Tesseract")
                    text, confidence = ocr_processor.extract_text(filepath)
                    nutrition_values = ocr_processor.extract_nutrition_values(text)
                    
                    if confidence < 60:
                        logging.warning(f"Low OCR confidence: {confidence}%")
                        # We can either error out or just add a warning flag
                        # For now, let's proceed but maybe add a warning to the response
                        if 'warnings' not in nutrition_values: 
                             # This dict is usually just numbers, warnings are separate list later
                             pass 
                             
                # Validate extraction
                if not nutrition_values or not ocr_processor.validate_extraction(nutrition_values):
                    logging.warning("OCR validation failed")
                    return jsonify({
                        'error': 'Could not extract valid nutrition data from image',
                        'suggestion': 'Image too blurry or text unclear. Please try re-uploading or enter manually.',
                        'confidence': locals().get('confidence', 0)
                    }), 400
            
            else:
                # Flow for Product Front
                print("[DEBUG] Processing as Product Front")
                
                # Use OpenAI to identify product name
                # Use OpenAI to identify product name
                print("[DEBUG] Step 2: Identifying Product Name (Front Mode)...")
                openai_name = openai_ocr.extract_product_name(filepath)
                logging.info(f"OpenAI identified product: {openai_name}")
                print(f"[DEBUG] Step 2 Result: Identified Name: {openai_name}")
                
                candidates = []
                if openai_name:
                    candidates.append(openai_name)
                
                # Fallback to Tesseract if OpenAI fails or to get more options
                tesseract_candidates = ocr_processor.extract_product_name(filepath)
                if tesseract_candidates:
                    candidates.extend(tesseract_candidates)
                
                if not candidates:
                    logging.warning("No candidates found for product name")
                    return jsonify({
                        'error': 'Could not identify product name',
                        'code': 'PRODUCT_NOT_FOUND_NEED_LABEL',
                        'suggestion': 'We could not read the product name. Please upload the Nutrition Facts label instead.'
                    }), 400
                
                # Try each candidate
                nutrition_values = None
                product_name = "Unknown"
                
                for candidate in candidates:
                    print(f"[DEBUG] Step 3: Searching API for candidate: {candidate}")
                    product_data = product_searcher.search_by_name(candidate)
                    print(f"[DEBUG] Step 3 Result for {candidate}: {'FOUND' if product_data else 'NOT FOUND'}")
                    
                    if product_data:
                        nutrition_values = product_data
                        product_name = candidate
                        logging.info(f"Product found via API match: {candidate}")
                        break
                
                if not nutrition_values:
                    logging.warning(f"Product not found for candidates: {candidates}")
                    return jsonify({
                        'error': f'Could not find nutrition data',
                        'code': 'PRODUCT_NOT_FOUND_NEED_LABEL',
                        'suggestion': f'We searched for "{candidates[0]}" but found nothing. Please upload the Nutrition Facts label instead.'
                    }), 400

            # Proceed with classification using the obtained nutrition_values (from OCR or API)
            
            # Classify food
            classification = classifier.classify_food(nutrition_values, FEATURE_MAP)
            nutrition_score = scorer.calculate_score(nutrition_values, FEATURE_MAP)
            warnings = warning_system.generate_warnings(nutrition_values)
            explanation = explainer.generate_explanation(
                classification,
                nutrition_score,
                nutrition_values,
                warnings
            )
            
            # NEW Features for Image Upload flow
            detailed_score = scorer.calculate_detailed_score(nutrition_values, FEATURE_MAP)
        
            traffic_lights = {}
            for nutrient, value in nutrition_values.items():
                color = classifier.get_traffic_light(value, nutrient)
                if color != 'neutral':
                    traffic_lights[nutrient] = color
                    
            alternatives = []
            if classification == 'Avoid' and product_name and product_name != "Unknown":
                 alternatives = suggester.suggest_alternatives(product_name)
                 print(f"[DEBUG] Alternatives for {product_name}: {alternatives}")
            
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
            
            print("[DEBUG] === FINISHED PROCESSING SUCCESSFULLY ===")
            logging.info("Processing successful")
            return jsonify({
                'success': True,
                'extracted_values': nutrition_values,
                'classification': classification,
                'classification': classification,
                'nutrition_score': nutrition_score,
                'detailed_score': detailed_score,
                'traffic_lights': traffic_lights,
                'alternatives': alternatives,
                'warnings': warnings,
                'explanation': explanation,
                'source': label_type,
                'product_name': product_name
            }), 200
        
        except Exception as ocr_error:
            # Clean up file on error
            if os.path.exists(filepath):
                os.remove(filepath)
            
            logging.error(f"Processing failed: {str(ocr_error)}", exc_info=True)
            print(f"[ERROR] Processing failed: {str(ocr_error)}")
            return jsonify({
                'error': f'Processing failed: {str(ocr_error)}',
                'suggestion': 'Please try a clearer image or enter values manually'
            }), 400
    
    except Exception as e:
        logging.critical(f"Server crash in upload_image: {str(e)}", exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}'}), 500


if __name__ == '__main__':
    print("="*80)
    print("AI FOOD LABEL DECODER API")
    print("="*80)
    print("\nStarting server...")
    print("API will be available at: http://localhost:5000")
    print("\nEndpoints:")
    print("  GET  /                  - Health check")
    print("  POST /api/predict       - Single food prediction")
    print("  POST /api/upload-image  - Image upload with OCR")
    print("  POST /api/batch-predict - Batch prediction")
    print("\n" + "="*80)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
