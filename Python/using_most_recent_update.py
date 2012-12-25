import pandas as pd
import leader_board as lb

import flightday as fd

from multiprocessing import Pool


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

	mode = "training"

	# Run model using the most recently updated estimates of 
	# the runway arrival and the gate arrival as the predictions 
	# for the actual arrival times:
	if mode == "leaderboard":
		fn = folder_names_test_set()
		data_set_name = "PublicLeaderboardSet"

		fd.run_model(fn, data_set_name, mode)
	elif mode == "training":
		fn = folder_names_init_set()
		data_set_name = "InitialTrainingSet_rev1"

		rmse = []
		for i in range(10):
			temp = fd.run_model(fn, data_set_name, mode)
			print temp
			rmse.append(temp)

		print rmse
		print sum(rmse) / float(len(rmse))
	else:
		print "Not a valid option!"

if __name__=='__main__':
	main()

