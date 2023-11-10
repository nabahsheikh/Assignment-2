from flask import Flask, request,jsonify,session
from email_validator import validate_email, EmailNotValidError
import mysql.connector
app = Flask(__name__)
app.secret_key = '\x8az"\x1f\x13\xcd\x99h\xf6\x11-_\x87\xe6\x98\x1dn_\x15\x1a\xdd\xfb\xa3I'

conn = mysql.connector.connect(host='localhost', password='root', user ='root',database = 'task')
cursor = conn.cursor()


def is_valid_email(email):
    try:
        v = validate_email(email)
        return True
    except EmailNotValidError as e:
        print(str(e))
        return False
    
@app.route('/register', methods = ['POST'])
def register_user():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not is_valid_email(email):
        return {'message': 'Email is not valid.'}, 400

    cursor.execute("SELECT * FROM user WHERE email = %s", [email])
    result = cursor.fetchone()

    if result:
        return {'message': 'Email already exists.'}, 400
    
    cursor.execute("INSERT INTO user(username, email, password) VALUES(%s, %s, %s)",
                (username, email, password))

    conn.commit()

    return {'message': 'User registered successfully!'}, 201
    
@app.route('/login',methods = ['POST'])
def user_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    cursor.execute("SELECT * from user where email = %s and password = %s",[email,password])
    result = cursor.fetchone()
    if result:
        session['userid'] = result[0]
        return {'message': "Login succefully!"},200
    else:
        return {'message':"Email or password is incorrect, Try again"},401

@app.route('/create-post',methods = ['POST'])
def create_post():
    if 'userid' not in session:
        return{"message":'User is not logged in'},401
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    userid = session['userid']
    cursor.execute("INSERT INTO post(title,content,userId) VALUES(%s,%s,%s)",(title,content,userid))
    conn.commit()

    return{'message':"post created successfully!"},201


@app.route('/comment',methods=['POST'])
def create_comment():
    if 'userid' not in session:
        return {'message': 'User is not logged in.'}, 401

    data = request.get_json()
    content = data.get('content')
    postId = data.get('postid')
    userId = session['userid']

    cursor.execute("INSERT INTO comments(content, postid, userid) VALUES(%s, %s, %s)",
                (content, postId, userId))
    conn.commit()

    return {'message': 'Comment created successfully!'}, 201

if __name__ == '__main__':
    app.run(debug=True)

