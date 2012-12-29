import pandas as pd
import datetime
from dateutil import parser
import pytz
import random

def generate_cutoff_times():
    """
    Generate a random cutoff time between using the same method as
    Kaggle. Returns a list of cutoff times, one for each day in the data
    """
    num_days = 14
    first_day = parser.parse("2012-11-12")
    first_day = pytz.utc.localize(first_day)
    interval_beginning_hours_after_midnight_UTC = 14
    interval_length = 12

    day_beginning = []
    selected_cutoff_time = []
    folder_names = []

    for day in range(num_days):
        db = first_day + datetime.timedelta(days = day, hours=9)
        interval_beginning = first_day + datetime.timedelta(days = day, 
            hours=interval_beginning_hours_after_midnight_UTC)
        sct = interval_beginning + datetime.timedelta(hours = random.uniform(0, interval_length))
        fn = str(db.year) + "_" + str(db.month) + "_" + str(db.day)

        day_beginning.append(db)
        selected_cutoff_time.append(sct)
        folder_names.append(fn)

    d = {'day_beginning' : day_beginning,
         'selected_cutoff_time' : selected_cutoff_time,
         'folder_name' : folder_names}

    cutoff_times = pd.DataFrame(d, columns=('day_beginning', 'selected_cutoff_time', 'folder_name'),
        index=folder_names)

    return cutoff_times

def select_valid_rows(df, cutoff_time, codes):
    """
    Given a flight history select rows for inclusion in the test set using
    the function flight_history_row_in_test_set which is given by the Kaggle
    admins
    """
    sel_rows = []

    for i, row in df.iterrows():
        temp = flight_history_row_in_test_set(row, cutoff_time, codes)
        sel_rows.append(temp)

    return df[['flight_history_id', 'actual_runway_arrival', 'actual_gate_arrival']][sel_rows]

def get_departure_time(row):
    """
    Try to select a valid departure time from the available ones
    """
    if row["published_departure"] != "MISSING":
        return row["published_departure"]
    if row["scheduled_gate_departure"] != "MISSING":
        return row["scheduled_gate_departure"]
    if row["scheduled_runway_departure"] != "MISSING":
        return row["scheduled_runway_departure"]
    return "MISSING"

def flight_history_row_in_test_set(row, cutoff_time, us_icao_codes):
    """
    This function returns True if the flight is in the air and it
    meets the other requirements to be a test row (continental US flight)
    """
    departure_time = get_departure_time(row)
    if departure_time > cutoff_time:
        return False
    if row["actual_gate_departure"] == "MISSING":
        return False
    if row["actual_runway_departure"] == "MISSING":
        return False
    if row["actual_runway_departure"] != "HIDDEN":
        if row["actual_runway_departure"] > cutoff_time:
            return False
    if row["actual_runway_arrival"] == "MISSING":
        return False
    if row["actual_runway_arrival"] != "HIDDEN":
        if row["actual_runway_arrival"] <= cutoff_time:
            return False
    if row["actual_gate_arrival"] == "MISSING":
        return False
    if row["actual_gate_arrival"] != "HIDDEN" and row["actual_runway_arrival"] != "HIDDEN":
        if row["actual_gate_arrival"] < row["actual_runway_arrival"]:
            return False
    if row["actual_runway_departure"] != "HIDDEN" and row["actual_gate_departure"] != "HIDDEN":
        if row["actual_runway_departure"] < row["actual_gate_departure"]:
            return False 
    if row["arrival_airport_icao_code"] not in us_icao_codes:
        return False
    if row["departure_airport_icao_code"] not in us_icao_codes:
        return False
    return True

def get_us_airport_icao_codes():
    df = pd.read_csv("../Data/Reference/usairporticaocodes.txt")
    return set(df["icao_code"])



# utilities.filter_file_based_on_cutoff_time_streaming(os.path.join(training_day_path, 
#     "FlightHistory", "flighthistoryevents.csv"),
#     os.path.join(utilities.get_output_subdirectory(test_day_path, "FlightHistory"), "flighthistoryevents.csv"),
#     "date_time_recorded",
#     utilities.parse_datetime_format3,
#     cutoff_time)

# def filter_file_based_on_cutoff_time_streaming(
#     input_path,
#     output_path,
#     date_column_name,
#     date_parser,
#     cutoff_time,
#     ids_to_track_column_name = None
#     ):

#     if ids_to_track_column_name is not None:
#         ids_tracked = set()
#     else:
#         ids_tracked = None

#     f_in = open(input_path)
#     reader = HeaderCsvReader(f_in)
#     f_out = open(output_path, "w")
#     writer = csv.writer(f_out, dialect=CsvDialect())
#     writer.writerow(reader.header)

#     converters = {date_column_name: date_parser}

#     i_total = 0
#     i_keep = 0

#     for row in reader:
#         i_total += 1
#         parse_row(converters, row)
#         if row[date_column_name] > cutoff_time:
#             continue
#         if ids_to_track_column_name is not None:
#             ids_tracked.add(row[ids_to_track_column_name])
#         i_keep += 1
#         row[date_column_name] = str(row[date_column_name])
#         writer.writerow([row[col_name] for col_name in reader.header])

#     print("%s, %s: %d lines remaining out of %d original lines" % \
#         (get_day_str(cutoff_time), os.path.split(input_path)[1], i_keep, i_total))

#     f_out.close()
#     return ids_tracked


def filter_data_based_on_cutoff_and_test_ids(test_flight_history_ids,
    input_data_to_filter, date_column_name, cutoff_time):

    df = pd.merge(left=test_flight_history_ids, right=input_data_to_filter.reset_index(),
        on='flight_history_id', how='left', sort=False)

    ind = df[df[date_column_name] > cutoff_time]

    return input_data_to_filter.drop(ind['index'].values, axis=0)





