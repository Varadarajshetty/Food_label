"""
Disease-Specific Warning System
Generates personalized health warnings based on nutrition values
"""

import pandas as pd
import numpy as np


class DiseaseWarningSystem:
    """Generate disease-specific warnings based on nutrition content"""
    
    def __init__(self):
        # Define disease-specific thresholds
        self.disease_rules = {
            'diabetes': {
                'sugar': {'threshold': 15, 'severity': 'high'},
                'carbs': {'threshold': 45, 'severity': 'moderate'},
                'fiber': {'threshold': 3, 'beneficial': True}
            },
            'hypertension': {
                'sodium': {'threshold': 400, 'severity': 'high'},
                'potassium': {'threshold': 200, 'beneficial': True}
            },
            'heart_disease': {
                'saturated_fat': {'threshold': 5, 'severity': 'high'},
                'cholesterol': {'threshold': 100, 'severity': 'moderate'},
                'fiber': {'threshold': 5, 'beneficial': True}
            },
            'obesity': {
                'calories': {'threshold': 300, 'severity': 'moderate'},
                'fat': {'threshold': 15, 'severity': 'moderate'},
                'fiber': {'threshold': 5, 'beneficial': True}
            },
            'kidney_disease': {
                'sodium': {'threshold': 300, 'severity': 'high'},
                'protein': {'threshold': 15, 'severity': 'moderate'},
                'potassium': {'threshold': 300, 'severity': 'moderate'}
            }
        }
    
    def generate_warnings(self, nutrition_values):
        """
        Generate warnings for all relevant diseases
        
        Args:
            nutrition_values: dict with nutrition information
            
        Returns:
            list of warning dictionaries
        """
        warnings = []
        
        for disease, rules in self.disease_rules.items():
            warning = self._check_disease(disease, rules, nutrition_values)
            if warning:
                warnings.append(warning)
        
        return warnings
    
    def _check_disease(self, disease_name, rules, nutrition_values):
        """Check if food triggers warnings for specific disease"""
        triggers = []
        benefits = []
        
        for nutrient, rule in rules.items():
            value = nutrition_values.get(nutrient, 0)
            
            if value == 0:
                continue
            
            # Check if beneficial
            if rule.get('beneficial'):
                if value >= rule.get('threshold', 0):
                    benefits.append(f"Good {nutrient} content ({value}g)")
                continue
            
            # Check if exceeds threshold
            threshold = rule.get('threshold', 0)
            severity = rule.get('severity', 'moderate')
            
            if value > threshold:
                triggers.append({
                    'nutrient': nutrient,
                    'value': value,
                    'threshold': threshold,
                    'severity': severity
                })
        
        # Generate warning if triggers found
        if triggers:
            return {
                'disease': disease_name,
                'severity': self._get_max_severity(triggers),
                'triggers': triggers,
                'benefits': benefits,
                'message': self._generate_message(disease_name, triggers, benefits)
            }
        
        return None
    
    def _get_max_severity(self, triggers):
        """Get maximum severity from triggers"""
        severity_order = {'low': 1, 'moderate': 2, 'high': 3}
        max_severity = 'low'
        
        for trigger in triggers:
            if severity_order.get(trigger['severity'], 0) > severity_order.get(max_severity, 0):
                max_severity = trigger['severity']
        
        return max_severity
    
    def _generate_message(self, disease, triggers, benefits):
        """Generate human-readable warning message"""
        disease_names = {
            'diabetes': 'Diabetes',
            'hypertension': 'High Blood Pressure',
            'heart_disease': 'Heart Disease',
            'obesity': 'Weight Management',
            'kidney_disease': 'Kidney Disease'
        }
        
        disease_display = disease_names.get(disease, disease.replace('_', ' ').title())
        
        # Build message
        msg_parts = []
        
        if triggers:
            trigger_nutrients = [t['nutrient'].replace('_', ' ').title() for t in triggers]
            msg_parts.append(f"⚠️ High in {', '.join(trigger_nutrients)}")
        
        if benefits:
            msg_parts.append(f"✓ {', '.join(benefits)}")
        
        message = f"{disease_display}: {' | '.join(msg_parts)}"
        
        return message


