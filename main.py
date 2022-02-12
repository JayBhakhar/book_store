import uvicorn
import random
import uuid
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from flask_pymongo import MongoClient
from auth import AuthHandler
from base_models import Login, Registration, UpdateUser, Passwords
from passlib.context import CryptContext

app = FastAPI()
MongoURL = "mongodb+srv://JayBhakhar:jay456789@book-cluster.oec1c.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
bookCollection = MongoClient(MongoURL).datadase.book
supplierCollection = MongoClient(MongoURL).datadase.supplier
userCollection = MongoClient(MongoURL).datadase.user
deliveryWaysCollection = MongoClient(MongoURL).datadase.deliveryWays

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


# eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfaWQiOiI4NjYyYzdmMy04NzhkLTQxYmQtYWQ4Zi1iZDUwZTk4MDFiY2UifQ.FDXBsAIG2KD10Bt4YPFGVMlAq6OptsrH6UYKmoR_LaU
@app.get('/registration')
def get_user(_token_id=Depends(auth_handler.auth_wrapper)):
    current_user = userCollection.find_one({'_id': _token_id['_id']})
    # pwd_context.hash(password) // save hashed password
    return JSONResponse({'User': [current_user]})


@app.post('/registration')
# {
# _id: str
# email: str
# name: str
# password: str
# address: str
# phone_number: str
# }
def create_user(_user: Registration):
    hashed_password = auth_handler.get_password_hash(_user.password)
    userCollection.insert_one({
        '_id': str(uuid.uuid4()),
        'user_name': _user.user_name,
        'email': _user.email,
        'password': hashed_password,
        'address': _user.password,
        'phone_number': _user.phone_number
    }
    )
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


@app.post('/test')
def create_user(_token_id=Depends(auth_handler.auth_wrapper)):
    current_user = userCollection.find_one({'_id': _token_id['_id']})
    print(current_user)
    # pwd_context.hash(password) // save hashed password
    return "nothing"


@app.get('/books')
def get_books():
    book_list = []
    for book in bookCollection.find().limit(50):
        book_list.append(book)
    output = random.sample(book_list, 10)
    return JSONResponse({'Books': output})


@app.get('/test2')
def delivery_ways():
    lst = []
    for i in deliveryWaysCollection.find({"Субъекты и населенные пункты": {"$regex": "Брянск"}}):
        # lst.append(i['Тарифная зона'])
        print(i)
    print(lst)


if __name__ == "__main__":
    uvicorn.run(app, host='10.194.80.78', port=5000)
    # uvicorn.run(app, port=5000)
