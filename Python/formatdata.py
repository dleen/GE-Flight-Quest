import numpy as np

def rmse_fun(actual, predicted):
	N = len(actual)
	if len(predicted) != N:
		print "Actual and Predicted array lengths do not match!"
		return

	diff = np.subtract(actual, predicted)
	square_diff = np.multiply(diff, diff)
	square_sum = np.sum(square_diff)

	return sqrt(square_sum / N)

def rmse_final(runway_act, runway_pred, gate_act, gate_pred):
	rmse_gate = rmse_fun(gate_act, gate_pred)
	rmse_run = rmse_fun(runway_act, runway_pred)

	return 0.75 * rmse_gate + 0.25 * rmse_run

if __name__=='__main__':
	gate_act_test = [1, 2, 3, 4]
	gate_pred_test = [1, 2, 3, 4]

	runway_act_test = [1, 2, 3, 4]
	runway_pred_test = [1, 2, 3, 4]	

	print rmse_final(runway_act_test, runway_pred_test, gate_act_test, gate_pred_test)



