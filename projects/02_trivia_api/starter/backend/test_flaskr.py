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
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'test queston?',
            'answer': 'test answer',
            'difficulty': 1,
            'category': '3'
        }

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    #before testing, trivia_test database needs to be populated by running trivia.psql

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['created'])
        self.assertTrue(data['total_questions'])
        self.assertIn('question_created', data)
        self.assertIn('questions', data)

    def test_405_create_question_now_allowed(self):
        res = self.client().post('/questions/45', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'method not allowed')

    def test_get_paginated_questions(self):
        # question = Question(
        #     question='question', answer='answer',
        #     category='2', difficulty=3
        # )
        # question.insert()
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['total_questions'])
        self.assertIn('questions', data)

    def test_404_invalid_page_resource_not_found(self):
        res = self.client().get('/questions?page=555')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        # question = Question(
        #     question='question', answer='answer',
        #     category='2', difficulty=3
        # )
        # question.insert()
        question = Question.query.first()
        res = self.client().delete('/questions/' + str(question.id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['deleted'])

    def test_404_delete_resource_not_found(self):
        res = self.client().delete('/questions/999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIn('categories', data)

    def test_405_post_categories_now_allowed(self):
        res = self.client().post('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'method not allowed')

    def test_404_wrong_end_point(self):
        res = self.client().post('/noEndPoint')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/3/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['current_category'])
        self.assertTrue(data['total_questions'])
        self.assertIn('questions', data) 

    def test_404_questions_by_invalid_category(self):
        res = self.client().get('/categories/99/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_play_quiz(self):
        question = Question.query.first()
        category = Category.query.first()
        pq=[]
        pq.append(question.id)
        res = self.client().post('/quizzes', json={'previous_questions': pq, 
                                                        'quiz_category': {'id': category.id, 'type': category.type}
                                                }
                                )
        
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('question', data)

    def test_400_bad_request_play_quiz(self):
        res = self.client().post('/quizzes', json={'quiz_category': {'id': 3}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()