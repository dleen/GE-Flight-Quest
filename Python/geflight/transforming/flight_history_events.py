import pandas as pd
import re

def parse_flight_history_events_day(day):
    grouped = day.flight_history_events.groupby('flight_history_id')
    test = grouped.apply(fhe.reduce_fhe_group_to_one_row)

def reduce_fhe_group_to_one_row(event_group):

    fhid = event_group['flight_history_id'].ix[event_group.index[0]]

    event_group = event_group.sort_index(by='date_time_recorded', ascending=False)

    event_list = event_group[['date_time_recorded','data_updated']]

    [era, ega, ard, agd, ara, aga] = get_all_time_adj_updates(event_list)

    sta = get_status_actual(event_list)

    [arr_gate, dep_gate] = get_both_gates(event_list)

    [arr_term, dep_term] = get_both_terminals(event_list)

    events = event_group['event']

    d = pd.Series({
    'ERA_most_recent' : era['data_updated'],
    'ERA_update_time' : era['date_time_recorded'],
    'EGA_most_recent' : ega['data_updated'],
    'EGA_update_time' : ega['date_time_recorded'],
    'last_update_time' : event_group['date_time_recorded'].ix[event_group.index[0]],
    'was_time_adjusted' : was_time_adjusted(events),
    'number_of_time_adjustments' : number_of_time_adjustments(events),
    'was_gate_adjusted' : was_gate_adjusted(events),
    'number_of_gate_adjustments' : number_of_gate_adjustments(events),
    'ARD_most_recent' : ard['data_updated'],
    'ARD_update_time' : ard['date_time_recorded'],
    'AGD_most_recent' : agd['data_updated'],
    'AGD_update_time' : agd['date_time_recorded'],
    'ARA_most_recent' : ara['data_updated'],
    'ARA_update_time' : ara['date_time_recorded'],
    'AGA_most_recent' : aga['data_updated'],
    'AGA_update_time' : aga['date_time_recorded'],
    'status_update_time' : sta['date_time_recorded'],
    'status' : sta['data_updated'],
    'arrival_gate' : arr_gate['data_updated'],
    'departure_gate' : dep_gate['data_updated'],
    'arrival_terminal' : arr_term['data_updated'],
    'departure_terminal' : dep_term['data_updated'],
     })

    return d

def was_time_adjusted(events):
    return "Time Adjustment" in events.values

def was_gate_adjusted(events):
    return "Gate Adjustment" in events.values

def number_of_time_adjustments(events):
    i = 0
    for e in events.values:
        if e == "Time Adjustment":
            i = i + 1

    return i

def number_of_gate_adjustments(events):
    i = 0
    for e in events.values:
        if e == "Gate Adjustment":
            i = i + 1

    return i

def get_all_time_adj_updates(event_list):
    """
    Takes in a group of events corresponding to one flight history id.
    Parses the events looking for estimated runway arrival or gate updates
    and returns the most recent update for each.
    """
    era = get_most_recent_event_update(event_list, "estimated runway arrival")

    ega = get_most_recent_event_update(event_list, "estimated gate arrival")

    ard = get_most_recent_event_update(event_list, "actual runway departure")

    agd = get_most_recent_event_update(event_list, "actual gate departure")

    ara = get_most_recent_event_update(event_list, "actual runway arrival")

    aga = get_most_recent_event_update(event_list, "actual gate arrival")

    return [era, ega, ard, agd, ara, aga]

def get_most_recent_event_update(event_list, time_adj_type):
    """
    Returns the most recent estimate of the arrival time. If that
    cannot be found it resorts to using the scheduled arrival times.
    """
    if time_adj_type == "estimated runway arrival":
        sig = "ERA"
    elif time_adj_type == "estimated gate arrival":
        sig = "EGA"
    elif time_adj_type == "actual runway departure":
        sig = "ARD"
    elif time_adj_type == "actual gate departure":
        sig = "AGD"
    elif time_adj_type == "actual runway arrival":
        sig = "ARA"
    elif time_adj_type == "actual gate arrival":
        sig = "AGA"
    else:
        print "Problem with signal type! {}".format(time_adj_type)

    temp = event_list.copy()

    temp['data_updated'] = temp['data_updated'].apply(lambda x: parse_fhe_events(x, sig))
    
    return get_most_recent(temp)

def get_status_actual(event_list):

    temp = event_list.copy()

    temp['data_updated'] = temp['data_updated'].apply(lambda x: parse_fhe_status(x, "STATUS"))

    return get_most_recent(temp)

