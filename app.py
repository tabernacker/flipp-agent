from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def search_flipp_item(postal_code, query):
    url = f"https://backflipp.wishabi.com/flipp/items/search?locale=en-ca&postal_code={postal_code}&q={query}"
    r = requests.get(url)
    r.raise_for_status()
    items = r.json().get("items", [])
    results = []
    for i in items:
        results.append({
            "store": i["merchant"]["name"],
            "flyer_item": i["name"],
            "price": i.get("current_price"),
            "valid_to": i.get("valid_to")
        })
    return results

@app.route("/flipp_search", methods=["POST"])
def flipp_search():
    data = request.json
    postal = data["postal_code"]
    items = data["items"]

    output = {}
    for item in items:
        output[item] = search_flipp_item(postal, item)
    return jsonify(output)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
