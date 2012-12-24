import pandas as pd
import leader_board as lb

import flightday as fd

def folder_names_test_set():
	'''
	Returns a list of folders containing data for the individual days
	'''
	year = "2012"
	dates = ["11_26","11_27","11_28","11_29","11_30",
			 "12_01","12_02","12_03","12_04","12_05",
			 "12_06","12_07","12_08","12_09",]

	return [year + "_" + d for d in dates]

def folder_names_init_set():
	'''
	Returns a list of folders containing data for the individual days
	'''
	year = "2012"
	dates = ["11_12","11_13","11_14","11_15","11_16",
			 "11_17","11_18","11_19","11_20","11_21",
			 "11_22","11_23","11_24","11_25",]

	return [year + "_" + d for d in dates]

def main():
	"""
	Main file.
	Directory structure is expected to be:
	main_folder/
		Data/
			PublicLeaderboardSet/
				2012_11_26/
				2012_11_27/
				etc...
			InitialTrainingSet_rev1/
				2012_11_12/
				2012_11_13/
				etc...
		Python/
			using_most_recent_update.py
			flightday.py
			date_utilities.py
			etc...
		R/
			R_code_here.R

	The current model uses the most recent arrival update which
	can be found in flight_history_events.csv
	"""
	# Returns list of the folder names to be opened
	fn = folder_names_init_set()
	#fn = folder_names_test_set()

	# Name of the main data folder
	#data_set_name = "PublicLeaderboardSet"
	data_set_name = "InitialTrainingSet_rev1"


	# Run model using the most recently updated estimates of 
	# the runway arrival and the gate arrival as the predictions 
	# for the actual arrival times:
	fd.using_most_recent_updates_all(fn, data_set_name)

	# x = fd.FlightDay(fn[10], data_set_name)
	# print x.flight_history
	# print x.test_data

	# x.generate_new_cutoff_times()
	# x.generate_new_test_data()

	# print x.test_data

if __name__=='__main__':
 	main()