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
    genome_tag = pd.read_csv('~/unidy_recommendation/model/data/campaign_type.csv')
    campaign = pd.read_csv('~/unidy_recommendation/model/data/campaign.csv')
    matrix_score = np.array(genome_tag)
    # print(matrix_score)
    model = joblib.load('~/unidy_recommendation/model/knnModel.joblib')

    vector = data

    # vector = matrix_score[index]
    # print(vector)
    distances, indices = model.kneighbors(vector)
    index_activity = [int(item) +1 for sublist in indices for item in sublist]
    listIds = genome_tag.iloc[index_activity]['campaign_id']
    campaign_ids_list = campaign[campaign['campaign_id'].isin(listIds)]['campaign_id'].tolist() 

    return json.dumps(index_activity)

