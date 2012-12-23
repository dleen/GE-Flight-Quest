import pandas as pd
import leader_board as lb
import re

import flightday as fd

from dateutil.parser import parse
from dateutil.tz import tzutc, tzoffset

from datetime import *

import utilities as ut


def main():
	fn = lb.folder_names()
	data_set_main = "PublicLeaderboardSet"

	fd.using_most_recent_updates_all(fn, data_set_main)

	# x = pd.DataFrame(None, columns = ('col1', 'col2'))

	# print x

	# x = x.reindex(range(10))

	# print x

	# x['col1'] = range(10)

	# print x

	# print len(data_test_set)


	# d = fd.using_most_recent_updates_daily(x, data_test_set)

	# print d.flight_predictions[0:10]




	# fin = pd.DataFrame(columns=('flight_history_id', 'actual_runway_arrival', 'actual_gate_arrival'))

	# for i in range(len(fh_location)):
	# 	df = flight_days(i)
	# 	fin = pd.concat([fin, df])

	# fin.to_csv('test.csv', index=False)


def flight_days(i):
	# Which dataset to use:
	data_set_main = "PublicLeaderboardSet"
	# Find the location of flighthistoryevents.csv for the leaderboard dataset:



	# Read in the flight_history_ids of the flight times to be predicted:
	data_test_set = \
		pd.read_csv("../Data/" + test_location[i])


	# Inner join the two data sets on flight_history_id:
	data_joined = pd.merge(left=data_test_set, right=data_train_set_2, on='flight_history_id', how='left')
	data_joined = pd.merge(left=data_joined,   right=data_train_set,   on='flight_history_id', how='left')

	prune_columns(data_joined)

	# Group entries in table by flight_history_id:
	data_grouped_fhid = data_joined.groupby('flight_history_id')

	# Select all entries corresponding to a particular fhid:
	era  = []
	ega  = []
	fhid = []

	for name, group in data_grouped_fhid:
		temp = most_recent_times(group)
		fhid.append(name)
		era.append(temp[0])
		ega.append(temp[1])

	d = {'flight_history_id' : fhid, 
		 'actual_runway_arrival' : era,
		 'actual_gate_arrival' : ega}

	test = pd.DataFrame(d, columns=('flight_history_id', 'actual_runway_arrival', 'actual_gate_arrival'))

	return test


def most_recent_times(common_fh_id):
	common_fh_id = common_fh_id.reset_index()
	ind  = common_fh_id['event'] == "Time Adjustment"
	val1 = common_fh_id[ind]
	val2 = val1.sort_index(by='date_time_recorded', ascending=False)

	offset = common_fh_id['arrival_airport_timezone_offset'][0]
	dep_day = common_fh_id['actual_runway_departure'][0].day

	if val2.empty:		
		a = common_fh_id['scheduled_runway_arrival_y'][0]
		if a != "MISSING":
			a_mins = a.hour * 60 + a.minute
			if a.day != dep_day:
				a_mins = 1440 + a_mins

		b = common_fh_id['scheduled_gate_arrival_y'][0]
		if b != "MISSING":
			b_mins = b.hour * 60 + b.minute
			if b.day != dep_day:
				b_mins = 1440 + b_mins

		c = common_fh_id['published_arrival_y'][0]
		if c != "MISSING":
			c_mins = c.hour * 60 + c.minute
			if c.day != dep_day:
				c_mins = 1440 + c_mins

		d = common_fh_id['published_departure_y'][0]
		if d != "MISSING":
			d_mins = d.hour * 60 + d.minute
			if d.day != dep_day:
				d_mins = 1440 + d_mins

		if   a != "MISSING" and b != "MISSING":
			return [a_mins, b_mins]
		elif a == "MISSING" and b != "MISSING":
			if c != "MISSING":
				return [c_mins, b_mins]
			elif d != "MISSING":
				return [d_mins, b_mins]
			else:
				return [1000, b_mins]
		elif a != "MISSING" and b == "MISSING":
			if c != "MISSING":
				return [a_mins, c_mins]
			elif d != "MISSING":
				return [a_mins, d_mins]
			else:
				return [a_mins, 1000]
		elif c != "MISSING":
			return [c_mins, c_mins]
		elif d != "MISSING":
			return [d_mins, d_mins]
		else:
			return [1000, 1000]
	else:
		if common_fh_id['scheduled_gate_arrival_y'][0] != "MISSING":
			era_val  = common_fh_id['scheduled_gate_arrival_y'][0]
		elif common_fh_id['scheduled_runway_arrival_y'][0] != "MISSING":
			era_val  = common_fh_id['scheduled_runway_arrival_y'][0]
		elif common_fh_id['published_arrival_y'][0] != "MISSING":
			era_val  = common_fh_id['published_arrival_y'][0]
		elif common_fh_id['published_departure_y'][0] != "MISSING":
			era_val  = common_fh_id['published_departure_y'][0]

		era_mins = era_val.hour * 60 + era_val.minute
		if era_val.day != dep_day:
			era_mins = 1440 + era_mins
		ega_mins = era_mins

		for x in val2['data_updated']:
			if "ERA" in x:
				era_mins = 0
				era = re.search('(ERA-.*?(?<=New=))(?P<dt>\d\d/\d\d/\d\d \d\d:\d\d)', x)
				era_val = parse(era.group('dt') + str(offset))
				era_val = era_val.astimezone(tzutc())
				era_mins = era_val.hour * 60 + era_val.minute
				if era_val.day != dep_day:
					era_mins = 1440 + era_mins				
				break

		for row in val2['data_updated']:
			if "EGA" in row:
				ega_mins = 0
				ega = re.search('(EGA-.*?(?<=New=))(?P<dt>\d\d/\d\d/\d\d \d\d:\d\d)', row)
				ega_val = parse(ega.group('dt') + str(offset))
				ega_val = ega_val.astimezone(tzutc())
				ega_mins = ega_val.hour * 60 + ega_val.minute
				if ega_val.day != dep_day:
					ega_mins = 1440 + ega_mins
				break

		return [era_mins, ega_mins]

def prune_columns(df):
	del df['departure_airport_code_x']
	del df['arrival_airport_code_x']
	del df['published_departure_x']
	del df['published_arrival_x']
	del df['scheduled_gate_departure_x']
	del df['scheduled_gate_arrival_x']
	del df['scheduled_runway_departure_x']
	del df['scheduled_runway_arrival_x']

	del df['airline_code']
	del df['airline_icao_code']
	del df['flight_number']
	del df['departure_airport_code_y']
	del df['departure_airport_icao_code']
	del df['arrival_airport_code_y']
	del df['arrival_airport_icao_code']
	del df['creator_code']	

	del df['scheduled_block_time']
	del df['scheduled_aircraft_type']
	del df['actual_aircraft_type']
	del df['icao_aircraft_type_actual']

	del df['actual_runway_arrival']
	del df['actual_gate_arrival']

	return df





if __name__=='__main__':
 	main()