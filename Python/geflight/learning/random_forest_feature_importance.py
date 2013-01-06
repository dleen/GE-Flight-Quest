import numpy as np

from models import flightday as fd

from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor

from sklearn import preprocessing

from sklearn import cross_validation

from uses_all_data import group_all_data as gad

from utilities import rmse

def load_and_format_data(filename, mode=""):
    Z = gad.load_all_parsed_fhe(filename)

    del Z['AGA_most_recent']
    del Z['ARA_most_recent']

    if mode != "leaderboard":
        Z = Z.dropna()
        Z = Z.reset_index(drop=True)

    X = Z.copy()

    del X['actual_gate_arrival_minutes_after_midnight']
    del X['actual_runway_arrival_minutes_after_midnight']
    del X['flight_history_id']

    le = preprocessing.LabelEncoder()

    cols = ['status',
        'icao_aircraft_type_actual',
        'departure_airport_icao_code',
        'arrival_airport_icao_code',
        'airline_icao_code',
        'flight_number',
        'arrival_gate',
        'arrival_terminal',
        'departure_gate',
        'departure_terminal'
    ]

    le.fit(X[cols].values)

    for c in cols:
        X[c] = le.transform(X[c])

    y = Z[['actual_runway_arrival_minutes_after_midnight',
        'actual_gate_arrival_minutes_after_midnight']]

    ind = Z[['flight_history_id']]

    return [X, y, ind]

def r_forest():

    [X_train, y_train, ind_train] = load_and_format_data('all_combined_no_dates')
    [X_test, y_test, ind_test] = load_and_format_data('all_combined_no_dates')

    print len(X_train)


    # y_train_runway = y_train['actual_runway_arrival_minutes_after_midnight']
    # y_train_gate   = y_train['actual_gate_arrival_minutes_after_midnight']


    forest = RandomForestRegressor(n_estimators=2, random_state=None, n_jobs=-1)
    # forest = ExtraTreesRegressor(n_estimators=200, random_state=None, n_jobs=-1)
    # forest = GradientBoostingRegressor(n_estimators=200,
    #     learn_rate=0.1, max_depth=5, random_state=None, loss='ls')


    # forest.fit(X_train, y_train_runway)
    # y_pred_runway = forest.predict(X_pred)

    # forest.fit(X_train, y_train_gate)
    # y_pred_gate = forest.predict(X_pred)

    # forest.fit(X_train, y_train)
    # y_pred = forest.predict(X_pred)


    # y_pred_runway = y_pred[:,0]
    # y_pred_gate = y_pred[:,1]


    # pred = fd.FlightPredictions()

    # pred.flight_predictions = pred.flight_predictions.reindex(range(len(ind_pred)))

    # pred.flight_predictions['flight_history_id']     = ind_pred
    # pred.flight_predictions['actual_runway_arrival'] = y_pred_runway
    # pred.flight_predictions['actual_gate_arrival']   = y_pred_gate

    # pred.flight_predictions = pred.flight_predictions.sort(columns='flight_history_id')

    # pred.flight_predictions.to_csv('test_rand_forest.csv', index=False)

    score = []
    kfold = cross_validation.KFold(n=len(X_train), k=2, indices=False, shuffle=True)

    for i, (traincv, testcv) in enumerate(kfold):

            print i

            pred = fd.FlightPredictions()
            y_pred = []; ind_pred = []; y_pred_runway = []; y_pred_gate = []

            print "Starting training...",
            forest.fit(X_train[traincv], y_train[traincv])
            print "done"
            print "Starting prediction...",
            y_pred = forest.predict(X_train[testcv])
            print "done"

            ind_pred = ind_train[testcv].values

            y_pred_runway = y_pred[:,0]
            y_pred_gate = y_pred[:,1]

            pred.flight_predictions = \
                pred.flight_predictions.reindex(range(len(ind_pred)))
            pred.test_data = \
                pred.test_data.reindex(range(len(ind_pred)))

            pred.flight_predictions['flight_history_id']     = ind_pred
            pred.flight_predictions['actual_runway_arrival'] = y_pred_runway
            pred.flight_predictions['actual_gate_arrival']   = y_pred_gate

            pred.test_data['flight_history_id']     = ind_pred
            pred.test_data['actual_runway_arrival'] = \
                y_train['actual_runway_arrival_minutes_after_midnight'][testcv].values
            pred.test_data['actual_gate_arrival']   = \
                y_train['actual_gate_arrival_minutes_after_midnight'][testcv].values

            score.append(rmse.calculate_rmse_score(pred.flight_predictions, pred.test_data))

    print score

    print np.mean(score)
    print np.std(score)

    
    # ans = [forest.fit(X.ix[train], y.ix[train]).score(X.ix[test], y.ix[test]) for train, test in kfold]

    # print ans

    # forest.fit(X,y)

    # for c in cols:
    #   Z[c] = le.inverse_transform(Z[c])

    # importances = forest.feature_importances_
    # std = np.std([tree.feature_importances_ for tree in forest.estimators_], axis=0)
    # indices = np.argsort(importances)[::-1]

    # # f_names = X.columns[indices]

    # # Plot the feature importances of the forest
    # import pylab as pl
    # pl.figure()
    # pl.title("Feature importances")
    # pl.bar(xrange(len(indices)), importances[indices], color="r", yerr=std[indices], align="center")
    # # pl.bar(xrange(len(indices)), importances[indices], color="r", align="center")
    # pl.xticks(xrange(len(indices)), indices, rotation='vertical')
    # pl.xlim([-1, len(indices)])
    # pl.show()

def init_vs_leader():
    pass
    # [X_pred, y_pred, ind_pred] = load_and_format_data('all_combined_test_no_dates_leaderboard', 'leaderboard')


