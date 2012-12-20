import numpy as np

def rmse_fun(actual, predicted):
	"""
	Calculate the root mean square difference between the actual and predicted times.
	"""
	N = len(actual)
	N1 = len(predicted)

	if N == 0 or N1 == 0: 
		raise "Zero length input!"
	elif N1 != N:
		raise "Actual and Predicted array lengths do not match!"


	diff = np.subtract(actual, predicted)
	square_diff = np.multiply(diff, diff)
	square_sum = np.sum(square_diff)

	return np.sqrt(float(square_sum) / N)

def rmse_final(runway_act, runway_pred, gate_act, gate_pred):
	"""
	The final rmse score is a weighted sum of the runway arrival times
	and the gate arrival times.
	"""
	rmse_gate = rmse_fun(gate_act, gate_pred)
	rmse_run = rmse_fun(runway_act, runway_pred)

	return 0.75 * rmse_gate + 0.25 * rmse_run

if __name__=='__main__':
	gate_act_test = [1, 5, 4, 3, 2, 77]
	gate_pred_test = [0, 5, 6, 7, 5, 99]

	runway_act_test = [1001, 2, 3, 4]
	runway_pred_test = [995, 2, 3, 4]	

	print rmse_final(runway_act_test, runway_pred_test, gate_act_test, gate_pred_test)



