import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

site = requests.get("https://forecast.weather.gov/MapClick.php?lat=40.71455000000003&lon=-74.00713999999994#.XrsVqRNKh24")
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