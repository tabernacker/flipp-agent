from flask import Flask, request, jsonify
import requests
import sys

app = Flask(__name__)

def fetch_items(url):
    """Helper function to request items from Flipp API and return the 'items' list."""
    r = requests.get(url)
    if r.status_code == 404:
        return []
    r.raise_for_status()
    return r.json().get("items", [])

def search_flipp_item(postal_code, query):
    """
    Searches Flipp for items in a given postal code.
    1. Tries /items/search (accurate)
    2. Falls back to /items (broader)
    Filters out entries without merchant or flyer/clipping IDs.
    """
    base = "https://backflipp.wishabi.com/flipp/items"

    # Step 1: Try accurate search
    url_search = f"{base}/search?locale=en-ca&postal_code={postal_code}&q={query}"
    items = fetch_items(url_search)

    # Step 2: Fallback to broader search if needed
    if not items:
        url_broad = f"{base}?locale=en-ca&postal_code={postal_code}&q={query}"
        items = fetch_items(url_broad)

    results = []
    for i in items:
        merchant = i.get("merchant", {}).get("name")
        flyer_id = i.get("flyer_id")
        clipping_id = i.get("clipping_id")

        # Skip entries without merchant or flyer/clipping IDs
        if not merchant or not flyer_id or not clipping_id:
            continue

        name = i.get("name", "Unnamed item")
        price = i.get("current_price", "N/A")
        valid_to = i.get("valid_to", None)

        # Bu
