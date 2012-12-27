import model_most_recent_update as mmru

class MRU_with_gate_delay_est(mmru.MRU):
    """
    This class allows us to make slight changes to our model by "overloading"
    the functions we want to make changes to.
    """
    def __repr__(self):
        """
        This is a descriptive name for the model for use in strings
        """
        return "Avg gate time by airport model"
