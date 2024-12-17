import json
import pickle
from flask import Flask, jsonify, request

# Initialize Flask app for the serverless function
app = Flask(__name__)

# Load preprocessed data and match results
with open('roommate_results.pkl', 'rb') as f:
    matches, individual_tables = pickle.load(f)


@app.route('/get_matches', methods=['GET'])
def get_matches():
    name = request.args.get('name')  # Get name input from the user
    if name not in individual_tables:
        return jsonify({"error": "Name not found"}), 404

    # Retrieve the top matches for the given name
    table = individual_tables[name]
    return jsonify(table.to_dict(orient='records'))


# The following line is needed for local testing (not for Netlify):
if __name__ == '__main__':
    app.run(debug=True)
