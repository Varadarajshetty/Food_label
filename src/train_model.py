
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, f1_score

# Paths
DATA_PATH = Path('Dataset/processed_food_data.csv')
MODEL_DIR = Path('models')
MODEL_PATH = MODEL_DIR / 'health_classifier.joblib'

def train_model():
    print("="*80)
    print("TRAINING HEALTH CLASSIFIER MODEL (IMPROVED)")
    print("="*80)
    
    # 1. Load Data
    # Check for human validated data first
    human_data_path = Path('Dataset/human_validated.csv')
    if human_data_path.exists():
        print(f"[INFO] Using Human-Validated Dataset: {human_data_path}")
        df = pd.read_csv(human_data_path)
    elif DATA_PATH.exists():
        print(f"[INFO] Using Processed Dataset: {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)
    else:
        print(f"Error: Dataset not found.")
        return
    print(f"Loaded data: {len(df)} samples")
    
    # 2. Prepare Features
    # Map dataset columns to our standard feature set
    # Using 'Caloric Value', 'Protein', 'Carbohydrates', 'Fat', 'Sodium', 'Sugars', 'Saturated Fats'
    
    feature_cols = [
        'Caloric Value', 
        'Protein', 
        'Carbohydrates', 
        'Fat', 
        'Sodium', 
        'Sugars', 
        'Saturated Fats', 
        'Dietary Fiber'
    ]
    
    # Check if columns exist
    missing_cols = [col for col in feature_cols if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing columns in dataset: {missing_cols}")
        return

    X = df[feature_cols].fillna(0)
    
    # 3. Prepare Target
    # We need a 'Label' column. If 'health_label' exists (rule-based), use it. 
    # Otherwise we might need to derive it or use 'Nutrition Density' if available.
    
    # Let's check if we have a target
    if 'health_label' in df.columns:
        y = df['health_label']
        print("Using existing 'health_label' as target.")
    elif 'Label' in df.columns:
         y = df['Label']
         print("Using 'Label' column as target.")
    else:
        print("No target label found. We need 'health_label' or 'Label'.")
        print("Running rule-based classifier to generate labels first...")
        
        # Determine labels using existing logic if not present
        from health_classifier import HealthClassifier
        classifier = HealthClassifier()
        
        # Create a temp feature map for the rule-based classifier
        feature_map = {
            'calories': 'Caloric Value',
            'protein': 'Protein',
            'carbs': 'Carbohydrates',
            'fat': 'Fat',
            'fiber': 'Dietary Fiber',
            'sugar': 'Sugars',
            'sodium': 'Sodium',
            'cholesterol': 'Cholesterol', # might be missing, handled in classifier
            'saturated_fat': 'Saturated Fats',
        }
        
        df = classifier.classify_dataset(df, feature_map)
        y = df['health_label']
    
    # Encode target
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Save classes for later use
    print(f"Classes: {le.classes_}")
    
    # 4. Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    # 5. Train & Compare Models
    print("\n--- Model Comparison ---")
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'XGBoost': XGBClassifier(eval_metric='mlogloss', random_state=42),
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Decision Tree': DecisionTreeClassifier(random_state=42)
    }
    
    best_model_name = None
    best_score = 0
    best_model = None
    
    print(f"{'Model':<20} | {'Accuracy':<10} | {'F1 Score':<10}")
    print("-" * 50)
    
    for name, model in models.items():
        try:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            print(f"{name:<20} | {acc:.4f}     | {f1:.4f}")
            
            if f1 > best_score:
                best_score = f1
                best_model_name = name
                best_model = model
        except Exception as e:
            print(f"{name} Error: {e}")
            
    print("-" * 50)
    print(f"Best Model: {best_model_name} (F1: {best_score:.4f})")
    
    # 6. Evaluate Best Model
    print(f"\nFinal Evaluation ({best_model_name}):")
    y_pred = best_model.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    
    # 7. Feature Importance (if applicable)
    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        plt.figure(figsize=(10, 6))
        plt.title(f"Feature Importances ({best_model_name})")
        sns.barplot(x=importances[indices], y=[feature_cols[i] for i in indices])
        plt.xlabel('Relative Importance')
        plt.tight_layout()
        
        # Save plot
        plot_path = Path('frontend/images/feature_importance.png')
        plot_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(plot_path)
        print(f"\n[INFO] Feature importance plot saved to {plot_path}")
        
    # 8. Save Model
    MODEL_DIR.mkdir(exist_ok=True)
    
    model_data = {
        'model': best_model,
        'encoder': le,
        'features': feature_cols,
        'model_name': best_model_name,
        'accuracy': best_score
    }
    
    joblib.dump(model_data, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")
    
    return best_model

if __name__ == "__main__":
    train_model()
