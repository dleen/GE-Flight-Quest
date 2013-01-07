import pandas as pd

def sanity_check(pred, mode):
    if mode == "training":

        combined_on_id = pd.merge(left=pred.flight_predictions, right=pred.test_data,
            on='flight_history_id', suffixes=('_predicted', '_actual'),  sort=False)

        j = 0; k = 0
        j_under_pred = 0; j_over_pred = 0
        k_under_pred = 0; k_over_pred = 0

        pred_len = float(len(combined_on_id))

        print ""
        print "\t\tPrediction problems:"
        for i, row in combined_on_id.iterrows():
            
            if row['actual_runway_arrival_predicted'] < 0 or row['actual_runway_arrival_predicted'] > 1980:
                print "\t\tSanity problem with flight {}! era: {}, ara: {}"\
                .format(row['flight_history_id'], row['actual_runway_arrival_predicted'], 
                    row['actual_runway_arrival_actual'])

            if abs(row['actual_runway_arrival_actual'] - row['actual_runway_arrival_predicted']) > 59:
                print "\t\tPred problem with flight {}! era: {}, ara: {}, diff: {}"\
                .format(row['flight_history_id'], row['actual_runway_arrival_predicted'], 
                    row['actual_runway_arrival_actual'],
                    row['actual_runway_arrival_actual'] - row['actual_runway_arrival_predicted'])

            if row['actual_gate_arrival_predicted'] < 0 or row['actual_gate_arrival_predicted'] > 1980:
                print "\t\tSanity problem with flight {}! ega: {}, aga: {}"\
                .format(row['flight_history_id'], row['actual_gate_arrival_predicted'], 
                    row['actual_gate_arrival_actual'])

            if abs(row['actual_gate_arrival_actual'] - row['actual_gate_arrival_predicted']) > 59:
                print "\t\tPred problem with flight {}! ega: {}, aga: {}, diff: {}"\
                .format(row['flight_history_id'], row['actual_gate_arrival_predicted'], 
                    row['actual_gate_arrival_actual'],
                    row['actual_gate_arrival_actual'] - row['actual_gate_arrival_predicted'])

            if abs(row['actual_runway_arrival_actual'] - row['actual_runway_arrival_predicted']) > 10:
                j = j + 1

            if abs(row['actual_gate_arrival_actual'] - row['actual_gate_arrival_predicted']) > 10:
                k = k + 1

            if   row['actual_runway_arrival_actual'] - row['actual_runway_arrival_predicted'] > 10:
                j_under_pred = j_under_pred + 1

            if - row['actual_runway_arrival_actual'] + row['actual_runway_arrival_predicted'] > 10:
                j_over_pred = j_over_pred + 1

            if   row['actual_gate_arrival_actual'] - row['actual_gate_arrival_predicted'] > 10:
                k_under_pred = k_under_pred + 1

            if - row['actual_gate_arrival_actual'] + row['actual_gate_arrival_predicted'] > 10:
                k_over_pred = k_over_pred + 1

        print ""
        print "\t\tPercent Runway wrong: {} %".format(100 * j / pred_len)
        print "\t\tPercent Gate wrong: {} %".format(100 * k / pred_len)
        print "\t\tRunway under (act > pred) predicted: {} %".format(100 * j_under_pred / pred_len)
        print "\t\tRunway over (pred > act) predicted: {} %".format(100 * j_over_pred / pred_len)
        print "\t\tGate under (act > pred) predicted: {} %".format(100 * k_under_pred / pred_len)
        print "\t\tGate over (pred > act) predicted: {} %".format(100 * k_over_pred / pred_len)
        print "\t",

    elif mode == "leaderboard":
        for i, row in pred.flight_predictions.iterrows():
            pass
