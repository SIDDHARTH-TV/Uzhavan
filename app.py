import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import pymysql

app = Flask(__name__)
app.secret_key = "secret123"  # Secret key for session management

# Configure MySQL Database (XAMPP)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/farmer_market'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Define the upload folder
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file types for images

db = SQLAlchemy(app)

# Dummy user credentials
users = {
    "farmer": {"username": "farmer1", "password": "123"},
    "customer": {"username": "customer1", "password": "123"}
}

# Product Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    kilo = db.Column(db.Float, nullable=False)  # New column for quantity in kg
    image_url = db.Column(db.String(200), nullable=False)


# Create tables in MySQL (XAMPP)
with app.app_context():
    db.create_all()

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    if role in users and users[role]["username"] == username and users[role]["password"] == password:
        session['user'] = username
        session['role'] = role
        if role == "farmer":
            return redirect(url_for('farmer_dashboard'))
        elif role == "customer":
            return redirect(url_for('customer_dashboard'))
    flash("Invalid Credentials!", "danger")
    return redirect(url_for('home'))


@app.route('/farmer', methods=['GET', 'POST'])
def farmer_dashboard():
    if 'user' not in session or session['role'] != 'farmer':
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        kilo = request.form['kilo']  # Get quantity from form
        image = request.files['image']

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            image_url = url_for('static', filename='uploads/' + filename)

            new_product = Product(name=name, price=price, kilo=kilo, image_url=image_url)
            db.session.add(new_product)
            db.session.commit()
            flash('Product Added Successfully!', 'success')
        else:
            flash('Invalid Image File! Only PNG, JPG, JPEG, or GIF files are allowed.', 'danger')

    products = Product.query.all()
    return render_template('farmer_dashboard.html', user=session['user'], products=products)


# Route to delete a product
@app.route('/delete_product/<int:product_id>', methods=['GET'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product Deleted Successfully!', 'success')
    return redirect(url_for('farmer_dashboard'))


# Route to update a product
@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        product.kilo = request.form['kilo']

        # If an image is uploaded, update it
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            product.image_url = url_for('static', filename='uploads/' + filename)

        db.session.commit()
        flash('Product Updated Successfully!', 'success')
        return redirect(url_for('farmer_dashboard'))

    return render_template('update_product.html', product=product)


@app.route('/customer')
def customer_dashboard():
    if 'user' not in session or session['role'] != 'customer':
        return redirect(url_for('home'))

    products = Product.query.all()
    return render_template('customer_dashboard.html', user=session['user'], products=products)


@app.route('/payment', methods=['POST'])
def payment():
    product_id = request.form['product_id']
    product = Product.query.get(product_id)  # Get the product details from the database
    return render_template('payment.html', product=product)

@app.route('/pay_success', methods=['POST'])
def pay_success():
    flash('Payment Successful!', 'success')  # Flash the success message
    return redirect(url_for('customer_dashboard'))  # Redirect to the customer dashboard





@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
