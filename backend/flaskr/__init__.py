import logging
import os
from flask import Flask, request, abort, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

from models import db
from sqlalchemy import exc, func

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        query_results = Category.query.all()
        categories = {query_result.id: query_result.type
                      for query_result in query_results}
        return jsonify({"categories": categories})

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_pagination_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10

        questions = Question.query.all()
        formatted_questions = [question.format() for question in questions]
        categories = Category.query.all()
        formatted_categories = {category.id: category.type
                                for category in categories}

        if len(formatted_questions[start:end]) == 0:
            abort(404)

        return jsonify({
            "questions": formatted_questions[start:end],
            "total_questions": len(formatted_questions),
            "categories": formatted_categories,
            "currentCategory": None
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question_by_id(question_id):
        if not question_id.isdigit():
            abort(400)
        try:
            Question.query.filter(Question.id == question_id).delete()
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            abort(500)
        return Response(status=204)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/question', methods=['POST'])
    def create_question():
        request_body = request.get_json()
        question = request_body.get('question', None)
        answer = request_body.get('answer', None)
        difficulty = request_body.get('difficulty', None)
        category = request_body.get('category', None)
        new_question = Question(
            question=question,
            answer=answer,
            difficulty=difficulty,
            category=category)
        try:
            db.session.add(new_question)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            logging.error('Error at creating question: %s', repr(e))
            db.session.rollback()
            abort(status=500)
        return Response(status=204)


    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions', methods=['POST'])
    def search_questions():
        request_body = request.get_json()
        search_term = request_body.get('searchTerm', None)
        questions = (Question.query
                     .filter(Question.question
                             .like('%' + search_term + '%'))).all()
        formatted_questions = [question.format() for question in questions]
        if len(formatted_questions) == 0:
            abort(404)

        return jsonify({
            "questions": formatted_questions,
            "total_questions": len(formatted_questions),
            "currentCategory": None
        })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<category_id>/questions', methods=['GET'])
    def get_questions_by_category_id(category_id):
        if not category_id.isdigit():
            abort(400)
        questions = (Question.query
                     .filter(Question.category == category_id).all())
        formatted_questions = [question.format() for question in questions]
        category = Category.query.filter(Category.id == category_id).first()

        return jsonify({
            "questions": formatted_questions,
            "total_questions": len(formatted_questions),
            "currentCategory": category.type
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        request_body = request.get_json()
        previous_questions = request_body.get('previous_questions', None)
        quiz_category = request_body.get('quiz_category', None)
        next_question = (Question.query
                         .filter(Question.id.notin_(previous_questions))
                         .filter(Question.category == quiz_category.get('id'))
                         .order_by(func.random()).first())
        return jsonify({
            "question": next_question.format()
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(400)
    def handle_not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Invalid request"
        }), 400

    @app.errorhandler(422)
    def handle_unprocessable_error(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable error"
        }), 422

    @app.errorhandler(500)
    def handle_unexpected_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Unexpected server error"
        }), 500

    return app
