import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from Classes import Event
import calc
class IBookie:
    name = ""
    urls = []
    drivers = []
    ready=False
    def get_consecutive_clicks(self,driver): return []
    def get_pre_clicks(self,driver): return []
    def get_event_tiles(self,soup): raise NotImplementedError
    def get_event_teams(self,soup): raise NotImplementedError
    def get_event_odds(self,soup): raise NotImplementedError
    def setup(self):
        if self.ready==True: raise RuntimeWarning("Already ready")
        for url in self.urls:
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            driver = webdriver.Chrome(chrome_options=options)
            driver.get(url)
            time.sleep(4)
            for j in self.get_consecutive_clicks(driver):
                i = j()
                a = ActionChains(driver)
                a.move_to_element(i).perform()
                i.click()
                time.sleep(0.1)
            for i in self.get_pre_clicks(driver):
                a = ActionChains(driver)
                a.move_to_element(i).perform()
                i.click()
            self.drivers.append(driver)
        time.sleep(1)
        self.ready=True
    def get_events(self,queue):
        for driver in self.drivers:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            event_data = self.get_event_tiles(soup)
            for i in event_data:
                event = Event()
                event.market = self.name
                event.teams = self.get_event_teams(i)
                event.odds = self.get_event_odds(i)
                queue.put(event)

class Smarkets(IBookie):
    name = "Smarkets"
    urls = [
        'https://smarkets.com/listing/sport/football?period=today',
    ]
    def get_consecutive_clicks(self,driver):
        return [
            lambda: driver.find_element_by_id("account-mobile-button"),#settings-dropdown-button"),
            lambda: [x for x in driver.find_elements_by_class_name("label") if x.text == "Odds"][0],
            lambda: [x for x in driver.find_elements_by_class_name("Select__option") if x.text == "Percent"][0],
            lambda: driver.find_element_by_id("account-mobile-button"),#settings-dropdown-button"),        
        ]
    def get_event_tiles(self,soup): return soup.find_all('li',class_="event-tile")
    def get_event_teams(self,soup): return [x.text.strip() for x in soup.find_all('span',class_="team-name")]
    def get_event_odds(self,soup): 
        return [calc.convert_odds(x.text.strip(),percent=True) for x in soup.select("span.price.tick.sell.formatted-price.numeric-value")]
class Smarkets_Back(IBookie):
    name = "Smarkets Back"
    urls = [
        'https://smarkets.com/listing/sport/football?period=today',
    ]
    def get_event_tiles(self,soup): return soup.find_all('li',class_="event-tile")
    def get_event_teams(self,soup): return [x.text.strip() for x in soup.find_all('span',class_="team-name")]
    def get_event_odds(self,soup): return [calc.convert_odds(x.text.strip()) for x in soup.select("span.price.tick.buy.formatted-price.numeric-value")]

class Ladbrokes(IBookie):
    name = "Ladbrokes"
    urls = [
        "https://sports.ladbrokes.com/en-gb/betting/football/"
    ]
    def get_event_tiles(self,soup): return soup.find_all('div',class_="event-list")
    def get_event_teams(self,soup): return soup.find('div',class_="event-list-details").find("div",class_="name").text.strip().split(" v ")
    def get_event_odds(self,soup): return [calc.convert_odds(x["odds-d"].strip()) for x in soup.find_all("span",class_="odds-convert")]
class Eight(IBookie):
    name = "888Sport"
    urls = [
        "https://www.888sport.com/football/#/filter/football/all/all/all/matches"
    ]
    def get_pre_clicks(self,driver): 
        return [driver.find_element_by_id("CookieMessageDiv").find_element_by_class_name("close"),
            *[x for x in driver.find_elements_by_class_name("KambiBC-collapsible-container") if "KambiBC-expanded" not in x.get_attribute("class")]]
    def get_event_tiles(self,soup): return soup.find_all('div',class_="KambiBC-event-item__event-wrapper")
    def get_event_teams(self,soup): return [x.text.strip() for x in soup.find_all('div',class_="KambiBC-event-participants__name")]
    def get_event_odds(self,soup): 
        normal = [calc.convert_odds(x.text.strip()) for x in soup.find_all("span",class_="KambiBC-mod-outcome__odds")]
        return normal #[x-1 if x != None else None for x in normal]
class Virgin(IBookie):
    name = "VirginBet"
    urls = [
        'https://www.virginbet.com/coupon/5665844310835200?time=all',
    ]
    def get_event_tiles(self,soup): return soup.find_all('div',class_="sc-1oncd4w-3")
    def get_event_teams(self,soup): return [x.text.strip() for x in soup.find_all('div',class_="sc-1ewcotm-11")]
    def get_event_odds(self,soup): 
        normal = [calc.convert_odds(x.text.strip()) for x in soup.find_all("div",class_="sc-18i223d-0")]
        return [x-1 if x != None else None for x in normal]
class TwoTwo(IBookie):
    name = "22Bet"
    urls = [
        "https://22bet.co.uk/sport"
    ]
    def get_pre_clicks(self,driver): 
        return [x for x in driver.find_elements_by_class_name("nav-link") if x.text == "Today"]
    def get_event_tiles(self,soup): return soup.select("div.event.d-md-flex")
    def get_event_teams(self,soup): 
        t1 = soup.find('span',class_="team1")
        t2 = soup.find('span',class_="team2")
        if t1 == None or t2 == None: return []
        return [t1.text.strip(),t2.text.strip()]
    def get_event_odds(self,soup): return [calc.convert_odds(self.trykey(x).strip()) for x in soup.find_all("span",class_="odd")]
    def trykey(self,x):
        try:
            return x["data-odd-value"]
        except KeyError:
            return "-1"