from flask import Flask, jsonify, request, make_response
from flask_pymongo import MongoClient, PyMongo
import jwt
import uuid
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import csv

MongoURL = "mongodb+srv://JayBhakhar:jay456789@book-cluster.oec1c.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
app = Flask(__name__)
app.config["MONGO_URI"] = MongoURL
mongo = PyMongo(app)
books = MongoClient(MongoURL).datadase.book
users = MongoClient(MongoURL).datadase.user
_cart = MongoClient(MongoURL).datadase.cart
orders = MongoClient(MongoURL).datadase.order
phototry = MongoClient(MongoURL).datadase.phototry
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
    print(current_user['admin'])
    return 'working'


@app.route('/photo', methods=['POST'])
@token_required
def save_photo(current_user):
    data = request.get_json()
    # {
    #     'bookID': idk from where they will send because they don't have it)))
    # }

    cover_photo = request.files['coverPhoto']
    mongo.save_file(cover_photo.filename, cover_photo)

    spine_photo = request.files['spinePhoto']
    mongo.save_file(spine_photo.filename, spine_photo)

    pictures_photo = request.files['picturesPhoto']
    mongo.save_file(pictures_photo.filename, pictures_photo)

    # photo = request.files['photo']
    # mongo.save_file(photo.filename, photo)

    phototry.insert_one(
        {
            '_id': str(uuid.uuid4()),
            'book_id': data['bookID'],
            'seller_name': current_user['userName'],
            'cover_photo': cover_photo.filename,
            'spine_photo': spine_photo.filename,
            'pictures_photo': pictures_photo.filename
        }
    )
    return 'working Done !'


@app.route('/photo', methods=['GET'])
def send_photo():
    data = request.get_json()
    # {
    #     'bookID': idk from where thry will send because they dont have it)))
    # }
    for photo in phototry.find({'book_id': data['bookID']}):
        cover_photo = photo['cover_photo']
        # spine_photo = photo['spine_photo']
        pictures_photo = photo['pictures_photo']
        print(cover_photo)
        print(pictures_photo)
        # return mongo.send_file(cover_photo)
        return mongo.send_file(pictures_photo)
    # mongo.send_file(spine_photo)
    # mongo.send_file(pictures_photo)
    return jsonify({'message': 'Error to load picture'})


@app.route('/photo', methods=['GET'])
def pa():
    output = []
    for pic in phototry.find():
        output.append(
            {
                '_id': str(pic['_id']),
                'book_id': pic['_id'],
                'seller_name': pic['seller_name'],
                'photo': pic['pictures_filename']
            }
        )
        print(output)
        return jsonify({'cover_pic': output})


# get user
@app.route('/user', methods=['GET'])
@token_required
def get_user(current_user):
    output = []

    for user in users.find({'_id': current_user['_id']}):
        output.append(
            {
                '_id': user['_id'],
                'userName': user['user_name'],
                'email': user['email'],
                'phoneNumber': user['phone_number'],
                'address': user['address'],
                'country': user['country'],
                'password': user['password'],
                'admin': user['admin'],
                'seller': user['seller'],
                'confirmSeller': user['confirm_seller']
            }  # left side print, right side database
        )
    return jsonify({'user': output})


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
                'userName': user['user_name'],
                'email': user['email'],
                'phoneNumber': user['phone_number'],
                'address': user['address'],
                'city': user['city'],
                'country': user['country'],
                'password': user['password'],
                'postindex': user['postindex'],
                'admin': user['admin'],
                'seller': user['seller'],
                'confirm_seller': user['confirm_seller']
            }  # left side print, right side database
        )
    return jsonify({'users': output})


# for get all books
@app.route('/books', methods=['GET'])
@token_required
def get_all_books(current_user):
    output = []
    for book in books.find():
        output.append(
            {
                '_id': book['_id'],
                'bookName': book['book_name'],
                'authors': book['authors'],
                'price': book['price'],
            }
        )
    return jsonify({'books': output})


@app.route('/seller/books', methods=['GET'])
@token_required
def seller_book(current_user):
    output = []
    for book in books.find({'seller_id': current_user['_id']}):
        output.append(
            {
                '_id': book['_id'],
                'bookName': book['book_name'],
                'authors': book['authors'],
                'price': book['price'],
                'quantity': book['quantity'],
            }
        )  # need to change parameters
    return jsonify({'sellerBook': output})


