from flask import Flask, request, jsonify
from main.python.com.smartprice.africa.services.services import scrape_jiji, scrape_konga, scrape_jumia, scrape_all_sorted
from flask_cors import CORS   # <-- add this


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


def filter_by_amount(results, amount):
    """Filter products that are <= given amount (numeric)."""
    filtered = []
    for item in results:
        try:
            price = int(item["price"]) if isinstance(item["price"], str) else item["price"]
            if price <= amount:
                filtered.append(item)
        except Exception:
            continue
    return filtered

@app.route("/scrape/jumia", methods=["GET"])
def jumia_controller():
    product = request.args.get("product")
    amount = request.args.get("amount", type=int)

    if not product or amount is None:
        return jsonify({"error": "Missing required parameters 'product' and 'amount'"}), 400

    results = scrape_jumia(product)
    results = filter_by_amount(results, amount)
    return jsonify(results)


@app.route("/scrape/jiji", methods=["GET"])
def jiji_controller():
    product = request.args.get("product")
    amount = request.args.get("amount", type=int)
    page = request.args.get("page", default=1, type=int)

    if not product or amount is None:
        return jsonify({"error": "Missing required parameters 'product' and 'amount'"}), 400

    results = scrape_jiji(product, page)
    results = filter_by_amount(results, amount)
    return jsonify(results)


@app.route("/scrape/konga", methods=["GET"])
def konga_controller():
    query = request.args.get("q")
    page = request.args.get("page", default=1, type=int)

    if not product or amount is None:
        return jsonify({"error": "Missing required parameters 'product' and 'amount'"}), 400

    results = scrape_konga(product, page)
    results = filter_by_amount(results, amount)
    return jsonify(results)


@app.route("/scrape/all", methods=["GET", "POST"])
def all_controller():
    if request.method == "POST":
        data = request.get_json()
        product = data.get("query")
        amount = data.get("budgetAmount")
    else:
        product = request.args.get("product")
        amount = request.args.get("amount", type=int)

    if not product or amount is None:
        return jsonify({"error": "Missing 'product' and 'amount'"}), 400

    results = scrape_all_sorted(product)
    results = filter_by_amount(results, int(amount))
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True, port=5000)