'''
File:        FeedMe.py

Author(s):   Simon Corpuz (scorpuz)
             Bonnie Li (bonnieli)
             Suryaa Raman (ssuryaar)
             Yiyang Yao (yiyangya)

Imports:     UrlLib
             BeautifulSoup
             Pandas

Imported By: FeedMe.py

This file serves to download the recipe data from AllRecipes and convert it to
a CSV format for the main application.
'''

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

# Function to download recipe data and convert to CSV
def download_allrecipes(file="allrecipes_default.csv"):
    html_list = ["https://www.allrecipes.com/chocolate-peanut-butter-protein-bars-recipe-8421618",      # Chocolate Peanut Butter Protein Bars
                "https://www.allrecipes.com/recipe/214947/perfect-summer-fruit-salad/",                 # Perfect Summer Fruit Salad
                "https://www.allrecipes.com/recipe/222352/jamies-sweet-and-easy-corn-on-the-cob/",      # Jamie's Sweet and Easy Corn on the Cob
                "https://www.allrecipes.com/recipe/233531/quick-whole-wheat-chapati/",                  # Quick Whole Wheat Chapati
                "https://www.allrecipes.com/recipe/13107/miso-soup/",                                   # Miso Soup
                "https://www.allrecipes.com/recipe/57783/emilys-famous-hash-browns/",                   # Homemade Crispy Hash Browns
                "https://www.allrecipes.com/recipe/13384/split-pea-soup/",                              # Split Pea Soup
                "https://www.allrecipes.com/recipe/20963/oven-roasted-potatoes/",                       # Oven Roasted Potatoes
                "https://www.allrecipes.com/recipe/8847/baked-honey-mustard-chicken/",                  # Baked Honey Mustard Chicken
                "https://www.allrecipes.com/recipe/18465/gnocchi-i/"]                                   # Gnocchi

    recipes = pd.DataFrame(columns = ["Name", "Time", "Nutrition", "Ingredients", "Directions"])

    for html_x in html_list:
        html = urlopen(html_x)
        soup = BeautifulSoup(html.read(), "lxml")
        soup = soup.find("body")

        # Recipe name
        name = soup.find("h1").text

        # Recipe time measurements
        time = soup.find("div", {"class": "mm-recipes-details__content"}).text.strip().replace(":\n", ": ").split("\n")
        time = [x for x in time if x != ""]

        # Recipe nutrition facts
        nutrition = soup.find("table", {"class": "mm-recipes-nutrition-facts-summary__table"}).text.strip().replace("\n\n", "|").replace("\n", " ").split("|")
        nutrition = [" ".join(x.strip().split()) for x in nutrition if x != ""]

        # Recipe ingredients
        ingredients = soup.find("ul", {"class": "mm-recipes-structured-ingredients__list"}).text.strip().split("\n")
        ingredients = [" ".join(x.strip().split()) for x in ingredients if x != ""]

        # Recipe directions
        directions = soup.find("div", {"id": "mm-recipes-steps__content_1-0"}).find_all("p", {"class": "comp mntl-sc-block mntl-sc-block-html"})
        directions = [" ".join(x.text.strip().split()) for x in directions]

        new_recipe = pd.DataFrame({
            "Name": [name],
            "Time": [time],
            "Nutrition": [nutrition],
            "Ingredients": [ingredients],
            "Directions": [directions]
        })

        recipes = recipes._append(new_recipe, ignore_index = True)

    recipes.to_csv(file)