class ExplanationGenerator:
    """Generate simple, clear explanations for classifications"""
    
    def __init__(self):
        self.templates = {
            'Healthy': [
                "This food is nutritious and can be part of a healthy diet.",
                "Good balance of nutrients with low harmful components.",
                "Recommended for regular consumption."
            ],
            'Limit': [
                "This food has moderate nutrition. Consume occasionally.",
                "Some beneficial nutrients but also contains components to watch.",
                "Okay in moderation as part of a balanced diet."
            ],
            'Avoid': [
                "This food is high in unhealthy components.",
                "Low nutritional value with high levels of harmful ingredients.",
                "Best to avoid or consume very rarely."
            ]
        }
    
    def generate_explanation(self, classification, nutrition_score, nutrition_values, warnings):
        """
        Generate comprehensive explanation
        
        Returns:
            dict with explanation components
        """
        explanation = {
            'classification': classification,
            'score': nutrition_score,
            'summary': self._get_summary(classification),
            'key_points': self._get_key_points(nutrition_values),
            'recommendations': self._get_recommendations(classification, warnings),
            'warnings': warnings
        }
        
        return explanation
    
    def _get_summary(self, classification):
        """Get summary text for classification"""
        return self.templates.get(classification, ['Unknown classification'])[0]
    
    def _get_key_points(self, nutrition_values):
        """Identify key nutritional points"""
        points = []
        
        # Positive points
        if nutrition_values.get('protein', 0) >= 10:
            points.append(f"✓ High protein ({nutrition_values['protein']}g)")
        
        if nutrition_values.get('fiber', 0) >= 5:
            points.append(f"✓ Excellent fiber ({nutrition_values['fiber']}g)")
        
        # Negative points
        if nutrition_values.get('sodium', 0) > 400:
            points.append(f"⚠ High sodium ({nutrition_values['sodium']}mg)")
        
        if nutrition_values.get('sugar', 0) > 15:
            points.append(f"⚠ High sugar ({nutrition_values['sugar']}g)")
        
        if nutrition_values.get('saturated_fat', 0) > 5:
            points.append(f"⚠ High saturated fat ({nutrition_values['saturated_fat']}g)")
        
        return points
    
    def _get_recommendations(self, classification, warnings):
        """Generate actionable recommendations"""
        recommendations = []
        
        if classification == 'Healthy':
            recommendations.append("Great choice! This food supports a healthy diet.")
            recommendations.append("Can be consumed regularly as part of balanced meals.")
        
        elif classification == 'Limit':
            recommendations.append("Consume in moderation.")
            recommendations.append("Balance with healthier options throughout the day.")
            
            if warnings:
                recommendations.append("Be mindful if you have specific health conditions.")
        
        else:  # Avoid
            recommendations.append("Consider healthier alternatives.")
            recommendations.append("If consumed, keep portions very small.")
            
            if warnings:
                recommendations.append("Especially important to avoid if you have the listed health conditions.")

        # Add specific nutrition-based advice
        if warnings:
            for warning in warnings:
                for trigger in warning['triggers']:
                    if trigger['nutrient'] == 'sodium':
                        recommendations.append("Try flavoring food with herbs, spices, or lemon instead of salt.")
                    elif trigger['nutrient'] in ['saturated_fat', 'fat']:
                        recommendations.append("Consider replacing with foods high in heart-healthy fats like avocados or nuts.")
                    elif trigger['nutrient'] == 'sugar':
                        recommendations.append("Opt for whole fruits or water to satisfy cravings instead of sugary processed items.")
        
        # Unique set of recommendations
        recommendations = list(dict.fromkeys(recommendations))
        
        return recommendations[:5] # Limit to top 5 most relevant


def test_warning_system():
    """Test the warning system with sample data"""
    print("="*80)
    print("DISEASE WARNING SYSTEM TEST")
    print("="*80)
    
    # Test cases
    test_foods = [
        {
            'name': 'Soda',
            'values': {
                'calories': 140,
                'sugar': 39,
                'sodium': 45,
                'protein': 0,
                'fiber': 0,
                'saturated_fat': 0,
                'cholesterol': 0
            }
        },
        {
            'name': 'Grilled Chicken Salad',
            'values': {
                'calories': 350,
                'sugar': 4,
                'sodium': 400,
                'protein': 30,
                'fiber': 5,
                'saturated_fat': 2,
                'cholesterol': 80
            }
        },
        {
            'name': 'Bacon',
            'values': {
                'calories': 86,
                'sugar': 0.1,
                'sodium': 330,
                'protein': 6,
                'fiber': 0,
                'saturated_fat': 6.8,
                'cholesterol': 18
            }
        }
    ]
    
    warning_system = DiseaseWarningSystem()
    explainer = ExplanationGenerator()
    
    for food in test_foods:
        print(f"\n{'='*80}")
        print(f"Food: {food['name']}")
        print(f"{'='*80}")
        
        # Generate warnings
        warnings = warning_system.generate_warnings(food['values'])
        
        print(f"\nWarnings ({len(warnings)}):")
        if warnings:
            for warning in warnings:
                print(f"\n  {warning['message']}")
                print(f"  Severity: {warning['severity'].upper()}")
        else:
            print("  No specific warnings")
        
        # Generate explanation
        classification = 'Limit'  # Placeholder
        score = 50  # Placeholder
        explanation = explainer.generate_explanation(
            classification, score, food['values'], warnings
        )
        
        print(f"\nKey Points:")
        for point in explanation['key_points']:
            print(f"  {point}")
        
        print(f"\nRecommendations:")
        for rec in explanation['recommendations']:
            print(f"  • {rec}")


if __name__ == "__main__":
    test_warning_system()
