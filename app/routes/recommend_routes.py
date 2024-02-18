from contextlib import nullcontext
from flask import Blueprint, json, request, jsonify
import joblib
import os
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from pathlib import Path


recommend_routes = Blueprint('user_routes', __name__)

@recommend_routes.route('/recommend-campaign', methods=['POST'])
def index():
    print( os.path.dirname(__file__))

    data = request.get_json()
    print(data)
    current_directory = Path(__file__).resolve().parent
    data_folder = current_directory.parent / 'data'
    genome_tag = pd.read_csv(data_folder / 'campaign_type.csv')
    campaign = pd.read_csv(data_folder / 'campaign.csv')
    matrix_score = np.array(genome_tag)
    
    # print(matrix_score)

    # model_folder = current_directory.parent / 'model'
    model = joblib.load(data_folder/'model/knnModel.joblib')

    vector = data
    print(vector)
    distances, indices = model.kneighbors(vector)
    index_activity = [int(item) for sublist in indices for item in sublist]
    listIds = genome_tag.iloc[index_activity]['campaign_id']
    campaign_ids_list = campaign[campaign['campaign_id'].isin(listIds)]['campaign_id'].tolist() 

    return json.dumps(campaign_ids_list)

