from flask import Flask, jsonify, render_template, request
from flask_cors import CORS, cross_origin
import pymysql
from flaskext.mysql import MySQL
# import json
from flask import make_response
# from flasgger import
from flask import Flask, request
from flask_cors import CORS
import pymysql
from flaskext.mysql import MySQL
from flasgger import Swagger
import requests
import json
import jwt
import datetime
# from flask_swagger_ui import get_swaggerui_blueprint


app = Flask(__name__)
CORS(app)

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'gopal123'
app.config['MYSQL_DATABASE_DB'] = 'flask_dv_survey'

mysql = MySQL()
mysql.init_app(app)

swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "SURVEY",
        "description": "API for SURVEY.",
        "version": "0.0.1"
    },
    "schemes": [
        "http"
    ],

    "tags": [
        {
            "name": "User Login",
            "description": "Operations related to Login"
        },
        {
            "name": "User",
            "description": "Operations related to User"
        },
        {
            "name": "Survey Result",
            "description": "Operations related to Survey Result"
        },
        {
            "name": "Survey Data",
            "description": "Operations related to Survey Data"
        },
        {
            "name": "Oauth 2.0",
            "description": "Operations related to Oauth"
        },
        {
            "name": "Contact",
            "description": "Operations related to Contact"
        },
        {
            "name": "Custom field",
            "description": "Operations related to Custom field"
        },
        {
            "name": "Custom value",
            "description": "Operations related to Custom value"
        },
    ],
    "externalDocs": {
        "url": "http://localhost:5000/apispec_1.json"
    },
    "swaggerUi": {
        "configUrl": "/swagger-config.json"
    }
})

#--------------------------------home page--------------------------------
@app.route("/")
def index():
    return render_template('index.html')


# --------------------------------------USER OPERATIONS---------------------------------------------------

@app.route('/user/add-user', methods=['POST'])
def create_user():
    """
    Add a new user to the database
    ---
    tags:
      - User
    parameters:
      - name: name
        in: formData
        type: string
        required: true
        description: User crud
      - name: email
        in: formData
        type: string
        required: true
        description: User's email
      - name: password
        in: formData
        type: string
        required: true
        description: User's password
    responses:
        200:
            description: User added successfully
        400:
            description: Invalid request
        409:
            description: User with email already exists
        500:
            description: Internal server error
    """
    try:
        status = False
        data = []
        user = request.form or request.json
        name = user['name']
        email = user['email']
        password = user['password']

        if name and email and password and request.method == 'POST':
            con = mysql.connect()
            cur = con.cursor(pymysql.cursors.DictCursor)

            # Check if user already exists in database
            sqlQuery = "SELECT * FROM users WHERE email = %s"
            bindData = (email,)
            cur.execute(sqlQuery, bindData)
            result = cur.fetchone()

            if result:
                # User already exists, return an error response
                message = 'User with email {} already exists'.format(email)
                status_code = 409  # HTTP status code for same record
            else:
                # User does not exist, insert a new record
                sqlQuery = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                bindData = (name, email, password)
                cur.execute(sqlQuery, bindData)
                con.commit()
                status = True
                data.append({
                    'name': name,
                    'email': email,
                    'password': password
                })
                message = 'User added successfully'
                status_code = 200
        else:
            message = 'Invalid request'
            status_code = 400  # HTTP status code for bad request
    except Exception as e:
        message = 'Error: {}'.format(str(e))
        status_code = 500  # HTTP status code for internal server error
    finally:
        cur.close()
        con.close()

    response = {
        'status': status,
        'status_code': status_code,
        'message': message,
        'data': data
    }
    return jsonify(response)

# according to given code pls implement swagger in given code


@app.route('/user/lists')
def get_users():
    """
    Get a list of users
    ---
    tags:
      - User
    responses:
      200:
        description: A list of users
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            status_code:
              type: integer
              example: 200
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  name:
                    type: string
                    example: John Doe
                  email:
                    type: string
                    example: john.doe@example.com
                  password:
                    type: string
                    example: abcdefg
    """
    try:
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT id, name, email, password FROM users")
        userrow = cur.fetchall()
        data = {'status': 'success', 'status_code': 200, 'data': userrow}
        return jsonify(data)
    except Exception as e:
        print(e)
        response = jsonify({
            'status': 'false',
            'status_code': 500,
            'message': 'Server error'
        })
        return response
    finally:
        cur.close()
        con.close()


@app.route('/user/details/<int:id>')
def user_id(id):
    """
    Get details of a user
    ---
    tags:
      - User
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID of the user
    responses:
      200:
        description: Details of the user
        schema:
          type: object
          properties:
            status:
              type: boolean
              example: true
            status_code:
              type: integer
              example: 200
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  name:
                    type: string
                    example: John Doe
                  email:
                    type: string
                    example: john.doe@example.com
                  password:
                    type: string
                    example: abcdefg
      404:
        description: User not found
        schema:
          type: object
          properties:
            status:
              type: boolean
              example: false
            status_code:
              type: integer
              example: 404
            data:
              type: array
              items: {}
    """
    try:
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute(
            "SELECT id, name, email, password FROM users WHERE id = %s", id)
        userrow = cur.fetchone()
        if userrow:
            data = [userrow]
            status = True
            status_code = 200
        else:
            data = []
            status = False
            status_code = 404
        response = jsonify({
            'status': status,
            'status_code': status_code,
            'data': data
        })
        return response
    except Exception as e:
        print(e)
        response = jsonify({
            'status': False,
            'status_code': 500,
            'message': 'Server error'
        })
        return response
    finally:
        cur.close()
        con.close()


