def leader_board_data():
	"""
	The locations of the leader board data files.
	"""
	# Define data locations and available directories:
	data_set_main = "PublicLeaderboardSet"
	year = "2012"
	dates = ["11_26","11_27","11_28","11_29","11_30",
			 "12_01","12_02","12_03","12_04","12_05",
			 "12_06","12_07","12_08","12_09",]

	# Define location of each flighthistoryevents.csv file:
	fhe_location = []
	for date in dates:
		fhe_temp = \
		data_set_main + "/" + year + "_" + date + \
		"/" + "FlightHistory" + "/" + "flighthistoryevents.csv"

		fhe_location.append(fhe_temp)

	return fhe_location