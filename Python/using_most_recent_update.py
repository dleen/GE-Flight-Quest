import numpy as np
import pandas as pd
import leader_board as lb
import re

def main():
	data_set_main = "PublicLeaderboardSet"
	# Find the location of flighthistoryevents.csv for the leaderboard dataset:
	fhe_location = lb.leader_board_data()

	# Read in the flight_history_ids of the flight times to be predicted:
	data_test_set = \
		pd.read_csv("../Data/" + data_set_main + "/test_flights_combined.csv", parse_dates=True)

	# Read in one of the training days, specifically the file flighthistoryevents.csv:
	data_train_set = \
		pd.read_csv("../Data/" + fhe_location[0], parse_dates=True)

	# Inner join the two data sets on flight_history_id:
	df_join = pd.merge(left=data_test_set, right=data_train_set, on='flight_history_id')

	# Group entries in table by flight_history_id:
	df_grouped = df_join.groupby('flight_history_id')

	# Select all entries corresponding to a particular fhid:
	# TODO: replace this with a loop over all ids.
	i = 0
	for name, group in df_grouped:
		if i < 100:
			#print name
			#print group
			print most_recent_update(group)
		else: 
			break

		i = i + 1


def most_recent_update(common_fh_id):
	val2 = common_fh_id.sort_index(by='date_time_recorded', ascending=False)

	for row in val2['data_updated']:
		if "ERA" in row:
			#print row
			era = re.search('(ERA-.*?(?<=New=))(?P<dt>\d\d/\d\d/\d\d \d\d:\d\d)', row)
			#print era.group('dt')
			break

	for row in val2['data_updated']:
		if "EGA" in row:
			#print row
			ega = re.search('(EGA-.*?(?<=New=))(?P<dt>\d\d/\d\d/\d\d \d\d:\d\d)', row)
			#print ega.group('dt')
			break

	return [era.group('dt'), ega.group('dt')]

if __name__=='__main__':
 	main()