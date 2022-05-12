import uvicorn
import random
import uuid
from fastapi import FastAPI, Depends, HTTPException, Request
from typing import Optional
from fastapi.responses import JSONResponse
from flask_pymongo import MongoClient
from auth import AuthHandler
from base_models import Login, Registration, UpdateUser, Passwords, BookId, Order
from passlib.context import CryptContext

app = FastAPI()
MongoURL = "mongodb+srv://JayBhakhar:jay456789@book-cluster.oec1c.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
bookCollection = MongoClient(MongoURL).datadase.bookMaster
supplierCollection = MongoClient(MongoURL).datadase.supplier
supplierBooksCollection = MongoClient(MongoURL).datadase.supplierBook
userCollection = MongoClient(MongoURL).datadase.user
deliveryWaysCollection = MongoClient(MongoURL).datadase.deliveryWays
orderCollection = MongoClient(MongoURL).datadase.order

auth_handler = AuthHandler()


@app.get('/')
def home():
    return '<h1> welcome to backend </h1>'


@app.get('/supplier')
def get_suppliers():
    output = []
    for supplier in supplierCollection.find():
        output.append(supplier)
    return JSONResponse({'suppliers': output})


@app.get('/users')
def get_users():
    output = []
    for user in userCollection.find():
        output.append(user)
    return JSONResponse({'user': output})


@app.post('/login')
# {
#   "login": "string",
#   "password": "string"
# }
def login(_user: Login):
    for user in userCollection.find({'email': _user.email}):
        if auth_handler.verify_password(_user.password, user['password']):
            token = auth_handler.encode_token(user)
            return JSONResponse({'token': token})
        else:
            return JSONResponse({"message": "Password does not match"}, 401)
    return JSONResponse({"message": "Could not find User"}, 401)


# eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfaWQiOiI1NDlmZWM0Ny1iODFjLTQ0YzMtYTc1YS1jNDNjOTc5NDEzYWIifQ.-j8aYvv5u0TAzDfSBKXd1UYtZIp4DmHVc1KEieHwUKU
@app.get('/registration')
def get_user(_token_id=Depends(auth_handler.auth_wrapper)):
    current_user = userCollection.find_one({'_id': _token_id['_id']})
    # pwd_context.hash(password) // save hashed password
    return JSONResponse({'User': [current_user]})


@app.post('/registration')
def create_user(_user: Registration):
    if userCollection.find_one({'email': _user.email}) is not None:
        message = 'Email already registered'
        return JSONResponse({'message': message}, 409)
    else:
        hashed_password = auth_handler.get_password_hash(_user.password)
        userCollection.insert_one({
            '_id': str(uuid.uuid4()),
            'user_name': _user.user_name,
            'email': _user.email,
            'password': hashed_password,
            'address': _user.address,
            'zip_code': _user.zip_code,
            'city': _user.city,
            'phone_number': _user.phone_number,
            'is_seller': False
        })
        message = 'User is successfully registered'
        return JSONResponse({'message': message})


@app.put('/registration')
def update_user(_user: UpdateUser, _token_id: auth_handler.auth_wrapper = Depends()):
    current_user = userCollection.find_one({'_id': _token_id['_id']})
    userCollection.find_one_and_update({
        "_id": current_user['_id'],
    },
        {
            "$set":
                {
                    'user_name': _user.user_name,
                    'address': _user.address,
                    'phone_number': _user.phone_number,
                    'zip_code': _user.zip_code,
                    'city': _user.city,
                }})
    message = "Your profile details has saved"
    return JSONResponse({'message': message})


@app.delete('/registration')
def delete_user(_token_id: auth_handler.auth_wrapper = Depends()):
    current_user = userCollection.find_one({'_id': _token_id['_id']})
    userCollection.delete_one({
        "_id": current_user['_id'],
    })
    message = "Deleted"
    return JSONResponse({'message': message})


@app.put('/change_password')
def update_user_password(_passwords: Passwords, _token_id: auth_handler.auth_wrapper = Depends()):
    current_user = userCollection.find_one({'_id': _token_id['_id']})
    hashed_password = auth_handler.get_password_hash(_passwords.new_password)
    if auth_handler.verify_password(_passwords.current_password, current_user['password']):
        userCollection.find_one_and_update({
            "_id": current_user['_id'],
        },
            {
                "$set":
                    {
                        'password': hashed_password,
                    }
            }
        )
        return JSONResponse({"message": "Password Changed"})
    else:
        return JSONResponse({"message": "Password does not match"}, 401)


@app.get('/books')
def get_books():
    book_list = []
    for book in bookCollection.find().limit(50):
        book_list.append(book)
    output = random.sample(book_list, 10)
    return JSONResponse({'Books': output})


