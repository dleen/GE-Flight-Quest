import numpy as np

from models import flightday as fd

from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor

from sklearn import preprocessing

from sklearn import cross_validation

from uses_all_data import group_all_data as gad

from utilities import rmse

from learning import random_forest_feature_importance as rffi


def predict_aga():

    [X_train, y_train, ind_train] = rffi.load_and_format_data('all_combined_no_dates')
