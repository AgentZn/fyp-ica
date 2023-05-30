from flask import Flask, render_template, request, url_for, redirect, session as fsession
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from cassandra.query import SimpleStatement
from flask_login import login_required
from flask_session import Session
from cassandra import ConsistencyLevel
from cassandra.policies import DCAwareRoundRobinPolicy


import uuid
import hashlib



app = Flask(__name__)
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'
app.config['SESSION_TYPE'] = 'cassandra'  # You can change the session type based on your requirements
Session(app)
cloud_config= {
  'secure_connect_bundle': 'C:\secure-connect-fyp-ica.zip'
}
auth_provider = PlainTextAuthProvider('RxnkOimyTprpDRaWZyEfWZTz', '5ydlP0.DQvbKjBv-GTt7tWxQnpBk5A+Kg84d3MZojxSNo8wciB+i0RnzYL_MIQgKgpCZEp9PH5Cdhf,s-1mJdEweY9N2vClPu+EqSlfmG1vHuAuw,9eS7k.UzrDOwT8W')
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

row = session.execute("select release_version from system.local").one()
if row:
  print(row[0])
else:
  print("An error occurred.")


@app.route('/sockets')
def pose_sockets():
    return render_template('pose_sockets.html')

@app.route('/tfjs')
def pose_tfjs():
    return render_template('pose_tfjs.html')

@app.route('/push_up')
def count_push_ups():
    return render_template('count_push_ups.html')

@app.route('/sit_up')
def count_sit_ups():
    return render_template('count_sit_ups.html')

# master-minion simultaneous video capturing
@app.route('/')
def home():
    
    return render_template('home.html')

@app.route('/vidmaster')
def vid_master():
    return render_template('video_master.html')

@app.route('/vidminion')
def vid_minion():
    gFaceMode = request.args.get('face')
    gCamPosition = request.args.get('camerapos')
    return render_template('video_minion.html', gFaceMode=gFaceMode,gCamPosition=gCamPosition)   

@app.route('/vidsample')
def vid_sample():
    return render_template('video_sample.html')

@app.route('/vidsampleios')
def vid_sample_ios():
    return render_template('video_sample_ios.html')

# end master-minion simultaneous video capturing

#Team Member pages
@app.route('/member')
def member():
    return render_template('project_member.html')

#About Page
@app.route('/about')
def about():
    return render_template('about.html')

#Contact Page
@app.route('/contact')
def contact():
    return render_template('contact.html')

#Login Page
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

#Validating of credentials
@app.route('/login', methods=['POST'])
def login_post():
    fsession['username'] = request.form.get('username')
    name = fsession['username']
    password = request.form['password']
    login_hash = hashlib.sha1(password.encode()).hexdigest()
    # Perform Cassandra query to validate the credentials
    query = "SELECT * FROM fyp.users WHERE name = %s AND password = %s ALLOW FILTERING"
    result = session.execute(query, (name, login_hash))


    
    if result.one():
        
        # Valid credentials, perform login logic
        return f"Login successful<br><a href='/'>Welcome {name}, Go to the Home Page</a>"
        

    else:
        # Invalid credentials, show error message
        return "Invalid username or password"


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
     # Render the dashboard template with the username
     return render_template('dashboard.html')
    


@app.route('/logout')
def logout():
    
    return redirect(url_for('login'))

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    new_uuid = uuid.uuid4()
    username = request.form['username']
    password = request.form['password']
    user_id = new_uuid
    yob = request.form['yob']
    age = int(request.form['age'])  # Convert age to integer
    
    password_hash = hashlib.sha1(password.encode()).hexdigest()
    # Perform Cassandra query to check if the username already exists
    query = "SELECT * FROM fyp.users WHERE name = %s ALLOW FILTERING"
    result = session.execute(query, (username,))
    
    if result.one():
        return "Username already exists<br><a href='/register'>Please Try Again</a>"
    else:
        # Perform Cassandra query to insert the new user into the users table
        query = "INSERT INTO fyp.users (id, age, name, password, yob) VALUES (%s, %s, %s, %s, %s)"
        session.execute(query, (user_id, age, username, password_hash, yob))
        return "Registration successful<br><a href='/login'>Log In Now</a>"

@app.route('/insert_vid', methods=['POST'])
def insert_video():
    new_rid = uuid.uuid4()
    rid = new_rid
    image = request.files['image']
    image.save("C:/fyp-ica/image/" + image.filename)
    imagedir = "C:/fyp-ica/image/" + image.filename
    video = request.files['video']
    video.save('C:/fyp-ica/video/' + video.filename)
    viddir = "C:/fyp-ica/video/" + video.filename
    query = "INSERT INTO fyp.score (rid, badcount, chart, excount, exercise, goodcount, poseresult, user_id,video) VALUES ($s, $s, $s,$s, $s, $s,$s, $s, $s)"
    session.execute(rid, badcount, imagedir, excount, exercuse, goodcount, poseresult, user_id, viddir)
    return 'Video uploaded successfully'


@app.route('/insert', methods=['POST'])
def insert_record():
    new_rid = uuid.uuid4()
    rid = new_rid
    image = request.files['image']
    image.save("C:/fyp-ica/image/" + image.filename)
    imagedir = "C:/fyp-ica/image/" + image.filename
    query = "INSERT INTO fyp.score (rid, badcount, chart, excount, exercise, goodcount, poseresult, user_id,video) VALUES ($s, $s, $s,$s, $s, $s,$s, $s, NULL)"
    session.execute(rid, badcount, imagedir, excount, exercuse, goodcount, poseresult, user_id)
    return 'Records uploaded successfully'

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500
    
if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=5000)
















