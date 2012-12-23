import pandas as pd
import leader_board as lb

import flightday as fd

def main():
	fn = lb.folder_names()
	data_set_main = "PublicLeaderboardSet"

	fd.using_most_recent_updates_all(fn, data_set_main)

if __name__=='__main__':
 	main()