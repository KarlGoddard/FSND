import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

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

  @app.route('/categories')
  def retrieve_categories():
    cats = Category.query.all()
    allcats = {cat.id:cat.type for cat in cats}

    # if len(current_books) == 0:
    #   abort(404)

    return jsonify ({
        'success': True,
        'categories' : allcats
    })

  '''
  @DONE:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
  @app.route('/questions')
  def retrieve_questions():
    questions = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, questions)

    if len(current_questions) == 0:
      abort(404)

    # allcats = {1:'Science'}
    cats = Category.query.order_by(Category.id).all()
    allcategories = {cat.id:cat.type for cat in cats}

    return jsonify ({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'current_category' : None,
      'categories' : allcategories
    })

  '''
  @DONE:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''

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

    except:
      abort(422)

  '''
  @DONE:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''

  @app.route('/questions', methods=['POST'])
  def add_question():
    body = request.get_json()

    new_question = body.get('question',None)
    new_answer = body.get('answer',None)
    new_difficulty = body.get('difficulty',None)
    new_category = body.get('category',None)

    try:
      question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
      # question = Question(question, answer, category, difficulty)
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

    except:
      abort(404)



  '''
  @DONE
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''

  @app.route('/questions/search', methods=['POST'])
  def search_questions():

    body = request.get_json()
    search = body.get('searchTerm', None)

    if search:
      try:
          searchResult = Question.query.filter(Question.question.ilike(f'%{search}%')).all()
#         # selection = Book.query.order_by(Book.id).filter(Book.title.ilike('%{}%'.format(search)))
#
          questions = []
          for question in searchResult:
             questions.append(question.format())


          return jsonify ({
            'success' : True,
            'questions' : questions,
            'total_questions' : len(searchResult),
            'current_category' : None
          })

      except:
        abort(404)


  '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''

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

    except:
      abort(422)

  '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''

  @app.route('/quizzes', methods=['POST'])
  def make_quiz():
    body = request.get_json() # get info passed
      # data: JSON.stringify({
      #   previous_questions: previousQuestions,
      #   quiz_category: this.state.quizCategory
    prev_questions = body.get('previous_questions', None)
    category = body.get('quiz_category', None)

    try:

        if category['id'] != 0:
            questionSet = Question.query.filter_by(question.category=category['id']).all()
        else
            questionSet = Question.query.all()
        # get random choice from questions?

    #
    #   return jsonify ({
    #       'success': True,
    #       'question_id': question.id,
    #       'question_created': question.question,
    #       'questions': current_questions,
    #       'total_questions': len(Question.query.all()),
    #       'category' : allcategories
    #   })

  # showAnswer: false,
  # previousQuestions: previousQuestions,
  # currentQuestion: result.question,
  # guess: '',
  # forceEnd: result.question ? false : true

    except:
      abort(404)

  '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''

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

  return app
