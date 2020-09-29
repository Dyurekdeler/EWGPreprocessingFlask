import requests
from bs4 import BeautifulSoup
import re
from flask import Flask, request, json

# https://www.twilio.com/blog/web-scraping-and-parsing-html-in-python-with-beautiful-soup

app = Flask(__name__) #create the Flask app

@app.route('/search_ingredient', methods=['GET'])
def search_ingredient():

    req_data = request.get_json(force=True)
    search_list = req_data['search_list']

    search_results = list()

    for ingredient in search_list:
        search_results.append(search(ingredient))

    response = ({"results": (search_results)})
    print(response)
    return response

def search(ingredient):
    SEARCH_URL = "https://www.ewg.org/skindeep/search/?utf8=%E2%9C%93&search="
    BASE_URL = "https://www.ewg.org/" #/skindeep/ingredients/702355-ETHYLPARABEN/"

    html_text = requests.get(SEARCH_URL + ingredient).text
    soup = BeautifulSoup(html_text, 'html.parser')

    section = (soup.body.find('section', attrs={'class':'product-listings'}))
    ingredients = section.find_all('p', attrs={'class':'product-name'})

    for ing in ingredients:

        ingredient_name = ing.text

        if ingredient_name.upper() == ingredient.upper():

            link = ing.find('a').get('href')
            html_text = requests.get(BASE_URL + link).text
            soup = BeautifulSoup(html_text, 'html.parser')

            score = str(soup.body.find('img', attrs={'class': 'squircle'}).get('src'))
            max_score = re.search('score=(.+?)&score', score).group(1)
            min_score = re.search('score_min=(.+?)', score).group(1)

            concerns = soup.body.find('p', attrs={'class':'chemical-concerns-text'}).text
            functions = soup.body.find('p', attrs={'class': 'chemical-functions-text'}).text
            about = soup.body.find('p', attrs={'class': 'chemical-about-text'}).text
            synonyms = soup.body.find('p', attrs={'class': 'chemical-synonyms-text'}).text

            gauge_img = soup.body.find_all('img', attrs={'class': 'gauge-img'})
            cancer = gauge_img[0].get('alt')
            toxicity = gauge_img[1].get('alt')
            allergy = gauge_img[2].get('alt')

            data_set = {"name": ingredient_name, "min_score": min_score, "max_score": max_score, "concerns":concerns,
                        "functions": functions, "about": about, "synonyms":synonyms,  "cancer":cancer, "toxicty":toxicity, "allergy":allergy}


            print(data_set)
            return data_set


if __name__ == "__main__":
    #host='0.0.0.0'
    app.run(port=8080, debug=True)
