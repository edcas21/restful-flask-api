from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required

from security import authenticate, identity

app = Flask(__name__)
app.secret_key = 'secret-key'
api = Api(app)

jwt = JWT(app, authenticate, identity) # /auth

items = []

# Every resource has to be a class that inherits from Resource
class Item(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('price', type=float, required=True, help='This field cannot be left blank!')

    @jwt_required()
    def get(self, name):
        print(name)
        # next gives the first item found
        item = next(filter(lambda x: x['name'] == name, items), None) # Returns none if the lambda function returns nothing
        # 404 is for not found
        return { 'item': item }, 200 if item else 404

    def post(self, name):

        # Making sure name is unique
        if next(filter(lambda x: x['name'] == name, items), None):
            # 400 is bad request
            return { 'message': "An item with name '{name}' already exists!".format(name=name) }, 400

        # Accessing the json payload
        req_body = Item.parser.parse_args()

        item = { 'name': name, 'price': req_body['price'] }
        items.append(item)
        # 201 is for creation or post
        return item, 201

    def delete(self, name):
        global items
        items = list(filter(lambda x: x['name'] != name, items))
        return {'message': 'Item deleted'}

    def put(self, name):

        req_body = Item.parser.parse_args()

        item = next(filter(lambda x: x['name'] == name, items), None)
        if item is None:
            item = { 'name': name, 'price': req_body['price'] }
            items.append(item)
        else:
            item.update(req_body)
        return item


class ItemList(Resource):

    def get(self):
        return { 'items': items }

api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')

if __name__ == '__main__':

    app.run(port=5000, debug=True)
