import pandas as pd

import numpy as np

def offset_func(offset):
    if pd.isnull(offset):
        return np.nan
    elif offset > 0:
        offset_str = "+" + str(offset)
        return offset_str
    else:
        offset_str = str(offset)
        return offset_str