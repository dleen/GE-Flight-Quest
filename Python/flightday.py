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


def using_most_recent_update(event_group):
	"""
	Description here
	"""
	event_group = event_group.sort_index(by='date_time_recorded', ascending=False)

	offset = event_group["arrival_airport_timezone_offset"].ix[event_group.index[0]]
	if offset>0:
		offset_str = "+" + str(offset)
	else:
		offset_str = str(offset)

	temp = event_group['data_updated']

	era_est = temp.apply(lambda x: parse_fhe_events(x, "ERA"))
	ega_est = temp.apply(lambda x: parse_fhe_events(x, "EGA"))

	return [get_most_recent(era_est) + offset_str,
			get_most_recent(ega_est) + offset_str]

def parse_fhe_events(event, e_type):
	"""
	Given a data updated event from flight_history_events
	extract the ERA or EGA times (if any) or else return None
	"""
	if type(event) != str:
		return None
	if e_type not in event:
		return None
	# VVV Interesting piece of information --
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









