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
    def get_pre_clicks(self,driver): return []
    def get_event_tiles(self,soup): raise NotImplementedError
    def get_event_teams(self,soup): raise NotImplementedError
    def get_event_odds(self,soup): raise NotImplementedError
    def get_events(self,queue):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        driver = webdriver.Chrome()
        for url in self.urls:
            driver.get(url)
            time.sleep(5)
            for i in self.get_pre_clicks(driver):
                #time.sleep(1)
                a = ActionChains(driver)
                a.move_to_element(i).perform()
                #time.sleep(1)
                i.click()
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            event_data = self.get_event_tiles(soup)
            for i in event_data:
                event = Event()
                event.market = self.name
                event.teams = self.get_event_teams(i)
                event.odds = self.get_event_odds(i)
                queue.put(event)
        #queue.put(events)

class Smarkets(IBookie):
    name = "Smarkets"
    urls = [
        'https://smarkets.com/listing/sport/football?period=today',
    ]
    def get_event_tiles(self,soup): return soup.find_all('li',class_="event-tile")
    def get_event_teams(self,soup): return [x.text.strip() for x in soup.find_all('span',class_="team-name")]
    def get_event_odds(self,soup): return [calc.convert_odds(x.text.strip()) for x in soup.select("span.price.tick.sell.formatted-price.numeric-value")]

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
        return [x for x in driver.find_elements_by_class_name("KambiBC-collapsible-container") if "KambiBC-expanded" not in x.get_attribute("class")]
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
