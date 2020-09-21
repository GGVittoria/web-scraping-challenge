# Dependencies
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()
    # Create mars_data dict that we can insert into mongoDB
    mars_data = {}


    # Access and visit the NASA Mars News Site URL
    news_url = 'https://mars.nasa.gov/news/'
    browser.visit(news_url)

    # HTML object
    html = browser.html

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

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


    # HTML object
    img_html = browser.html

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(img_html, 'html.parser')

    # Retrieve Featured Mars Image url from style tag 
    featured_image_url  = soup.find('article')['style'].replace('background-image: url(','').replace(');', '')[1:-1]

    # Put the website url together with the features image url
    featured_image_url = 'https://www.jpl.nasa.gov' + featured_image_url

    # Add it to our mars_data dict
    featured_image_url = str(featured_image_url)
    mars_data["featured_image_url"] = featured_image_url


    # Access and visit Mars Weather twitter URL
    mars_twitter_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(mars_twitter_url)

    # HTML object
    twitter_marswx_html = browser.html

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(twitter_marswx_html, 'html.parser')

    # Get the text from the latest Mars weather tweet
    mars_weather = soup.find('p', class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text").text

    # Add it to our mars_data dict
    mars_weather = str(mars_weather)
    mars_data["mars_weather"] = mars_weather


    # Access and visit the Mars facts webpage
    mars_facts_url = 'https://space-facts.com/mars/'

    # Get any tabular data from the webpage
    facts_tables = pd.read_html(mars_facts_url)
    facts_tables

    # Slice off the dataframe that we want usin normal indexing
    facts_df = facts_tables[0]
    facts_df.columns = ['Description', 'Value']

    # Set the index to the `Fact` column
    facts_df.set_index('Description', inplace=True)

    # Convert the Dataframe to HTML
    html_table = facts_df.to_html()

    # Add facts table to our mars_data dict
    html_table = (html_table)
    mars_data["facts_table"] = html_table


    # Access and visit the USGS Astrogeology site
    mars_hemis_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(mars_hemis_url)
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
        soup = BeautifulSoup(mars_usgs_html, 'html.parser')
        partial_img_url = soup.find("img", class_="wide-image")["src"]
        
        img_url = 'https://astrogeology.usgs.gov/' + partial_img_url
        
        # Scrape the browser into soup and use soup to find the title of the image
        # Save the image's title to a variable called `img_title`
        img_title = soup.find('h2', class_="title").text
        
        # Get the data into a dictionary
        img_url = str(img_url)
        img_title = str(img_title)
        img_dict = {
            'img_url': img_url,
            'img_title': img_title
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