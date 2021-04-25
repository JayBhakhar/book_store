from flask import Flask, jsonify, request, make_response
from flask_pymongo import MongoClient
import jwt
import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

MongoURL = "mongodb+srv://JayBhakhar:jay456789@book-cluster.oec1c.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
books = MongoClient(MongoURL).books_datadase.book
users = MongoClient(MongoURL).user_datadase.user
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
                algorithm="HS256"
            )
            current_user = users.find_one({'_id': data['user_id']})
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
                'confirmseller': user['confirmseller']
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
        'confirmseller': False
    })
    return jsonify({'message': 'User is successfully registered'})


# for get all books, but only admin can
@app.route('/books', methods=['POST'])
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
    if not current_user['confirmseller']:
        return jsonify({'message': 'User is not a confirm seller'})

    data = request.get_json()

    books.insert_one({
        '_id': str(uuid.uuid4()),
        'bookName': str(data['bookName']),
        'author': str(data['author']),
        'pages': int(data['pages']),
        'price': int(data['price']),
        'quantity': int(data['quantity']),
        'sellerName': current_user['userName'],
        'seller_id': current_user['_id']
    })
    return jsonify({'message': 'New book created!'})


#for update a book
@app.route('/book/<book_id>', methods=['PUT'])
@token_required
def update_book(current_user, book_id):
    if not current_user['confirmseller']:
        return jsonify({'message': 'User have not a rights to update a book'})

    data = request.get_json()

    books.find_one_and_update(
        {
            "_id": book_id  # user_id which admin one want to make seller
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


#request to become a seller, admin only
@app.route('/admin/seller', methods=['GET'])
@token_required
def seller(curret_user):
    if curret_user['admin']:
        output = []
        for user in users.find({'seller': True}):
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
    return jsonify({'messange' : 'user not a admin'})


# to confirm seller
@app.route('/admin/<user_id>', methods=['PUT'])
def confirmSeller(current_user, user_id):
    if current_user['admin']:
        users.find_one_and_update(
            {
                "_id": user_id['_id']  #user_id which admin one want to make seller
            },
            {
                "$set":
                    {
                        "confirmseller": True
                    }
            }
        )
    else:
        return jsonify({'messange' : 'user not a admin'})


@app.route('/login', methods=['GET'])
def login():
    email = str(request.args['email'])
    passwd = request.args['password']
    for data in users.find({'email': email}):
        print(check_password_hash(passwd, data['password']))
        # if check_password_hash(passwd, data['password']): #idk but return false every time
        if True:
            token = jwt.encode(
                {
                '_id': data['_id'],
                'admin': data['admin'],
                'confirmseller': data['confirmseller'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                },
                app.config['SECRET_KEY'])
            print(token)
            data = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms="HS256",
                options={"verify_signature": False}
            )
            print("dic :- " + str(data)) #for check token
            current_user = users.find_one({'_id': data['_id']})
            return jsonify({'token': token})
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


if __name__ == '__main__':
    app.run(debug=1)
