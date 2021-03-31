from flask import Flask, jsonify
from flask_pymongo import MongoClient

app = Flask(__name__)

MongoURL = "mongodb+srv://JayBhakhar:jay456789@book-cluster.oec1c.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = MongoClient(MongoURL).books_datadase.book


@app.route('/')
def index():
    BooksData = []
    for doc in client.find():
        BooksData.append({'name': doc['name'],
                           'pages': doc['pages'],
                           'book': doc['book'],
                           '_id': str(doc['_id'])
                           })
    return jsonify({'books': BooksData})


if __name__ == '__main__':
    app.run(debug=1)