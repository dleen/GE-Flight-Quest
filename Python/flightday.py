import re
import pandas as pd
from dateutil.tz import tzutc
from datetime import datetime

import date_utilities as dut
import test_data_utils as tdu
import rmse

class FlightDay:
	"""
	A Day class for storing the most basic information we know about one day of flight data i.e.:
	flight_history
	flight_history_events

	flight_predictions: our predictions for the actual arrival times

	cutoff_time_list: this is a list of the times each day where the following is true:
	    flight_history["actual_runway_departure"] < cutoff_time:
    	flight_history["actual_runway_arrival"] >= cutoff_time:

    cutoff_time: is the value in cutoff_time_list corresponding to the folder containing flight_history

    midnight_time: this is the midnight against which we start counting the minutes until arrival
	"""

	def __init__(self, folder_name, data_set_name, mode):
		self.flight_history = \
			pd.read_csv("../Data/" + data_set_name + \
			"/" + folder_name + "/" + "FlightHistory/flighthistory.csv",
			converters = dut.get_flight_history_date_converter())

		if data_set_name == "PublicLeaderboardSet":
			conv = dut.parse_datetime_format6
		else:
			conv = dut.parse_datetime_format3

		self.flight_history_events = \
			pd.read_csv("../Data/" + data_set_name + "/" + folder_name + "/" + \
			 "FlightHistory/flighthistoryevents.csv",
			converters={"date_time_recorded": conv})

		self.flight_predictions = pd.DataFrame(None, columns=('flight_history_id',
			'actual_runway_arrival', 
			'actual_gate_arrival'))

		if data_set_name == "PublicLeaderboardSet":
			cutoff_time_list = pd.read_csv("../Data/" + data_set_name + "/" "days.csv",
				index_col='folder_name', parse_dates=[1])
		else:
			cutoff_time_list = tdu.generate_cutoff_times()

		self.cutoff_time = cutoff_time_list['selected_cutoff_time'].ix[folder_name]

		self.midnight_time = datetime(self.cutoff_time.year, 
									  self.cutoff_time.month, 
									  self.cutoff_time.day, 
									  tzinfo=tzutc())

		self.folder_name = folder_name
		self.data_set_name = data_set_name
		self.mode = mode

		self.test_data = pd.DataFrame(None)

		if mode == "leaderboard":
			self.test_data = \
				pd.read_csv("../Data/" + data_set_name + "/" + folder_name + "/test_flights.csv",
		 		usecols=[0])
		elif mode == "training":
			codes = tdu.get_us_airport_icao_codes()
			self.test_data = tdu.select_valid_rows(self.flight_history, self.cutoff_time, codes)
		else:
			print "Not a valid option!"

	def generate_new_cutoff_times(self):
		"""
		Description
		"""
		if self.data_set_name == "PublicLeaderboardSet":
			print "You don't need to do this."
		else:
			cutoff_time_list = tdu.generate_cutoff_times()
			# Fix folder names, currently static. They need to change?
			self.cutoff_time = cutoff_time_list['selected_cutoff_time'].ix[self.folder_name]

	def generate_new_test_data(self):
		"""
		Description
		"""
		if self.data_set_name == "PublicLeaderboardSet":
			print "You don't need to do this."
		else:
			codes = tdu.get_us_airport_icao_codes()
			self.test_data = tdu.select_valid_rows(self.flight_history, self.cutoff_time, codes)

	def flight_history_id_grouping(self):
		"""
		This function does a "left join" (exactly like SQL join) using the test data flight ids
		as the left data and the flight history events as the right data. We then join the rest
		of the flight history data in a similar manner.
		Maybe this second join will be changed to something smarter?
		"""
		joined_data = pd.merge(left=self.test_data, right=self.flight_history_events, 
							   on='flight_history_id', how='left', sort=False)
		joined_data = pd.merge(left=joined_data, right=self.flight_history, 
							   on='flight_history_id', how='left', sort=False)

		grouped_on_fhid = joined_data.groupby('flight_history_id')

		return grouped_on_fhid

def run_model(days_list, data_set_name, mode):
	[fin, tst] = using_most_recent_updates_all(days_list, data_set_name, mode)

	if mode == "leaderboard":
		fin.to_csv('test.csv', index=False)
		print "All files done!"
		print "Predictions written to csv file in Python folder."
	elif mode == "training":
		# print to log file rmse score
		return calculate_rmse_score(fin, tst)
	else:
		print "Not an option!"

def calculate_rmse_score(fin, tst):
	combined_on_id = pd.merge(left=tst, right=fin,
		on='flight_history_id', suffixes=('_predicted', '_actual'),  sort=False)

	return rmse.rmse_final(combined_on_id)
	
