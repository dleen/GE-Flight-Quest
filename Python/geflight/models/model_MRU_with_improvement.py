import model_most_recent_update as mmru

class MRU_with_improvement(mmru.MRU):
    """
    Description
    """
    def __repr__(self):
        return "Small improvment model"
        
    def find_most_recent_event_update(self, event_group):
        """
        Takes in a group of events corresponding to one flight history id.
        Parses the events looking for estimated runway arrival or gate updates
        and returns the most recent update for each.
        """
        event_group = event_group.sort_index(by='date_time_recorded', ascending=False)

        event_list = event_group['data_updated']

        offset = event_group["arrival_airport_timezone_offset"].ix[event_group.index[0]]
        if offset>0:
            offset_str = "+" + str(offset)
        else:
            offset_str = str(offset)

        era_est = self.get_updated_event_arrival(event_list, event_group.ix[event_group.index[0]],
            "runway", offset_str)

        ega_est = self.get_updated_event_arrival(event_list, event_group.ix[event_group.index[0]],
            "gate", offset_str)

        if era_est > ega_est:
            # VV Improves score on Kaggle, worsens training set score
            ega_est = era_est

        return [era_est, ega_est]