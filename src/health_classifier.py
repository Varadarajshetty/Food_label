"""
Health Classification Rules and Scoring Logic
Defines criteria for classifying foods as Healthy/Limit/Avoid
"""

import pandas as pd
import numpy as np
from pathlib import Path


class HealthClassifier:
    """
    Classify foods based on nutrition thresholds
    
    Classification Criteria:
    - HEALTHY: Nutrient-dense, low in harmful components
    - LIMIT: Moderate nutrition, consume occasionally  
    - AVOID: High in harmful components, low nutritional value
    """
    
    
    def __init__(self):
        # Define thresholds based on general nutrition guidelines
        self.thresholds = {
            'sodium': {
                'healthy': 140,    # Low sodium: <140mg
                'limit': 300,      # Moderate: 140-300mg (Tightened from 400)
                'avoid': 300       # High: >300mg
            },
            'sugar': {
                'healthy': 5,      # Low sugar: <5g
                'limit': 15,       # Moderate: 5-15g
                'avoid': 15        # High: >15g
            },
            'saturated_fat': {
                'healthy': 1.5,    # Low sat fat: <1.5g (Tightened from 2)
                'limit': 4,        # Moderate: 1.5-4g (Tightened from 5)
                'avoid': 4         # High: >4g
            },
            'fiber': {
                'good': 3,         # Good fiber: >3g
                'excellent': 5     # Excellent: >5g
            },
            'protein': {
                'good': 5,         # Good protein: >5g
                'excellent': 10    # Excellent: >10g
            },
            'calories': {
                'low': 100,
                'moderate': 250,
                'high': 400
            }
        }
        
        # Load ML Model
        import joblib
        self.model_data = None
        try:
            model_path = Path(__file__).parent.parent / 'models' / 'health_classifier.joblib'
            if model_path.exists():
                self.model_data = joblib.load(model_path)
                print("[INFO] Loaded ML Model")
            else:
                print("[WARN] ML Model not found, using rules")
        except Exception as e:
            print(f"[ERROR] Failed to load ML model: {e}")
    
    def classify_food(self, row, feature_map):
        """
        Classify a single food item
        
        Returns: 'Healthy', 'Limit', or 'Avoid'
        """
        # Try ML Model first
        if self.model_data:
            try:
                model = self.model_data['model']
                encoder = self.model_data['encoder']
                features = self.model_data['features']
                
                # prepare input vector
                input_vector = []
                for feat in features:
                    # Map 'Caloric Value' -> 'calories' from input
                    # We need reverse mapping or direct lookup
                    # The input 'row' uses keys like 'calories', 'protein'
                    # The model expects 'Caloric Value', 'Protein'
                    
                    # Manual mapping to model features
                    val = 0
                    if feat == 'Caloric Value': val = row.get('calories', 0)
                    elif feat == 'Protein': val = row.get('protein', 0)
                    elif feat == 'Carbohydrates': val = row.get('carbs', 0)
                    elif feat == 'Fat': val = row.get('fat', 0)
                    elif feat == 'Sodium': val = row.get('sodium', 0)
                    elif feat == 'Sugars': val = row.get('sugar', 0)
                    elif feat == 'Saturated Fats': val = row.get('saturated_fat', 0)
                    elif feat == 'Dietary Fiber': val = row.get('fiber', 0)
                    
                    input_vector.append(val)
                
                prediction_idx = model.predict([input_vector])[0]
                prediction = encoder.inverse_transform([prediction_idx])[0]
                print(f"[INFO] ML Prediction: {prediction}")
                return prediction
            
            except Exception as e:
                print(f"[ERROR] ML prediction failed: {e}")
                # Fallback to rules
        
        print("[INFO] Using Rule-based Classification")
        
        score = 0  # Positive score = healthy, negative = unhealthy
        
        # Get values
        sodium = row.get(feature_map.get('sodium', ''), 0)
        sugar = row.get(feature_map.get('sugar', ''), 0)
        sat_fat = row.get(feature_map.get('saturated_fat', ''), 0)
        fiber = row.get(feature_map.get('fiber', ''), 0)
        protein = row.get(feature_map.get('protein', ''), 0)
        calories = row.get(feature_map.get('calories', ''), 0)
        
        # Negative factors (reduce score)
        # Penalize high values heavily, do NOT reward low values (0 points)
        if sodium > self.thresholds['sodium']['avoid']:
            score -= 3
        elif sodium > self.thresholds['sodium']['limit']:
            score -= 1
        
        if sugar > self.thresholds['sugar']['avoid']:
            score -= 3
        elif sugar > self.thresholds['sugar']['limit']:
            score -= 1
        
        if sat_fat > self.thresholds['saturated_fat']['avoid']:
            score -= 2
        elif sat_fat > self.thresholds['saturated_fat']['limit']:
            score -= 1
        
        # Positive factors (increase score)
        # Only significant nutritional value adds points
        if fiber >= self.thresholds['fiber']['excellent']:
            score += 2
        elif fiber >= self.thresholds['fiber']['good']:
            score += 1
        
        if protein >= self.thresholds['protein']['excellent']:
            score += 2
        elif protein >= self.thresholds['protein']['good']:
            score += 1
        
        # Empty Calorie Penalty (Density Based)
        # Calculate nutrient density per 100 calories
        if calories > 0:
            protein_density = (protein / calories) * 100
            fiber_density = (fiber / calories) * 100
        else:
            protein_density = 0
            fiber_density = 0
            
        # If food has calories (>50) but low density (Prot < 2g/100cal AND Fiber < 1g/100cal)
        if calories > 50 and (protein_density < 2 and fiber_density < 1):
            score -= 2
            
        # Logging for debug
        print(f"  [DEBUG] Score: {score} | Na:{sodium} Sug:{sugar} SatFat:{sat_fat} Prot:{protein} Fib:{fiber} Cal:{calories}")
        
        # Calorie consideration
        if calories > self.thresholds['calories']['high']:
            score -= 1
        
        # Final classification logic
        # Stricter: Needs positive score to be Healthy
        if score >= 2:
            return 'Healthy'
        elif score >= -1:
            return 'Limit'
        else:
            return 'Avoid'
    
    def classify_dataset_rules(self, data, feature_map):
        """Helper to run rules on dataset (for initial training fallback)"""
         # .. implementation of old classify_dataset logic just for training script usage if needed ...
        classifications = []
        for idx, row in data.iterrows():
            # Use internal rule logic (copy-pasted from old classify_food to avoid recursion if we call classify_food which now calls ML)
            # Actually, for training script we can just use the rule logic directly.
            # But simpler: Just temporarily disable ML to generate labels.
            pass 
        return data # Placeholder, handled in train_model.py via direct instantiation or different method

    def classify_dataset(self, data, feature_map):
        """Classify all foods in dataset"""
        classifications = []
        
        for idx, row in data.iterrows():
            classification = self.classify_food(row, feature_map)
            classifications.append(classification)
        
        data['health_label'] = classifications
        
        # Print distribution
        print("\nHealth Classification Distribution:")
        print(data['health_label'].value_counts())
        print(f"\nPercentages:")
        print(data['health_label'].value_counts(normalize=True) * 100)
        
        return data
    
    def get_traffic_light(self, value, nutrient):
        """
        Get traffic light color for a nutrient value
        Returns: 'low', 'med', 'high' (mapping to green, yellow, red)
        """
        # Map nutrient names to threshold keys
        key_map = {
            'sodium': 'sodium',
            'sugar': 'sugar',
            'saturated_fat': 'saturated_fat',
            'fat': None, # No strict threshold defined yet
            'protein': 'protein',
            'fiber': 'fiber'
        }
        
        key = key_map.get(nutrient)
        if not key or key not in self.thresholds:
            return 'neutral'
            
        t = self.thresholds[key]
        
        # Logic for "Limit" nutrients (Less is better)
        if nutrient in ['sodium', 'sugar', 'saturated_fat']:
            if value <= t['healthy']:
                return 'green'
            elif value <= t['limit']:
                return 'yellow'
            else:
                return 'red'
                
        # Logic for "Good" nutrients (More is better)
        if nutrient in ['protein', 'fiber']:
            if value >= t['excellent']:
                return 'green'
            elif value >= t['good']:
                return 'yellow'
            else:
                return 'red' # Or maybe orange/neutral? Let's say red for very low if key
                
        return 'neutral'


