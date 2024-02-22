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
    with mysql:
        with mysql.cursor() as campaign_cursor:
            campaign_cursor.execute('SELECT campaign_id, content, numbers_volunteer, start_day, end_day, location, status, create_day, update_day, update_by FROM campaign')
            mysql.commit()

            campaigns_data = [
                ['campaign_id', 'content', 'numbers_volunteer', 'start_day', 'end_day', 'location', 'status', 'create_day', 'update_day','update_by']
            ]
            campaigns_type_data = [
                ['type_id', 'campaign_id', 'community_type', 'education_type', 'research_writing_editing', 'help_other', 'environment', 'healthy', 'emergency_preparedness']
            ]

            for row in campaign_cursor.fetchall():
                with mysql.cursor() as campaign_type_cursor:
                    campaign_type_cursor.execute('SELECT * FROM campaign_type WHERE campaign_id = %s', (row['campaign_id'],))
                    mysql.commit()
                    campaign_type = campaign_type_cursor.fetchone()
                    if campaign_type is not None:
                        campaigns_data.append([
                            row['campaign_id'],
                            row['content'],
                            row['numbers_volunteer'],
                            row['start_day'].strftime('%Y-%m-%d') if row['start_day'] is not None else None,
                            row['end_day'].strftime('%Y-%m-%d') if row['end_day'] is not None else None,
                            row['location'],
                            row['status'],
                            row['create_day'].strftime('%Y-%m-%d') if row['create_day'] is not None else None,
                            row['update_day'].strftime('%Y-%m-%d') if row['update_day'] is not None else None,
                            row['update_by']
                        ])

                        campaigns_type_data.append([
                            campaign_type['type_id'],
                            campaign_type['campaign_id'],
                            campaign_type['community_type'],
                            campaign_type['education_type'],
                            campaign_type['research_writing_editing'],
                            campaign_type['help_other'],
                            campaign_type['environment'],
                            campaign_type['healthy'],
                            campaign_type['emergency_preparedness']
                        ])

                        print('Sleeping for 0.5 seconds...')
                        time.sleep(0.5)
        
    return campaigns_data, campaigns_type_data
