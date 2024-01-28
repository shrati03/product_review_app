from werkzeug.urls import unquote
from flask import Flask, render_template, request
import spacy
from bs4 import BeautifulSoup
import json
import requests

app = Flask(__name__)

# Load the spaCy English model (you may need to download it using: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/getsentiment', methods=['POST'])
def getsentiment():
    # get the URL from the form
    url = request.form['url']

    # Prepare the list needed
    names = []
    reviews = []
    rate = []
    data_string = ""
    
    # Get the whole web content of the product page
    response_pre = requests.get(url, headers={'User-Agent': 'My User Agent 1.0', 'From': 'personal@domain.com'})
    soup_pre = BeautifulSoup(response_pre.text, 'html.parser')
    scrapped_review_url = soup_pre.find("a", string="See all reviews").get('href')
    url_review_page = "https://www.amazon.com" + scrapped_review_url

    # Get the whole web content of the review page
    response = requests.get(url_review_page, headers={'User-Agent': 'My User Agent 1.0', 'From': 'personal@domain.com'})
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate every user's comment block
    soup1 = soup.find_all("div", {"id": "cm_cr-review_list"})
    for soup2 in soup1:
        # Locate every user's comment block
        soup3 = soup2.find_all("div", {"class": "a-section review aok-relative"})
        for soup4 in soup3:
            # Get every user's rate
            item = soup4.find("span", class_="a-icon-alt")
            data_string = data_string + item.get_text()
            rate.append(data_string)
            data_string = ""
            # Get every user's name
            item = soup4.find("span", class_="a-profile-name")
            data_string = data_string + item.get_text()
            names.append(data_string)
            data_string = ""  
            # Get every user's review which will be used for emotion analysis
            item = soup4.find("span", {"data-hook": "review-body"})
            data_string = data_string + item.get_text()
            data_string = data_string.replace('\n', '')
            data_string = data_string.replace('\t', '')
            reviews.append(data_string)
            data_string = ""	

    # Varible used to store emotion results and emotion scores
    results = []
    anger = []
    disgust = []
    fear = []
    joy = []
    sadness = []

    # Getting the emotion scores for the scrapped reviews
    for content in reviews:
        # Use spaCy for sentiment analysis
        doc = nlp(content)

        # Calculate sentiment scores
        joy_score = doc.sentiment.joy
        sadness_score = doc.sentiment.sadness
        anger_score = doc.sentiment.anger
        disgust_score = doc.sentiment.disgust
        fear_score = doc.sentiment.fear

        # Append scores to lists
        anger.append(round(anger_score, 3))
        disgust.append(round(disgust_score, 3))
        fear.append(round(fear_score, 3))
        joy.append(round(joy_score, 3))
        sadness.append(round(sadness_score, 3))

        results.append(f'Joy: {round(joy_score, 3)} \tSadness: {round(sadness_score, 3)} \tAnger: {round(anger_score, 3)} \tDisgust: {round(disgust_score, 3)} \tFear: {round(fear_score, 3)}')

    # Sum score for each emotion
    anger_score = round(sum(anger) / len(reviews), 3)
    disgust_score = round(sum(disgust) / len(reviews), 3)
    fear_score = round(sum(fear) / len(reviews), 3)
    joy_score = round(sum(joy) / len(reviews), 3)
    sadness_score = round(sum(sadness) / len(reviews), 3)
    score = [joy_score, sadness_score, anger_score, disgust_score, fear_score]

    # Store the averaged score of each emotion
    results.append(f'Joy: {joy_score} \tSadness: {sadness_score} \tAnger: {anger_score} \tDisgust: {disgust_score} \tFear: {fear_score}')

    # Return template with data
    return render_template('getsentiment.html', url=url, reviews=reviews, results=results, score=score)

if __name__ == '__main__':
    app.run()
