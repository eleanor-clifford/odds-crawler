CMSN = 0.02
from itertools import combinations
from functools import reduce
import operator
import math
import matplotlib.pyplot as plt
import numpy as np

def convert_odds(x):
    if x == None: return None
    if isinstance(x,str): x = x.replace(" ","").replace("\n","")
    try: return float(x)
    except (ValueError):
        if "/" in x:
            return float(x.split("/")[0])/float(x.split("/")[1]) + 1
        else: return None
        
def ratio(back_odds,lay_odds,cmsn):
    return back_odds - (1 + back_odds*(lay_odds - 1)/(lay_odds - cmsn))
def back_stakes(odds):
    if odds == []: return -1
    comb = list(combinations(odds,len(odds) - 1))

    zs = sum(product(a for a in z) for z in comb)
    return [product(x for x in odds if not x is y)/zs for y in odds]
def back_ratio(odds):
    if odds == []: return -1
    odds = [convert_odds(x) for x in odds]
    st = back_stakes(odds)
    return st[0]*odds[0] - sum(st)
def product(iterable):
    return reduce(operator.mul, iterable, 1)

##### COMPLEX METHODS FOR VARIABLE TURNOVER #####

def r_w(t,back_odds,lay_odds):
    '''
    ratio of profit for each back win, variable on lay stake t
    '''
    return (back_odds) - t*(lay_odds - 1)
def r_l(t,back_odds,lay_odds):
    '''
    ratio of profit for the lay win, variable on lay stake t
    '''
    return t*(1-CMSN)
def powersum(base,power):
    return sum(base**n for n in range(power))
def _max_full_bets(odds,turnover):
    i = 0
    while True:
        r = turnover - powersum(odds,i)
        if r < 0: return i - 1
        else: i += 1
def px(t,back_odds,lay_odds,max_turnover,fair_odds=None):
    if fair_odds==None: fair_odds = (back_odds + lay_odds)/2
    p = 1/fair_odds
    q = 1-p
    max_full_bets = _max_full_bets(back_odds,max_turnover)
    turnover_remaining = max_turnover - powersum(back_odds,max_full_bets)
    # so E(X) = (r_l*q) + ... + (r_w*back_odds*p)^max_full_bets*(r_l*q) + final_bet_win + final_bet_loss
    rw = r_w(t,back_odds,lay_odds)
    rl = r_l(t,back_odds,lay_odds)
    EX = []
    for i in range(max_full_bets):
        x = rl*back_odds**(i) - t*(lay_odds-1)*powersum(back_odds,i)
        EX.append((q*p**i,x))
    released_amount = back_odds**(max_full_bets) - t*(lay_odds-1)*powersum(back_odds,max_full_bets)
    EX.append((q*p**max_full_bets,(released_amount + (rl-1)*turnover_remaining))) # final bet loss
    EX.append((p**(max_full_bets + 1),(released_amount + (rw-1)*turnover_remaining))) # final bet win
    #print(t,EX)
    return EX

def max_liabiity(t,back_odds,lay_odds,max_turnover):
    max_full_bets = _max_full_bets(back_odds,max_turnover)
    turnover_remaining = max_turnover - powersum(back_odds,max_full_bets)
    return 1 + powersum(back_odds,max_full_bets)*t*(lay_odds-1) + turnover_remaining*t*(lay_odds-1)
