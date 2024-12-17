import json
from flask import Flask, request, jsonify, render_template
import pickle  # To load saved results
from werkzeug.wrappers import Response

app = Flask(__name__)

# Load preprocessed data and match results
with open('roommate_results.pkl', 'rb') as f:
    matches, individual_tables = pickle.load(f)

# Route to serve the homepage


@app.route('/')
def home():
    return render_template('index.html')  # Serves the HTML file

# Route to fetch matches for a given name


@app.route('/get_matches', methods=['GET'])
def get_matches():
    name = request.args.get('name')  # Get name input from user
    if name not in individual_tables:
        return jsonify({"error": "Name not found"}), 404

    # Retrieve the top matches for the given name
    table = individual_tables[name]
    return jsonify(table.to_dict(orient='records'))  # Return results as JSON

# Netlify serverless function handler


def handler(event, context):
    # Use Flask's request context and return a response
    with app.app_context():
        return Response(
            app.full_dispatch_request(),
            status=200,
            mimetype='application/json'
        )
