
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn import metrics
from pathlib import Path
from sklearn.neighbors import NearestNeighbors
import joblib
import os


import warnings
warnings.filterwarnings("ignore")

def training(): 
  """# Input data"""
  current_directory = Path(__file__).resolve().parent
  data_folder = current_directory.parent / 'data'
  genome_tag = pd.read_csv(data_folder / 'campaign_type.csv')
  campaign_data = pd.read_csv(data_folder / 'campaign.csv')

  """# Content-based recommendation"""
  matrix_score = genome_tag[["community_type","education_type","research_writing_editing","help_other","environment","healthy","emergency_preparedness"]]
  matrix_score = np.array(matrix_score)
  knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=100 if matrix_score.shape[0] > 100 else matrix_score.shape[0], n_jobs=-1)
  knn.fit(matrix_score)

  #delete old model
  os.remove(data_folder / 'model' / 'knnModel.joblib')
  #export model trained
  joblib.dump(knn, data_folder / 'model' / 'knnModel.joblib')
