'''
File:        FeedMe.py

Author(s):   Simon Corpuz (scorpuz)
             Bonnie Li (bonnieli)
             Suryaa Raman (ssuryaar)
             Yiyang Yao (yiyangya)

Imports:     recipe_scraper.py
             well_scraper.py
             store_scraper.py
             Pandas
             Regex
             Math
             Enum
             Folium
             WebBrowser
             OS
             DateTime

Imported By: N/A

This is the main file that runs the FeedMe application. It uses a logic loop in
order to display catalogued recipes, track daily caloric intake, and display a
map of all supermarkets in Pittsburgh.
'''

import recipe_scraper
import well_scraper
import store_scraper
import pandas as pd
import re
import math
from enum import Enum
import folium
import webbrowser
import os
from datetime import datetime

# Enumeration for prompt type
class promptType(Enum):
    MAIN = 0
    SEARCH = 1
    SEARCH_NAME = 2
    SEARCH_TIME = 3
    SEARCH_CALORIES = 4
    SEARCH_INGREDIENT = 5
    SEARCH_RESULTS = 6
    RECIPE = 7
    RECIPE_ACTION = 8
    MY_RECIPES = 9
    USER_SETTINGS = 10
    QUIT = 11

# Load default CSV files
recipes = pd.read_csv("allrecipes_default.csv")._append(pd.read_csv("eatingwell_default.csv"), ignore_index=True)
stores = pd.read_csv("stores_default.csv")

# Load favorites
with open("favorites.txt", "rt", encoding="utf-8") as f:
    favorites = [x for x in f]
    favorites = [eval(x) for x in favorites]

# Global variables
currentPromptType = promptType.MAIN
prompt = ""
selected_recipes = []
calorie_limit = 0.0
total_calories = 0.0
date = datetime.today()

# Function to parse strings from lists
def parse_list_string(list_string):
    return list_string.strip("['").strip("']").split("', '")

# Function to download newest versions of files
def refresh_files():
    print("\nDownloading files...")
    recipe_scraper.download_allrecipes("allrecipes.csv")
    well_scraper.download_eatingwell("eatingwell.csv")
    store_scraper.download_stores("stores.csv")
    global recipes, stores
    recipes = pd.read_csv("allrecipes.csv")._append(pd.read_csv("eatingwell.csv"), ignore_index=True)
    stores = pd.read_csv("stores.csv")
    print("\nAll files have been updated.")

# Function to calculate calorie limit and write it to file
def calculate_calorie_limit(weight, height, age, gender):
    if gender.lower() == "male":
        return 9.99 * weight + 6.25 * height - 4.92 * age + 5
    elif gender.lower() == "female":
        return 9.99 * weight + 6.25 * height - 4.92 * age - 161
    return 0

# Function to update user settings
def update_user_settings(calorie_limit, total_calories, date):
    with open("user_settings.txt", "wt", encoding = "utf-8") as f:
        f.write(str(calorie_limit) + "\n")
        f.write(str(total_calories) + "\n")
        f.write(date.strftime("%m/%d/%Y") + "\n")

# Initialize user settings
if os.path.isfile("user_settings.txt"):
    with open("user_settings.txt", "rt", encoding = "utf-8") as f:
        content = f.readlines()
        calorie_limit = float(content[0])
        total_calories = float(content[1])
        date = datetime.strptime(content[2].strip(), "%m/%d/%Y")
        if date.day != datetime.today().day or date.month != datetime.today().month or date.year != datetime.today().year:
            date = datetime.today()
            total_calories = 0
            update_user_settings(calorie_limit, total_calories, date)
else:
    currentPromptType = promptType.USER_SETTINGS

