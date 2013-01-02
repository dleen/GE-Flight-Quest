import numpy as np

from sklearn.ensemble import ExtraTreesClassifier

from sklearn.feature_extraction.text import CountVectorizer

from sklearn import tree


from uses_all_data import group_all_data as gad


def forest():
	Z = gad.load_all_parsed_fhe()

	X = np.asarray(Z[['airline_icao_code',
		'flight_number',
		'departure_airport_icao_code',
		'AGD_most_recent',
		'AGD_update_time',
		'ARA_update_time',
		'ARD_most_recent',
		'ARD_update_time',
		'EGA_minutes_after_midnight',
		'EGA_most_recent',
		'EGA_update_time',
		'ERA_minutes_after_midnight',
		'ERA_most_recent',
		'ERA_update_time',
		'actual_gate_departure',
		'actual_runway_departure',
		'arrival_airport_icao_code',
		'departure_airport_icao_code',
		'arrival_gate',
		'arrival_terminal',
		'departure_gate',
		'departure_terminal',
		'icao_aircraft_type_actual',
		'last_update_time',
		'number_of_gate_adjustments',
		'number_of_time_adjustments',
		'published_arrival',
		'published_departure',
		'scheduled_air_time',
		'scheduled_block_time',
		'scheduled_gate_arrival',
		'scheduled_gate_departure',
		'scheduled_runway_arrival',
		'scheduled_runway_departure',
		'status',
		'status_update_time',
		'was_gate_adjusted',
		'was_time_adjusted']])

	xx = Z['status'].values

	vectorizer = CountVectorizer(min_df=1)

	Z = vectorizer.fit_transform(xx)

	print vectorizer.get_feature_names()


	y = np.asarray(Z[['actual_gate_minutes_after_midnight',
		'actual_runway_minutes_after_midnight']])

	# clf = tree.DecisionTreeClassifier()

	# clf = clf.fit(X,y)

	# r_forest = ExtraTreesClassifier(n_estimators=200,
	# 	compute_importances=True,
	# 	random_state=0)

	# r_forest.fit(X,y)