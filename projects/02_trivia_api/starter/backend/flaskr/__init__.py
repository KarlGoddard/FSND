import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

# function to paginate questions and use a parameter to define number of questions per page

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
  @app.after_request
  def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods','GET, POST, PATCH, DELETE, OPTIONS')
        return response

  # Endpoint to handle GET requests for categories.

  @app.route('/categories')
  def retrieve_categories():
    try:
        cats = Category.query.all()
        allcats = {cat.id:cat.type for cat in cats}

        if len(cats) == 0:
          abort(404)

        return jsonify ({
            'success': True,
            'categories' : allcats
        })
    except Exception as e:
        print(e)
        abort(422)

  # Endpoint to handle GET requests for questions, includes pagination (every 10 questions).
  # Return a list of questions, number of total questions, current category, categories.

  @app.route('/questions')
  def retrieve_questions():
    try:
        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)

        if len(current_questions) == 0:
          abort(404)

        cats = Category.query.order_by(Category.id).all()
        allcategories = {cat.id:cat.type for cat in cats}

        return jsonify ({
          'success': True,
          'questions': current_questions,
          'total_questions': len(Question.query.all()),
          'current_category' : None,
          'categories' : allcategories
        })
    except Exception as e:
        print(e)
        abort(422)

  # Endpoint to DELETE question using a question ID

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()

      questions = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, questions)

      cats = Category.query.order_by(Category.id).all()
      allcategories = {cat.id:cat.type for cat in cats}

      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(Question.query.all()),
        'current_category' : None,
        'categories' : allcategories
      })

    except Exception as e:
        print(e)
        abort(422)


  # Endpoint to POST a new question, which will require the question and
  # answer text, category, and difficulty score.

  @app.route('/questions', methods=['POST'])
  def add_question():
    body = request.get_json()

    new_question = body.get('question',None)
    new_answer = body.get('answer',None)
    new_difficulty = body.get('difficulty',None)
    new_category = body.get('category',None)

    try:
      question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
      question.insert()

      questions = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, questions)

      cats = Category.query.order_by(Category.id).all()
      allcategories = {cat.id:cat.type for cat in cats}

      return jsonify ({
          'success': True,
          'question_id': question.id,
          'question_created': question.question,
          'questions': current_questions,
          'total_questions': len(Question.query.all()),
          'category' : allcategories
      })

    except Exception as e:
        print(e)
        abort(404)


  # Endpoint to get questions based on a search term, returns any questions
  # for which the search term is a substring of the question.

  @app.route('/questions/search', methods=['POST'])
  def search_questions():

    body = request.get_json()
    search = body.get('searchTerm', None)

    if search:
      try:
          searchResult = Question.query.filter(Question.question.ilike(f'%{search}%')).all()

          questions = []
          for question in searchResult:
             questions.append(question.format())


          return jsonify ({
            'success' : True,
            'questions' : questions,
            'total_questions' : len(searchResult),
            'current_category' : None
          })

      except Exception as e:
            print(e)
            abort(404)


  # Endpoint to get questions based on category id.

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_categoryquestions(category_id):
    try:
      cat_questions = Question.query.filter(Question.category == str(category_id)).all()

      questions = []
      for question in cat_questions:
        questions.append(question.format())

      return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(cat_questions),
            'current_category': category_id
        })

    except Exception as e:
        print(e)
        abort(422)

  # Dndpoint to get questions to play the quiz.  This endpoint takes category and previous question parameters
  # and returns a random questions within the given category, if provided, and not one of the previous questions.

  @app.route('/quizzes', methods=['POST'])
  def make_quiz():
    body = request.get_json()
    prev_questions = body.get('previous_questions', None)
    category = body.get('quiz_category', None)

    try:

        if category['id'] != 0:
            questionSet = Question.query.filter_by(category = category['id']).all()
        else:
            questionSet = Question.query.all()

        questionsAvailable = []

        for question in questionSet:
            if question.id not in prev_questions:
                questionsAvailable.append(question.format())

        if len(questionsAvailable) > 0:
            randomQuestion = random.choice(questionsAvailable)
            return jsonify({
                'success': True,
                'question': randomQuestion
              })
        else:
            return jsonify({
                'success': False,
                'question': None
              })

    except Exception as e:
        print(e)
        abort(404)


  # Error handlers for all expected errors

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
      }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(405)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "method not allowed"
      }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(500)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "internal server error"
      }), 500

  return app
