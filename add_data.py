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


# # BookMaster
# bookMaster = MongoClient(MongoURL).datadase.bookMaster
# bookMaster.remove()
# data = pd.read_excel(r'Книги.xlsx')
# df = data[['ISBN', 'Автор', 'Название', 'Издательство',
#            'язык_оригинала', 'Год', 'Кол-во_стр.',
#            'Размер', 'Вес', 'Тип_обл.', 'Аннотация', 'файл_обложки',
#            'id_книги_наш']]
# df['_id'] = 0
# for i in range(len(df['_id'])):
#     df.loc[i, '_id'] = str(uuid.uuid4())
# df = df.where(pd.notnull(df), None)
# print('start')
# # df.replace({pd.nan: None})
# results = df.to_dict(orient="records")
# # bookMaster.insert_many(results)
# print('finish')

# supplier
# supplierCollection = MongoClient(MongoURL).datadase.supplier
# # supplierCollection.remove()
# data = pd.read_excel(r'Поставщики.xlsx')
# df = pd.DataFrame(data)
# df['_id'] = 0
# for i in range(len(df['_id'])):
#     df.loc[i, '_id'] = str(uuid.uuid4())
# df = df.where(pd.notnull(df), None)
# results = df.to_dict(orient="records")
# print(results)
# supplierCollection.insert_many(results)
# print('finish')



# deliveryWays
# deliveryWaysCollection = MongoClient(MongoURL).datadase.deliveryWays
# deliveryWaysCollection.update_many(
#     {},
#     {
#         "$set": {"name": "5post"}
#     },
#     upsert=True,
# )
# data = pd.read_excel(r'5post1.xlsx')
# df = pd.DataFrame(data)
# df['_id'] = 0
# for i in range(len(df['_id'])):
#     df.loc[i, '_id'] = str(uuid.uuid4())
# df = df.where(pd.notnull(df), None)
# # df = df['location'].str.split(',')
# results = df.to_dict(orient="records")
# print(results)
# deliveryWaysCollection.insert_many(results)
# print('finish')


# supplierBook = MongoClient(MongoURL).datadase.supplierBook
# data = pd.read_excel(r'Книги.xlsx')
# df = data[['Цена_поставщика', 'id_книги_наш', 'id_книги_поставщика',
#            'поставщик', 'срок_отправки_поставщика']]
# df['_id'] = 0
# for i in range(len(df['_id'])):
#     df.loc[i, '_id'] = str(uuid.uuid4())
# df = df.where(pd.notnull(df), None)
# print('start')
# # df.replace({pd.nan: None})
# results = df.to_dict(orient="records")
# # print(results)
# supplierBook.insert_many(results)
# print('finish')
