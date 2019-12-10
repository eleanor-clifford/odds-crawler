import time
import pickle
import threading
from collections import OrderedDict
from queue import Queue
from selenium import webdriver
from bs4 import BeautifulSoup
import tkinter
from tkinter import scrolledtext
from bookies import *
from Matcher import matched_options
from DataText import DataText

backs = [Ladbrokes(), Eight(), Virgin()]
lays = [Smarkets()]
#lay_unmatched = [Smarkets_Back()]

window = tkinter.Tk()
window.title("Odds Scraper")
window.geometry('1600x900')
data = DataText(window,backs,lays,width=600,height=600)
data.grid(column=0,row=0)
window.mainloop()