@app.route('/user/edit-user/<int:id>', methods=['PUT'])
def update_user(id):
    """
        Update user details.

        This API updates the details of a user identified by their ID.

        ---
        tags:
            - User

        parameters:
          - name: id
            in: path
            description: ID of the user to update
            required: true
            schema:
              type: integer
          - name: name
            in: formData
            type: string
            description: User's name
            required: true
          - name: email
            in: formData
            type: string
            description: User's email address
            required: true
          - name: password
            in: formData
            type: string
            description: User's password
            required: true
        responses:
          200:
            description: User updated successfully
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: success
                status_code:
                  type: integer
                  example: 200
                message:
                  type: string
                  example: User updated successfully
                user:
                  $ref: '#/definitions/User'
          401:
            description: Unauthorized
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: false
                status_code:
                  type: integer
                  example: 401
                message:
                  type: string
                  example: Unauthorized
          404:
            description: User not found
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: false
                status_code:
                  type: integer
                  example: 404
                message:
                  type: string
                  example: User not found
          422:
            description: Validation error
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: false
                status_code:
                  type: integer
                  example: 422
                message:
                  type: string
                  example: Validation error
        """
    # cur = None
    try:

        user = request.form or request.json
        name = user['name']
        email = user['email']
        password = user['password']

        if name and email and password and request.method == 'PUT':
            con = mysql.connect()
            cur = con.cursor(pymysql.cursors.DictCursor)
            # Check if user exists in the database
            cur.execute("SELECT * FROM users WHERE id = %s", id)
            result = cur.fetchone()
            if not result:
                # User not found, return error response
                response = jsonify({
                    'status': 'false',
                    'status_code': 404,
                    'message': 'User not found'
                })
                return response

            # Update the user details
            sqlQuery = "UPDATE users SET name = %s, email = %s, password = %s WHERE id = %s"
            bindData = (name, email, password, id)
            cur.execute(sqlQuery, bindData)
            con.commit()
            response = jsonify({
                'status': 'success',
                'status_code': 200,
                'message': 'User updated successfully',
                'user': {
                    'name': name,
                    'email': email,
                    'password': password
                }
            })
            return response
        else:
            # Bad request, return error response
            response = jsonify({
                'status': 'false',
                'status_code': 400,
                'message': 'Bad request'
            })
            return response
    except Exception as e:
        # Server error, return error response
        print(e)
        response = jsonify({
            'status': 'false',
            'status_code': 500,
            'message': 'Server error'
        })
        return response
    finally:
        cur.close()
        con.close()


@app.route("/user/destroy-user/<int:id>", methods=['DELETE'])
def delete_user(id):
    """
    Deletes a user from the database by ID
    ---
    tags:
      - User
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the user to delete
    responses:
      200:
        description: User deleted successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            status_code:
              type: integer
              example: 200
            message:
              type: string
              example: "User deleted successfully"
            user:
              type: object
              properties:
                name:
                  type: string
                  example: "John"
                email:
                  type: string
                  example: "john@example.com"
                password:
                  type: string
                  example: "mypassword"
      400:
        description: User not found
        schema:
          type: object
          properties:
            status:
              type: string
              example: "false"
            status_code:
              type: integer
              example: 400
            message:
              type: string
              example: "User not found"
    """
    try:
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE id = %s", (id,))
        user = cur.fetchone()
        if user:
            name = user['name']
            email = user['email']
            password = user['password']
            cur.execute("DELETE FROM users WHERE id = %s", (id,))
            con.commit()
            response = {
                'status': 'success',
                'status_code': 200,
                'message': 'User deleted successfully',
                'user': {
                    'name': name,
                    'email': email,
                    'password': password
                }
            }
            return jsonify(response)
        else:
            # Bad request, return error response
            response = {
                'message': 'User not found',
                'status': 'false',
                'status_code': 400
            }
            return jsonify(response)
    except Exception as e:
        print(e)
        response = {
            'status': 'false',
            'status_code': 500,
            'message': 'Server error'
        }
        return jsonify(response)
    finally:
        cur.close()
        con.close()


# ----------------- LOGIN API for USER-----------------------------


@app.route('/user/login', methods=['POST'])
def login_user():
    """
    Login a user
    ---
    tags:
      - User Login
    parameters:
      - name: email
        in: formData
        type: string
        required: true
        description: Email of the user
      - name: password
        in: formData
        type: string
        required: true
        description: Password of the user
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            status:
              type: boolean
              example: true
            status_code:
              type: integer
              example: 200
            message:
              type: string
              example: Login successful
            data:
              type: object
              properties:
                email:
                  type: string
                  example: john.doe@example.com
                password:
                  type: string
                  example: abcdefg
      422:
        description: Incorrect details provided
        schema:
          type: object
          properties:
            status:
              type: boolean
              example: false
            status_code:
              type: integer
              example: 422
            message:
              type: string
              example: Please Enter Correct Details
            errors:
              type: object
              properties:
                email:
                  type: array
                  items:
                    type: string
                  example: ['The email field is required.']
                password:
                  type: array
                  items:
                    type: string
                  example: ['The password field is required.',
                      'Invalid password.']
    """
    try:
        status = False
        data = {}
        user = request.form or request.json
        email = user.get('email')
        password = user.get('password')

        if not email and not password:
            message = 'Please Enter Correct Details'
            status_code = 422
            data['errors'] = {
                'email': ['The email field is required.'],
                'password': ['The password field is required.']
            }
        elif not email:
            message = 'Please Enter Correct Details'
            status_code = 422
            data['errors'] = {
                'email': ['The email field is required.']
            }
        elif not password:
            message = 'Please Enter Correct Details'
            status_code = 422
            data['errors'] = {
                'password': ['The password field is required.']
            }
        else:
            con = mysql.connect()
            cur = con.cursor(pymysql.cursors.DictCursor)

            # Check if user already exists in database
            sqlQuery = "SELECT * FROM users WHERE email = %s"
            bindData = (email,)
            cur.execute(sqlQuery, bindData)
            result = cur.fetchone()

            if result:
                # Check if the password matches
                if password == result['password']:
                    token= jwt.encode({'user':result['email'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)},'thesecretkey54321')
                    status = True
                    data['email'] = result['email']
                    data['password'] = result['password']
                    data['token'] = token
                    data['id'] = result['id']
                    message = 'Login successful'
                    status_code = 200
                else:
                    message = 'Please Enter Correct Details'
                    status_code = 422
                    data['errors'] = {
                        'password': ['Invalid password.']
                    }
            else:
                message = 'Please Enter Correct Details'
                status_code = 422
                data['errors'] = {
                    'email': ['User not found.']
                }

            cur.close()
            con.close()

    except Exception as e:
        message = 'Error: {}'.format(str(e))
        status_code = 500
        data['errors'] = {
            'message': [message]
        }

    response_data = {
        'status': status,
        'status_code': status_code,
        'message': message,
        'data': data
    }
    response = make_response(json.dumps(response_data), status_code)
    response.headers['Content-Type'] = 'application/json'
    return response


