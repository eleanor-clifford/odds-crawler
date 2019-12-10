MIN_FUZZ = 50
import threading
from collections import OrderedDict
from queue import Queue
import calc
from fuzzywuzzy import fuzz
from Classes import Event,Option
def match(events_1,events_2):
    matched_events = []
    for i in events_1:
        if i.teams == [] or i.odds == []: continue
        for j in events_2:
            if j.teams == [] or j.odds == []: continue
            if len(i.odds) != len(j.odds): continue
            if all(fuzz.ratio(x,y) >= MIN_FUZZ for x,y in zip(i.teams,j.teams)):
                matched_events.append((i,j))
            elif all(fuzz.ratio(x,y) >= MIN_FUZZ for x,y in zip(i.teams[::-1],j.teams)):
                k = Event()
                k.teams = i.teams[::-1]
                k.odds = i.teams[::-1]
                matched_events.append((k,j))
    return matched_events
def matched_options(events_1,events_2):
    matched_data = match(events_1,events_2)
    options = []
    for i,j in matched_data:
        for x,y in zip(i.odds,j.odds):
            if not (isinstance(x,float) and isinstance(y,float)): continue
            option = Option()
            option.back_teams = i.teams
            option.lay_teams = j.teams
            option.back_odds = x
            option.lay_odds = y
            option.profit_ratio = calc.ratio(x,y,calc.CMSN)
            option.arbitrage_profit = calc.liablity_ratio(x,y,calc.CMSN)
            option.back_market = i.market
            option.lay_market = j.market
            options.append(option)
    return options
def get_matched_options(backs,lays,q):
    back_queue = Queue()
    lay_queue = Queue()
    threads = [
        threading.Thread(
            target=x.get_events,
            name="Thread_{}".format(x.name),
            args=[back_queue],
        ) for x in backs
    ] + [
        threading.Thread(
            target=x.get_events,
            name="Thread_{}".format(x.name),
            args=[lay_queue],
        ) for x in lays
    ]
    for t in threads: t.start()
    for t in threads: t.join()
    back_events = []
    lay_events = []
    while not back_queue.empty(): back_events.append(back_queue.get_nowait())
    while not lay_queue.empty(): lay_events.append(lay_queue.get_nowait())
    options = matched_options(back_events,lay_events)
    q.put(options)
    return options
def get_matched_options_formatted(backs,lays,q):
    get_matched_options(backs,lays,q)
    options = q.get_nowait()
    options_str = [str(x) for x in sorted(options,key=lambda x: x.profit_ratio,reverse=True)]
    data_text = "\n".join(list(OrderedDict.fromkeys(options_str)))
    q.put(data_text)
    return data_text