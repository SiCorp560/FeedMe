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

This file serves to download the recipe data from EatingWell and convert it to
a CSV format for the main application.
'''

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

# Function to download recipe data and convert to CSV
def download_eatingwell(file="eatingwell_default.csv"):
    html_list = ["https://www.eatingwell.com/recipe/270291/mermaid-smoothie-bowl/",                     # Mermaid Smoothie Bowl
                "https://www.eatingwell.com/recipe/272746/mascarpone-berries-toast/",                   # Mascarpone & Berries Toast
                "https://www.eatingwell.com/recipe/8030933/egg-spinach-cheddar-breakfast-sandwich/",    # Egg, Spinach & Cheddar Breakfast Sandwich
                "https://www.eatingwell.com/recipe/272745/apple-peanut-butter-toast/",                  # Apple & Peanut Butter Toast
                "https://www.eatingwell.com/recipe/269844/vegan-superfood-grain-bowls/",                # Vegan Superfood Grain Bowls
                "https://www.eatingwell.com/sauteed-corn-with-basil-shallots-8661227",                  # Sautéed Corn with Basil & Shallots
                "https://www.eatingwell.com/cucumber-cream-cheese-roll-8660948",                        # Cucumber Cream Cheese Roll
                "https://www.eatingwell.com/recipe/8052446/best-tomato-sandwich/",                      # The Best Tomato Sandwich to Make All Summer Long
                "https://www.eatingwell.com/recipe/8069814/tomato-burrata-sandwich/",                   # Tomato & Burrata Sandwich
                "https://www.eatingwell.com/recipe/262096/edamame-veggie-rice-bowl/"]                   # Edamame & Veggie Rice Bowl

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
        directions = soup.find("div", {"id": "mm-recipes-steps_1-0"}).find("ol").find_all("li")
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
