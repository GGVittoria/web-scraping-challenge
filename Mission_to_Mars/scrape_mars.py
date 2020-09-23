# Dependencies
import pymongo
import requests
from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import time

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "c:/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()
    # Create mars_data dict that we can insert into mongoDB
    mars_data = {}


    # Access and visit the NASA Mars News Site URL
    news_url = 'https://mars.nasa.gov/news/'
    browser.visit(news_url)

    time.sleep(1)

    # HTML object
    html = browser.html

    # Parse HTML with BeautifulSoup
    soup = bs(html, "html.parser")

    # Retrieve all elements that contain news title
    latest_news = soup.find_all('div', class_="list_text")

    # Get the latest news    
    news = latest_news[0]

    # Use BeautifulSoup' find() method to navigate and retrieve attributes
    news_title = news.find('div', class_="content_title").text
    news_p = news.find('div', class_="article_teaser_body").text

    # Add them to our mars_data dict
    news_title = str(news_title)
    news_p = str(news_p)
    mars_data["news_title"] = news_title
    mars_data["news_p"] = news_p

    # Access and visit the JPL Mars Space Images URL
    featured_img_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(featured_img_url)

    time.sleep(1)

    # HTML object
    img_html = browser.html

    # Parse HTML with BeautifulSoup
    soup = bs(img_html, 'html.parser')

    # Retrieve Featured Mars Image url from style tag 
    featured_image_url  = soup.find('article')['style'].replace('background-image: url(','').replace(');', '')[1:-1]

    # Put the website url together with the features image url
    featured_image_url = 'https://www.jpl.nasa.gov' + featured_image_url

    # Add it to our mars_data dict
    featured_image_url = str(featured_image_url)
    mars_data["featured_image_url"] = featured_image_url

    # Access and visit the Mars facts webpage
    mars_facts_url = 'https://space-facts.com/mars/'

    time.sleep(1)

    # Use Pandas to scrape data
    table = pd.read_html(mars_facts_url)
    facts_df = table[0]

    # Rename columns and set index
    facts_df.columns=['description', 'value']

    # Convert the Dataframe to HTML
    html_table = facts_df.to_html(classes='data table', index=False, header=False, border=0)

    # Add facts table to our mars_data dict
    mars_data["facts_table"] = html_table

    # Access and visit the USGS Astrogeology site
    mars_hemis_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(mars_hemis_url)

    time.sleep(1)

    xpath = '//div//a[@class="itemLink product-item"]/img'

    # Use splinter to Click the image to bring up the full resolution image
    results = browser.find_by_xpath(xpath)

    # Initiate hemisphere_image_urls list
    hemisphere_image_urls = []

    # Loop over results to get image data
    for i in range(len(results)):
        img = results[i]
                
        img.click()
        
        # Scrape the browser into soup and use soup to find the full resolution image of mars
        # Save the image url to a variable called `img_url`
        mars_usgs_html = browser.html
        soup = bs(mars_usgs_html, 'html.parser')
        partial_img_url = soup.find("img", class_="wide-image")["src"]
        
        img_url = 'https://astrogeology.usgs.gov/' + partial_img_url
        
        # Scrape the browser into soup and use soup to find the title of the image
        # Save the image's title to a variable called `img_title`
        img_title = soup.find('h2', class_="title").text
        
        # Get the data into a dictionary
        img_dict = {
            'title': img_title,
            'img_url': img_url
        }
        # Append image dictionaries to the list
        hemisphere_image_urls.append(img_dict)

        browser.back()
        results = browser.find_by_xpath(xpath)
        i = i + 1

    # Add hemispheres dictionary to mars_data dictionary
    mars_data['hemisphere_image_urls'] = hemisphere_image_urls


    # Close the browser after scraping
    browser.quit()

    # Return our mars_data dict
    return mars_data