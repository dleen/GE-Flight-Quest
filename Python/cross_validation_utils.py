from sklearn import cross_validation
import pandas as pd

import datetime
from dateutil import parser
import pytz
import random

import leader_board as lb


def main():
	#x = generate_cutoff_times()

	test()

def generate_cutoff_times():
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
		interval_beginning = first_day + datetime.timedelta(days = day, hours=interval_beginning_hours_after_midnight_UTC)
		sct = interval_beginning + datetime.timedelta(hours = random.uniform(0, interval_length))
		fn = str(db.year) + "_" + str(db.month) + "_" + str(db.day)

		day_beginning.append(db)
		selected_cutoff_time.append(sct)
		folder_names.append(fn)

	d = {'day_beginning' : day_beginning,
		 'selected_cutoff_time' : selected_cutoff_time,
		 'folder_name' : folder_names}

	cutoff_times = pd.DataFrame(d, columns=('day_beginning', 'selected_cutoff_time', 'folder_name'))

	return cutoff_times


def test():
	fn = lb.folder_names()
	data_set_main = "InitialTrainingSet_rev1"

	flight_history = \
		pd.read_csv("../Data/" + data_set_name + \
		"/" + fn[0] + "/" + "FlightHistory/flighthistory.csv")

	print flight_history

	#kf = cross_validation.KFold(4, k=2)


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
    if row["actual_runway_departure"] > cutoff_time:
        return False
    if row["actual_runway_arrival"] == "MISSING":
        return False
    if row["actual_runway_arrival"] <= cutoff_time:
        return False
    if row["actual_gate_arrival"] == "MISSING":
        return False
    if row["actual_gate_arrival"] < row["actual_runway_arrival"]:
        return False   
    if row["actual_runway_departure"] < row["actual_gate_departure"]:
        return False 
    if row["arrival_airport_icao_code"] not in us_icao_codes:
        return False
    if row["departure_airport_icao_code"] not in us_icao_codes:
        return False
    return True


if __name__=='__main__':
	main()