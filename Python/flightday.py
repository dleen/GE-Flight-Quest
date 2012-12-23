import re
import pandas as pd
from dateutil.tz import tzutc
from datetime import datetime


import date_utilities as dut

class FlightDay:
	"""
	A Day class for storing all the information we know about one day of flight data
	"""

	def __init__(self, folder_name, data_set_name):
		self.flight_history = \
			pd.read_csv("../Data/" + data_set_name + \
			"/" + folder_name + "/" + "FlightHistory/flighthistory.csv",
			converters = dut.get_flight_history_date_converter())

		self.flight_history_events = \
			pd.read_csv("../Data/" + data_set_name + "/" + folder_name + "/" + "FlightHistory/flighthistoryevents.csv",
			converters={"date_time_recorded": dut.parse_datetime_format6})

		self.flight_predictions = pd.DataFrame(None, columns=('flight_history_id', 'actual_runway_arrival', 'actual_gate_arrival'))

		cutoff_time_list = pd.read_csv("../Data/" + data_set_name + "/" "days.csv", index_col='folder_name', parse_dates=[1])
		self.cutoff_time = cutoff_time_list['selected_cutoff_time'].ix[folder_name]

		self.midnight_time = datetime(self.cutoff_time.year, 
									  self.cutoff_time.month, 
									  self.cutoff_time.day, 
									  tzinfo=tzutc())

		self.data_set_name = data_set_name

		
	def flight_history_id_grouping(self, that_df):
		"""
		Description here
		"""
		joined_data = pd.merge(left=that_df,     right=self.flight_history_events, on='flight_history_id', how='left', sort=False)
		joined_data = pd.merge(left=joined_data, right=self.flight_history,        on='flight_history_id', how='left', sort=False)

		grouped_on_fhid = joined_data.groupby('flight_history_id')

		return grouped_on_fhid

	def confirm_read(self):
		print self.flight_predictions

def using_most_recent_updates_all(days_list, data_set_name):
	fin = pd.DataFrame(columns=('flight_history_id', 'actual_runway_arrival', 'actual_gate_arrival'))

	print data_set_name
	for d in days_list:
		print d,
		data_test_set = pd.read_csv("../Data/" + data_set_name + "/" + d + "/test_flights.csv", usecols=[0])
		day = FlightDay(d, data_set_name)
		day_preds = using_most_recent_updates_daily(day, data_test_set)
	
		fin = pd.concat([fin, day_preds])
		print "...done"

	fin.to_csv('test.csv', index=False)

def using_most_recent_updates_daily(day, data_test_set):
	flight_events = day.flight_history_id_grouping(data_test_set)

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

	day.flight_predictions['actual_runway_arrival'] = \
		day.flight_predictions['actual_runway_arrival'].apply(dut.parse_to_utc)

	day.flight_predictions['actual_gate_arrival'] = \
		day.flight_predictions['actual_gate_arrival'].apply(dut.parse_to_utc)

	day.flight_predictions = \
		day.flight_predictions.fillna(value=day.cutoff_time)

	day.flight_predictions = \
		dut.convert_predictions_from_datetimes_to_minutes(day.flight_predictions, day.midnight_time)

	return day.flight_predictions

def most_recent_update(event_group):
	"""
	Description here
	"""
	event_group = event_group.sort_index(by='date_time_recorded', ascending=False)

	temp = event_group['data_updated']

	era_est_list = temp.apply(lambda x: parse_fhe_events(x, "ERA"))
	ega_est_list = temp.apply(lambda x: parse_fhe_events(x, "EGA"))

	era_est = get_most_recent(era_est_list)
	ega_est = get_most_recent(ega_est_list)

	offset = event_group["arrival_airport_timezone_offset"].ix[event_group.index[0]]
	if offset>0:
		offset_str = "+" + str(offset)
	else:
		offset_str = str(offset)

	if era_est:
		era_est = era_est + offset_str

	if ega_est:
		ega_est = ega_est + offset_str

	return [era_est, ega_est]

def get_updated_arrival(event_list, row, arrival_type, cutoff_time, offset):
	if arrival_type == "runway"
		sig = "ERA"
	elif arrival_type == "gate":
		sig = "EGA"
	else:
		print "Problem with signal type!"

	est_list = temp.apply(lambda x: parse_fhe_events(x, "ERA"))


def get_scheduled_arrival(row, arrival_type, cutoff_time):
	if row["scheduled_%s_arrival" % arrival_type] != "MISSING":
		return row["scheduled_%s_arrival" % arrival_type]
	if row["scheduled_%s_arrival" % get_other_arrival_type(arrival_type)] != "MISSING":
		return row["scheduled_%s_arrival" % get_other_arrival_type(arrival_type)]
	if row["published_arrival"] != "MISSING":
		return row["published_arrival"]
	return cutoff_time 

def get_estimated_arrival(row, arrival_type, cutoff_time):
	if row["estimated_%s_arrival" % arrival_type] != "MISSING":
		return row["estimated_%s_arrival" % arrival_type]
	if row["estimated_%s_arrival" % get_other_arrival_type(arrival_type)] != "MISSING":
			return row["estimated_%s_arrival" % get_other_arrival_type(arrival_type)]
	return get_scheduled_arrival(row, arrival_type, cutoff_time)

def get_other_arrival_type(arrival_type):
	if arrival_type == "runway":
		return "gate"
	return "runway"

def parse_fhe_events(event, e_type):
	"""
	Given a data updated event from flight_history_events
	extract the ERA or EGA times (if any) or else return None
	"""
	if type(event) != str:
		return None
	if e_type not in event:
		return None
	# VVV (Below) Interesting piece of information --
	# is EGA calculated just from distance and speed?
	if event == "EGA- Based on Distance and Airspeed":
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
	pick the first entry which is not None
	"""
	for x in est_list:
		if x:
			return x
