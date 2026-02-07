"""
Feature Engineering Module
Creates derived features for health classification
"""

import pandas as pd
import numpy as np
from pathlib import Path


class FeatureEngineer:
    """Create health-relevant features from nutrition data"""
    
    def __init__(self, data):
        self.data = data.copy()
        self.feature_map = self._map_columns()
        
    def _map_columns(self):
        """Map standard feature names to actual column names"""
        mapping = {}
        
        # Define possible column names for each feature
        possible_names = {
            'calories': ['Caloric Value', 'Calories (kcal)', 'Calories'],
            'protein': ['Protein', 'Protein (g)'],
            'carbs': ['Carbohydrates', 'Carbohydrates (g)'],
            'fat': ['Fat', 'Fat (g)'],
            'fiber': ['Dietary Fiber', 'Fiber (g)'],
            'sugar': ['Sugars', 'Sugars (g)'],
            'sodium': ['Sodium', 'Sodium (mg)'],
            'cholesterol': ['Cholesterol', 'Cholesterol (mg)'],
            'saturated_fat': ['Saturated Fats', 'Saturated Fat (g)'],
        }
        
        for feature, possible_cols in possible_names.items():
            for col in possible_cols:
                if col in self.data.columns:
                    mapping[feature] = col
                    break
        
        return mapping
    
    def create_all_features(self):
        """Create all engineered features"""
        print("Creating engineered features...")
        
        self._create_macro_ratios()
        self._create_density_features()
        self._create_quality_scores()
        self._create_risk_indicators()
        
        print(f"✓ Created {len([c for c in self.data.columns if c.startswith('feat_')])} new features")
        return self.data
    
    def _create_macro_ratios(self):
        """Create macronutrient ratio features"""
        if all(k in self.feature_map for k in ['protein', 'carbs', 'fat']):
            protein_col = self.feature_map['protein']
            carbs_col = self.feature_map['carbs']
            fat_col = self.feature_map['fat']
            
            total_macros = (self.data[protein_col] + 
                           self.data[carbs_col] + 
                           self.data[fat_col])
            
            # Percentage of each macro
            self.data['feat_protein_pct'] = (self.data[protein_col] / total_macros * 100).fillna(0)
            self.data['feat_carbs_pct'] = (self.data[carbs_col] / total_macros * 100).fillna(0)
            self.data['feat_fat_pct'] = (self.data[fat_col] / total_macros * 100).fillna(0)
            
            # Protein to carb ratio (higher is better for satiety)
            self.data['feat_protein_carb_ratio'] = (
                self.data[protein_col] / (self.data[carbs_col] + 1)
            )
    
    def _create_density_features(self):
        """Create nutrient density features"""
        if 'calories' in self.feature_map:
            cal_col = self.feature_map['calories']
            
            # Calorie density (calories per 100g assumed)
            self.data['feat_calorie_density'] = self.data[cal_col]
            
            # Protein density (protein per 100 calories)
            if 'protein' in self.feature_map:
                self.data['feat_protein_density'] = (
                    self.data[self.feature_map['protein']] / (self.data[cal_col] + 1) * 100
                )
            
            # Fiber density (fiber per 100 calories)
            if 'fiber' in self.feature_map:
                self.data['feat_fiber_density'] = (
                    self.data[self.feature_map['fiber']] / (self.data[cal_col] + 1) * 100
                )
    
    def _create_quality_scores(self):
        """Create nutrition quality indicators"""
        
        # Sugar percentage (of total carbs)
        if all(k in self.feature_map for k in ['sugar', 'carbs']):
            sugar_col = self.feature_map['sugar']
            carbs_col = self.feature_map['carbs']
            self.data['feat_sugar_pct'] = (
                self.data[sugar_col] / (self.data[carbs_col] + 1) * 100
            ).fillna(0)
        
        # Fiber adequacy (fiber per serving)
        if 'fiber' in self.feature_map:
            fiber_col = self.feature_map['fiber']
            # Score: 0-10 based on fiber content (5g+ is excellent)
            self.data['feat_fiber_score'] = np.minimum(
                self.data[fiber_col] * 2, 10
            )
        
        # Sodium per calorie ratio
        if all(k in self.feature_map for k in ['sodium', 'calories']):
            sodium_col = self.feature_map['sodium']
            cal_col = self.feature_map['calories']
            self.data['feat_sodium_per_cal'] = (
                self.data[sodium_col] / (self.data[cal_col] + 1)
            )
    
    def _create_risk_indicators(self):
        """Create disease risk indicators"""
        
        # High sodium flag (>400mg per serving is high)
        if 'sodium' in self.feature_map:
            sodium_col = self.feature_map['sodium']
            self.data['feat_high_sodium'] = (self.data[sodium_col] > 400).astype(int)
        
        # High sugar flag (>15g per serving is high)
        if 'sugar' in self.feature_map:
            sugar_col = self.feature_map['sugar']
            self.data['feat_high_sugar'] = (self.data[sugar_col] > 15).astype(int)
        
        # High saturated fat flag (>5g per serving is high)
        if 'saturated_fat' in self.feature_map:
            sat_fat_col = self.feature_map['saturated_fat']
            self.data['feat_high_sat_fat'] = (self.data[sat_fat_col] > 5).astype(int)
        
        # High cholesterol flag (>100mg per serving is high)
        if 'cholesterol' in self.feature_map:
            chol_col = self.feature_map['cholesterol']
            self.data['feat_high_cholesterol'] = (self.data[chol_col] > 100).astype(int)


def main():
    """Test feature engineering"""
    # Load processed data
    data_file = Path('Dataset/processed_food_data.csv')
    if not data_file.exists():
        print("Error: Run data_preparation.py first!")
        return
    
    data = pd.read_csv(data_file)
    print(f"Loaded {len(data)} food items")
    
    # Create features
    engineer = FeatureEngineer(data)
    engineered_data = engineer.create_all_features()
    
    # Show new features
    new_features = [col for col in engineered_data.columns if col.startswith('feat_')]
    print(f"\nNew Features ({len(new_features)}):")
    for feat in new_features:
        print(f"  - {feat}")
    
    # Save
    output_file = Path('Dataset/engineered_food_data.csv')
    engineered_data.to_csv(output_file, index=False)
    print(f"\n✓ Saved to: {output_file}")
    
    return engineered_data


if __name__ == "__main__":
    data = main()
