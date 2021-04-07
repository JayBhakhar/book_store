from flask import Flask, jsonify, request
from flask_pymongo import MongoClient
app = Flask(__name__)

MongoURL = "mongodb+srv://JayBhakhar:jay456789@book-cluster.oec1c.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = MongoClient(MongoURL).books_datadase.book


# Books = [
#     {'id': 0,
#      'title': 'A Fire Upon the Deep',
#      'author': 'Vernor Vinge',
#      'first_sentence': 'The coldsleep itself was dreamless.',
#      'year_published': '1992'},
#     {'id': 1,
#      'title': 'The Ones Who Walk Away From Omelas',
#      'author': 'Ursula K. Le Guin',
#      'first_sentence': 'With a clamor of bells that set.',
#      'published': '1973'},
#     {'id': 2,
#      'title': 'Dhalgren',
#      'author': 'Samuel R. Delany',
#      'first_sentence': 'to wound the autumnal city.',
#      'published': '1975'}
# ]

@app.route('/login')
def registeration():
    return 'login'


@app.route('/all')
def all_books():
    BooksData = []
    for doc in client.find():
        BooksData.append({'name': doc['name'],
                           'email': doc['email'],
                           'phoneNumber': doc['phoneNumber'],
                           'city': doc['city'],
                           'password': doc['password'],
                           'postindex': doc['postindex'],
                           '_id': str(doc['_id'])
                           })
    return jsonify({'books': BooksData})


# @app.route('/')
# def book_id():
#     # Check if an ID was provided as part of the URL.
#     # If ID is provided, assign it to a variable.
#     # If no ID is provided, display an error in the browser.
#     if 'id' in request.args:
#         id = int(request.args['id'])
#     else:
#         return "Error: No id field provided. Please specify an id."
#
#     # Create an empty list for our results
#     results = []
#
#     # Loop through the data and match results that fit the requested ID.
#     # IDs are unique, but other fields might return many results
#     for book in Books:
#         if book['id'] == id:
#             results.append(book)
#
#     # Use the jsonify function from Flask to convert our list of
#     # Python dictionaries to the JSON format.
#     return jsonify({'book': results})


@app.route('/', methods=['POST'])
def add_book():
    # http://127.0.0.1:5000/?name=jay&email=jaybhakhar@gmail.coom&
    # phoneNumber=+79961011395&city=surat&password=123456&postindex=395010
    message = 'registration'
    name = str(request.args['name'])
    email = str(request.args['email'])
    phoneNumber = str(request.args['phoneNumber'])
    city = str(request.args['city'])
    password = str(request.args['password'])
    postindex = str(request.args['postindex'])
    client.insert_one({
            'name': name,
            'email': email,
            'phoneNumber': phoneNumber,
            'city': city,
            'password': password,
            'postindex': postindex
        })
    return jsonify({'message': message})


if __name__ == '__main__':
    app.run(debug=1)