# -#------------------ USER operation ENDS------------------------------------------------------


# ---------------------------SURVEY DATA API--------------------------------------------------------

@app.route('/survey/add-survey', methods=['POST'])
def create_survey():
    """
    Add a new survey.
    ---
    tags:
      - Survey Data
    parameters:
      - name: survey_data
        in: formData
        type: string
        required: true
        description: Survey data
      - name: user_id
        in: formData
        type: integer
        required: true
        description: User ID
      - name: created_by
        in: formData
        type: string
        required: true
        description: Created By
    responses:
      200:
        description: Survey added successfully
        schema:
          type: object
          properties:
            status:
              type: boolean
              default: true
            status_code:
              type: integer
              default: 200
            message:
              type: string
              default: "Survey added successfully"
            data:
              type: array
              items:
                type: object
                properties:
                  survey_data:
                    type: string
                  user_id:
                    type: integer
                  created_by:
                    type: string
      400:
        description: Invalid request
        schema:
          type: object
          properties:
            status:
              type: boolean
              default: false
            status_code:
              type: integer
              default: 400
            message:
              type: string
              default: "Invalid request"
      409:
        description: Data with user ID already exists
        schema:
          type: object
          properties:
            status:
              type: boolean
              default: false
            status_code:
              type: integer
              default: 409
            message:
              type: string
              default: "Data with user ID already exists"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            status:
              type: boolean
              default: false
            status_code:
              type: integer
              default: 500
            message:
              type: string
              default: "Error: {error_message}"
    """

    try:
        status = False
        data = []
        json_data = request.form or request.json
        survey_data = json_data['survey_data']
        user_id = json_data['user_id']
        created_by = json_data['created_by']

        if survey_data and user_id and created_by and request.method == 'POST':
            con = mysql.connect()
            cur = con.cursor(pymysql.cursors.DictCursor)

            # Check if user already exists in database
            sqlQuery = "SELECT * FROM json_data WHERE user_id = %s"
            bindData = (user_id,)
            cur.execute(sqlQuery, bindData)
            result = cur.fetchone()

            if result:
                # User already exists, return an error response
                message = 'data with user_id {} already exists'.format(
                    user_id)
                status_code = 409  # HTTP status code for same record
            else:
                # User does not exist, insert a new record
                sqlQuery = "INSERT INTO json_data (survey_data, user_id, created_by) VALUES (%s, %s, %s)"
                bindData = (survey_data, user_id, created_by)
                cur.execute(sqlQuery, bindData)
                con.commit()
                status = True
                data.append({
                    'survey_data': survey_data,
                    'user_id': user_id,
                    'created_by': created_by
                })
                message = 'survey_data added successfully'
                status_code = 200
        else:
            message = 'Invalid request'
            status_code = 400  # HTTP status code for bad request

    except Exception as e:
        message = 'Error: {}'.format(str(e))
        status_code = 500  # HTTP status code for internal server error
        cur = None
        con = None
    finally:
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()

    response = {'status': status, 'status_code': status_code,
                'message': message, 'data': data}
    return jsonify(response)


@app.route('/survey/fetch-survey/list', methods=['GET'])
def get_survey_data():
    """
    Retrieve all survey data from the database.
    ---
    tags:
      - Survey Data
    responses:
      200:
        description: survey data retrieved successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: boolean
                  description: Indicates whether the operation was successful
                  example: true
                status_code:
                  type: integer
                  description: HTTP status code for the response
                  example: 200
                message:
                  type: string
                  description: A message describing the result of the operation
                  example: 'survey data retrieved successfully'
                data:
                  type: array
                  description: An array of survey data
                  items:
                    type: object
                    properties:
                      survey_data:
                        type: string
                        description: Survey data
                        example: '{"question1": "Answer 1", "question2": "Answer 2"}'
                      user_id:
                        type: integer
                        description: The ID of the user who created the survey
                        example: 1
                      created_by:
                        type: string
                        description: The name of the user who created the survey
                        example: 'John Doe'
      500:
        description: An error occurred while retrieving survey data from the database
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: boolean
                  description: Indicates whether the operation was successful
                  example: false
                status_code:
                  type: integer
                  description: HTTP status code for the response
                  example: 500
                message:
                  type: string
                  description: A message describing the result of the operation
                  example: 'Error: database connection failed'
                data:
                  type: array
                  description: An empty array
                  items: {}
    """
    try:
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)

        # Retrieve all survey data from the database
        cur.execute("SELECT * FROM json_data")
        rows = cur.fetchall()

        data = []
        for row in rows:
            data.append(row)

        status = True
        message = 'survey data retrieved successfully'
        status_code = 200

    except Exception as e:
        message = 'Error: {}'.format(str(e))
        status_code = 500  # HTTP status code for internal server error
        status = False
        data = []

    finally:
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()

    response = {'status': status, 'status_code': status_code,
                'message': message, 'data': data}
    return jsonify(response)


