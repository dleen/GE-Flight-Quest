from sklearn import cross_validation
import pandas as pd

import datetime
from dateutil import parser
import pytz
import random

import leader_board as lb

import date_utilities as dut


#
# This file is currently under construction
# It will eventually contain the code to:
# 1. Select valid test data in flight_history.csv (valid according to
# flight_history_row_in_test_set, which is deemed correct by the
# Kaggle admins)
# 2. Run a cross validation using this data set.
# 3. More?
#

def main():
	test()

def generate_cutoff_times():
	"""
	Description
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

	cutoff_times = pd.DataFrame(d, columns=('day_beginning', 'selected_cutoff_time', 'folder_name'))

	return cutoff_times

def test():
	"""
	Description
	"""
	cutoff = generate_cutoff_times()

	data_set_name = "InitialTrainingSet_rev1"

	flight_history = \
		pd.read_csv("../Data/" + data_set_name + \
		"/" + cutoff['folder_name'][0] + "/" + "FlightHistory/flighthistory.csv",
		converters = dut.get_flight_history_date_converter())

	codes = get_us_airport_icao_codes("../Data/Reference/usairporticaocodes.txt")




	print select_valid_rows(flight_history, cutoff, codes)



	#kf = cross_validation.KFold(4, k=2)

def select_valid_rows(df, cutoff_time, codes):
	"""
	Description
	"""
	sel_rows = []

	for i, row in df.iterrows():
		temp = flight_history_row_in_test_set(row, cutoff_time, codes)
		sel_rows.append(temp)

	return df[['flight_history_id', 'actual_runway_arrival', 'actual_gate_arrival']][sel_rows]

def get_departure_time(row):
	"""
	Description
	"""
	if row['published_departure'] != "MISSING":
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
	if departure_time == "MISSING":
		return False
	if departure_time > cutoff_time:
		return False
	if row["actual_gate_departure"] in ["MISSING", "HIDDEN"]:
		return False
	if row["actual_runway_departure"] in ["MISSING", "HIDDEN"]:
		return False
	if row["actual_runway_departure"] > cutoff_time:
		return False
	if row["actual_runway_arrival"] in ["MISSING", "HIDDEN"]:
		return False
	if row["actual_runway_arrival"] <= cutoff_time:
		return False
	if row["actual_gate_arrival"] in ["MISSING", "HIDDEN"]:
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

def get_us_airport_icao_codes(codes_file):
    df = pd.read_csv(codes_file)
    return set(df["icao_code"])

if __name__=='__main__':
	main()