class NutritionScorer:
    """Calculate nutrition score (0-100)"""
    
    def __init__(self):
        # Weights for different components
        self.weights = {
            'protein': 0.15,
            'fiber': 0.15,
            'vitamins': 0.10,
            'sodium_penalty': 0.20,
            'sugar_penalty': 0.20,
            'sat_fat_penalty': 0.15,
            'balance': 0.05
        }
    
    def calculate_score(self, row, feature_map):
        """
        Calculate nutrition score (0-100)
        Higher is better
        """
        score = 50  # Start at neutral
        
        # Get values
        sodium = row.get(feature_map.get('sodium', ''), 0)
        sugar = row.get(feature_map.get('sugar', ''), 0)
        sat_fat = row.get(feature_map.get('saturated_fat', ''), 0)
        fiber = row.get(feature_map.get('fiber', ''), 0)
        protein = row.get(feature_map.get('protein', ''), 0)
        
        # Positive contributions
        protein_score = min(protein / 20 * 15, 15)  # Max 15 points
        fiber_score = min(fiber / 10 * 15, 15)      # Max 15 points
        
        # Negative contributions
        sodium_penalty = min(sodium / 2000 * 20, 20)  # Max -20 points
        sugar_penalty = min(sugar / 50 * 20, 20)      # Max -20 points
        sat_fat_penalty = min(sat_fat / 20 * 15, 15)  # Max -15 points
        
        # Calculate final score
        final_score = (score + 
                      protein_score + 
                      fiber_score - 
                      sodium_penalty - 
                      sugar_penalty - 
                      sat_fat_penalty)
        
        # Ensure 0-100 range
        final_score = max(0, min(100, final_score))
        
        return round(final_score, 1)
    
    def score_dataset(self, data, feature_map):
        """Calculate scores for all foods"""
        scores = []
        
        for idx, row in data.iterrows():
            score = self.calculate_score(row, feature_map)
            scores.append(score)
        
        data['nutrition_score'] = scores
        
        print(f"\nNutrition Score Statistics:")
        print(f"  Mean: {data['nutrition_score'].mean():.1f}")
        print(f"  Median: {data['nutrition_score'].median():.1f}")
        print(f"  Min: {data['nutrition_score'].min():.1f}")
        print(f"  Max: {data['nutrition_score'].max():.1f}")
        
        return data

    def calculate_detailed_score(self, row, feature_map):
        """
        Calculate detailed score components
        Returns: dict with total, quality_score, risk_score
        """
        # Get values
        sodium = row.get(feature_map.get('sodium', ''), 0)
        sugar = row.get(feature_map.get('sugar', ''), 0)
        sat_fat = row.get(feature_map.get('saturated_fat', ''), 0)
        fiber = row.get(feature_map.get('fiber', ''), 0)
        protein = row.get(feature_map.get('protein', ''), 0)
        
        # 1. Quality Score (0-100) based on positive nutrients
        # normalized to be impactful
        prot_pts = min(protein / 20 * 50, 50) # Max 50
        fiber_pts = min(fiber / 10 * 50, 50)  # Max 50
        quality_score = prot_pts + fiber_pts
        
        # 2. Risk Score (0-100) based on negative nutrients (Higher is riskier)
        # normalized
        sod_risk = min(sodium / 1000 * 33, 33) 
        sug_risk = min(sugar / 20 * 34, 34)
        sat_risk = min(sat_fat / 10 * 33, 33)
        risk_score = sod_risk + sug_risk + sat_risk
        
        # 3. Total Score (0-100)
        # Base 70, + Quality/2 - Risk/2
        # Use existing calculation for consistency or upgrade?
        # Let's use the new granular components to perform a weighted score
        total_score = 70 + (quality_score * 0.4) - (risk_score * 0.6)
        total_score = max(0, min(100, total_score))
        
        return {
            'total': round(total_score, 1),
            'quality': round(quality_score, 1),
            'risk': round(risk_score, 1)
        }


