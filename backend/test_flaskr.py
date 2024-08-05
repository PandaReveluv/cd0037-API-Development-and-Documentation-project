import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from dotenv import load_dotenv


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        load_dotenv(dotenv_path='.flaskenv')
        self.database_name = "trivia_test"
        self.database_username = os.getenv('TEST_DATABASE_USERNAME')
        self.database_password = os.getenv('TEST_DATABASE_PASSWORD')
        self.database_url = os.getenv('TEST_DATABASE_URL')
        self.database_path = ('postgresql://{}:{}@{}/{}'.format(
            self.database_username,
            self.database_password,
            self.database_url,
            self.database_name))

        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path
        })

        self.client = self.app.test_client

        self.new_question = {
            "question":  "Dummy question",
            "answer":  "Dummy answer",
            "difficulty": 1,
            "category": 3,
        }

        self.search_term = {
            "searchTerm": 'title'
        }

        self.quiz_body = {
            "previous_questions": [],
            "quiz_category": {
                "type": "Science",
                "id": "1"
            }
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["categories"])

    def test_get_pagination_questions(self):
        res = self.client().get("/questions?page=1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["categories"])
        self.assertIsNone(data["currentCategory"])

    def test_get_pagination_questions_not_found(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["message"], "Not found")

    def test_delete_question_by_id(self):
        res = self.client().delete("/questions/1")
        self.assertEqual(res.status_code, 204)

    def test_delete_question_by_id_got_bad_request_error(self):
        res = self.client().delete("/questions/dummy")
        self.assertEqual(res.status_code, 400)

    def test_create_question(self):
        res = self.client().post("/question", json=self.new_question)
        self.assertEqual(res.status_code, 204)

    def test_create_question_got_unexpected_error(self):
        error_question = self.new_question.copy()
        error_question["category"] = 1000
        res = self.client().post("/question", json=error_question)
        self.assertEqual(res.status_code, 500)

    def test_search_question(self):
        res = self.client().post("/questions", json=self.search_term)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertIsNone(data['currentCategory'])

    def test_search_question_not_found(self):
        not_found_search_term = self.search_term.copy()
        not_found_search_term['searchTerm'] = 'somedummysearchterm'
        res = self.client().post("/questions", json=not_found_search_term)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["message"], "Not found")

    def test_get_questions_by_category_id(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["currentCategory"])

    def test_get_questions_by_category_id_got_bad_request(self):
        res = self.client().get("/categories/dummy/questions")
        self.assertEqual(res.status_code, 400)

    def test_play_quiz(self):
        res = self.client().post("/quizzes", json=self.quiz_body)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question']['id'])
        self.assertTrue(data['question']['question'])
        self.assertTrue(data['question']['answer'])
        self.assertTrue(data['question']['category'])
        self.assertTrue(data['question']['difficulty'])

    def test_play_quiz_invalid_request_body(self):
        invalid_request_body = self.quiz_body.copy()
        invalid_request_body['previous_questions'] = None
        res = self.client().post("/quizzes", json=invalid_request_body)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