@app.route('/survey/fetch-survey/<int:id>')
def survey_id(id):
    """
    This endpoint returns survey data for a given survey ID.
    ---
    tags:
      - Survey Data
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the survey to retrieve.
    responses:
      200:
        description: Survey data retrieved successfully.
        schema:
          type: object
          properties:
            status:
              type: boolean
              description: Indicates whether the request was successful.
            status_code:
              type: integer
              description: The HTTP status code of the response.
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: The ID of the survey.
                  survey_data:
                    type: string
                    description: The survey data.
                  user_id:
                    type: integer
                    description: The ID of the user who created the survey.
                  created_by:
                    type: string
                    description: The name of the user who created the survey.
      404:
        description: Survey not found.
        schema:
          type: object
          properties:
            status:
              type: boolean
              description: Indicates whether the request was successful.
            status_code:
              type: integer
              description: The HTTP status code of the response.
            data:
              type: array
              items:
                type: object
                properties: {}
            message:
              type: string
              description: The error message.
      500:
        description: Server error.
        schema:
          type: object
          properties:
            status:
              type: boolean
              description: Indicates whether the request was successful.
            status_code:
              type: integer
              description: The HTTP status code of the response.
            message:
              type: string
              description: The error message.
    """
    try:
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute(
            "SELECT id, survey_data , user_id , created_by FROM json_data WHERE id = %s", id)
        userrow = cur.fetchone()
        if userrow:
            data = [userrow]
            status = True
            status_code = 200
        else:
            data = []
            status = False
            message = "survey_data not found"
            status_code = 404
        response = jsonify({
            'status': status,
            'status_code': status_code,
            'data': data,
            'message': message
        })
        return response
    except Exception as e:
        print(e)
        response = jsonify({
            'status': 'false',
            'status_code': 500,
            'message': 'Server error'
        })
        return response
    finally:
        cur.close()
        con.close()


@app.route('/survey/update-survey/<int:id>', methods=['PUT'])
def update_survey(id):
    """
    Update survey data

    ---
    tags:
      - Survey Data
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID of survey to update
      - name: survey_data
        in: formData
        type: string
        required: true
        description: Survey data to update
      - name: user_id
        in: formData
        type: string
        required: true
        description: User ID associated with survey
      - name: created_by
        in: formData
        type: string
        required: true
        description: Creator of the survey
    responses:
      200:
        description: Survey data updated successfully
      400:
        description: Bad request
      404:
        description: User not found
      500:
        description: Server error
    """
    try:
        status = False
        data = []
        json_data = request.form or request.json
        survey_data = json_data['survey_data']
        user_id = json_data['user_id']
        created_by = json_data['created_by']

        if survey_data and user_id and created_by and request.method == 'PUT':
            con = mysql.connect()
            cur = con.cursor(pymysql.cursors.DictCursor)

            # Check if survey exists in the database
            cur.execute("SELECT * FROM json_data WHERE id = %s", id)
            result = cur.fetchone()

            if not result:
                # Survey not found, return error response
                response = jsonify({
                    'status': False,
                    'status_code': 404,
                    'message': 'Survey not found'
                })
                return response

            # Update the survey details
            sqlQuery = "UPDATE json_data SET survey_data = %s , user_id= %s ,created_by = %s WHERE id = %s"
            bindData = (survey_data, user_id, created_by, id)
            cur.execute(sqlQuery, bindData)
            con.commit()

            status = True
            data.append({'survey_data': survey_data,
                        'user_id': user_id, 'created_by': created_by})
            message = 'Survey data updated successfully'
            status_code = 200

        else:
            # Bad request, return error response
            message = 'Bad request'
            status_code = 400

        response = {'status': status, 'status_code': status_code,
                    'message': message, 'data': data}
        return jsonify(response)

    except Exception as e:
        # Server error, return error response
        print(e)
        message = 'Server error'
        status_code = 500
        response = {'status': False, 'status_code': status_code,
                    'message': message, 'data': data}
        return jsonify(response)

    finally:
        cur.close()
        con.close()


@app.route('/survey/destroy-survey/<int:id>', methods=['DELETE'])
def delete_survey(id):
    """
    Delete a survey by ID

    ---
    tags:
      - Survey Data
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID of the survey to be deleted
    responses:
      200:
        description: Survey data deleted successfully
        schema:
          type: object
          properties:
            status:
              type: boolean
              default: true
            status_code:
              type: integer
              default: 200
            message:
              type: string
              default: Survey data deleted successfully
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  # Add other properties of the survey here
      404:
        description: User not found
        schema:
          type: object
          properties:
            status:
              type: boolean
              default: false
            status_code:
              type: integer
              default: 404
            message:
              type: string
              default: survey not found
    """
    try:
        status = False
        data = []
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)

        # Check if user exists in the database
        cur.execute("SELECT * FROM json_data WHERE id = %s", id)
        result = cur.fetchone()

        if not result:
            # User not found, return error response
            response = jsonify({
                'status': False,
                'status_code': 404,
                'message': 'User not found'
            })
            return response

        # Delete the user from the database
        cur.execute("DELETE FROM json_data WHERE id = %s", id)
        con.commit()

        status = True
        message = 'Survey data deleted successfully'
        status_code = 200

        response = {'status': status, 'status_code': status_code,
                    'message': message, 'data': data}
        return jsonify(response)

    except Exception as e:
        # Server error, return error response
        print(e)
        message = 'Server error'
        status_code = 500
        response = {'status': False, 'status_code': status_code,
                    'message': message, 'data': data}
        return jsonify(response)

    finally:
        cur.close()
        con.close()