@app.get('/book')
async def get_book(request: Request):
    book_id = request.headers.get('book_id')
    book = bookCollection.find_one({'_id': book_id})
    return JSONResponse({'Book': [book]})


@app.get('/order')
async def get_order(request: Request, _token_id: auth_handler.auth_wrapper = Depends()):
    is_clients_order = request.headers.get('is_clients_order')
    current_user = userCollection.find_one({'_id': _token_id['_id']})
    orders_list = []
    if current_user['is_seller'] & is_clients_order:
        for order in orderCollection.find({'user_name': current_user['user_name']}):
            orders_list.append(order)
    else:
        for order in orderCollection.find({'client_id': _token_id['_id']}):
            orders_list.append(order)
    return JSONResponse({'Order': orders_list})


@app.post('/order')
def create_order(order: Order, _token_id: auth_handler.auth_wrapper = Depends()):
    current_user = userCollection.find_one({'_id': _token_id['_id']})
    for i in order.order:
        i = i.dict()
        orderCollection.insert_one({
            '_id': str(uuid.uuid4()),
            'status': 'not sent yet',
            'book_id': i['book_id'],
            'supplier_name': i['supplier_name'],
            'supplier_book_id': i['supplier_book_id'],
            'total': i['total'],
            'post': i['post'],
            'client_id': current_user['_id'],
            'client_name': current_user['user_name'],
            'client_email': current_user['email'],
            'client_address': current_user['address'],
            'client_zip_code': current_user['zip_code'],
            'client_city': current_user['city'],
            'client_phone_number': current_user['phone_number']
        })
    message = 'Order Confirmed'
    return JSONResponse({'message': message})


# eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfaWQiOiI1NDlmZWM0Ny1iODFjLTQ0YzMtYTc1YS1jNDNjOTc5NDEzYWIifQ.-j8aYvv5u0TAzDfSBKXd1UYtZIp4DmHVc1KEieHwUKU
@app.get('/delivery_charges')
def delivery_charges_counter(request: Request, _token_id: auth_handler.auth_wrapper = Depends()):
    # todo: need to change
    lst = []
    weight = float(request.headers.get('weight'))
    current_user = userCollection.find_one({'_id': _token_id['_id']})
    for i in deliveryWaysCollection.find({"location": {"$regex": current_user['city'].capitalize()}}):
        lst.append(i)
    delivery_charge = lst[0]['price']
    if weight > 3.0:
        n = weight // 3
        delivery_charge += (n * lst[0]['additional_charge'])
    return JSONResponse({'delivery_charge': delivery_charge, 'delivery_time': lst[0]['delivery_time']})


@app.get('/supplier_options')
def supplier_options(request: Request, _token_id: auth_handler.auth_wrapper = Depends()):
    current_user = userCollection.find_one({'_id': _token_id['_id']})
    book_weight = float(request.headers.get('book_weight'))
    our_book_id = int(request.headers.get('our_book_id'))
    delivery_ways = []
    supplier_books = []
    for delivery_way in deliveryWaysCollection.find({"location": {"$regex": current_user['city']}}):
        delivery_ways.append(delivery_way)
    for supplier_book in supplierBooksCollection.find({"id_книги_наш": our_book_id}):
        i = 0
        delivery_charge = delivery_ways[i]['price']
        if book_weight > 3.0:
            n = book_weight // 3
            delivery_charge += (n * delivery_ways[i]['additional_charge'])
        supplier_book['delivery_charge'] = delivery_charge
        supplier_book['срок_отправки_поставщика'] += delivery_ways[i]['delivery_time']
        supplier_book['delivery_name'] = delivery_ways[i]['name']
        supplier_books.append(supplier_book)
        # Todo: FOR NOW ITS RETURN ONLY ONE QUERY BECAUSE suppliers HAVE ONLY ONE 'deliveryWay'.
        # for supplier in supplierCollection.find({'поставщик': supplier_book['поставщик']}):
        #     print(supplier['поставщик'])
        #     suppliers.append(supplier)
        # for deliveryWay in deliveryWaysCollection.find(
        #         {"location": {"$regex": current_user['city'].capitalize()}, 'name': supplier['deliveryWay']}):
        #     delivery_ways.append(deliveryWay)
        # delivery_ways = [i for n, i in enumerate(delivery_ways) if
        #                      i not in delivery_ways[n + 1:]]  # Remove duplicate dict in list
    return JSONResponse({'ChooseSupplier': supplier_books})


if __name__ == "__main__":
    uvicorn.run("main:app", host='192.168.50.95', port=5000, reload=True)
    # uvicorn.run(app, port=5000)
