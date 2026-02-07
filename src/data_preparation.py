"""
Data Preparation Module for AI Food Label Decoder
Loads and analyzes nutrition datasets, performs initial exploration
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class DataLoader:
    """Load and combine all food nutrition datasets"""
    
    def __init__(self, data_dir='Dataset'):
        self.data_dir = Path(data_dir)
        self.combined_data = None
        
    def load_all_groups(self):
        """Load all FOOD-DATA-GROUP CSV files and combine them"""
        group_files = list(self.data_dir.glob('FOOD-DATA-GROUP*.csv'))
        
        if not group_files:
            raise FileNotFoundError(f"No group files found in {self.data_dir}")
        
        dfs = []
        for file in sorted(group_files):
            df = pd.read_csv(file)
            df['source_group'] = file.stem  # Add source tracking
            dfs.append(df)
            print(f"Loaded {file.name}: {len(df)} rows")
        
        self.combined_data = pd.concat(dfs, ignore_index=True)
        print(f"\nTotal combined data: {len(self.combined_data)} rows")
        return self.combined_data
    
    def load_daily_nutrition(self):
        """Load the daily food nutrition dataset"""
        daily_file = self.data_dir / 'daily_food_nutrition_dataset.csv'
        if daily_file.exists():
            df = pd.read_csv(daily_file)
            print(f"Loaded daily nutrition data: {len(df)} rows")
            return df
        return None
    
    def get_feature_summary(self):
        """Get summary statistics of all features"""
        if self.combined_data is None:
            raise ValueError("Data not loaded. Call load_all_groups() first.")
        
        print("\n" + "="*80)
        print("DATASET SUMMARY")
        print("="*80)
        
        print(f"\nShape: {self.combined_data.shape}")
        print(f"Columns: {self.combined_data.shape[1]}")
        
        print("\n--- Column Names ---")
        print(self.combined_data.columns.tolist())
        
        print("\n--- Data Types ---")
        print(self.combined_data.dtypes.value_counts())
        
        print("\n--- Missing Values ---")
        missing = self.combined_data.isnull().sum()
        missing_pct = (missing / len(self.combined_data)) * 100
        missing_df = pd.DataFrame({
            'Missing': missing,
            'Percentage': missing_pct
        })
        print(missing_df[missing_df['Missing'] > 0].sort_values('Missing', ascending=False))
        
        print("\n--- Key Nutrition Features Statistics ---")
        nutrition_cols = ['Caloric Value', 'Protein', 'Carbohydrates', 'Fat', 
                         'Dietary Fiber', 'Sugars', 'Sodium', 'Cholesterol']
        
        available_cols = [col for col in nutrition_cols if col in self.combined_data.columns]
        if available_cols:
            print(self.combined_data[available_cols].describe())
        
        return self.combined_data.describe()


class FeatureAnalyzer:
    """Analyze features for health classification"""
    
    def __init__(self, data):
        self.data = data
        
    def identify_key_features(self):
        """Identify most important features for health classification"""
        print("\n" + "="*80)
        print("KEY FEATURES FOR HEALTH CLASSIFICATION")
        print("="*80)
        
        # Identify available nutrition columns
        key_features = {
            'calories': ['Caloric Value', 'Calories (kcal)'],
            'protein': ['Protein', 'Protein (g)'],
            'carbs': ['Carbohydrates', 'Carbohydrates (g)'],
            'fat': ['Fat', 'Fat (g)'],
            'fiber': ['Dietary Fiber', 'Fiber (g)'],
            'sugar': ['Sugars', 'Sugars (g)'],
            'sodium': ['Sodium', 'Sodium (mg)'],
            'cholesterol': ['Cholesterol', 'Cholesterol (mg)'],
            'saturated_fat': ['Saturated Fats'],
        }
        
        found_features = {}
        for feature_name, possible_cols in key_features.items():
            for col in possible_cols:
                if col in self.data.columns:
                    found_features[feature_name] = col
                    break
        
        print("\nFound Features:")
        for name, col in found_features.items():
            print(f"  {name:15s} -> {col}")
        
        return found_features
    
    def analyze_distributions(self, features_map):
        """Analyze distribution of key nutrition features"""
        print("\n--- Feature Distributions ---")
        
        for feature_name, col_name in features_map.items():
            if col_name in self.data.columns:
                values = self.data[col_name].dropna()
                print(f"\n{feature_name} ({col_name}):")
                print(f"  Min: {values.min():.2f}")
                print(f"  25%: {values.quantile(0.25):.2f}")
                print(f"  Median: {values.median():.2f}")
                print(f"  75%: {values.quantile(0.75):.2f}")
                print(f"  Max: {values.max():.2f}")
                print(f"  Mean: {values.mean():.2f}")
                print(f"  Std: {values.std():.2f}")


def main():
    """Main execution function"""
    print("="*80)
    print("AI FOOD LABEL DECODER - DATA PREPARATION")
    print("="*80)
    
    # Load data
    loader = DataLoader()
    data = loader.load_all_groups()
    
    # Get summary
    loader.get_feature_summary()
    
    # Analyze features
    analyzer = FeatureAnalyzer(data)
    features_map = analyzer.identify_key_features()
    analyzer.analyze_distributions(features_map)
    
    # Save processed data
    output_file = Path('Dataset/processed_food_data.csv')
    data.to_csv(output_file, index=False)
    print(f"\n✓ Saved processed data to: {output_file}")
    
    print("\n" + "="*80)
    print("DATA PREPARATION COMPLETE")
    print("="*80)
    
    return data, features_map


if __name__ == "__main__":
    data, features = main()
