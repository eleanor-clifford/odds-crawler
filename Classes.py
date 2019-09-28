class Event:
    def __init__(self):
        self.market = ""
        self.teams = []
        self.odds = []
    def __str__(self):
        return self.market + "," + str(self.teams) + "," + str(self.odds)

class Option:
    def __init__(self):
        self.back_teams = []
        self.lay_teams = []
        self.back_odds = -1
        self.lay_odds = -1
        self.profit_ratio = 0
        self.back_market = ""
        self.lay_market = ""
    #def __eq__(a,b):
    #    return str(a) == str(b)
    def __str__(self):
        return "{:<20}|{:<20}|{:<20}|{:<20}| {:06.2f} | {:06.2f} | {:+.5f} | {:<10} | {:<10}".format(self.back_teams[0],self.back_teams[1],self.lay_teams[0],self.lay_teams[1],self.back_odds,self.lay_odds, self.profit_ratio,self.back_market,self.lay_market)
