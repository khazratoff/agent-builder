# """
# Weather tools for the Weather Agent.

# Since external MCP weather servers may not be available, these are
# simple mock weather tools for demonstration purposes.
# """

# from langchain.tools import tool
# import random
# from datetime import datetime, timedelta


# @tool
# def get_weather(city: str, country: str = "") -> str:
#     """
#     Get current weather for a city.

#     Args:
#         city: Name of the city
#         country: Country code (optional)

#     Returns:
#         Current weather information
#     """
#     # Mock weather data
#     conditions = ["sunny", "partly cloudy", "cloudy", "rainy", "stormy"]
#     temp = random.randint(10, 30)
#     condition = random.choice(conditions)
#     humidity = random.randint(40, 90)
#     wind = random.randint(5, 25)

#     location = f"{city}, {country}" if country else city

#     return f"""Current weather in {location}:
# Temperature: {temp}°C
# Condition: {condition}
# Humidity: {humidity}%
# Wind: {wind} km/h
# Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"""


# @tool
# def get_forecast(city: str, days: int = 3) -> str:
#     """
#     Get weather forecast for a city.

#     Args:
#         city: Name of the city
#         days: Number of days to forecast (default 3)

#     Returns:
#         Weather forecast information
#     """
#     # Mock forecast data
#     conditions = ["sunny", "partly cloudy", "cloudy", "rainy", "stormy"]
#     forecast_data = []

#     for day in range(min(days, 7)):
#         date = datetime.now() + timedelta(days=day+1)
#         temp_high = random.randint(15, 30)
#         temp_low = random.randint(5, 15)
#         condition = random.choice(conditions)
#         precipitation = random.randint(0, 80)

#         forecast_data.append(
#             f"{date.strftime('%A, %b %d')}: "
#             f"{condition.title()}, High: {temp_high}°C, Low: {temp_low}°C, "
#             f"Precipitation: {precipitation}%"
#         )

#     return f"Weather forecast for {city}:\n" + "\n".join(forecast_data)


# @tool
# def get_alerts(city: str, country: str = "") -> str:
#     """
#     Get weather alerts for a city.

#     Args:
#         city: Name of the city
#         country: Country code (optional)

#     Returns:
#         Weather alerts if any
#     """
#     # Mock alerts
#     has_alert = random.choice([True, False, False])  # 33% chance of alert

#     location = f"{city}, {country}" if country else city

#     if has_alert:
#         alert_types = [
#             "Heavy Rain Warning",
#             "Strong Wind Advisory",
#             "Heat Advisory",
#             "Thunderstorm Watch"
#         ]
#         alert = random.choice(alert_types)
#         return f"Weather alerts for {location}:\n⚠️ {alert}\nIssued: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
#     else:
#         return f"No weather alerts for {location} at this time."


# @tool
# def compare_weather(city1: str, city2: str) -> str:
#     """
#     Compare weather between two cities.

#     Args:
#         city1: First city name
#         city2: Second city name

#     Returns:
#         Weather comparison
#     """
#     # Get weather for both cities
#     temp1 = random.randint(10, 30)
#     temp2 = random.randint(10, 30)
#     conditions = ["sunny", "partly cloudy", "cloudy", "rainy"]
#     cond1 = random.choice(conditions)
#     cond2 = random.choice(conditions)

#     comparison = f"""Weather Comparison:

# {city1}:
#   Temperature: {temp1}°C
#   Condition: {cond1}

# {city2}:
#   Temperature: {temp2}°C
#   Condition: {cond2}

# Difference: {abs(temp1 - temp2)}°C"""

#     if temp1 > temp2:
#         comparison += f"\n{city1} is warmer than {city2}"
#     elif temp2 > temp1:
#         comparison += f"\n{city2} is warmer than {city1}"
#     else:
#         comparison += f"\nBoth cities have the same temperature"

#     return comparison
