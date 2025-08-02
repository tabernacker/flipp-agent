from flask import Flask, request, jsonify
import requests
import sys

app = Flask(__name__)

def search_flipp_item(postal_code, query):
    url = f"https://backflipp.wishabi.com/flipp/items/search?locale=en-ca&postal_code={postal_code}&q={query}"
    r = requests.get(url)
    r.raise_for_status()
    items = r.json().get("items", [])
    results = []
    for i in items:
        merchant = i.get("merchant", {}).get("name", "Unknown")
        name = i.get("name", "Unnamed item")
        price = i.get("current_price", "N/A")
        valid_to = i.get("valid_to", None)
        results.append({
            "store": merchant,
            "flyer_item": name,
            "price": price,
            "valid_to": valid_to
        })
    return results

@app.route("/")
def home():
    return "Flipp agent is running!"

@app.route("/flipp_search", methods=["POST"])
def flipp_search():
    try:
        data = request.get_json(force=True)  # ensures JSON parsing
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
