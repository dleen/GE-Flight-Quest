from numpy import genfromtxt, savetxt
import numpy as np
import csv
import pandas as pd
import leader_board as lb

def main():
	data_set_main = "PublicLeaderboardSet"
	fhe_location = lb.leader_board_data()

	# Read in the flight_history_ids of the flight times to be predicted:
	data_test_set = \
		pd.read_csv("../Data/" + data_set_main + "/test_flights_combined.csv", parse_dates=True)

	# Read in one of the training days:
	data_train_set = \
		pd.read_csv("../Data/" + fhe_location[0], parse_dates=True)


	df = data_train_set.groupby('flight_history_id')


	test = df.groups[281417384]
	
	test2 = data_train_set.ix[test]

	test3 = test2['event'] == "Time Adjustment"
	print test3

	print test2.sort_index(by='date_time_recorded')

def most_recent_update(grouped_vals):
	val = grouped_vals.sort_index(by='date_time_recorded')




if __name__=='__main__':
 	main()