# -#---------------SURVEY DATA API ENDS-----------------------------------------------------


# ---------------SURVEY_RESULT Api ---------------------------------------------------------


@app.route('/survey/result/add-survey', methods=['POST'])
def create_survey_result():
    """
    Add a survey result
    ---
    tags:
      - Survey Result
    parameters:
      - name: survey_id
        in: formData
        type: integer
        required: true
        description: The ID of the survey being added
      - name: user_id
        in: formData
        type: integer
        required: true
        description: The ID of the user associated with the survey
      - name: survey_result
        in: formData
        type: string
        required: true
        description: The result of the survey
    responses:
      200:
        description: Successfully added survey result
      400:
        description: Invalid request
      409:
        description: Survey result with user_id already exists
      500:
        description: Error while processing the request
    """
    try:
        status = False
        data = []
        user = request.form or request.json
        survey_id = user['survey_id']
        user_id = user['user_id']
        survey_result = user['survey_result']

        if survey_id and user_id and survey_result and request.method == 'POST':
            con = mysql.connect()
            cur = con.cursor(pymysql.cursors.DictCursor)

            # Check if user already exists in database
            sqlQuery = "SELECT * FROM survey_result WHERE user_id = %s"
            bindData = (user_id,)
            cur.execute(sqlQuery, bindData)
            result = cur.fetchone()

            if result:
                # User already exists, return an error response
                message = 'survey_result with user_id {} already exists'.format(
                    user_id)
                status_code = 409  # HTTP status code for same record
            else:
                # User does not exist, insert a new record
                sqlQuery = "INSERT INTO survey_result (survey_id, user_id, survey_result) VALUES (%s, %s, %s)"
                bindData = (survey_id, user_id, survey_result)
                cur.execute(sqlQuery, bindData)
                con.commit()
                status = True
                data.append({
                    'survey_id': survey_id,
                    'user_id': user_id,
                    'survey_result': survey_result
                })
                message = 'survey_result added successfully'
                status_code = 200
        else:
            message = 'Invalid request'
            status_code = 400  # HTTP status code for bad request
    except Exception as e:
        message = 'Error: {}'.format(str(e))
        status_code = 500  # HTTP status code for internal server error
    finally:
        cur.close()
        con.close()

    response = {
        'status': status,
        'status_code': status_code,
        'message': message,
        'data': data
    }
    return jsonify(response)


@app.route('/survey/result/fetch-survey/lists', methods=['GET'])
def get_all_survey_results():
    """
    Returns a list of all survey results.

    ---
    tags:
      - Survey Result
    responses:
      200:
        description: A list of all survey results
        schema:
          type: object
          properties:
            status:
              type: boolean
              default: true
            status_code:
              type: integer
              default: 200
            message:
              type: string
              default: Survey results retrieved successfully
            data:
              type: array
              items:
                type: object
                properties:
                  survey_id:
                    type: integer
                  user_id:
                    type: integer
                  survey_result:
                    type: string
    """
    try:
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)

        # Retrieve all survey results
        sqlQuery = "SELECT * FROM survey_result"
        cur.execute(sqlQuery)
        results = cur.fetchall()

        data = []
        for result in results:
            data.append({
                'survey_id': result['survey_id'],
                'user_id': result['user_id'],
                'survey_result': result['survey_result']
            })

        message = 'Survey_results retrieved successfully'
        status_code = 200
        status = True

    except Exception as e:
        message = 'Error: {}'.format(str(e))
        status_code = 500  # HTTP status code for internal server error
        status = False

    finally:
        cur.close()
        con.close()

    response = {
        'status': status,
        'status_code': status_code,
        'message': message,
        'data': data
    }

    return jsonify(response)


@app.route('/survey/result/fetch-survey/<int:id>')
def get_survey_result(id):
    """
    Retrieve a survey result by ID

    ---
    tags:
      - Survey Result
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the survey result to retrieve
    responses:
      200:
        description: A survey result object
        schema:
          type: object
          properties:
            survey_id:
              type: integer
              description: The ID of the survey
            user_id:
              type: integer
              description: The ID of the user who took the survey
            survey_result:
              type: string
              description: The survey result data
      404:
        description: The requested survey result was not found
    """
    try:
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute(
            "SELECT id, survey_id, user_id, survey_result FROM survey_result WHERE id = %s", id)
        userrow = cur.fetchone()
        if userrow:
            data = [userrow]
            status = True
            status_code = 200
            message = "Success"
        else:
            data = []
            status = False
            status_code = 404
            message = "survey_result not found"
        response = jsonify({
            'status': status,
            'status_code': status_code,
            'data': data,
            'message': message
        })
        return response
    except Exception as e:
        print(e)
        response = jsonify({
            'status': False,
            'status_code': 500,
            'message': 'Server error'
        })
        return response
    finally:
        cur.close()
        con.close()


