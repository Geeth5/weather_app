from flask import Flask, render_template, request
from pymongo import MongoClient
from open_meteo import OpenMeteo
from geopy.geocoders import Nominatim

app = Flask(__name__)

#Connects to MongoDb database named Weather with Collection details
def connect_to_mongodb():
    client = MongoClient()
    db = client.weather
    collection = db.details
    return collection


#Checks if City data or lat/lon data is given and returns dict of forecast
async def get_weather_data(city=None, user_latitude=None, user_longitude=None):
    if city is not None:
        geolocator = Nominatim(user_agent="my_app")
        location = geolocator.geocode(city)
        latitude = location.latitude
        longitude = location.longitude
    elif user_latitude is not None and user_longitude is not None:
        latitude = user_latitude
        longitude = user_longitude
    else:
        print("Undefined Parameters")
        return
    
    async with OpenMeteo() as open_meteo:
        forecast = await open_meteo.forecast(
            latitude=latitude,
            longitude=longitude,
            current_weather=True
        )

    return forecast.dict()

#Stores the Data provided to MongoDB
def store_weather_data(collection, data):
    collection.insert_one(data)

''' FLASK FUNCTIONS '''
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/weather", methods=["POST"])
async def weather():
    city = request.form.get("city") if request.form.get("city") else None
    latitude = request.form.get("latitude") if True else 0
    longitude = request.form.get("longitude") if True else 0

    collection = connect_to_mongodb()
    data = await get_weather_data(city, latitude, longitude)
    if data is not None:
        store_weather_data(collection, data)
    else:
        return "Sorry data could not be stored! Try Again!"

    return "Weather data stored in MongoDB!"

@app.route("/show_details")
def show_details():
    collection = connect_to_mongodb()
    data = collection.find()
    return render_template("show_details.html", data=data)

if __name__ == "__main__":
    app.run()
