from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import yaml

app = Flask(__name__, static_url_path='/static')

# Set a secret key for your application
app.secret_key = ' '


# Load YAML configuration
with open('database.yaml', 'r') as yaml_file:
    db_config = yaml.load(yaml_file, Loader=yaml.SafeLoader)

# Set SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = db_config['uri'] 
db = SQLAlchemy(app)
CORS(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255),nullable=False)
    
    def __init__(self, email, password):
        self.email = email
        self.set_password(password)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return '%s/%s/%s' % (self.id, self.email, self.password)
    # Survey model definition
class Survey(db.Model):
    __tablename__ = 'surveys'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    tel = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    timing = db.Column(db.String(20), nullable=False)
    other_category = db.Column(db.String(100))
    image_urls = db.Column(db.ARRAY(db.Text)) 

@app.route('/')
def index():
    if 'user_id' in session:
        # User is authenticated, fetch user data if needed
        user_id = session['user_id']
        user = User.query.get(user_id)
        return render_template('home.html', user=user)
    else:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('login'))
   

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Validate credentials (this is a basic example, you should hash passwords securely)
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        # Authentication successful
        session['user_id'] = user.id  # Store user ID in session
        return jsonify({'message': 'Login successful', 'redirect': url_for('index')})
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

# Route to render register.html
@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

# API endpoint for registration
@app.route('/api/register', methods=['POST'])
def api_register():
    email = request.form.get('email')
    password = request.form.get('password')
    confirmPassword = request.form.get('confirmPassword')
    
    # Basic validation (add more as needed)
    if not email or not password or not confirmPassword:
        return jsonify({'error': 'All fields are required'}), 400
    
    if password != confirmPassword:
        return jsonify({'error': 'Passwords do not match'}), 400
    

    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Registration successful', 'redirect': url_for('index')})
@app.route('/survey', methods=['GET'])
def survey():
    # Handle GET request (rendering the form)
    return render_template('survey.html')
@app.route('/api/survey', methods=['POST'])
def api_survey():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        tel = request.form.get('tel')
        address = request.form.get('address')
        city = request.form.get('city')
        pincode = request.form.get('pincode')
        category = request.form.get('category')
        timing = request.form.get('timing')
        other_category = request.form.get('other_category')
        
        image_files = request.files.getlist('image')
        image_urls = []
        for file in image_files:
            # Handle file upload here
            image_urls.append(file.filename)  # Store filenames as an example
        
        new_survey = Survey(
            name=name,
            email=email,
            tel=tel,
            address=address,
            city=city,
            pincode=pincode,
            category=category,
            timing=timing,
            other_category=other_category,
            image_urls=image_urls
        )
        
        db.session.add(new_survey)
        db.session.commit()
        
        flash('Survey submitted successfully', 'success')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.debug = True
    app.run()