# for book
@app.route('/book', methods=['GET'])
@token_required
def get_book(current_user):
    output = []
    for book in books.find({'_id': request.headers['book_id']}):
        output.append(
            {
                '_id': book['_id'],
                'sellerId': book['seller_id'],
                'bookName': book['book_name'],
                'authors': book['authors'],
                'illustrators': book['illustrators'],
                'interpreters': book['interpreters'],
                'publisher': book['publisher'],
                'originalLanguage': book['original_language'],
                'year': book['year'],
                'ISBN': book['ISBN'],
                'EAN': book['EAN'],
                'ISSN': book['ISSN'],
                'numberOfPages': book['number_of_pages'],
                'height': book['height'],
                'width': book['width'],
                'length': book['length'],
                'weight': book['weight'],
                'price': book['price'],
                'quantity': book['quantity'],
                'sellerBookId': book['seller_book_id'],
                'briefAnnotation': book['brief_annotation'],
                'longAnnotation': book['long_annotation'],
                'coverType': book['cover_type'],
                'sellerName': book['seller_name'],
            }
        )
    return jsonify({'book': output})


# for add a book, but only confirm seller can
@app.route('/book', methods=['POST'])
@token_required
def add_book(current_user):
    if not current_user['confirm_seller']:
        return jsonify({'message': 'User is not a confirm seller'})

    data = request.get_json()

    # # example of data
    # {
    #     'bookName': 'The life of pi',
    #     'authors': 'jay bhakhar',
    #     'illustrators': 'person name',
    #     'interpreters': 'person name',
    #     'publisher': 'anton',
    #     'originalLanguage': 'Russian',
    #     'year': 1999,
    #     'ISBN': 846454532,
    #     'EAN': 12321231321,
    #     'ISSN': 132123132,
    #     'numberOfPages': 100,
    #     'height': 23,
    #     'width': 452,
    #     'length': 54,
    #     'weight': 75,
    #     'price': 75,
    #     'quantity': 48,
    #     'sellerBookID': 1,
    #     'briefAnnotation': '50-100 words',
    #     'longAnnotation': '500-600 words',
    #     'coverType': 'Hard/Soft'
    # }

    books.insert_one({
        '_id': str(uuid.uuid4()),
        'book_name': str(data['bookName']),
        'authors': str(data['authors']),
        'illustrators': str(data['illustrators']),
        'interpreters': str(data['interpreters']),
        'publisher': str(data['publisher']),
        'original_language': str(data['originalLanguage']),
        'year': int(data['year']),
        'ISBN': int(data['ISBN']),
        'EAN': int(data['EAN']),
        'ISSN': int(data['ISSN']),
        'number_of_pages': int(data['numberOfPages']),
        'height': int(data['height']),
        'width': int(data['width']),
        'length': int(data['length']),
        'weight': int(data['weight']),
        'price': int(data['price']),
        'quantity': int(data['quantity']),
        'seller_book_id': int(data['sellerBookID']),
        'brief_annotation': str(data['briefAnnotation']),
        'long_annotation': str(data['longAnnotation']),
        'cover_type': str(data['coverType']),
        'seller_name': current_user['user_name'],
        'seller_id': current_user['_id'],
    })
    return jsonify({'message': 'New book Added!'})


# for update a book
@app.route('/book', methods=['PUT'])
@token_required
def update_book(current_user):
    if not current_user['confirm_seller']:
        return jsonify({'message': 'User have not a rights to update a book'})

    data = request.get_json()

    # # example of data
    # {
    #     'book_id': 's5646' // for find a book
    #     'bookName': 'The life of pi',
    #     'authors': 'jay bhakhar',
    #     'illustrators': 'person name',
    #     'interpreters': 'person name',
    #     'publisher': 'anton',
    #     'originalLanguage': 'Russian',
    #     'year': 1999,
    #     'ISBN': 846454532,
    #     'EAN': 12321231321,
    #     'ISSN': 132123132,
    #     'numberOfPages': 100,
    #     'height': 23,
    #     'width': 452,
    #     'length': 54,
    #     'weight': 75,
    #     'price': 75,
    #     'quantity': 48,
    #     'sellerBookID': 1,
    #     'briefAnnotation': '50-100 words',
    #     'longAnnotation': '500-600 words',
    #     'coverType': 'Hard/Soft'
    # }

    books.find_one_and_update(
        {
            "_id": data['book_id'],
        },
        {
            "$set":
                {
                    'book_name': str(data['bookName']),
                    'authors': str(data['authors']),
                    'illustrators': str(data['illustrators']),
                    'interpreters': str(data['interpreters']),
                    'publisher': str(data['publisher']),
                    'original_language': str(data['originalLanguage']),
                    'year': int(data['year']),
                    'ISBN': int(data['ISBN']),
                    'EAN': int(data['EAN']),
                    'ISSN': int(data['ISSN']),
                    'number_of_pages': int(data['numberOfPages']),
                    'height': int(data['height']),
                    'width': int(data['width']),
                    'length': int(data['length']),
                    'weight': int(data['weight']),
                    'price': int(data['price']),
                    'quantity': int(data['quantity']),
                    'seller_book_id': int(data['sellerBookID']),
                    'brief_annotation': str(data['briefAnnotation']),
                    'long_annotation': str(data['longAnnotation']),
                    'cover_type': str(data['coverType']),
                }
        }
    )
    return jsonify({'message': 'book updated!'})


