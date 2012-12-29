def folder_names_test_set():
    """
    TEST days
    Returns a list of folders containing data for the individual days
    """
    year = "2012"
    dates = ["11_26","11_27","11_28","11_29","11_30",
             "12_01","12_02","12_03","12_04","12_05",
             "12_06","12_07","12_08","12_09"]

    return [year + "_" + d for d in dates]

def folder_names_init_set():
    """
    TRAINING days
    Returns a list of folders containing data for the individual days
    """
    year = "2012"
    dates = ["11_12","11_13","11_14","11_15","11_16",
             "11_17","11_18","11_19","11_20","11_21",
             "11_22","11_23","11_24","11_25"]

    return [year + "_" + d for d in dates]