def get_both_gates(event_list):

    ag = get_gate(event_list, "arrival")

    dg = get_gate(event_list, "departure")

    return [ag, dg]

def get_gate(event_list, gate):

    if gate == "arrival":
        g_type = "DGATE"
    elif gate == "departure":
        g_type = "AGATE"
    else:
        print "Problem with gate!"

    temp = event_list.copy()

    temp['data_updated'] = temp['data_updated'].apply(lambda x: parse_fhe_gate(x, g_type))

    return get_most_recent(temp)

def get_both_terminals(event_list):

    at = get_terminal(event_list, "arrival")

    dt = get_terminal(event_list, "departure")

    return [at, dt]

def get_terminal(event_list, terminal):

    if terminal == "arrival":
        t_type = "ATERM"
    elif terminal == "departure":
        t_type = "DTERM"
    else:
        print "Problem with terminal!"

    temp = event_list.copy()

    temp['data_updated'] = temp['data_updated'].apply(lambda x: parse_fhe_terminal(x, t_type))

    return get_most_recent(temp)

def get_most_recent(est_list):
    """
    Given an ordered list, with most recent time first,
    pick the first entry which is not None otherwise return None
    """
    for i, row in est_list.iterrows():
        if row['data_updated']:
            return row

    return est_list.ix[est_list.index[0]]

def parse_fhe_events(event, e_type):
    """
    Given a data updated event from flight_history_events
    extract the ERA or EGA times (if any) or else return None
    If an event does not meet any of these criteria print the event
    and return None
    """
    if type(event) != str:
        return None
    if e_type + "-" not in event:
        return None
    # VVV (Below) Interesting piece of information --
    # is EGA calculated just from distance and speed?
    if event in ["EGA- Based on Distance and Airspeed",
    "EGA- Based on Flight Histories"]:
        return None

    est = re.search('(%s-.*?(?<=New=))(?P<dt>\d\d/\d\d/\d\d \d\d:\d\d)'%e_type, event)

    if est:
        if len(est.group('dt')) > 14:
            print "Parsing time: {}".format(est.group('dt'))
        return est.group('dt')
    else:
        print "Looking for: {} in {}".format(e_type, event)
        return None

def parse_fhe_status(event, st_type):
    """
    Description
    """
    if type(event) != str:
        return None
    if st_type + "-" not in event:
        return None

    stat = re.search('(%s-.*?(?<=New=))(?P<st>[A-Z])'%st_type, event)

    if stat:
        return stat.group('st')
    else:
        print "Looking for: {} in {}".format(st_type, event)
        return None

def parse_fhe_gate(event, g_type):
    """
    Description
    """
    if type(event) != str:
        return None
    if g_type + "-" not in event:
        return None

    gate = re.search('%s-\s(Old=[\w/]+?\s)?New=(?P<gt>\w*)[,\s]?'%g_type, event)

    if gate: 
        if gate.group('gt') == "DPRTD":
            return None
        if len(gate.group('gt')) > 4:
            print "Parsing gate: {} from {}".format(gate.group('gt'), event)
        return gate.group('gt')

    gate = re.search('%s-\sOld=(?P<gt>\w*)[,\s]?'%g_type, event)

    if gate:
        if gate.group('gt') == "DPRTD":
            return None
        if len(gate.group('gt')) > 4:
            print "Parsing gate: {} from {}".format(gate.group('gt'), event)
        return gate.group('gt')
    else:
        print "Looking for: {} in {}".format(g_type, event)
        return None

def parse_fhe_terminal(event, term_type):
    """
    Description
    """
    if type(event) != str:
        return None
    if term_type + "-" not in event:
        return None

    term = re.search('%s-\s(Old=\w+?\s)?New=(?P<tt>\w*)[,\s]?'%term_type, event)

    if term:
        if term.group('tt') == "Gate":
            return None
        # print "Term {} from {}".format(term.group('tt'), event)
        if len(term.group('tt')) > 2:
            print "Parsing terminal: {}".format(term.group('tt'))
            print event
        return term.group('tt')

    term = re.search('%s-\sOld=(?P<tt>\w*)[,\s]?'%term_type, event)

    if term:
        if term.group('tt') == "Gate":
            return None
        # print "Term {} from {}".format(term.group('tt'), event)
        if len(term.group('tt')) > 2:
            print "Parsing terminal: {}".format(term.group('tt'))
            print event
        return term.group('tt')
    else:
        print "Looking for: {} in {}".format(term_type, event)
        return None