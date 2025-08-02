from flask import Flask, request, jsonify
import requests
import sys

app = Flask(__name__)

def fetch_items(url):
    """Helper function to request items from Flipp API and return the 'items' list."""
    r = requests.get(url)
    # Flipp sometimes returns 404 for queries with no matches
    if r.status_code == 404:
        return []
    r.raise_for_status()
    return r.json().get("items", [])

def search_flipp_item(postal_code, query):
    base = "https://backflipp.wishabi.com/flipp/items"

    # Try the more accurate /search endpoint first
    url_search = f"{base}/search?locale=en-ca&postal_code={postal_code}&q={query}"
    items = fetch_items(url_search)

    # Fallback: if no results, try the broader /items endpoint
    if not items:
        url_broad = f"{base}?locale=en-ca&postal_code={postal_code}&q={query}"
        items = fetch_items(url_broad)

    results = []
    for i in items:
        # Use merchant name if available, otherwise mark as Unknown
        merchant = i.get("merchant", {}).get("name", "Unknown")
        name = i.get("name", "Unnamed item")
        price = i.get("current_price", "N/A")
        valid_to = i.get("valid_to", None)

        # Build a flyer link if flyer_id and clipping_id are available
        flyer_id = i.get("flyer_id")
        clipping_id = i.get("clipping_id")
        link = None
        if flyer_id and clipping_id:
            link = f"https://flipp.com/flyer/{flyer_id}?clippingId={clipping_id}"

        results.append({
            "store": merchant,
            "flyer_item": name,
            "price": price,
            "valid_to": valid_to,
            "link": link
        })

    return results

@app.route("/")
def home():
    return "Flipp agent is running!"

@app.route("/flipp_search", methods=["POST"])
def flipp_search():
    try:
        data = request.get_json(force=True)
        postal = data.get("postal_code")
        items = data.get("items")

        if not postal or not items:
            return jsonify({"error": "postal_code and items are required"}), 400

        output = {}
        for item in items:
            output[item] = search_flipp_item(postal, item)

        return jsonify(output)

    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
