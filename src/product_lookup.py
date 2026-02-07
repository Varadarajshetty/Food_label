
import requests
import json
import time

class ProductSearch:
    """
    Search for products using OpenFoodFacts API
    """
    
    BASE_URL = "https://world.openfoodfacts.org/cgi/search.pl"
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'FoodLabelDecoder/1.0 (Integration Test)'
        }
    
    def search_by_name(self, product_name):
        """
        Search for a product by name and return nutrition data
        
        Args:
            product_name: Name of the product to search
            
        Returns:
            Dictionary with nutrition values or None if not found
        """
        print(f"Searching for product: {product_name}")
        
        params = {
            'search_terms': product_name,
            'search_simple': 1,
            'action': 'process',
            'json': 1,
            'page_size': 5
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('products'):
                print("No products found")
                return None
            
            # Get the first product
            product = data['products'][0]
            product_name_found = product.get('product_name', 'Unknown')
            print(f"Found product: {product_name_found}")
            
            # Extract nutrition data
            nutriments = product.get('nutriments', {})
            
            # Map to our internal structure
            nutrition_values = {
                'calories': self._get_value(nutriments, ['energy-kcal_100g', 'energy-kcal', 'energy_100g', 'energy']),
                'protein': self._get_value(nutriments, ['proteins_100g', 'proteins']),
                'carbs': self._get_value(nutriments, ['carbohydrates_100g', 'carbohydrates']),
                'fat': self._get_value(nutriments, ['fat_100g', 'fat']),
                'fiber': self._get_value(nutriments, ['fiber_100g', 'fiber']),
                'sugar': self._get_value(nutriments, ['sugars_100g', 'sugars']),
                'sodium': self._get_value(nutriments, ['sodium_100g', 'sodium'], conversion_factor=1000), # g to mg if needed
                'cholesterol': self._get_value(nutriments, ['cholesterol_100g', 'cholesterol'], conversion_factor=1000),
                'saturated_fat': self._get_value(nutriments, ['saturated-fat_100g', 'saturated-fat']),
                'source': 'OpenFoodFacts',
                'product_name': product_name_found
            }
            
            # Clean up sodium (API usually gives sodium in grams, we want mg)
            # Checked OpenFoodFacts - nutriments['sodium_100g'] is usually in grams
            if nutrition_values['sodium'] < 10:  # If it looks like grams (<10g is massive for sodium if it was already mg)
                 nutrition_values['sodium'] *= 1000
                 
            return nutrition_values
            
        except requests.RequestException as e:
            print(f"API Request failed: {e}")
            return None
        except Exception as e:
            print(f"Error parsing product data: {e}")
            return None

    def _get_value(self, data, keys, conversion_factor=1.0):
        """Helper to safely get value from multiple potential keys"""
        for key in keys:
            if key in data and data[key] is not None:
                try:
                    val = float(data[key])
                    return val * conversion_factor
                except (ValueError, TypeError):
                    continue
        return 0.0

if __name__ == "__main__":
    searcher = ProductSearch()
    result = searcher.search_by_name("Lays Classic Salted")
    if result:
        print("\nExtracted Data:")
        print(json.dumps(result, indent=2))
