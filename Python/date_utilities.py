import datetime
import dateutil
from dateutil.tz import tzoffset, tzutc

#
# Convert from date times to minutes after midnight of the
# day that the flight departed
#
def convert_df_predictions_from_datetimes_to_minutes(df_predictions,
    midnight_time):
    """
    For each day we 
    """

    for i in df_predictions.index:
        df_predictions["actual_runway_arrival"][i] = minutes_difference(
            df_predictions["actual_runway_arrival"][i], midnight_time)
        df_predictions["actual_gate_arrival"][i] = minutes_difference(
            df_predictions["actual_gate_arrival"][i], midnight_time)

    return df_predictions

def minutes_difference(datetime1, datetime2):
    """ Returns the minutes difference between two datetimes """
    diff = datetime1 - datetime2
    return diff.days*24*60+diff.seconds/60

#
# Parse date times in flight_history_events.csv
#
def parse_datetime_format6(datestr):
    """
    Doing this manually for efficiency

    Format: 2012-11-13 14:45:41.964-08:00
    Alternative: 2012-11-13 15:03:16.62-08:00
    Year-Month-Day Hour:Minute:Second.Millise:conds-TimeZoneUTCOffsetInHours:00

    Converts into UTC
    """
    microseconds = datestr[20:-6]
    if not microseconds:
        microseconds=0
    else:
        microseconds = int(microseconds) * (10**(6-len(microseconds)))
   
    dt = datetime.datetime(int(datestr[:4]),
                           int(datestr[5:7]),
                           int(datestr[8:10]),
                           int(datestr[11:13]),
                           int(datestr[14:16]),
                           int(datestr[17:19]),
                           microseconds,
                           tzoffset(None, int(datestr[-6:-3]) * 3600)
                           )
    dt = dt.astimezone(tzutc())
    return dt

#
# parse dates in flighthistory.csv
#
def get_flight_history_date_converter():
    """ 
    Dict of which columns, and the function to apply to convert 
    to datetimes when importing flight_history csv file
    """
    return {x : to_utc_date for x in get_flight_history_date_columns()}

def get_flight_history_date_columns():
    """
    List of the columns which should be converted to datetimes
    """
    flight_history_date_columns = [
        "published_departure",
        "published_arrival",
        "scheduled_gate_departure",
        "scheduled_gate_arrival",
        "actual_gate_departure",
        "actual_gate_arrival",
        "scheduled_runway_departure",
        "scheduled_runway_arrival",
        "actual_runway_departure",
        "actual_runway_arrival",
    ]
    return flight_history_date_columns

def to_utc_date(datestr):
    """
    Convert strings imported from csv to datetimes
    dealing with non-date strings
    """
    if not datestr or datestr == "MISSING":
        return "MISSING"
    if datestr == "HIDDEN":
        return "HIDDEN"
    return parse_datetime_format1(datestr)

def parse_datetime_format1(datestr):
    """
    Doing this manually for efficiency

    Format: 2012-11-12 01:00:03-08
    Year-Month-Day Hour:Minute:Second-TimeZoneUTCOffsetInHours

    Converts into UTC
    """
    dt = datetime.datetime(int(datestr[:4]),
                           int(datestr[5:7]),
                           int(datestr[8:10]),
                           int(datestr[11:13]),
                           int(datestr[14:16]),
                           int(datestr[17:19]),
                           0,
                           tzoffset(None, int(datestr[19:22]) * 3600))
    dt = dt.astimezone(tzutc())
    return dt
