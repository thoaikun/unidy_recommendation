from contextlib import nullcontext
from flask import Blueprint, json, request, jsonify
import joblib
import os
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from pathlib import Path
import csv
import time
from .. import mysql

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


@recommend_routes.route('/sync-campaign', methods=['GET'])
def sync_campaign():
    print('Starting sync campaign...')

    campaigns_data, campaigns_type_data = get_campaign_from_db()

    current_directory = Path(__file__).resolve().parent
    data_folder = current_directory.parent / 'data'

    with open(data_folder / 'campaign.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # clean file before writing
        writer.writerows([])
        # write new data
        for row in campaigns_data:
            writer.writerow(row)
    
    with open(data_folder / 'campaign_type.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for row in campaigns_type_data:
            writer.writerow(row)

    print('Sync campaign done!')
    return json.dumps({'message': 'Sync campaign done!'})


def get_campaign_from_db():
    campaign_cursor = mysql.connection.cursor()
    campaign_type_cursor = mysql.connection.cursor()
    campaign_cursor.execute('SELECT campaign_id, content, numbers_volunteer, start_day, end_day, location, status, create_day, update_day, update_by FROM campaign')

    campaigns_data = [
        ['campaign_id', 'content', 'numbers_volunteer', 'start_day', 'end_day', 'location', 'status', 'create_day', 'update_day','update_by']
    ]
    campaigns_type_data = [
        ['type_id', 'campaign_id', 'community_type', 'education_type', 'research_type', 'research_writing_editing', 'help_other', 'environment', 'healthy', 'emergency_preparedness']
    ]

    for row in campaign_cursor.fetchall():
        campaign_type_cursor.execute(f'SELECT * FROM campaign_type WHERE campaign_id = {row[0]}')
        campaign_type = campaign_type_cursor.fetchone()
        if campaign_type is not None:
            campaigns_data.append([
                row[0],
                row[1],
                row[2],
                row[3].strftime('%Y-%m-%d') if row[3] is not None else None,
                row[4].strftime('%Y-%m-%d') if row[4] is not None else None,
                row[5],
                row[6],
                row[7].strftime('%Y-%m-%d') if row[7] is not None else None,
                row[8].strftime('%Y-%m-%d') if row[8] is not None else None,
                row[9]
            ])

            campaigns_type_data.append([
                campaign_type[0],
                campaign_type[1],
                campaign_type[2],
                campaign_type[3],
                campaign_type[4],
                campaign_type[5],
                campaign_type[6],
                campaign_type[7],
                campaign_type[8]
            ])

            print('Sleeping for 0.5 seconds...')
            time.sleep(0.5)

    campaign_cursor.close()
    campaign_type_cursor.close()
    
    return campaigns_data, campaigns_type_data