@app.route('/book', methods=['DELETE'])
@token_required
def remove_book(current_user):
    data = request.get_json()
    books.delete_one({
        '_id': data['book_id'],
    })
    _cart.delete_one({
        'book_id': data['book_id'],
    })
    return jsonify({'message': 'Book removed !!'})


# confirm sellers list, admin only
@app.route('/confirm_sellers', methods=['GET'])
@token_required
def seller(curret_user):
    if curret_user['admin']:
        output = []
        for user in users.find({'confirm_seller': True}):
            output.append(
                {
                    '_id': user['_id'],
                    'userName': user['user_name'],
                    'email': user['email'],
                    'phoneNumber': user['phone_number'],
                    'address': user['address'],
                    'country': user['country']
                }
            )
        return jsonify({'sellers': output})
    return jsonify({'message': 'user not a admin'})


# to remove confirm seller and seller request
@app.route('/confirm_seller', methods=['PUT'])
@token_required
def confirmSeller(current_user):
    data = request.get_json()
    # {
    #     'user_id': 'user_id'
    # }
    if current_user['admin']:
        users.find_one_and_update(
            {
                "_id": data['user_id']  # user_id which admin one want to make seller
            },
            {
                "$set":
                    {
                        "confirm_seller": False,
                        "seller": False
                    }
            }
        )
        return jsonify({'message': 'removed successfully'})
    return jsonify({'message': 'user not a admin'})


# just recently ask to seller
@app.route('/newSellers', methods=['GET'])
@token_required
def new_sellers(curret_user):
    if curret_user['admin']:
        output = []
        for user in users.find({'seller': True, 'confirm_seller': False}):
            output.append(
                {
                    '_id': user['_id'],
                    'userName': user['user_name'],
                    'email': user['email'],
                    'phoneNumber': user['phone_number'],
                    'address': user['address'],
                    'country': user['country']
                }
            )
        return jsonify({'newSellers': output})
    return jsonify({'message': 'user not a admin'})


# add to confirm selller
@app.route('/newSellers', methods=['PUT'])
@token_required
def make_confirm_seller(curret_user):
    data = request.get_json()

    # {
    #     'user_id' : '64654das-4654s-user_id'
    # }

    users.find_one_and_update({
        "_id": data['user_id']  # user_id which admin one want to make seller
    },
        {
            "$set":
                {
                    "confirm_seller": True,
                }
        })
    return jsonify({'message': 'Added to confirm seller'})


