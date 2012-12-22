import datetime
import dateutil
from dateutil.tz import tzoffset, tzutc

def convert_df_predictions_from_datetimes_to_minutes(df_predictions,
    midnight_time):
    """
    For each day we 
    """

    for i in df_predictions.index:
        df_predictions["actual_runway_arrival"][i] = tu.minutes_difference(
            df_predictions["actual_runway_arrival"][i], midnight_time)
        df_predictions["actual_gate_arrival"][i] = tu.minutes_difference(
            df_predictions["actual_gate_arrival"][i], midnight_time)

    return df_predictions

def minutes_difference(datetime1, datetime2):
    diff = datetime1 - datetime2
    return diff.days*24*60+diff.seconds/60

if __name__=='__main__':
    print "arf"