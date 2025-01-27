import requests
from flask import Flask, render_template, request  # type:ignore

app = Flask(__name__)

def get_product_info(barcode):
    """
    Retrieve detailed product information from Open Food Facts based on the barcode.
    """
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 1:  
            product = data['product']
            
            product_info = {
                'name': product.get('product_name', 'Unknown'),
                'brands': product.get('brands', 'Unknown'),
                'barcode': barcode,
                'ingredients': product.get('ingredients_text', 'N/A').split(', '),
                'nutrient_levels': product.get('nutrient_levels', {}),
                'additives': product.get('additives_tags', []),
                'allergens': product.get('allergens_tags', []),
                'eco_score': product.get('ecoscore_score', 'Unknown'),
                'certifications': product.get('labels', 'None'),
                'packaging': product.get('packaging', 'N/A'),
                'origin': product.get('countries_tags', []),
                'nutritional_info': product.get('nutriments', {}),
                'labels': product.get('labels_tags', []),
                'quantity': product.get('quantity', 'N/A'),
                'categories': product.get('categories_tags', []),
                'manufacturing_places': product.get('manufacturing_places', 'Unknown'),
                'conservation': product.get('conservation_conditions', 'N/A'),
                'traces': product.get('traces_tags', []),
                'image_url': product.get('image_url', None),
                'serving_size': product.get('serving_size', 'N/A'),
                'nutriscore_grade': product.get('nutriscore_grade', 'N/A'),
                'product_code': product.get('code', 'N/A'),
            }
            return product_info
        else:
            return None
    else:
        return None

def search_products(query):
    """
    Search for products by name using the Open Food Facts API.
    """
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&json=1"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        return [
            {
                'product_name': product.get('product_name', 'Unknown Product'),
                'brands': product.get('brands', 'Unknown Brand'),
                'barcode': product.get('code', 'N/A')
            }
            for product in products
        ]
    else:
        return []

def check_fda_compliance(ingredients_list):
    """
    Check the ingredients list against the OpenFDA API for compliance.
    """
    fda_compliance_report = []
    
    for ingredient in ingredients_list:
        url = f"https://api.fda.gov/drug/label.json?search=active_ingredient:{ingredient}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                fda_compliance_report.append(f"{ingredient}: FDA approved.")
            else:
                fda_compliance_report.append(f"{ingredient}: Not found in FDA approved list.")
        else:
            fda_compliance_report.append(f"{ingredient}: Not found in FDA approved list.")
    
    return fda_compliance_report

@app.route("/", methods=["GET", "POST"])
def index():
    product_info = None
    search_results = []
    fda_compliance_report = None
    error_message = None
    
    if request.method == "POST":
        barcode = request.form.get("barcode")
        if barcode:
            product_info = get_product_info(barcode)
            if product_info and 'ingredients' in product_info:
                ingredients_list = product_info['ingredients']
                fda_compliance_report = check_fda_compliance(ingredients_list)
            elif not product_info:
                error_message = "No product found for the provided barcode."
        
        query = request.form.get("query")
        if query:
            search_results = search_products(query)
            if not search_results:
                error_message = "No products found for the provided search query."

    return render_template(
        "index.html",
        product_info=product_info,
        search_results=search_results,
        fda_compliance_report=fda_compliance_report,
        error_message=error_message
    )

if __name__ == '__main__':
    app.run(debug=True)