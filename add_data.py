# from flask import Flask
# from flask_pymongo import MongoClient, PyMongo
import pandas as pd


# MongoURL = "mongodb+srv://JayBhakhar:jay456789@book-cluster.oec1c.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
# app = Flask(__name__)
# app.config["MONGO_URI"] = MongoURL
# mongo = PyMongo(app)
# supplier_books = MongoClient(MongoURL).datadase.supplier_books
# app.config['SECRET_KEY'] = 'secret'

data = pd.read_excel(r'Книги.xlsx')
df = pd.DataFrame(data, columns= ['ISBN'])
results = df.to_json(orient="records")
print(results)