from flask import Flask, jsonify, request, make_response
from flask_pymongo import MongoClient
import jwt
import datetime
from functools import wraps

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

@app.route('/reg')
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
                           'country': doc['country'],
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
    print(request.get_json())
    data = request.get_json()
    name = str(data['name'])
    email = str(data['email'])
    phoneNumber = str(data['phoneNumber'])
    city = str(data['city'])
    country = str(data['country'])
    password = str(data['password'])
    postindex = str(data['postindex'])
    client.insert_one({
            'name': name,
            'email': email,
            'phoneNumber': phoneNumber,
            'city': city,
            'country': country,
            'password': password,
            'postindex': postindex
        })
    return jsonify({'message': message})

@app.route('/admin', methods=['POST'])
def admin():
    data = request.get_json()
    login = str(data['login'])
    password = str(data['password'])
    for doc in client.find():
        return doc['admin']
        # if doc['admin'] == True:
        #     return True
        # else:
        #     return False
    return ''

# token authorization example
#
# @app.route('/login', methods = ['GET','POST'])
# def login():
#     auth = request.authorization
#
#     if auth and auth.password == 'password':
#         return ''
#     return make_response('abc', 200, {'ss':'ss'})
#
# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = request.args.get('token') #http://127.0.0.1:5000/route?token=alshfjfjdklsfj89549834ur
#
#         if not token:
#             return jsonify({'message' : 'Token is missing!'}), 403
#
#         try:
#             data = jwt.decode(token, app.config['SECRET_KEY'])
#         except:
#             return jsonify({'message' : 'Token is invalid!'}), 403
#
#         return f(*args, **kwargs)
#
#     return decorated
#
# @app.route('/unprotected')
# def unprotected():
#     return jsonify({'message' : 'Anyone can view this!'})
#
# @app.route('/protected')
# @token_required
# def protected():
#     return jsonify({'message' : 'This is only available for people with valid tokens.'})
#
# @app.route('/login')
# def login():
#     auth = request.authorization
#
#     if auth and auth.password == 'secret':
#         token = jwt.encode({'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=15)}, app.config['SECRET_KEY'])
#
#         return jsonify({'token' : token.decode('UTF-8')})
#
#     return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

if __name__ == '__main__':
    app.run(debug=1)