@app.route('/login', methods=['POST'])
def login():
    user = request.get_json()
    # {
    #     "email": "jaybhakhar@gmail.com",
    #     "password": "123456"
    # }
    for data in users.find({'email': user['email']}):
        if check_password_hash(data['password'], user['password']):
            token = jwt.encode(
                {
                    '_id': data['_id'],
                    # 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                },
                app.config['SECRET_KEY'],
                algorithm="HS256")
            return jsonify({'token': token})
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


# get user
@app.route('/cart', methods=['GET'])
@token_required
def get_cart(current_user):
    output = []
    for cart in _cart.find({'user_id': current_user['_id']}):
        output.append(
            {
                'item_id': cart['_id'],
                'bookID': cart['book_id'],
            }  # left side print, right side database
        )
    return jsonify({'cart': output})


@app.route('/cart', methods=['POST'])
@token_required
def add_item_to_cart(current_user):
    data = request.get_json()
    # TODO : user_id and seller_id must be different if not it mean seller buy is own book

    # # example of data
    # {
    #     '"book_id": "${book[0].book_id}",'
    #     '"seller_id": "${book[0].seller_id}",'
    #     '"seller_book_id": "${book[0].sellerBookID}",'
    # }

    _cart.insert_one({
        '_id': str(uuid.uuid4()),
        'user_id': str(current_user['_id']),
        'book_id': str(data['book_id']),
        'seller_id': str(data['seller_id']),
        'seller_book_id': str(data['seller_book_id']),
    })
    return jsonify({'message': 'New Item Added!'}) 


@app.route('/cart', methods=['DELETE'])
@token_required
def remove_item_from_cart(current_user):
    data = request.get_json()
    # {
    #     '_id': 'item_id'
    # }
    _cart.delete_one({"_id": data['_id']})
    return jsonify({'message': 'removed successfully'})


# list of all orders, only admin
@app.route('/orders', methods=['GET'])
@token_required
def all_order(current_user):
    output = []
    if current_user['admin']:
        for order in orders.find():
            output.append(
                {
                    '_id': order['_id'],
                    'sellerID': order['sellerID'],
                    'buyerID': order['buyerID'],
                }
            )
    if current_user['confirm_seller']:
        for order in orders.find(
                {'sellerID': current_user['_id']}
        ):
            output.append(
                {
                    '_id': order['_id'],
                    'buyerID': order['buyerID'],
                    'seller_book_id': order['seller_book_id'],
                    'sellerID': order['sellerID']
                }
            )
    else:
        for order in orders.find(
                {'buyerID': current_user['_id']}
        ):
            output.append(
                {
                    '_id': order['_id'],
                    'seller_book_id': order['seller_book_id'],
                }
            )
    return jsonify({'orders': output})


# add a order
@app.route('/order', methods=['POST'])
@token_required
def create_order(current_user):
    data = request.get_json()

    # {
    #     'bookID': '1asd246sadsa5sada4455',
    #     'sellerID': '1asd2465sada4455',
    #     'sellerBookID': 42,
    # }

    orders.insert_one({
        '_id': str(uuid.uuid4()),
        'buyer_id': current_user['_id'],
        'seller_id': data['sellerID'],
        'seller_book_id': data['sellerBookID'],
    })
    return jsonify({'message': 'order taken'})


# registration of new user
@app.route('/registration', methods=['POST'])
def create_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    users.insert_one({
        '_id': str(uuid.uuid4()),
        'user_name': str(data['userName']),
        'email': str(data['email']),
        'phone_number': str(data['phoneNumber']),
        'address': str(data['address']),
        'country': int(data['country']),
        'password': hashed_password,
        'admin': False,
        'seller': bool(data['seller']),
        'confirm_seller': False
    })
    return jsonify({'message': 'User is successfully registered'})


# edit order
@app.route('/editorder', methods=['PUT'])
def edirOrder(current_user):
    data = request.get_json()

    # {
    #     quantity:2
    # }

    orders.find_one_and_update(
        {
            "buyer_id": current_user['_id']  # user_id which admin one want to make seller
        },
        {
            "$set":
                {
                    "quantity": data['quantity']
                }
        }
    )
    return jsonify({'message': 'order changed'})


# remove order
@app.route('/order', methods=['DELETE'])
@token_required
def remove_order(current_user):
    orders.deleteOne({
        'buyer_id': current_user['_id'],
    })
    return jsonify({'message': 'order canceled'})


def csva():
    with open('oktmo.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count == 5:
                # print(f'Column names are {", ".join(row)}')
                # print(len(row))
                print("row number 0 :- " + row[0])
                print("row number 1 :- " + row[1])
                print("row number 2 :- " + row[2])
                print("row number 3 :- " + row[3])
                print("row number 4 :- " + row[4])
                print("row number 5 :- " + row[5])
                print("row number 6 :- " + row[6])
                print("row number 7 :- " + row[7])
                print("row number 8 :- " + row[8])
                print("row number 9 :- " + row[9])
                print("row number 10 :- " + row[10])
                print("row number 11 :- " + row[11])
                print("row number 12 :- " + row[12])
                line_count += 1
            else:
                # print(f'\t {row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                line_count += 1
        print(f'Processed {line_count} lines.')


if __name__ == '__main__':
    app.run(host='192.168.0.122', debug=1)
    # app.run(debug=1)
