from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'nd06works'
socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456789',
    'database': 'surplus_platform'
}

class User(UserMixin):
    def __init__(self, id, name, email, user_type):
        self.id = id
        self.name = name
        self.email = email
        self.user_type = user_type

@login_manager.user_loader
def load_user(user_id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    connection.close()
    if user_data:
        return User(user_data['id'], user_data['name'], user_data['email'], user_data['user_type'])
    return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        hashed_password = generate_password_hash(password)

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        try:
            cursor.execute('INSERT INTO users (name, email, password, user_type) VALUES (%s, %s, %s, %s)',
                           (name, email, hashed_password, user_type))
            connection.commit()
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
            return redirect(url_for('register'))
        finally:
            cursor.close()
            connection.close()

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user_data = cursor.fetchone()
        cursor.close()
        connection.close()

        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data['id'], user_data['name'], user_data['email'], user_data['user_type'])
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('marketplace'))
        else:
            flash('Invalid email or password.')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('login'))

@app.route('/marketplace', methods=['GET', 'POST'])
@login_required
def marketplace():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    
    if request.method == 'POST':
        crop = request.form['crop']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])

        cursor.execute('INSERT INTO listings (crop, quantity, price, seller_id) VALUES (%s, %s, %s, %s)',
                       (crop, quantity, price, current_user.id))
        connection.commit()

    cursor.execute('SELECT * FROM listings')
    listings = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('marketplace.html', listings=listings)

@app.route('/dashboard')
@login_required
def dashboard():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    
    if current_user.user_type == 'seller':
        cursor.execute('SELECT * FROM listings WHERE seller_id = %s', (current_user.id,))
        listings = cursor.fetchall()
    else:
        listings = []
    
    cursor.close()
    connection.close()
    return render_template('dashboard.html', user=current_user, listings=listings)

@app.route('/send-message/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def send_message(recipient_id):
    if request.method == 'POST':
        content = request.form['content']
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute('INSERT INTO messages (sender_id, recipient_id, content) VALUES (%s, %s, %s)',
                       (current_user.id, recipient_id, content))
        connection.commit()
        cursor.close()
        connection.close()

        flash('Message sent successfully!')
        return redirect(url_for('inbox'))

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id = %s', (recipient_id,))
    recipient = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('send_message.html', recipient=recipient)

@app.route('/inbox')
@login_required
def inbox():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM messages WHERE recipient_id = %s ORDER BY timestamp DESC', (current_user.id,))
    messages = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('inbox.html', messages=messages)

@app.route('/sent')
@login_required
def sent():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM messages WHERE sender_id = %s ORDER BY timestamp DESC', (current_user.id,))
    messages = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('sent.html', messages=messages)

if __name__ == '__main__':
    socketio.run(app, debug=True)
