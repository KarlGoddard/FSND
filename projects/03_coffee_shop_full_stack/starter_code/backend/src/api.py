import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['GET'])
def get_drinks():
  try:
    drinks = Drink.query.all()

    get_drinklist = []
    for dk in drinks:
        get_drinklist.append(dk.short())

    if len(get_drinklist) == 0:
      abort(404)

    return jsonify ({
        'success': True,
        'drinks' : get_drinklist
    })
  except Exception as e:
    print(e)
    abort(422)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(jwt):
      try:
        drinks = Drink.query.order_by(Drink.id).all()
        get_drinklist = [drink.long() for drink in drinks]
        # get_drinklist = []
        # for dk in drinks:
        #     get_drinklist.append(dk.long())

        if len(get_drinklist) == 0:
          abort(404)

        return jsonify ({
            'success': True,
            'drinks' : get_drinklist
        })
      except Exception as e:
        print(e)
        abort(422)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

# @app.route('/drinks', methods=['POST'])
# @requires_auth('post:drinks')
# def get_drinks_new(jwt):
#     body = request.get_json()
#
#     req_title = body.get('title',None)
#     req_recipe = body.get('recipe',None)
#
#     if not (req_title and req_recipe):
#         abort(422)
#     else:
#       try:
#         drink = Drink(title=req_title, recipe=req_recipe)
#         drink.insert()
#
#         return jsonify ({
#             'success': True,
#             'drinks' : drink.long()
#         })
#
#       except Exception as e:
#         print(e)
#         abort(422)

'''
# @TODO implement endpoint
#     PATCH /drinks/<id>
#         where <id> is the existing model id
#         it should respond with a 404 error if <id> is not found
#         it should update the corresponding row for <id>
#         it should require the 'patch:drinks' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
#         or appropriate status code indicating reason for failure
# '''

# @app.route('/drinks/<int:drink_id>', methods=['PATCH'])
# @requires_auth('patch:drinks')
# def get_drinks_edit(jwt):
#     body = request.get_json()
#
#     req_title = body.get('title',None)
#     req_recipe = body.get('recipe',None)
#
#     drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
#
#     if drink == 0:
#         abort(404)
#     else:
#       try:
#         if req_title:
#             drink.title = req_title
#         if req_recipe:
#             drink.recipe = req_recipe
#         drink.update()
#
#         return jsonify ({
#             'success': True,
#             'drinks' : drink.long()
#         })
#
#       except Exception as e:
#         print(e)
#         abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

# @app.route('/drinks/<int:drink_id>', methods=['DELETE'])
# @requires_auth('delete:drinks')
# def drinks_delete(jwt):
#
#     drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
#
#     if drink == 0:
#         abort(404)
#     else:
#       try:
#         drink.delete()
#
#         return jsonify ({
#             'success': True,
#             'deleted' : drink_id
#         })
#
#       except Exception as e:
#         print(e)
#         abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def error_authError(error):
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response
# @app.errorhandler(AuthError)
# def auth_error(error):
#     return jsonify({
#         "success": False,
#         "error": 422,
#         "message": "Authorisation Error"
#     }), 422

    # raise AuthError({
    #             'code': 'invalid_header',
    #             'description': 'Unable to find the appropriate key.'
    #         }, 400)
