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
gc = geonamescache.GeonamesCache()
city_dict = gc.get_cities()

cities = []
for cid, cinfo in city_dict.items():
    if cinfo.get("countrycode") == "US":
        cities.append(cinfo.get("name").lower())


global user_input
# Get valid user input
def getInput():
    user_input = str(input("Enter the name of your city to get the forecast: ")).lower()
    while user_input not in cities:
        user_input = str(input("\nCity not found. Perhaps enter the name of a more populated, nearby city: ")).lower()
    return user_input


# Instantiate web driver and search for the specified city's weather
def navigateToPage(the_input):
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    driver = webdriver.Chrome(options=opts)
    driver.get("https://www.weather.gov/")

    search = driver.find_element_by_xpath("/html/body/div[4]/div[2]/div[1]/div[1]/div/form/input[1]")
    search.clear()
    search.send_keys(the_input)
    go = driver.find_element_by_id("btnSearch")
    time.sleep(1)
    go.click()

    time.sleep(2)

    return driver.current_url


def scrapePage(current_url):
    site = requests.get(current_url)
    soup = BeautifulSoup(site.content, "html.parser")

    week_div = soup.find(id="seven-day-forecast-body")

    periods = week_div.find_all(class_="tombstone-container")

    
    try:
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

        return (day_names, descriptions, parsed_temperatures)
    except Exception as e:
        print("Sorry, something went wrong. Perhaps you should try a different city.")


def createTable(threetuple):
    weather_data = pd.DataFrame(
        {
            "Day": threetuple[0],
            "Description": threetuple[1],
            "Temperature": threetuple[2],
        }
    )

    # Prints a preview of the table in the console
    print(weather_data)

    # Creates a corresponding "(city name).csv" file with the table values
    #weather_data.to_csv(f"{user_input}.csv")




## Main loop ##
quit_prompt = ''
while quit_prompt != 'q':
    user_input = getInput()
    createTable(scrapePage(navigateToPage(user_input)))
    quit_prompt = input("To check the weather of another city, enter any character:\nIf you want to quit Weatherman, enter 'q': ").lower()