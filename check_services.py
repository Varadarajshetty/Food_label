
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

# Load environment variables
load_dotenv()

print("Checking OpenAI API Key...")
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY not found in environment variables")
else:
    print(f"OPENAI_API_KEY found (starts with {api_key[:8]}...)")

print("\nChecking OpenAI Connectivity...")
try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello, are you there?"}],
        max_tokens=10
    )
    print("OpenAI says:", response.choices[0].message.content)
    print("SUCCESS: OpenAI is reachable.")
except Exception as e:
    print(f"ERROR: OpenAI connection failed: {e}")

print("\nChecking OpenFoodFacts Connectivity...")
try:
    from product_lookup import ProductSearch
    searcher = ProductSearch()
    # Test with a known product
    result = searcher.search_by_name("Lays Classic Salted")
    if result:
        print(f"SUCCESS: Found product {result.get('product_name')}")
    else:
        print("WARNING: OpenFoodFacts reachable but product not found.")
except Exception as e:
    print(f"ERROR: OpenFoodFacts connection failed: {e}")
