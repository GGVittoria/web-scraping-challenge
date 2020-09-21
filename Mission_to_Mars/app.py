# Import Dependencies
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

# Create Instance of Flask App
app = Flask(__name__)

# Set up mongo connection in line 
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")


@app.route('/')
def index():
    # Finding one document from our mongoDB and return it
    mars_data = mongo.db.mars_data.find_one()

    # Pass that listing to render template
    return render_template('index.html', mars_data=mars_data)


@app.route('/scrape')
def scrape():
    # Create mars info collection
    mars = mongo.db.mars_data
    mars_data = scrape_mars.scrape()
    mars.update(
        {},
        mars_data,
        upsert=True
    )
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=False)