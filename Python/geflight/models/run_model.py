import pandas as pd
import datetime

from models import flightday as fd
from models import extended_flightday as efd

from utilities import rmse

def run_model(model_A, model_B, days_list, data_set_name, mode, cutoff_filename=""):
    """
    Runs the most recent update model for each day in the dataset and returns the result to a 
    csv file in the python directory.
    """
    fin_A = fd.FlightPredictions()
    if model_B != None:
        fin_B = fd.FlightPredictions()

    print "Using mode: {}".format(mode)
    print "Using data from {}".format(data_set_name)

    for i, d in enumerate(days_list):
        if model_B == None:
            print "Running model '{}' on day {} (day {} of {}):".format(model_A, d, i + 1, len(days_list))
        else:
            print "Running models '{}', '{}' on day {} (day {} of {}):".format(model_A, model_B, d, i + 1, len(days_list))

        # day = efd.ExtendedFlightDay(d, data_set_name, mode, cutoff_filename)
        day = fd.FlightDay(d, data_set_name, mode, cutoff_filename)

        fin_A = return_predictions(model_A, day, fin_A)

        if model_B != None:
            fin_B = return_predictions(model_B, day, fin_B)

        print "\tDay {} has finished".format(d)
        print ""

    print "All days in {} are done!".format(data_set_name)

    if "leaderboard" in mode:

        fin_A.flight_predictions = fin_A.flight_predictions.sort(columns='flight_history_id')
        fin_A.flight_predictions.to_csv('test.csv', index=False)
        print "Predictions written to csv file in Python folder."
        if model_B != None:
            print "Warning: we have disregarded the output of '{}'!".format(model_B)

    elif "training" in mode:

        score_A = rmse.calculate_rmse_score(fin_A.flight_predictions, fin_A.test_data)

        if model_B != None:
            score_B = rmse.calculate_rmse_score(fin_B.flight_predictions, fin_B.test_data)
        else:
            score_B = None

        scores = {str(model_A) : score_A, 
                  str(model_B) : score_B}

        log_predictions(day, model_A, model_B, scores, "scores.log")

        return scores

    else:
        print "Not an option!"

def return_predictions(model, day, fin):
    """
    Takes in a model, a day of data and a dataframe for holding the predictions.
    It runs the model, stores the predictions and concatenates them with fin
    which holds the predictions from the other days.
    """
    print "\tStarting model: '{}'...".format(model),
    pred = fd.FlightPredictions()
    pred = model.run_day(day, pred)
    fin.flight_predictions = pd.concat([fin.flight_predictions, pred.flight_predictions])
    fin.test_data          = pd.concat([fin.test_data, pred.test_data])
    print "done"

    return fin

def log_predictions(day, model_A, model_B, scores, filename):
    with open(filename, "a+b") as f:
        f.write("{}: Using model(s): {}, {}. Scores: {}. Using mode: {}. Using cutoff data: {}\n"\
            .format(datetime.datetime.now(), model_A, model_B, scores, day.mode, day.cutoff_filename))