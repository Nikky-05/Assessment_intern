from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, StringField, PasswordField, TextAreaField, validators
import sqlite3
import os
from sendgrid_service import send_email as send_email_sg

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key')

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email, phone):
        self.id = id
        self.username = username
        self.email = email
        self.phone = phone

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  phone TEXT NOT NULL,
                  password_hash TEXT NOT NULL)''')
    conn.commit()
    conn.close()

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user_data = c.fetchone()
    conn.close()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2], user_data[3])
    return None

# Forms
class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    email = StringField('Email', [validators.Email()])
    phone = StringField('Phone', [validators.Length(min=10, max=15)])
    password = PasswordField('Password', [validators.Length(min=6)])

class LoginForm(Form):
    email = StringField('Email', [validators.Email()])
    password = PasswordField('Password')

class MessageForm(Form):
    message = TextAreaField('Message', [validators.Length(min=1, max=500)])

# Dummy user data for dashboard
dummy_users = [
    {'username': 'john_doe', 'email': 'john@example.com', 'phone': '+1234567890'},
    {'username': 'jane_smith', 'email': 'jane@example.com', 'phone': '+1234567891'},
    {'username': 'bob_johnson', 'email': 'bob@example.com', 'phone': '+1234567892'},
    {'username': 'alice_brown', 'email': 'alice@example.com', 'phone': '+1234567893'},
    {'username': 'charlie_davis', 'email': 'charlie@example.com', 'phone': '+1234567894'},
    {'username': 'diana_wilson', 'email': 'diana@example.com', 'phone': '+1234567895'},
    {'username': 'edward_miller', 'email': 'edward@example.com', 'phone': '+1234567896'},
    {'username': 'fiona_garcia', 'email': 'fiona@example.com', 'phone': '+1234567897'},
    {'username': 'george_martinez', 'email': 'george@example.com', 'phone': '+1234567898'},
    {'username': 'helen_anderson', 'email': 'helen@example.com', 'phone': '+1234567899'},
    {'username': 'ivan_taylor', 'email': 'ivan@example.com', 'phone': '+1234567800'},
    {'username': 'julia_thomas', 'email': 'julia@example.com', 'phone': '+1234567801'},
    {'username': 'kevin_jackson', 'email': 'kevin@example.com', 'phone': '+1234567802'},
    {'username': 'laura_white', 'email': 'laura@example.com', 'phone': '+1234567803'},
    {'username': 'mike_harris', 'email': 'mike@example.com', 'phone': '+1234567804'},
    {'username': 'nancy_clark', 'email': 'nancy@example.com', 'phone': '+1234567805'},
    {'username': 'samruddhi', 'email': 'samruddhinathile@gmail.com', 'phone': '+917249430984'},
    {'username': 'vanshika', 'email': 'vanshikarpatel@gmail.com', 'phone': '+919730211941'}
]

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        phone = form.phone.data
        password = form.password.data
        
        if not password:
            flash('Password is required')
            return render_template('register.html', form=form)
        
        # Check if user already exists
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
        existing_user = c.fetchone()
        
        if existing_user:
            flash('Username or email already exists')
            conn.close()
            return render_template('register.html', form=form)
        
        # Create new user
        password_hash = generate_password_hash(password)
        c.execute('INSERT INTO users (username, email, phone, password_hash) VALUES (?, ?, ?, ?)',
                  (username, email, phone, password_hash))
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        
        if not password:
            flash('Password is required')
            return render_template('login.html', form=form)
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user_data = c.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data[4], password):
            user = User(user_data[0], user_data[1], user_data[2], user_data[3])
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', users=dummy_users)

@app.route('/send_email', methods=['POST'])
@login_required
def send_email():
    recipient_email = request.form.get('email')
    message = request.form.get('message')
    
    if recipient_email and message:
        # Check if SendGrid API key is available
        sendgrid_key = os.environ.get('SENDGRID_API_KEY')
        if sendgrid_key:
            # Use SendGrid to send email
            success = send_email_sg(
                to_email=recipient_email,
                from_email='noreply@example.com',  # You may want to configure this
                subject='Message from User Management System',
                text_content=message
            )
            if success:
                flash(f'Email sent successfully to {recipient_email}')
            else:
                flash(f'Failed to send email to {recipient_email}')
        else:
            # Dummy email logic when SendGrid key is not available
            flash(f'Email sent (dummy) to {recipient_email}: {message}')
    else:
        flash('Failed to send email - missing recipient or message')
    
    return redirect(url_for('dashboard'))

@app.route('/send_sms', methods=['POST'])
@login_required
def send_sms():
    recipient_phone = request.form.get('phone')
    message = request.form.get('message')
    
    if recipient_phone and message:
        # Dummy SMS logic
        flash(f'SMS sent to {recipient_phone}: {message}')
    else:
        flash('Failed to send SMS - missing recipient or message')
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)