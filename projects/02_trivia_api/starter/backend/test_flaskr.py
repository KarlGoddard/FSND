import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        # self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres','pass1','localhost:5432', 'trivia_test')
        # self.database_name = "trivia_test"
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    # new_question = body.get('question',None)
    # new_answer = body.get('answer',None)
    # new_difficulty = body.get('difficulty',None)
    # new_category = body.get('category',None)
        self.add_question = {
            'question':"New Question",
            'answer':"New Answer",
            'difficulty': 3,
            'category': 1
        }

        self.searchItem = {
            'searchTerm':"Title"
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # def test_delete(self):
    #     res = self.client().delete('/questions/6')
    #     data = json.loads(res.data)
    #
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)

    def test_delete_beyond_valid_question_number(self):
        res = self.client().delete('/questions/5000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'unprocessable')

    def test_add_new_question(self):
        res = self.client().post('/questions', json=self.add_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question_id'])

    # def test_search(self):
    #     res = self.client().post('/questions/search')
    #     data = json.loads(res.data, json=self.searchItem)
    #
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)

    #
    # def test_questions_by_category(self):
    #     res = self.client().get('/categories/1/questions')
    #     data = json.loads(res.data)
    #
    # def test_quiz(self):
    #     res = self.client().post('/quizzes')
    #     data = json.loads(res.data)

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