@app.route('/survey/result/update-survey/<int:id>', methods=['PUT'])
def edit_survey_result(id):
    """
    Edit survey result.
    ---
    tags:
      - Survey Result

    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - name: survey_id
        in: formData
        type: integer
        required: true
      - name: user_id
        in: formData
        type: integer
        required: true
      - name: survey_result
        in: formData
        type: string
        required: true
    responses:
      200:
        description: Success
        schema:
          properties:
            status:
              type: boolean
            status_code:
              type: integer
            message:
              type: string
            data:
              properties:
                survey_id:
                  type: integer
                user_id:
                  type: integer
                survey_result:
                  type: string
      400:
        description: Bad request
        schema:
          properties:
            status:
              type: boolean
            status_code:
              type: integer
            message:
              type: string
            data:
              type: array
              items: {}
      404:
        description: User not found
        schema:
          properties:
            status:
              type: boolean
            status_code:
              type: integer
            message:
              type: string
            data:
              type: array
              items: {}

    """
    try:
        status = False
        data = []
        json_data = request.form or request.json
        survey_id = json_data['survey_id']
        user_id = json_data['user_id']
        survey_result = json_data['survey_result']

        if survey_id and user_id and survey_result and request.method == 'PUT':
            con = mysql.connect()
            cur = con.cursor(pymysql.cursors.DictCursor)

            # Check if user exists in the database
            cur.execute("SELECT * FROM survey_result WHERE id = %s", id)
            result = cur.fetchone()

            if not result:
                # User not found, return error response
                response = jsonify({
                    'status': False,
                    'status_code': 404,
                    'message': 'survey_result not found'
                })
                return response

            # Update the user details
            sqlQuery = "UPDATE survey_result SET survey_id = %s , user_id = %s , survey_result = %s WHERE id = %s"
            bindData = (survey_id, user_id, survey_result, id)
            cur.execute(sqlQuery, bindData)
            con.commit()

            status = True
            data.append({'survey_id': survey_id, 'user_id': user_id,
                        'survey_result': survey_result})
            message = 'Survey_result data updated successfully'
            status_code = 200

        else:
            # Bad request, return error response
            message = 'Bad request'
            status_code = 400

        response = {'status': status, 'status_code': status_code,
                    'message': message, 'data': data}
        return jsonify(response)

    except Exception as e:
        # Server error, return error response
        print(e)
        message = 'Server error'
        status_code = 500
        response = {'status': False, 'status_code': status_code,
                    'message': message, 'data': data}
        return jsonify(response)

    finally:
        cur.close()
        con.close()


@app.route('/survey/result/destroy-survey/<int:id>', methods=['DELETE'])
def destroy_survey_result(id):
    """
    Deletes a survey result from the database.

    ---
    tags:
      - Survey Result

    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the survey result to delete.
    responses:
      200:
        description: Survey data deleted successfully.
        schema:
          type: object
          properties:
            status:
              type: boolean
              description: Whether the operation was successful.
              example: true
            status_code:
              type: integer
              description: The HTTP status code.
              example: 200
            message:
              type: string
              description: A message describing the result of the operation.
              example: Survey data deleted successfully
            data:
              type: array
              description: An array of survey results.
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: The ID of the survey result.
                    example: 1
                  question:
                    type: string
                    description: The question asked in the survey.
                    example: What is your favorite color?
                  answer:
                    type: string
                    description: The answer given in the survey.
                    example: Blue
      404:
        description: User not found.
        schema:
          type: object
          properties:
            status:
              type: boolean
              description: Whether the operation was successful.
              example: false
            status_code:
              type: integer
              description: The HTTP status code.
              example: 404
            message:
              type: string
              description: A message describing the result of the operation.
              example: User not found
            data:
              type: array
              description: An empty array.
              items:
                type: object
                properties: {}
      500:
        description: Server error.
        schema:
          type: object
          properties:
            status:
              type: boolean
              description: Whether the operation was successful.
              example: false
            status_code:
              type: integer
              description: The HTTP status code.
              example: 500
            message:
              type: string
              description: A message describing the result of the operation.
              example: Server error
            data:
              type: array
              description: An empty array.
              items:
                type: object
                properties: {}
    """
    try:
        status = False
        data = []
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)

        # Check if user exists in the database
        cur.execute("SELECT * FROM survey_result WHERE id = %s", id)
        result = cur.fetchone()

        if not result:
            # User not found, return error response
            response = jsonify({
                'status': False,
                'status_code': 404,
                'message': 'survey_result not found'
            })
            return response

        # Delete the user from the database
        cur.execute("DELETE FROM survey_result WHERE id = %s", id)
        con.commit()

        status = True
        message = 'Survey_result deleted successfully'
        status_code = 200

        response = {'status': status, 'status_code': status_code,
                    'message': message, 'data': data}
        return jsonify(response)

    except Exception as e:
        # Server error, return error response
        print(e)
        message = 'Server error'
        status_code = 500
        response = {'status': False, 'status_code': status_code,
                    'message': message, 'data': data}
        return jsonify(response)

    finally:
        cur.close()
        con.close()

# -#--------------SURVEY_RESULT ends-------------------------------------------------


# ------------------oauth 2 api start -------------------------------------------------

@app.route('/oauth', methods=['POST'])
def post_data():
    """
     This endpoint retrieves an OAuth token from a mock OAuth server.
     ---
     tags:
       - Oauth 2.0
     requestBody:
       content:
         application/x-www-form-urlencoded:
           schema:
             type: object
             properties:
               client_id:
                 type: string
               client_secret:
                 type: string
               grant_type:
                 type: string
               code:
                 type: string
               refresh_token:
                 type: string
               user_type:
                 type: string
               redirect_uri:
                 type: string
     responses:
       200:
         description: Returns the OAuth token as JSON.
         content:
           application/json:
             schema:
               type: object
               properties:
                 access_token:
                   type: string
                 token_type:
                   type: string
                 expires_in:
                   type: integer
                 refresh_token:
                   type: string
     """
    # Get the request data
    # client_id = request.form.get('client_id')
    # client_secret = request.form.get('client_secret')
    # grant_type = request.form.get('grant_type')
    # code = request.form.get('code')
    # refresh_token = request.form.get('refresh_token')
    # user_type = request.form.get('user_type')
    # redirect_uri = request.form.get('redirect_uri')

    url = "https://stoplight.io/mocks/highlevel/integrations/39582851/oauth/token"

    payload = 'client_id=628d41f442f5e33b3bea5c6b-ldltqbmg&client_secret=7c001689-121d-490a-8956-e0cef1f4bc2e&grant_type=authorization_code&refresh_token=&user_type=Location&redirect_uri=localhost%3A5000%2Foauth%2Fcallback%2Fgohighlevel'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'GCLB=CM6NypyvrfOxrwE; __cf_bm=kaC5qC..uyZOVWil7igPU6B3zxmCBunkqPbDFvL5Mnk-1683087273-0-ARVIqk7une/pjyoWva1g0xUEYtD9Q+2pQVHC5TNYLmk/lMnThqgHBCR37qTPHqBumkuwveUXICnxOSfruRsCzcc='
    }

    response = requests.post(url, headers=headers, data=payload)
    #
    data = response.json()
    return data


