import requests
from flask import Flask, render_template, request
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)

def search_products(query):
    """
    Search for products by name using the Open Food Facts API.
    """
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&json=1"

    session = requests.Session()
    retries = Retry(
        total=5, 
        backoff_factor=1, 
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    try:
        response = session.get(url, timeout=15)  # Set timeout to 15 seconds
        response.raise_for_status()  # Raise an error for HTTP errors (4xx, 5xx)
        data = response.json()
        
        # Process products to extract necessary fields
        products = data.get('products', [])
        result = []
        for product in products:
            result.append({
                'product_name': product.get('product_name', 'Unknown Product'),
                'brands': product.get('brands', 'Unknown Brand'),
                'barcode': product.get('code', 'N/A')  # Extract the barcode
            })
        return result
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error searching products: {e}")
        return []

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Render the main page and handle product search.
    """
    search_results = []
    error_message = None
    
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            search_results = search_products(query)
            if not search_results:
                error_message = "No products found or an error occurred during the search."
        else:
            error_message = "Please enter a valid search query."

    return render_template("index.html", search_results=search_results, error_message=error_message)

if __name__ == "__main__":
    app.run(debug=True)
