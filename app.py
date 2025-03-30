import mysql.connector
from flask import Flask, render_template, request

app = Flask(__name__)
#databse setup
db_config={'host':'MSI','user':'root','password':'123456789','database':'surplus_platform'}
# Homepage Route
@app.route('/')
def home():
    return render_template('home.html')  # Render the homepage

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Capture form data
        name = request.form['name']
        email = request.form['email']
        user_type = request.form['user_type']
    
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute('INSERT INTO users (name, email, user_type) VALUES (%s, %s, %s)', (name, email, user_type))
        connection.commit()
        cursor.close()
        connection.close()
        return "Registration Successful!" 
    return render_template('register.html')  # Render the registration form

@app.route('/test-db-connection', methods=['GET'])
def test_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return "Database connection successful!"
    except mysql.connector.Error as err:
        return f"Error: {err}"
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
@app.route('/marketplace', methods=['GET', 'POST'])
def marketplace():
    if request.method == 'POST':
        crop = request.form['crop']
        quantity = request.form['quantity']
        price = request.form['price']

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute('INSERT INTO listings (crop, quantity, price) VALUES (%s, %s, %s)', (crop, quantity, price))
        connection.commit()
        cursor.close()
        connection.close()

        return "Listing Added Successfully!"

    # Retrieve all listings from the database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM listings')
    listings = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('marketplace.html', listings=listings)


if __name__ == '__main__':
    app.run(debug=True)  