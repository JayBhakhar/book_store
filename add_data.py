from flask import Flask
from flask_pymongo import MongoClient, PyMongo
import json
import pandas as pd
import uuid


MongoURL = "mongodb+srv://JayBhakhar:jay456789@book-cluster.oec1c.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
app = Flask(__name__)
app.config["MONGO_URI"] = MongoURL
mongo = PyMongo(app)
app.config['SECRET_KEY'] = 'secret'

# BookMaster
# bookMaster = MongoClient(MongoURL).datadase.bookMaster
# data = pd.read_excel(r'Книги.xlsx')
# df = data[['ISBN', 'Автор', 'Название', 'Издательство', 'Год', 'Кол-во_стр.',
#                                  'Размер', 'Вес', 'Тип_обл.', 'Аннотация', 'файл_обложки']]
# df['_id'] = 0
# for i in range(len(df['_id'])):
#     df.loc[i, '_id'] = str(uuid.uuid4())
# df = df.where(pd.notnull(df), None)
# print('start')
# # df.replace({pd.nan: None})
# results = df.to_dict(orient="records")
# bookMaster.insert_many(results)
# print('finish')

# supplier
# supplierCollection = MongoClient(MongoURL).datadase.supplier
# supplierCollection.update_many(
#     {},
#     {
#         "$set": {"deliveryWays": []}
#     },
#     upsert=True,
# )


# 5post
# deliveryWays = MongoClient(MongoURL).datadase.deliveryWays
# data = pd.read_excel(r'5post.xlsx')
# df = pd.DataFrame(data)
# df = df.where(pd.notnull(df), None)
# # df = df['Субъекты и населенные пункты'].str.split(',')
# results = df.to_dict(orient="records")
# deliveryWays.insert_many(results)
# print('finish')