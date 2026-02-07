"""
Food Alternative Suggestions Module
Provides healthier alternatives for "Avoid" category foods
"""

class AlternativeSuggester:
    """Suggests healthier alternatives based on food category/keywords"""
    
    def __init__(self):
        # Simple database of alternatives
        self.alternatives = {
            'chips': [
                'Roasted Fox Nuts (Makhana)', 
                'Baked Kale Chips', 
                'Air-popped Popcorn (Light Salt)',
                'Roasted Chickpeas'
            ],
            'crisps': [ # Synonyms
                'Roasted Fox Nuts (Makhana)', 
                'Baked Kale Chips', 
                'Air-popped Popcorn'
            ],
            'soda': [
                'Sparkling Water with Lemon', 
                'Kombucha', 
                'Freshly Squeezed Juice (with pulp)',
                'Iced Herbal Tea'
            ],
            'coke': [
                'Sparkling Water with Lemon', 
                'Kombucha',
                'Iced Herbal Tea'
            ],
            'chocolate': [
                'Dark Chocolate (>70% Cocoa)', 
                'Dates with Almonds',
                'Fresh Berries'
            ],
            'candy': [
                'Fresh Fruit (Grapes, Berries)',
                'Dried Apricots (Unsweetened)'
            ],
            'cookie': [
                'Homemade Oatmeal Banana Cookies',
                'Apple Slices with Peanut Butter',
                'Greek Yogurt with Granola'
            ],
            'biscuit': [
                'Whole Wheat Crackers',
                'Oatcakes'
            ],
            'instant noodles': [
                'Whole Wheat Pasta with Veggies',
                'Zucchini Noodles (Zoodles)',
                'Buckwheat Noodles (Soba)'
            ],
            'sauce': [
                'Homemade Salsa',
                'Greek Yogurt Dip',
                'Hummus'
            ],
             'frozen meal': [
                'Meal Prepped Grilled Chicken & Veggies',
                'Fresh Salad with Protein'
            ]
        }
    
    def suggest_alternatives(self, product_name):
        """
        Get suggestions based on product name keywords
        
        Args:
            product_name: Name of the food item
            
        Returns:
            List of suggestion strings
        """
        if not product_name:
            return []
            
        name_lower = product_name.lower()
        suggestions = []
        
        # Check against keywords
        for key, alts in self.alternatives.items():
            if key in name_lower:
                suggestions.extend(alts)
        
        # Deduplicate and limit
        return list(set(suggestions))[:3]

    def get_category_suggestions(self, category):
        """Get suggestions by explicit category if known"""
        return self.alternatives.get(category.lower(), [])
