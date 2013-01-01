import numpy as np
import pandas as pd

def rmse_fun(actual, predicted):
    """
    Calculate the root mean square difference between the actual and predicted times.
    """
    N = len(actual)
    N1 = len(predicted)

    if N == 0 or N1 == 0: 
        raise "Zero length input!"
    elif N1 != N:
        raise "Actual and Predicted array lengths do not match!"

    diff = np.subtract(actual, predicted)
    square_diff = np.multiply(diff, diff)
    square_sum = np.sum(square_diff)

    return np.sqrt(float(square_sum) / N)

def rmse_final(data):
    """
    The final rmse score is a weighted sum of the runway arrival times
    and the gate arrival times.
    """
    rmse_gate = rmse_fun(data['actual_gate_arrival_actual'].values, 
        data['actual_gate_arrival_predicted'].values)
    rmse_run = rmse_fun(data['actual_runway_arrival_actual'].values, 
        data['actual_runway_arrival_predicted'].values)

    return 0.75 * rmse_gate + 0.25 * rmse_run

def calculate_rmse_score(fin, tst):
    if len(fin) != len(tst):
        print "Error with the lengths of predicted and test data!"
        print "Test length: {}, Pred length: {}".format(len(tst), len(fin))
    
    combined_on_id = pd.merge(left=tst, right=fin,
        on='flight_history_id', suffixes=('_predicted', '_actual'),  sort=False)

    return rmse_final(combined_on_id)
