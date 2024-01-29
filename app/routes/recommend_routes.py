from contextlib import nullcontext
from flask import Blueprint, json, request, jsonify
import joblib
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors


recommend_routes = Blueprint('user_routes', __name__)

@recommend_routes.route('/recommend-campaign', methods=['POST'])
def index():
    data = request.get_json()
    print(data)
    genome_tag = pd.read_csv('/Users/truonghuythai/Documents/unidy_project/unidy_recommendation/model/data/campaign_type.csv')
    matrix_score = np.array(genome_tag)
    # print(matrix_score)
    model = joblib.load('/Users/truonghuythai/Documents/unidy_project/unidy_recommendation/model/knnModel.joblib')

    vector = data

    # vector = matrix_score[index]
    # print(vector)
    distances, indices = model.kneighbors(vector)

    index_activity = [int(item) for sublist in indices for item in sublist]

    return json.dumps(index_activity)
