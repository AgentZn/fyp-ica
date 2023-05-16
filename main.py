from flask import Flask, render_template, request, url_for, redirect
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
#from cassandra.cluster import Cluster
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#cluster = Cluster(['<cassandra_host>'], port=7000)
#session_db = cluster.connect('<keyspace_name>')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    if user_id is None:
        return None
    return User.query.get(int(user_id))



class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')    

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
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Retrieve user data from the database
        result = session_db.execute(
            "SELECT * FROM users WHERE username = %s", (username,))
        user = result.one()

        # Check if user exists and password is correct
        if user is None or not check_password_hash(user.password, password):
            return render_template('login.html', error='Invalid credentials')

        # Set session variables and redirect to the homepage
        session['username'] = user.username
        session['logged_in'] = True
        return redirect(url_for('home'))

    return render_template('login.html')



@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/logout')
def logout():
    # Clear session variables and redirect to the homepage
    session.clear()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if user already exists
        result = session_db.execute(
            "SELECT * FROM users WHERE username = %s", (username,))
        if result.one() is not None:
            return render_template('signup.html', error='User already exists')

        # Hash password and store user data in the database
        hashed_password = generate_password_hash(password)
        session_db.execute(
            """
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
            """,
            (username, email, hashed_password)
        )

        # Set session variables and redirect to the homepage
        session['username'] = username
        session['logged_in'] = True
        return redirect(url_for('home'))

    return render_template('signup.html')


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500
    
if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
    















