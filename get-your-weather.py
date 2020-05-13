from bs4 import BeautifulSoup
import geonamescache
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Get names of US cities by importing city data
def getCities():
    gc = geonamescache.GeonamesCache()
    city_dict = gc.get_cities()

    cities = []
    for cid, cinfo in city_dict.items():
        if cinfo.get("countrycode") == "US":
            cities.append(cinfo.get("name").lower())

# Get valid user input
def getInput(cities):
    user_input = str(input("Enter the name of your city to get the forecast: ")).lower()
    while user_input not in cities:
        user_input = str(input("City not found. Enter the name of a more populated, nearby city: ")).lower()


# Instantiate web driver and proceed with automation
def navigateToPage(user_input):
    driver = webdriver.Chrome()
    driver.get("https://www.weather.gov/")


    search = driver.find_element_by_xpath("/html/body/div[4]/div[2]/div[1]/div[1]/div/form/input[1]")
    search.clear()
    search.send_keys(user_input)
    go = driver.find_element_by_id("btnSearch")
    time.sleep(1)
    go.click()

time.sleep(2)


################################################################################################################################
site = requests.get(driver.current_url)
soup = BeautifulSoup(site.content, "html.parser")

week_div = soup.find(id="seven-day-forecast-body")

periods = week_div.find_all(class_="tombstone-container")

# Get temperatures
temperatures = [period.find(class_="temp").get_text() for period in periods]
parsed_temperatures = []
for temp in temperatures:
    t = "".join(filter(str.isdigit, temp)) + "F"
    parsed_temperatures.append(t)

# Apporopriately spaced period names/descriptions
detailed_forecast_div = soup.find(id="detailed-forecast-body")
days = detailed_forecast_div.find_all(class_="row")

day_names = [day.find(class_="forecast-label").get_text() for day in days]
descriptions = [day.find(class_="forecast-text").get_text() for day in days]

day_names = day_names[0:len(parsed_temperatures)]
descriptions = descriptions[0:len(parsed_temperatures)]


# Create corresponding data table using Pandas
weather_data = pd.DataFrame(
    {
        "Day": day_names,
        "Description": descriptions,
        "Temperature": parsed_temperatures,
    }
)

#weather_data.to_csv("results.csv")
print(weather_data)