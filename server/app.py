#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/restaurants', methods = ['GET'])
def all_restaurants():
    restaurants = Restaurant.query.all()
    response_body = [restaurant.to_dict(rules=('-restaurant_pizzas',))for restaurant in restaurants]
    return make_response(response_body, 200)

@app.route('/restaurants/<int:id>', methods = ['GET', 'DELETE'])
def resturants_by_id(id):
    restaurants = db.session.get(Restaurant, id)
    if restaurants:
        if request.method == "GET":
            response_body = restaurants.to_dict(rules=('-restaurant_pizzas.pizza.restaurant_pizzas','-restaurant_pizzas.restaurant'))
            return make_response(response_body, 200)
        elif request.method == "DELETE":
            db.session.delete(restaurants)
            db.session.commit()
            return make_response({}, 204)
    else: 
        response_body = {
            "error": "Restaurant not found"
        }
        return make_response(response_body, 404)

@app.route('/pizzas', methods = ['GET'])
def all_pizzas():
    #pizza = db.session.get(Pizza)
    pizzas = Pizza.query.all()
    response_body = [pizza.to_dict(rules=('-restaurant_pizzas',)) for pizza in pizzas]
    return make_response(response_body, 200)

@app.route('/restaurant_pizzas', methods = ['POST'])
def all_restaurant_pizza():
    price_data = request.json.get('price')
    pizza_id_data = request.json.get('pizza_id')
    restaurant_id_data = request.json.get('restaurant_id')
    try:
        new_restaurant_pizza = RestaurantPizza(price=price_data, pizza_id=pizza_id_data, restaurant_id= restaurant_id_data)
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        response_body = new_restaurant_pizza.to_dict(rules=('-pizza.restaurant_pizzas', '-restaurant.restaurant_pizzas'))
        return make_response(response_body, 201)
    
    except:
        response_body = {
            "errors": ["validation errors"]
        }
        return make_response(response_body, 400)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

if __name__ == "__main__":
    app.run(port=5555, debug=True)
