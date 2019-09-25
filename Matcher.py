MIN_FUZZ = 50
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
            #print(x,y)
            option = Option()
            option.back_teams = i.teams
            option.lay_teams = j.teams
            option.back_odds = x
            option.lay_odds = y
            option.profit_ratio = calc.ratio(x,y,calc.CMSN)
            option.back_market = i.market
            option.lay_market = j.market
            options.append(option)