# Main logic loop
while currentPromptType != promptType.QUIT:
    # Prompt type: edit user settings
    if currentPromptType == promptType.USER_SETTINGS:
        weight = 0.0
        height = 0.0
        age = 0
        gender = "male"
        continueSettings = False
        while not continueSettings:
            prompt = input("\nPlease enter your weight (in kilograms): ")
            if re.match(r'^[1-9][0-9]*\.*[0-9]*$', prompt) is not None:
                weight = float(prompt)
                continueSettings = True
            else:
                print("\nYour choice is not valid. Please re-input your choice.")
        continueSettings = False
        while not continueSettings:
            prompt = input("\nPlease enter your height (in centimeters): ")
            if re.match(r'^[1-9][0-9]*\.*[0-9]*$', prompt) is not None:
                height = float(prompt)
                continueSettings = True
            else:
                print("\nYour choice is not valid. Please re-input your choice.")
        continueSettings = False
        while not continueSettings:
            prompt = input("\nPlease enter your age: ")
            if prompt.isdigit() and int(prompt) > 0:
                age = int(prompt)
                continueSettings = True
            else:
                print("\nYour choice is not valid. Please re-input your choice.")
        continueSettings = False
        while not continueSettings:
            prompt = input("\nPlease enter your gender (male or female): ")
            if prompt.lower() == "male" or prompt.lower() == "female":
                gender = prompt.lower()
                continueSettings = True
            else:
                print("\nYour choice is not valid. Please re-input your choice.")
        calorie_limit = calculate_calorie_limit(weight, height, age, gender)
        update_user_settings(calorie_limit, total_calories, date)
        print("\nYour calorie limit has been saved.")
        currentPromptType = promptType.MAIN
    
    # Prompt type: main interface
    if currentPromptType == promptType.MAIN:
        print(f'''\nFeedMe
Calorie Limit: {round(calorie_limit, 2)}
Today's Calories: {round(total_calories, 2)}
    1)  Search for recipes
    2)  Check my recipes
    3)  Locate nearby supermarkets
    4)  Refresh recipes and locations
    5)  Recalculate calorie limit
    6)  Quit''')
        prompt = input('\nYour choice: ').strip()
        if prompt == "1":
            currentPromptType = promptType.SEARCH
        elif prompt == '2':
            if len(favorites) > 0:
                currentPromptType = promptType.MY_RECIPES
            else:
                print("\nYou have no favorite recipes.")
        elif prompt == '3':
            map = folium.Map(location=[40.44062, -79.99589])
            for index, row in stores.iterrows():
                if not math.isnan(row["Lat"]) and not math.isnan(row["Lon"]):
                    iconColor = "red"
                    if row["Category"] == "Convenience Store":
                        iconColor = "blue"
                    folium.Marker(
                        location=[row["Lat"], row["Lon"]],
                        popup=row["Name"],
                        icon=folium.Icon(color=iconColor)
                    ).add_to(map)
            map.save("map.html")
            webbrowser.open("file://" + os.path.realpath("map.html"), new=1, autoraise=True)
        elif prompt == "4":
            refresh_files()
        elif prompt == "5":
            currentPromptType = promptType.USER_SETTINGS
        elif prompt.lower() == "quit" or prompt == "6":
            currentPromptType = promptType.QUIT
        else:
            print("\nYour choice is not valid. Please re-input your choice.")

    # Prompt type: basic search
    if currentPromptType == promptType.SEARCH:
        print('''\nHow would you like to search for recipes?
    1)  By name
    2)  By prep time
    3)  By calories
    4)  By ingredient
    5)  Back''')
        prompt = input("\nYour choice: ").strip()
        if prompt == "1":
            currentPromptType = promptType.SEARCH_NAME
        elif prompt == "2":
            currentPromptType = promptType.SEARCH_TIME
        elif prompt == "3":
            currentPromptType = promptType.SEARCH_CALORIES
        elif prompt == "4":
            currentPromptType = promptType.SEARCH_INGREDIENT
        elif prompt.lower() == "back" or prompt == "5":
            currentPromptType = promptType.MAIN
        else:
            print("\nYour choice is not valid. Please re-input your choice.")

    # Prompt type: search by recipe name
    if currentPromptType == promptType.SEARCH_NAME:
        prompt = input("\nSearch recipe name using keyword: ").strip()
        selected_recipes = []
        for index, row in recipes.iterrows():
            if prompt.lower() in row["Name"].lower():
                selected_recipes.append(index)
        if len(selected_recipes) > 0:
            currentPromptType = promptType.SEARCH_RESULTS
        else:
            print("\nNo matches were found.")
            currentPromptType = promptType.SEARCH

    # Prompt type: search by total prep time
    if currentPromptType == promptType.SEARCH_TIME:
        prompt = input("\nInput your maximum desired prep time (in minutes): ").strip()
        if prompt.isdigit() and int(prompt) > 0:
            selected_recipes = []
            for index, row in recipes.iterrows():
                time = parse_list_string(row["Time"])
                total_time = 0
                for x in time:
                    if "Total Time" in x:
                        hrs_mins = re.sub("[^0-9]", "|", x).split("|")
                        hrs_mins = [y for y in hrs_mins if y != ""]
                        if len(hrs_mins) == 1:
                            total_time += int(hrs_mins[0])
                        elif len(hrs_mins) == 2:
                            total_time += (60 * int(hrs_mins[0]) + int(hrs_mins[1]))
                if int(prompt) >= total_time:
                    selected_recipes.append(index)
            if len(selected_recipes) > 0:
                currentPromptType = promptType.SEARCH_RESULTS
            else:
                print("\nNo matches were found.")
                currentPromptType = promptType.SEARCH
        else:
            print("\nYour choice is not valid. Please re-input your choice.")

    # Prompt type: search by recipe calories
    if currentPromptType == promptType.SEARCH_CALORIES:
        prompt = input("\nInput your maximum desired calories: ").strip()
        if prompt.isdigit() and int(prompt) > 0:
            selected_recipes = []
            for index, row in recipes.iterrows():
                nutrition = parse_list_string(row["Nutrition"])
                calories = 0
                for x in nutrition:
                    if "Calories" in x:
                        calories = int(re.sub("[^0-9]", "", x))
                if int(prompt) >= calories:
                    selected_recipes.append(index)
            if len(selected_recipes) > 0:
                currentPromptType = promptType.SEARCH_RESULTS
            else:
                print("\nNo matches were found.")
                currentPromptType = promptType.SEARCH
        else:
            print("\nYour choice is not valid. Please re-input your choice.")
    
    # Prompt type: search by recipe ingredients
    if currentPromptType == promptType.SEARCH_INGREDIENT:
        prompt = input("\nSearch recipe ingredient using keyword: ").strip()
        selected_recipes = []
        for index, row in recipes.iterrows():
            ingredients = parse_list_string(row["Ingredients"])
            for x in ingredients:
                if prompt.lower() in x.lower():
                    selected_recipes.append(index)
        if len(selected_recipes) > 0:
            currentPromptType = promptType.SEARCH_RESULTS
        else:
            print("\nNo matches were found.")
            currentPromptType = promptType.SEARCH

    # Prompt type: display search results
    if currentPromptType == promptType.SEARCH_RESULTS:
        print("\nFound the following recipes:")
        for x in selected_recipes:
            print(str(x) + ")\t" + recipes.loc[x]["Name"])
        print("<<< Back")
        prompt = input("\nPlease select a recipe: ")

        if prompt.isdigit() and int(prompt) in selected_recipes:
            currentPromptType = promptType.RECIPE
        elif prompt.lower() == "back":
            currentPromptType = promptType.MAIN
        else:
            print("\nYour choice is not valid. Please re-input your choice.")

    # Prompt type: display favorite recipes
    if currentPromptType == promptType.MY_RECIPES:
        print("\nFound the following recipes:\n")
        for x in favorites:
            print(str(x) + ")\t" + recipes.loc[x]["Name"])
        print("<<< Back")
        prompt = input("\nPlease select a recipe: ")
        if prompt.isdigit() and int(prompt) in favorites:
            currentPromptType = promptType.RECIPE
        elif prompt.lower() == "back":
            currentPromptType = promptType.MAIN
        else:
            print("\nYour choice is not valid. Please re-input your choice.")

    # Prompt type: display a single recipe
    if currentPromptType == promptType.RECIPE:
        recipe = recipes.loc[int(prompt)]
        print("\n" + recipe["Name"])
        time = parse_list_string(recipe["Time"])
        print("\nTime to Make")
        for x in time:
            print(x)
        nutrition = parse_list_string(recipe["Nutrition"])
        print("\nNutrition Facts")
        for x in nutrition:
            print(x)
        ingredients = parse_list_string(recipe["Ingredients"])
        print("\nIngredients")
        for x in ingredients:
            print(x)
        directions = parse_list_string(recipe["Directions"])
        print("\nDirections")
        for x in directions:
            print(x)
        currentPromptType = promptType.RECIPE_ACTION

    # Prompt type: prompt for recipe options
    if currentPromptType == promptType.RECIPE_ACTION:
        index = int(prompt)
        print('''\nWhat would you like to do?
    1)  Add recipe calories to daily total
    2)  Toggle favorites
    3)  Back''')
        prompt = input("\nYour choice: ").strip()
        if prompt == "1":
            nutrition = parse_list_string(recipes.iloc[index]["Nutrition"])
            calories = 0
            for x in nutrition:
                if "Calories" in x:
                    calories = int(re.sub("[^0-9]", "", x))
            if total_calories + calories > calorie_limit:
                print("\nWarning: eating this meal would exceed your daily caloric intake.")
            else:
                total_calories += calories
                update_user_settings(calorie_limit, total_calories, date)
                print("\nYour caloric intake has been updated.")
        elif prompt == "2":
            if index in favorites:
                favorites.remove(index)
                print("\nThis recipe has been removed from your favorites.")
            else:
                favorites.append(index)
                print("\nThis recipe has been added to your favorites.")
            fout = open("favorites.txt", "wt", encoding="utf-8")
            for x in favorites:
                fout.write(str(x) + "\n")
            fout.close()
        elif prompt.lower() == "back" or prompt == "3":
            currentPromptType = promptType.MAIN
        else:
            print("\nYour choice is not valid. Please re-input your choice.")