import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page-1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'/':{'origin':'*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add(
      'Access-Control-Allow-Headers','Content-Type, Authorization, true')
    response.headers.add(
      'Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')

    return response
    
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    category_dict={category.id: category.type for category in categories}
    if len(category_dict) == 0:
      abort(404)
    return jsonify(
      {
        'success': True,
        'categories': category_dict
      }
    )

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    selection = Question.query.order_by(Question.id).all()
    total_questions = len(selection)
    page_questions = paginate_questions(request, selection)

    categories = Category.query.all()
    category_dict={category.id: category.type for category in categories}

    if len(page_questions) == 0:
      abort(404)

    return jsonify(
      {
        'success': True,
        'questions': page_questions,
        'total_questions': total_questions,
        'categories': category_dict
      }
    )

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    question = Question.query.filter_by(id=id).one_or_none()
    
    if question is None:
      abort(404)
    else:
      try:
        question.delete()
        return jsonify(
          {
            'success': True,
            'deleted': id
          }
        )
      except:
        abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def post_question():
    body = request.get_json()

    question = body.get('question')
    answer = body.get('answer')
    category = body.get('category')
    difficulty = body.get('difficulty')
    

    try:
      question = Question(
        question=question, answer=answer,
        category=category, difficulty=difficulty
        )
      question.insert()

      selection = Question.query.order_by(Question.id).all()
      total_questions=len(selection)
      page_questions = paginate_questions(request, selection)

      return jsonify(
        {
          'success': True,
          'created': question.id,
          'question_created': question.question,
          'questions':page_questions,
          'total_questions':total_questions
        }
      )
    
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  # I've updated QuestionView.js url to use this endpoint instead of /quesions
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm')
    selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
    total_questions = len(selection)
    page_questions = paginate_questions(request, selection)

    return jsonify(
      {
        'success': True,
        'questions': page_questions,
        'total_questions': total_questions
      }
    )

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def get_questions_per_cat(id):
    #check category exists
    category = Category.query.filter_by(id=id).one_or_none()
    if category is None:
      abort(404)
    else:
      selection = Question.query.filter_by(category = category.id).all()
      total_questions = len(selection)
      page_questions = paginate_questions(request, selection)
      
      return jsonify(
        {
          'success': True,
          'questions': page_questions,
          'total_questions': total_questions,
          'current_category': category.type
        }
      )

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
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body = request.get_json()
    previous_questions = body.get('previous_questions')
    quiz_category = body.get('quiz_category')
    
    if ((previous_questions is None) or (quiz_category is None)):
      # print("aborting")
      # print(previous_questions)
      # print(quiz_category)
      abort(400)

    if (quiz_category['id'] == 0):
      questions = Question.query.order_by(func.random())
    else:
      questions = Question.query.filter_by(category=quiz_category['id']).order_by(func.random())

    if questions.first() is None:
      abort(404)
    else:
      question = questions.filter(Question.id.notin_(previous_questions)).first()

    if question is None:
      return jsonify(
        {
          'success': True
        }
      )
    else:
      return jsonify(
        {
          'success': True,
          'question': question.format()
        }
      )
    

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def not_found(error):
    return jsonify(
      {
        'success': False,
        'error': 400,
        'message': 'bad request'
      }
    ), 400


  @app.errorhandler(404)
  def not_found(error):
    return jsonify(
      {
        'success': False,
        'error': 404,
        'message': 'resource not found'
      }
    ), 404

  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify(
      {
        'success': False,
        'error': 405,
        'message': 'method not allowed'
      }
    ), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify(
      {
        'success': False,
        'error': 422,
        'message': 'unprocessable'
      }
    ), 422

  @app.errorhandler(500)
  def server_error(error):
    return jsonify(
      {
        'success': False,
        'error': 500,
        'message': 'server error'
      }
    ), 500
  
  return app

    