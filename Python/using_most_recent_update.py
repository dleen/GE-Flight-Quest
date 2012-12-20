from numpy import genfromtxt, savetxt
import numpy as np
import csv
import pandas as pd
import leader_board as lb

def main():
	data_set_main = "PublicLeaderboardSet"
	fhe_location = lb.leader_board_data()

	# Read in the flight_history_ids of the flight times to be predicted:
	#data_test_set = \
	#	genfromtxt(open("../Data/" + data_set_main + "/test_flights_combined.csv",'r'),
	#				delimiter=',', dtype='i8', usecols=0, skip_header=1)

	data_test_set = \
		pd.read_csv("../Data/" + data_set_main + "/test_flights_combined.csv", parse_dates=True)

	
	# Read in one of the training days:
	data_train_set = \
		pd.read_csv("../Data/" + fhe_location[0], parse_dates=True)

	print data_train_set	


if __name__=='__main__':
 	main() 