def using_most_recent_updates_all(days_list, data_set_name, mode):
	"""
	Runs the most recent update model for each day in the dataset and returns the result to a 
	csv file in the python directory.
	"""
	fin = pd.DataFrame(columns=('flight_history_id', 'actual_runway_arrival', 'actual_gate_arrival'))
	tst = pd.DataFrame(columns=('flight_history_id', 'actual_runway_arrival', 'actual_gate_arrival'))

	print data_set_name
	for d in days_list:
		print d,
		day = FlightDay(d, data_set_name, mode)
		day = using_most_recent_updates_daily(day)
	
		fin = pd.concat([fin, day.flight_predictions])
		tst = pd.concat([tst, day.test_data])
		print "...done"

	return [fin, tst]

def using_most_recent_updates_daily(day):
	"""
	Given a day of flights calculates the most recent update for runway and
	gate arrival for each of the flights. Enters this into the flight prediction
	dataframe. Replaces any missing values with just the value of the cutoff time.
	Finally converts the predictions to minutes past midnight.
	"""
	flight_events = day.flight_history_id_grouping()

	fid = []
	era = [] 
	ega = []

	for flight_id, event_group in flight_events:
		temp =  most_recent_update(event_group)
		fid.append(flight_id)
		era.append(temp[0])
		ega.append(temp[1])

	day.flight_predictions = day.flight_predictions.reindex(range(len(fid)))

	day.flight_predictions['flight_history_id']     = fid
	day.flight_predictions['actual_runway_arrival'] = era
	day.flight_predictions['actual_gate_arrival']   = ega

	day.flight_predictions = \
		day.flight_predictions.fillna(value=day.cutoff_time)

	day.flight_predictions = \
		dut.convert_predictions_from_datetimes_to_minutes(day.flight_predictions, day.midnight_time)

	if day.mode == "training": 
		day.test_data = \
			dut.convert_predictions_from_datetimes_to_minutes(day.test_data, day.midnight_time)

	return day

def most_recent_update(event_group):
	"""
	Takes in a group of events corresponding to one flight history id.
	Parses the events looking for estimated runway arrival or gate updates
	and returns the most recent update for each.
	"""
	event_group = event_group.sort_index(by='date_time_recorded', ascending=False)

	event_list = event_group['data_updated']

	offset = event_group["arrival_airport_timezone_offset"].ix[event_group.index[0]]
	if offset>0:
		offset_str = "+" + str(offset)
	else:
		offset_str = str(offset)

	era_est = get_updated_arrival(event_list, event_group.ix[event_group.index[0]],
								  "runway", offset_str)

	ega_est = get_updated_arrival(event_list, event_group.ix[event_group.index[0]],
								  "gate", offset_str)

	return [era_est, ega_est]

def get_updated_arrival(event_list, row, arrival_type, offset_str):
	"""
	Returns the most recent estimate of the arrival time. If that
	cannot be found resorts to using the scheduled arrival times.
	"""
	if arrival_type == "runway":
		sig = "ERA"
	elif arrival_type == "gate":
		sig = "EGA"
	else:
		print "Problem with signal type!"

	est_list = event_list.apply(lambda x: parse_fhe_events(x, sig))
	est = get_most_recent(est_list)

	if est:
		est = dut.parse_to_utc(est + offset_str)
	else:
		est = get_scheduled_arrival(row, arrival_type)

	return est

def get_scheduled_arrival(row, arrival_type):
	"""
	Try each of the columns containing arrival information in order
	of perceived importance. If one type runway or gate cannot be found
	use the opposite type information before moving onto the next column of 
	data. Return None is all data is missing
	"""
	if row["scheduled_%s_arrival" % arrival_type] != "MISSING":
		return row["scheduled_%s_arrival" % arrival_type]
	if row["scheduled_%s_arrival" % get_other_arrival_type(arrival_type)] != "MISSING":
		return row["scheduled_%s_arrival" % get_other_arrival_type(arrival_type)]
	if row["published_arrival"] != "MISSING":
		return row["published_arrival"]
	return None 

def get_other_arrival_type(arrival_type):
	"""
	Quick swapping of runway and gate
	"""
	if arrival_type == "runway":
		return "gate"
	return "runway"

def parse_fhe_events(event, e_type):
	"""
	Given a data updated event from flight_history_events
	extract the ERA or EGA times (if any) or else return None
	If an event does not meet any of these criteria print the event
	and return None
	"""
	if type(event) != str:
		return None
	if e_type not in event:
		return None
	# VVV (Below) Interesting piece of information --
	# is EGA calculated just from distance and speed?
	if event in ["EGA- Based on Distance and Airspeed",
	"EGA- Based on Flight Histories"]:
		return None

	est = re.search('(%s-.*?(?<=New=))(?P<dt>\d\d/\d\d/\d\d \d\d:\d\d)'%e_type, event)

	if est:
		return est.group('dt')
	else:
		print event
		return None

def get_most_recent(est_list):
	"""
	Given an ordered list, with most recent time first,
	pick the first entry which is not None otherwise return None
	"""
	for x in est_list:
		if x:
			return x
	return None
