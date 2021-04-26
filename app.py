from flask import Flask, jsonify, request, make_response
from flask_pymongo import MongoClient
import jwt
import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

MongoURL = "mongodb+srv://JayBhakhar:jay456789@book-cluster.oec1c.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
books = MongoClient(MongoURL).datadase.book
users = MongoClient(MongoURL).datadase.user
orders = MongoClient(MongoURL).datadase.order
app.config['SECRET_KEY'] = 'secret'


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms="HS256"
            )
            current_user = users.find_one({'_id': data['_id']})
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/')
@token_required
def home(current_user):
    return 'working'

# for get all users,but only admin can
@app.route('/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    if not current_user['admin']:
        return jsonify({'message': 'User is not a admin'})

    output = []

    for user in users.find():
        output.append(
            {
                '_id': user['_id'],
                'userName': user['userName'],
                'email': user['email'],
                'phoneNumber': user['phoneNumber'],
                'address': user['address'],
                'city': user['city'],
                'country': user['country'],
                'password': user['password'],
                'postindex': user['postindex'],
                'admin': user['admin'],
                'seller': user['seller'],
                'confirm_seller': user['confirm_seller']
            }
        )
    return jsonify({'users': output})


# registration of new user
@app.route('/registration', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')

    users.insert_one({
        '_id': str(uuid.uuid4()),
        'userName': str(data['userName']),
        'email': str(data['email']),
        'phoneNumber': str(data['phoneNumber']),
        'address': str(data['address']),
        'city': int(data['city']),
        'country': int(data['country']),
        'password': hashed_password,
        'postindex': int(data['postindex']),
        'admin': False,
        'seller': bool(data['seller']),
        'confirm_seller': False
    })
    return jsonify({'message': 'User is successfully registered'})


# for get all books, but only admin can
@app.route('/admin/books', methods=['GET'])
@token_required
def get_all_books(current_user):
    if not current_user['admin']:
        return jsonify({'message': 'Cannot perform that function!'})

    output = []

    for book in books.find():
        output.append(
            {
                '_id': book['_id'],
                'sellerName': book['sellerName'],
                'bookName': book['bookName'],
                'author': book['author'],
                'pages': book['pages'],
                'price': book['price'],
                'quantity': book['quantity'],
                'seller_id': book['seller_id']
            }
        )

    return jsonify({'books': output})


# for add a book, but only confirm seller can
@app.route('/book', methods=['POST'])
@token_required
def create_book(current_user):
    if not current_user['confirm_seller']:
        return jsonify({'message': 'User is not a confirm seller'})

    data = request.get_json()

    books.insert_one({
        '_id': str(uuid.uuid4()),
        'seller_book_id': int(data['seller_book_id']),
        'book_name': str(data['bookName']),
        'author': str(data['author']),
        'pages': int(data['pages']),
        'price': int(data['price']),
        'quantity': int(data['quantity']),
        'seller_name': current_user['userName'],
        'seller_id': current_user['_id']
    })
    return jsonify({'message': 'New book created!'})


#for update a book
@app.route('/book/<book_id>', methods=['PUT'])
@token_required
def update_book(current_user, book_id):
    if not current_user['confirm_seller']:
        return jsonify({'message': 'User have not a rights to update a book'})

    data = request.get_json()

    books.find_one_and_update(
        {
            "seller_book_id": book_id,
            "seller_id": current_user['_id']# user_id which admin one want to make seller
        },
        {
            "$set":
                {
                    'bookName': str(data['bookName']),
                    'author': str(data['author']),
                    'pages': int(data['pages']),
                    'price': int(data['price']),
                    'quantity': int(data['quantity'])
                }
        }
    )
    return jsonify({'message': 'book updated!'})


#seller list, admin only
@app.route('/admin/sellers', methods=['GET'])
@token_required
def seller(curret_user):
    if curret_user['admin']:
        output = []
        for user in users.find({'confirm_seller': True}):
            output.append(
                {
                    '_id': user['_id'],
                    'userName': user['userName'],
                    'email': user['email'],
                    'phoneNumber': user['phoneNumber'],
                    'address': user['address'],
                    'city': user['city'],
                    'country': user['country'],
                    'postindex': user['postindex']
                }
            )
        return jsonify({'users': output})
    return jsonify({'message' : 'user not a admin'})


# just recently ask to seller
@app.route('/admin/newSellers', methods=['GET'])
@token_required
def new_sellers(curret_user):
    if curret_user['admin']:
        output = []
        for user in users.find({'seller': True, 'confirm_seller': False}):
            output.append(
                {
                    '_id': user['_id'],
                    'userName': user['userName'],
                    'email': user['email'],
                    'phoneNumber': user['phoneNumber'],
                    'address': user['address'],
                    'city': user['city'],
                    'country': user['country'],
                    'postindex': user['postindex']
                }
            )
        return jsonify({'users': output})
    return jsonify({'message' : 'user not a admin'})


# to confirm seller
# in data should have two parameter id and confirm(bool)
@app.route('/confirm_seller', methods=['PUT'])
def confirmSeller(current_user):
    data = request.get_json()
    if current_user['admin']:
        if data['confirm']:
            users.find_one_and_update(
                {
                    "_id": data['_id']  #user_id which admin one want to make seller
                },
                {
                    "$set":
                        {
                            "confirm_seller": True
                        }
                }
            )
        else:
            users.find_one_and_update(
                {
                    "_id": data['_id']  # user_id which admin one want to make seller
                },
                {
                    "$set":
                        {
                            "seller": False
                        }
                }
            )
    else:
        return jsonify({'message' : 'user is not a admin'})


@app.route('/login', methods=['GET'])
def login():
    email = str(request.args['email'])
    passwd = request.args['password']
    for data in users.find({'email': email}):
        if check_password_hash(data['password'], passwd):
            token = jwt.encode(
                {
                '_id': data['_id'],
                'admin': data['admin'],
                'confirm_seller': data['confirm_seller'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                },
                app.config['SECRET_KEY'],
                algorithm="HS256")
            return jsonify({'token': token})
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


if __name__ == '__main__':
    app.run(debug=1)
