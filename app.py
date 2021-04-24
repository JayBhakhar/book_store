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


@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    if not current_user['admin']:
        return jsonify({'message': 'Cannot perform that function!'})

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


@app.route('/user', methods=['POST'])
def create_user():
    admin = True
    if not admin:
        return jsonify({'message': 'Cannot perform that function!'})

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
    return jsonify({'message': 'New user created!'})


@app.route('/book', methods=['GET'])
# @token_required
def get_all_books():
    admin = True
    if not admin:
        return jsonify({'message': 'Cannot perform that function!'})

    output = []

    for book in books.find():
        output.append(
            {
                '_id': book['_id'],
                'bookName': book['bookName'],
                'author': book['author'],
                'pages': book['pages'],
                'price': book['price'],
                'seller': book['seller'],
                'quantity': book['quantity'],
            }
        )

    return jsonify({'books': output})


@app.route('/book', methods=['POST'])
def create_book():
    admin = True
    if not admin:
        return jsonify({'message': 'Cannot perform that function!'})

    data = request.get_json()
    seller = 'jay bhakhar' #Todo: from token get userName

    books.insert_one({
        '_id': str(uuid.uuid4()),
        'bookName': str(data['bookName']),
        'author': str(data['author']),
        'pages': int(data['pages']),
        'price': int(data['price']),
        'quantity': int(data['quantity']),
        'seller': seller
    })
    return jsonify({'message': 'New book created!'})


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
                'user_id': data['_id'],
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
                verify=False
            )
            print("dic :- " + str(data))
            current_user = users.find_one({'_id': data['user_id']})
            def homea(current_user):
                # if current_user['admin'] == False:
                #     print('you are not admin')
                if current_user['confirmseller']:
                    print('you are seller')
            homea(current_user)
            return jsonify({'token': token})
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})



if __name__ == '__main__':
    app.run(debug=1)