# ------------------------------contact api -----------------------------------------------------------

# @app.route('/contacts/<string:contactId>', methods=['GET'])
# def get_contact(contactId):
#     """
#     Get contact information by ID
#     ---
#     tags:
#       - Contact
#     parameters:
#       - name: contactId
#         in: path
#         type: string
#         required: true
#         description: ID of the contact to retrieve
#     responses:
#       200:
#         description: Contact information
#         schema:
#           type: object
#       404:
#         description: Failed to retrieve contact information
#         schema:
#           type: object
#           properties:
#             error:
#               type: string
#     """
#     url = "https://stoplight.io/mocks/highlevel/integrations/39582863/contacts/{contactId}"

#     headers = {
#         "Authorization": "2345",
#         "Version": "2021-07-28",
#         "Accept": "application/json"
#     }

#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:
#         return jsonify(response.json())
#     else:
#         return jsonify({'error': 'Failed to retrieve contact information.'}), response.status_code




@app.route('/contacts', methods=['GET'])
def get_contact():
    """
    Get contact  information by ID
    ---
    tags:
      - Contact
    parameters:
      - name: contactId
        in: query
        type: string
        required: true
        description: ID of the contact to retrieve
      - name: Authorization
        in: header
        type: string
        required: false
        description: Token to authorize the request
    responses:
      200:
        description: contact information retrieve successful
        schema:
          type: object
      401:
        description: Failed to retrieve contact information
        schema:
          type: object
          properties:
            status:
              type: boolean
              example: false
            status_code:
              type: integer
              example: 401
            message:
              type: string
              example: Please Enter Authorization token
            data:
              type: array
              items:
                type: object
                properties:
                  errors:
                    type: object
                    properties:
                      Authorization:
                        type: array
                        items:
                          type: string
                          example: The Authorization token is missing.
      404:
        description: Failed to retrieve contact information
        schema:
          type: object
          properties:
            status:
              type: boolean
              example: false
            status_code:
              type: integer
              example: 500
            message:
              type: string
              example: Unable to retrieve contact.
            data:
              type: array
              items:
                type: object
                properties:
                  errors:
                    type: object
                    properties:
                      Custom fields:
                        type: array
                        items:
                          type: string
                          example: Please check the code and then try again to retrieve the contact

    """
    contactId = request.args.get('contactId')
    if not contactId:
        return jsonify({
            "status": False,
            "status_code": 400,
            "message": "Please provide contactId in query parameters.",
            "data": []
        }), 400

    url = "https://stoplight.io/mocks/highlevel/integrations/39582863/contacts/" + contactId

    #check if the authorization token is provided
    token = request.headers.get('Authorization')
    if token:
        headers = {
            "Authorization": token,
            "Version": "2021-07-28",
            "Accept": "application/json"
        }
    else:
        return jsonify({
            "status": False,
            "status_code": 401,
            "message": "Please Enter Authorization token ",
            "data": [{
                "errors": {
                    "Authorization": [
                        "The Authorization token  is missing."
                    ]
                }
            }]
        }), 401

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return jsonify({'status': True, 'status_code': 200, 'message': 'Contact retrieved successfully', 'data': [response.json()]})
    else:
        return jsonify({'status': False, 'status_code': 500, 'message': 'Unable to retrieve contact .', 'data': [{
            "errors": {
                "Contact ": [
                        "Please check the code and then try again to retrieve the contact"
                        ]
            }
        }]}), 500


@app.route('/contact', methods=['POST'])
def create_contact():

    url = "https://stoplight.io/mocks/highlevel/integrations/39582863/contacts/"

    payload = json.dumps({
        "firstName": "Rosan",
        "lastName": "Deo",
        "name": "Rosan Deo",
        "email": "rosan@deos.com",
        "locationId": "ve9EPM428h8vShlRW1KT",
        "gender": "male",
        "phone": "+1 888-888-8888",
        "address1": "3535 1st St N",
        "city": "Dolomite",
        "state": "AL",
        "postalCode": "35061",
        "website": "https://www.tesla.com",
        "timezone": "America/Chihuahua",
        "dnd": True,
        "dndSettings": {
            "Call": {
                "status": "active",
                "message": "string",
                "code": "string"
            },
            "Email": {
                "status": "active",
                "message": "string",
                "code": "string"
            },
            "SMS": {
                "status": "active",
                "message": "string",
                "code": "string"
            },
            "WhatsApp": {
                "status": "active",
                "message": "string",
                "code": "string"
            },
            "GMB": {
                "status": "active",
                "message": "string",
                "code": "string"
            },
            "FB": {
                "status": "active",
                "message": "string",
                "code": "string"
            }
        },
        "tags": [
            "nisi sint commodo amet",
            "consequat"
        ],
        "customFields": [
            {
                "id": "6dvNaf7VhkQ9snc5vnjJ",
                "field_value": "9039160788"
            }
        ],
        "source": "public api",
        "country": "US",
        "companyName": "DGS VolMAX"
    })
    headers = {
        'Accept': 'application/json',
        'Authorization': '1234',
        'Content-Type': 'application/json',
        'Version': '2021-07-28',
        'Cookie': 'GCLB=CM6NypyvrfOxrwE; __cf_bm=ISVs7Z.ulmgZp4OFGhQNDqrBdFPKM27gwIDZwBGdw5M-1683093221-0-AQbLDKPveU2O6WrFaaMHzpxtKQ3j0O/TJXOCpfF388aytnVXFgU00Rtdr3tcBtjfBizEW37vBih+ij2K8l23z7g='
    }

    response = requests.post(url, headers=headers, data=payload)
    data = response.json()
    return data
    # print(response.text)


