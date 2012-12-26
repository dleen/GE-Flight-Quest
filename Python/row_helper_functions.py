import re

def get_scheduled_arrival(row, arrival_type):
    """
    Try each of the columns containing arrival information in order
    of perceived importance. If one type runway or gate cannot be found
    use the opposite type information before moving onto the next column of 
    data. Return None is all data is missing
    """
    if row["scheduled_%s_arrival" % arrival_type] != "MISSING":
        return row["scheduled_%s_arrival" % arrival_type]
    if row["scheduled_%s_arrival" % get_other_arrival_type(arrival_type)] != "MISSING":
        return row["scheduled_%s_arrival" % get_other_arrival_type(arrival_type)]
    if row["published_arrival"] != "MISSING":
        return row["published_arrival"]
    return None 

def get_other_arrival_type(arrival_type):
    """
    Quick swapping of runway and gate
    """
    if arrival_type == "runway":
        return "gate"
    return "runway"

def parse_fhe_events(event, e_type):
    """
    Given a data updated event from flight_history_events
    extract the ERA or EGA times (if any) or else return None
    If an event does not meet any of these criteria print the event
    and return None
    """
    if type(event) != str:
        return None
    if e_type not in event:
        return None
    # VVV (Below) Interesting piece of information --
    # is EGA calculated just from distance and speed?
    if event in ["EGA- Based on Distance and Airspeed",
    "EGA- Based on Flight Histories"]:
        return None

    est = re.search('(%s-.*?(?<=New=))(?P<dt>\d\d/\d\d/\d\d \d\d:\d\d)'%e_type, event)

    if est:
        return est.group('dt')
    else:
        print event
        return None