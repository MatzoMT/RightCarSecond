#!flask/bin/python
import requests
from src.data_helper import get_all_sales_json, get_sales
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# Returns JSON object of all recorded sales of a model
@app.route('/api/v1/all-sales', methods=['POST'])
def get_all_sales():
    if not request.json or 'make' not in request.json or 'model' not in request.json:
        print("ABORTING")
        abort(400)
    data = request.get_json()
    dict = get_all_sales_json(data['make'], data['model'])

    return jsonify({
        "allSales": dict
    })

# Returns JSON object of sales recorded for a specified model year
# Returns: sales provided if available, -1 if not found
@app.route('/api/v1/year-sales', methods=['POST'])
def get_year_sales():
    if not request.json or 'year' not in request.json or 'make' not in request.json or 'model' not in request.json:
        print("ABORTING")
        abort(400)
    data = request.get_json()
    sales_for_year = get_sales(int(data['year']), data['make'], data['model'])

    return jsonify({
        "sales": sales_for_year
    })



if __name__ == '__main__':
    app.run(debug=True)