# --------------------------custom field api------------------------------------------------------

@app.route('/customfields/<string:customId>', methods=['GET'])
def get_custom_fields(customId):
    """
    Get custom fields information by ID
    ---
    tags:
      - Custom field
    parameters:
      - name: customId
        in: path
        type: string
        required: true
        description: ID of the custom fields to retrieve
    responses:
      200:
        description: custom information
        schema:
          type: object
      404:
        description: Failed to retrieve custom fields information
        schema:
          type: object
          properties:
            error:
              type: string
    """
    url = f"https://stoplight.io/mocks/highlevel/integrations/39582857/locations/ve9EPM428h8vShlRW1KT/customFields/{customId}"
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer 123',
        'Version': '2021-07-28',
        'Cookie': 'GCLB=CM6NypyvrfOxrwE; __cf_bm=ISVs7Z.ulmgZp4OFGhQNDqrBdFPKM27gwIDZwBGdw5M-1683093221-0-AQbLDKPveU2O6WrFaaMHzpxtKQ3j0O/TJXOCpfF388aytnVXFgU00Rtdr3tcBtjfBizEW37vBih+ij2K8l23z7g='
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Unable to retrieve custom fields.'}), 500


# -------------------custom value api--------------------------------------------------

@app.route('/customvalue/<string:customId>', methods=['GET'])
def get_custom_value(customId):
    """
      Get Custom value information by ID
      ---
      tags:
        - Custom value
      parameters:
        - name: customId
          in: path
          type: string
          required: true
          description: ID of the custom value to retrieve
      responses:
        200:
          description: custom value information
          schema:
            type: object
        404:
          description: Failed to retrieve custom value information
          schema:
            type: object
            properties:
              error:
                type: string
      """

    url = f"https://stoplight.io/mocks/highlevel/integrations/39582857/locations/ve9EPM428h8vShlRW1KT/customValues/{customId}"

    payload = {}
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer 123',
        'Version': '2021-07-28',
        'Cookie': 'GCLB=CM6NypyvrfOxrwE; __cf_bm=ISVs7Z.ulmgZp4OFGhQNDqrBdFPKM27gwIDZwBGdw5M-1683093221-0-AQbLDKPveU2O6WrFaaMHzpxtKQ3j0O/TJXOCpfF388aytnVXFgU00Rtdr3tcBtjfBizEW37vBih+ij2K8l23z7g='
    }

    response = requests.get(url, headers=headers, data=payload)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Unable to retrieve custom fields.'}), 500

        # print(response.text)


# @app.route('/create/contacts', methods=['POST'])
# def create_contact():
#     con = None
#     cur = None
#     try:
#         # Get the request data
#         first_name = request.json.get['firstName']
#         last_name = request.json.get['lastName']
#         name = request.json.get['name']
#         email = request.json.get['email']
#         location_id = request.json.get['locationId']
#         gender = request.json.get['gender']
#         phone = request.json.get['phone']
#         address1 = request.json.get['address1']
#         city = request.json.get['city']
#         state = request.json.get['state']
#         postal_code = request.json.get['postalCode']
#         website = request.json.get['website']
#         timezone = request.json.get['timezone']
#         dnd = request.json.get['dnd']
#         dnd_settings = request.json.get['dndSettings']
#         tags = request.json.get['tags']
#         custom_fields = request.json.get['customFields']
#         source = request.json.get['source']
#         country = request.json.get['country']
#         company_name = request.json.get['companyName']


#         if first_name and last_name and name and email and location_id and gender and phone and address1 and city and state and postal_code and website and timezone and dnd and dnd_settings and tags and custom_fields and source and country and company_name and request.method == 'POST':
#             con = mysql.connect()
#             cur = con.cursor(pymysql.cursors.DictCursor)
#             sqlQuery = "INSERT INTO contacts (first_name, last_name, name, email, location_id, gender, phone, address1, city, state, postal_code, website, timezone, dnd, dnd_settings, tags, custom_fields, source, country, company_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
#             bindData = (first_name, last_name, name, email, location_id, gender, phone, address1, city, state, postal_code, website, timezone, dnd, str(dnd_settings), str(tags), str(custom_fields), source, country, company_name)
#             cur.execute(sqlQuery, bindData)
#             con.commit()
#             status = True
#             data = []
#             data.append({
#                 'first_name': first_name,
#                 'last_name': last_name,
#                 'name': name,
#                 'email': email,
#                 'location_id': location_id,
#                 'gender': gender,
#                 'phone': phone,
#                 'address1': address1,
#                 'city': city,
#                 'state': state,
#                 'postal_code': postal_code,
#                 'website': website,
#                 'timezone': timezone,
#                 'dnd': dnd,
#                 'dnd_settings': dnd_settings,
#                 'tags': tags,
#                 'custom_fields': custom_fields,
#                 'source': source,
#                 'country': country,
#                 'company_name': company_name
#             })
#             message = 'contact added successfully'
#             status_code = 200
#         else:
#             status = False
#             message = 'Invalid request'
#             status_code = 400  # HTTP status code for bad request
#             data = []

#     except Exception as e:
#         message = 'Error: {}'.format(str(e))
#         status_code = 500  # HTTP status code for internal server error
#         status = False
#         data = []

#     finally:
#         if cur:
#           cur.close()
#         if con:
#            con.close()

#     response = {
#         'status': status,
#         'status_code': status_code,
#         'message': message,
#         'data': {}
#     }
#     return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