def main():
    """Test classification and scoring"""
    # Load engineered data
    data_file = Path('Dataset/engineered_food_data.csv')
    if not data_file.exists():
        print("Error: Run feature_engineering.py first!")
        return
    
    data = pd.read_csv(data_file)
    print(f"Loaded {len(data)} food items")
    
    # Map features
    feature_map = {
        'calories': 'Caloric Value',
        'protein': 'Protein',
        'carbs': 'Carbohydrates',
        'fat': 'Fat',
        'fiber': 'Dietary Fiber',
        'sugar': 'Sugars',
        'sodium': 'Sodium',
        'cholesterol': 'Cholesterol',
        'saturated_fat': 'Saturated Fats',
    }
    
    # Classify foods
    classifier = HealthClassifier()
    data = classifier.classify_dataset(data, feature_map)
    
    # Calculate nutrition scores
    scorer = NutritionScorer()
    data = scorer.score_dataset(data, feature_map)
    
    # Show examples
    print("\n" + "="*80)
    print("SAMPLE CLASSIFICATIONS")
    print("="*80)
    
    for label in ['Healthy', 'Limit', 'Avoid']:
        print(f"\n{label} Foods (sample):")
        sample = data[data['health_label'] == label].head(3)
        for idx, row in sample.iterrows():
            food_name = row.get('food', row.get('Food_Item', 'Unknown'))
            score = row['nutrition_score']
            print(f"  - {food_name}: Score {score}")
    
    # Save
    output_file = Path('Dataset/classified_food_data.csv')
    data.to_csv(output_file, index=False)
    print(f"\n✓ Saved to: {output_file}")
    
    return data


if __name__ == "__main__":
    data = main()
