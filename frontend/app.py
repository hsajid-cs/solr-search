from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
SOLR_URL = "http://localhost:8983/solr/Lab1/select"

@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "*:*")
    category = request.args.get("category")
    
    solr_query = query if query else "*:*"
    fq = f"category:{category}" if category else None

    params = {
        "q": solr_query,
        "wt": "json",
        "indent": "true"
    }

    if fq:
        params["fq"] = fq

    response = requests.get(SOLR_URL, params=params)
    data = response.json()
    results = data["response"]["docs"]
    facet_response = requests.get(SOLR_URL, params={
        "q": "*:*",
        "facet": "true",
        "facet.field": "category",
        "rows": 0,
        "wt": "json"
    }).json()
    categories = facet_response["facet_counts"]["facet_fields"]["category"]
    category_list = [categories[i] for i in range(0, len(categories), 2)]  # every 2nd item is count

    return render_template("index.html", results=results, query=query, selected_category=category, categories=category_list)

@app.route("/autocomplete")
def autocomplete():
    prefix = request.args.get("term", "")
    if not prefix:
        return jsonify([])

    response = requests.get(SOLR_URL, params={
        "q": f"title:{prefix}*",
        "fl": "title",
        "rows": 5,
        "wt": "json"
    })

    docs = response.json()["response"]["docs"]
    suggestions = [doc["title"][0] for doc in docs if "title" in doc]
    return jsonify(suggestions)

if __name__ == "__main__":
    app.run(debug=True)