if __name__ == "__main__":
    turnover = float(input("turnover? "))
    back_stake  = int(float(input("back stake? "))*100)
    back_odds  = float(input("back odds?  "))
    lay_odds  = float(input("lay odds?   "))
    if turnover == 1.0:
        lay_stake  = ((back_odds*back_stake)/(lay_odds-CMSN))
        profit = ((back_stake*back_odds)-(back_stake+((lay_odds-1)*lay_stake)))
        profit2= (lay_stake-(CMSN*lay_stake)-back_stake)
        liability = (((lay_odds-1)*lay_stake)+back_stake)
        print("lay stake:        ",int(round(lay_stake))/100)
        print("liability:        ",int(round(liability))/100)
        print("profit:          ",int(round(profit))/100)
        print("alt. profit:     ",int(round(profit2))/100)
    else:
        liability_cap = float(input("liabiliity cap? "))
        fair_odds = float(input("fair odds? "))
        x = np.arange(0,1.5,0.01)
        y = np.arange(0,1.5,0.01)
        z = np.arange(0,1.5,0.01)
        w = np.arange(0,1.5,0.01)
        liability_cap_t = 0
        for i in range(len(x)):
            px_i = px(x[i],back_odds,lay_odds,turnover,fair_odds=fair_odds)
            mu = sum(p*x for (p,x) in px_i)
            y[i] = sum(p*(x-mu)**2 for (p,x) in px_i)
            z[i] = min(x for (p,x) in px_i)
            w[i] = max_liabiity(x[i],back_odds,lay_odds,turnover)
            if w[i] < liability_cap: liability_cap_t = x[i]

        px_liability_cap = px(liability_cap_t,back_odds,lay_odds,turnover,fair_odds=fair_odds)
        ex_liability_cap = sum(p*x for (p,x) in px_liability_cap)
        print("\nHighest value under liability cap at t={0:.4f}, E(X)={1:.4f}".format(liability_cap_t,ex_liability_cap))
        print("Max Profit: {}, Min Profit: {}".format(max(x for (p,x) in px_liability_cap),min(x for (p,x) in px_liability_cap)))
        print("Maximum Liability: {}".format(max_liabiity(liability_cap_t,back_odds,lay_odds,turnover)))
        print([x for (p,x) in px_liability_cap])

        ordinary_t = back_odds/(lay_odds-CMSN)
        px_ordinary = px(ordinary_t,back_odds,lay_odds,turnover,fair_odds=fair_odds)
        ex_ordinary = sum(p*x for (p,x) in px_ordinary)
        print("\nNormal at t={0:.4f}, E(X)={1:.4f}".format(ordinary_t,ex_ordinary))
        print("Max Profit: {}, Min Profit: {}".format(max(x for (p,x) in px_ordinary),min(x for (p,x) in px_ordinary)))
        print("Maximum Liability: {}".format(max_liabiity(ordinary_t,back_odds,lay_odds,turnover)))
        print([x for (p,x) in px_ordinary])

        a,b,c = np.polyfit(x,y,2)
        min_var_t = -b/(2*a)
        px_min_var = px(min_var_t,back_odds,lay_odds,turnover,fair_odds=fair_odds)
        ex_min_var = sum(p*x for (p,x) in px_min_var)
        print("\nMinimum Variance at t={0:.2f}, E(X)={1:.4f}".format(min_var_t,ex_min_var))
        print("Max Profit: {}, Min Profit: {}".format(max(x for (p,x) in px_min_var),min(x for (p,x) in px_min_var)))
        print("Maximum Liability: {}".format(max_liabiity(min_var_t,back_odds,lay_odds,turnover)))
        print([x for (p,x) in px_min_var])

        max_guaranteed_t = sorted(zip(x,z),key=lambda t: t[1])[-1][0]
        px_max_guaranteed = px(max_guaranteed_t,back_odds,lay_odds,turnover,fair_odds=fair_odds)
        ex_max_guaranteed = sum(p*x for (p,x) in px_max_guaranteed)
        print("\nMaximum Guaranteed Return at t={0:.4f}, E(X)={1:.4f}".format(max_guaranteed_t,ex_max_guaranteed))
        print("Max Profit: {}, Min Profit: {}".format(max(x for (p,x) in px_max_guaranteed),min(x for (p,x) in px_max_guaranteed)))
        print("Maximum Liability: {}".format(max_liabiity(max_guaranteed_t,back_odds,lay_odds,turnover)))
        print([x for (p,x) in px_max_guaranteed])

        fig, ax = plt.subplots()
        ax.plot(x,y)
        ax.plot(x,z)
        ax.plot(x,w)
        plt.show()
