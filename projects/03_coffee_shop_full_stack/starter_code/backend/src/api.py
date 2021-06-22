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

# db_drop_and_create_all()

# ROUTES

# Get drinks endpoint

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

# Get drinks detail endpoint

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

# Post drinks endpoint

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def get_drinks_new(jwt):
    body = request.get_json()

    req_title = body.get('title',None)
    req_recipe = body.get('recipe',None)

    if not (req_title and req_recipe):
        abort(422)
    else:
      try:
        drink = Drink(title=req_title, recipe=json.dumps(req_recipe))
        drink.insert()

        return jsonify ({
            'success': True,
            'drinks' : drink.long()
        }),200

      except Exception as e:
        print(e)
        abort(422)

# Patch drinks endpoint

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def get_drinks_edit(jwt, drink_id):
    body = request.get_json()

    req_title = body.get('title',None)
    req_recipe = body.get('recipe',None)

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink == 0:
        abort(404)
    else:
      try:
        if req_title:
            drink.title = req_title
        if req_recipe:
            drink.recipe = req_recipe
        drink.update()

        return jsonify ({
            'success': True,
            'drinks' : [drink.long()]
        })

      except Exception as e:
        print(e)
        abort(422)

# Delete drinks endpoint

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def drinks_delete(jwt, drink_id):

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink == 0:
        abort(404)
    else:
      try:
        drink.delete()

        return jsonify ({
            'success': True,
            'deleted' : drink_id
        })

      except Exception as e:
        print(e)
        abort(422)

# Error handling for unprocessable and resource not found

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

# error handler for AuthError

@app.errorhandler(AuthError)
def error_authError(error):
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response
