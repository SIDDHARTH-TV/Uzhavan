import os
import logging
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import pymysql
import json
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "secret123"

# Configure MySQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/update'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)

# Models
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

class Farmer(db.Model):
    __tablename__ = 'farmer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(10), nullable=False, unique=True)
    state = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')
    products = db.relationship('Product', backref='farmer', lazy=True)

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(10), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    addresses = db.relationship('Address', backref='customer', lazy=True)

class Address(db.Model):
    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    house_number = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    landmark = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(6), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    kilo = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)

# Comprehensive list of Indian states and districts
INDIAN_STATES_DISTRICTS = {
    "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam", "Vizianagaram", "West Godavari", "YSR Kadapa"],
    "Arunachal Pradesh": ["Tawang", "West Kameng", "East Kameng", "Papum Pare", "Kurung Kumey", "Kra Daadi", "Lower Subansiri", "Upper Subansiri", "West Siang", "East Siang", "Siang", "Upper Siang", "Lower Siang", "Lower Dibang Valley", "Dibang Valley", "Anjaw", "Lohit", "Namsai", "Changlang", "Tirap", "Longding"],
    "Assam": ["Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dibrugarh", "Goalpara", "Golaghat", "Hailakandi", "Hojai", "Jorhat", "Kamrup", "Kamrup Metropolitan", "Karbi Anglong", "Karimganj", "Kokrajhar", "Lakhimpur", "Majuli", "Morigaon", "Nagaon", "Nalbari", "Dima Hasao", "Sivasagar", "Sonitpur", "South Salmara-Mankachar", "Tinsukia", "Udalguri", "West Karbi Anglong"],
    "Bihar": ["Araria", "Arwal", "Aurangabad", "Banka", "Begusarai", "Bhagalpur", "Bhojpur", "Buxar", "Darbhanga", "East Champaran", "Gaya", "Gopalganj", "Jamui", "Jehanabad", "Kaimur", "Katihar", "Khagaria", "Kishanganj", "Lakhisarai", "Madhepura", "Madhubani", "Munger", "Muzaffarpur", "Nalanda", "Nawada", "Patna", "Purnia", "Rohtas", "Saharsa", "Samastipur", "Saran", "Sheikhpura", "Sheohar", "Sitamarhi", "Siwan", "Supaul", "Vaishali", "West Champaran"],
    "Chhattisgarh": ["Balod", "Baloda Bazar", "Balrampur", "Bastar", "Bemetara", "Bijapur", "Bilaspur", "Dantewada", "Dhamtari", "Durg", "Gariaband", "Janjgir-Champa", "Jashpur", "Kabirdham", "Kanker", "Kondagaon", "Korba", "Koriya", "Mahasamund", "Mungeli", "Narayanpur", "Raigarh", "Raipur", "Rajnandgaon", "Sukma", "Surajpur", "Surguja"],
    "Goa": ["North Goa", "South Goa"],
    "Gujarat": ["Ahmedabad", "Amreli", "Anand", "Aravalli", "Banaskantha", "Bharuch", "Bhavnagar", "Botad", "Chhota Udaipur", "Dahod", "Dang", "Devbhoomi Dwarka", "Gandhinagar", "Gir Somnath", "Jamnagar", "Junagadh", "Kheda", "Kutch", "Mahisagar", "Mehsana", "Morbi", "Narmada", "Navsari", "Panchmahal", "Patan", "Porbandar", "Rajkot", "Sabarkantha", "Surat", "Surendranagar", "Tapi", "Vadodara", "Valsad"],
    "Haryana": ["Ambala", "Bhiwani", "Charkhi Dadri", "Faridabad", "Fatehabad", "Gurugram", "Hisar", "Jhajjar", "Jind", "Kaithal", "Karnal", "Kurukshetra", "Mahendragarh", "Nuh", "Palwal", "Panchkula", "Panipat", "Rewari", "Rohtak", "Sirsa", "Sonipat", "Yamunanagar"],
    "Himachal Pradesh": ["Bilaspur", "Chamba", "Hamirpur", "Kangra", "Kinnaur", "Kullu", "Lahaul and Spiti", "Mandi", "Shimla", "Sirmaur", "Solan", "Una"],
    "Jharkhand": ["Bokaro", "Chatra", "Deoghar", "Dhanbad", "Dumka", "East Singhbhum", "Garhwa", "Giridih", "Godda", "Gumla", "Hazaribagh", "Jamtara", "Khunti", "Koderma", "Latehar", "Lohardaga", "Pakur", "Palamu", "Ramgarh", "Ranchi", "Sahebganj", "Seraikela-Kharsawan", "Simdega", "West Singhbhum"],
    "Karnataka": ["Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural", "Bengaluru Urban", "Bidar", "Chamarajanagar", "Chikkaballapur", "Chikkamagaluru", "Chitradurga", "Dakshina Kannada", "Davanagere", "Dharwad", "Gadag", "Hassan", "Haveri", "Kalaburagi", "Kodagu", "Kolar", "Koppal", "Mandya", "Mysuru", "Raichur", "Ramanagara", "Shivamogga", "Tumakuru", "Udupi", "Uttara Kannada", "Vijayapura", "Yadgir"],
    "Kerala": ["Alappuzha", "Ernakulam", "Idukki", "Kannur", "Kasaragod", "Kollam", "Kottayam", "Kozhikode", "Malappuram", "Palakkad", "Pathanamthitta", "Thiruvananthapuram", "Thrissur", "Wayanad"],
    "Madhya Pradesh": ["Agar Malwa", "Alirajpur", "Anuppur", "Ashoknagar", "Balaghat", "Barwani", "Betul", "Bhind", "Bhopal", "Burhanpur", "Chhatarpur", "Chhindwara", "Damoh", "Datia", "Dewas", "Dhar", "Dindori", "Guna", "Gwalior", "Harda", "Hoshangabad", "Indore", "Jabalpur", "Jhabua", "Katni", "Khandwa", "Khargone", "Mandla", "Mandsaur", "Morena", "Narsinghpur", "Neemuch", "Panna", "Raisen", "Rajgarh", "Ratlam", "Rewa", "Sagar", "Satna", "Sehore", "Seoni", "Shahdol", "Shajapur", "Sheopur", "Shivpuri", "Sidhi", "Singrauli", "Tikamgarh", "Ujjain", "Umaria", "Vidisha"],
    "Maharashtra": ["Ahmednagar", "Akola", "Amravati", "Aurangabad", "Beed", "Bhandara", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur", "Latur", "Mumbai City", "Mumbai Suburban", "Nagpur", "Nanded", "Nandurbar", "Nashik", "Osmanabad", "Palghar", "Parbhani", "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"],
    "Manipur": ["Bishnupur", "Chandel", "Churachandpur", "Imphal East", "Imphal West", "Jiribam", "Kakching", "Kamjong", "Kangpokpi", "Noney", "Pherzawl", "Senapati", "Tamenglong", "Tengnoupal", "Thoubal", "Ukhrul"],
    "Meghalaya": ["East Garo Hills", "East Jaintia Hills", "East Khasi Hills", "North Garo Hills", "Ri Bhoi", "South Garo Hills", "South West Garo Hills", "South West Khasi Hills", "West Garo Hills", "West Jaintia Hills", "West Khasi Hills"],
    "Mizoram": ["Aizawl", "Champhai", "Hnahthial", "Khawzawl", "Kolasib", "Lawngtlai", "Lunglei", "Mamit", "Saiha", "Saitual", "Serchhip"],
    "Nagaland": ["Dimapur", "Kiphire", "Kohima", "Longleng", "Mokokchung", "Mon", "Peren", "Phek", "Tuensang", "Wokha", "Zunheboto"],
    "Odisha": ["Angul", "Balangir", "Balasore", "Bargarh", "Bhadrak", "Boudh", "Cuttack", "Deogarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghpur", "Jajpur", "Jharsuguda", "Kalahandi", "Kandhamal", "Kendrapara", "Kendujhar", "Khordha", "Koraput", "Malkangiri", "Mayurbhanj", "Nabarangpur", "Nayagarh", "Nuapada", "Puri", "Rayagada", "Sambalpur", "Subarnapur", "Sundargarh"],
    "Punjab": ["Amritsar", "Barnala", "Bathinda", "Faridkot", "Fatehgarh Sahib", "Fazilka", "Ferozepur", "Gurdaspur", "Hoshiarpur", "Jalandhar", "Kapurthala", "Ludhiana", "Mansa", "Moga", "Muktsar", "Nawanshahr", "Pathankot", "Patiala", "Rupnagar", "Sangrur", "SAS Nagar", "Tarn Taran"],
    "Rajasthan": ["Ajmer", "Alwar", "Banswara", "Baran", "Barmer", "Bharatpur", "Bhilwara", "Bikaner", "Bundi", "Chittorgarh", "Churu", "Dausa", "Dholpur", "Dungarpur", "Hanumangarh", "Jaipur", "Jaisalmer", "Jalore", "Jhalawar", "Jhunjhunu", "Jodhpur", "Karauli", "Kota", "Nagaur", "Pali", "Pratapgarh", "Rajsamand", "Sawai Madhopur", "Sikar", "Sirohi", "Sri Ganganagar", "Tonk", "Udaipur"],
    "Sikkim": ["East Sikkim", "North Sikkim", "South Sikkim", "West Sikkim"],
    "Tamil Nadu": ["Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kancheepuram", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai", "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai", "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", "Tenkasi", "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli", "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur", "Vellore", "Viluppuram", "Virudhunagar"],
    "Telangana": ["Adilabad", "Bhadradri Kothagudem", "Hyderabad", "Jagtial", "Jangaon", "Jayashankar Bhupalpally", "Jogulamba Gadwal", "Kamareddy", "Karimnagar", "Khammam", "Kumuram Bheem", "Mahabubabad", "Mahbubnagar", "Mancherial", "Medak", "Medchal-Malkajgiri", "Nagarkurnool", "Nalgonda", "Nirmal", "Nizamabad", "Peddapalli", "Rajanna Sircilla", "Rangareddy", "Sangareddy", "Siddipet", "Suryapet", "Vikarabad", "Wanaparthy", "Warangal Rural", "Warangal Urban", "Yadadri Bhuvanagiri"],
    "Tripura": ["Dhalai", "Gomati", "Khowai", "North Tripura", "Sepahijala", "South Tripura", "Unakoti", "West Tripura"],
    "Uttar Pradesh": ["Agra", "Aligarh", "Ambedkar Nagar", "Amethi", "Amroha", "Auraiya", "Ayodhya", "Azamgarh", "Baghpat", "Bahraich", "Ballia", "Balrampur", "Banda", "Barabanki", "Bareilly", "Basti", "Bhadohi", "Bijnor", "Budaun", "Bulandshahr", "Chandauli", "Chitrakoot", "Deoria", "Etah", "Etawah", "Farrukhabad", "Fatehpur", "Firozabad", "Gautam Buddha Nagar", "Ghaziabad", "Ghazipur", "Gonda", "Gorakhpur", "Hamirpur", "Hapur", "Hardoi", "Hathras", "Jalaun", "Jaunpur", "Jhansi", "Kannauj", "Kanpur Dehat", "Kanpur Nagar", "Kasganj", "Kaushambi", "Kushinagar", "Lakhimpur Kheri", "Lalitpur", "Lucknow", "Maharajganj", "Mahoba", "Mainpuri", "Mathura", "Mau", "Meerut", "Mirzapur", "Moradabad", "Muzaffarnagar", "Pilibhit", "Pratapgarh", "Prayagraj", "Raebareli", "Rampur", "Saharanpur", "Sambhal", "Sant Kabir Nagar", "Shahjahanpur", "Shamli", "Shravasti", "Siddharthnagar", "Sitapur", "Sonbhadra", "Sultanpur", "Unnao", "Varanasi"],
    "Uttarakhand": ["Almora", "Bageshwar", "Chamoli", "Champawat", "Dehradun", "Haridwar", "Nainital", "Pauri Garhwal", "Pithoragarh", "Rudraprayag", "Tehri Garhwal", "Udham Singh Nagar", "Uttarkashi"],
    "West Bengal": ["Alipurduar", "Bankura", "Birbhum", "Cooch Behar", "Dakshin Dinajpur", "Darjeeling", "Hooghly", "Howrah", "Jalpaiguri", "Jhargram", "Kalimpong", "Kolkata", "Maldah", "Murshidabad", "Nadia", "North 24 Parganas", "Paschim Bardhaman", "Paschim Medinipur", "Purba Bardhaman", "Purba Medinipur", "Purulia", "South 24 Parganas", "Uttar Dinajpur"],
    "Andaman and Nicobar Islands": ["Nicobar", "North and Middle Andaman", "South Andaman"],
    "Chandigarh": ["Chandigarh"],
    "Dadra and Nagar Haveli and Daman and Diu": ["Daman", "Diu", "Dadra and Nagar Haveli"],
    "Delhi": ["Central Delhi", "East Delhi", "New Delhi", "North Delhi", "North East Delhi", "North West Delhi", "Shahdara", "South Delhi", "South East Delhi", "South West Delhi", "West Delhi"],
    "Jammu and Kashmir": ["Anantnag", "Bandipora", "Baramulla", "Budgam", "Doda", "Ganderbal", "Jammu", "Kathua", "Kishtwar", "Kulgam", "Kupwara", "Poonch", "Pulwama", "Rajouri", "Ramban", "Reasi", "Samba", "Shopian", "Srinagar", "Udhampur"],
    "Ladakh": ["Kargil", "Leh"],
    "Lakshadweep": ["Lakshadweep"],
    "Puducherry": ["Karaikal", "Mahe", "Puducherry", "Yanam"]
}

# Create tables
with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def calculate_delivery_time(cart, address):
    max_days = 0
    order_date = datetime.now()
    for pid, quantity in cart.items():
        product = Product.query.get(int(pid))
        if product:
            if address.state == product.farmer.state and address.district == product.farmer.district:
                days = 1
            elif address.state == product.farmer.state:
                days = 2
            else:
                days = 7
            max_days = max(max_days, days)

    if max_days == 1:
        delivery_date = order_date + timedelta(days=1)
        return f"Delivery by {delivery_date.strftime('%B %d, %Y')}"
    elif max_days == 2:
        delivery_date = order_date + timedelta(days=2)
        return f"Delivery by {delivery_date.strftime('%B %d, %Y')}"
    else:
        delivery_date = order_date + timedelta(days=7)
        return f"Delivery by {delivery_date.strftime('%B %d, %Y')}"

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')

    if not username or not password or not role:
        flash('Please fill all fields', 'danger')
        return redirect(url_for('home'))

    if role == 'admin':
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.password == password:
            session['user'] = username
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        flash('Wrong username or password', 'danger')
        return redirect(url_for('admin_login'))

    elif role == 'farmer':
        farmer = Farmer.query.filter_by(name=username).first()
        if farmer and farmer.password == password and farmer.approved:
            session['user'] = username
            session['role'] = 'farmer'
            session['farmer_id'] = farmer.id
            return redirect(url_for('farmer_dashboard'))
        flash('Invalid credentials or account not approved', 'danger')
        return render_template('login.html', error='Invalid credentials or account not approved')

    elif role == 'customer':
        customer = Customer.query.filter_by(username=username).first()
        if customer and customer.password == password:
            session['user'] = username
            session['role'] = 'customer'
            session['customer_id'] = customer.id
            return redirect(url_for('customer_dashboard'))
        flash('Invalid credentials', 'danger')
        return render_template('login.html', error='Invalid credentials')

    flash('Invalid role', 'danger')
    return redirect(url_for('home'))

@app.route('/admin')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' not in session or session['role'] != 'admin':
        flash('Please log in as admin', 'danger')
        return redirect(url_for('admin_login'))
    farmers = Farmer.query.all()
    customers = Customer.query.all()
    return render_template('admin_dashboard.html', farmer=farmers, customer=customers)

@app.route('/admin_approve_farmer/<int:farmer_id>')
def admin_approve_farmer(farmer_id):
    farmer = Farmer.query.get_or_404(farmer_id)
    farmer.approved = True
    farmer.status = 'approved'
    db.session.commit()
    flash('Farmer approved successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_reject_farmer/<int:farmer_id>')
def admin_reject_farmer(farmer_id):
    farmer = Farmer.query.get_or_404(farmer_id)
    farmer.approved = False
    farmer.status = 'rejected'
    db.session.commit()
    flash('Farmer rejected successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/farmer_reg')
def farmer_reg():
    return render_template('farmer_reg.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        name = request.form.get('name')
        phone = request.form.get('phone')
        state = request.form.get('state')
        district = request.form.get('district')
        password = request.form.get('password')

        if not all([name, phone, state, district, password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('farmer_reg'))

        if Farmer.query.filter_by(name=name).first():
            flash('Farmer name already exists!', 'danger')
            return redirect(url_for('farmer_reg'))
        if Farmer.query.filter_by(phone=phone).first():
            flash('Phone number already exists!', 'danger')
            return redirect(url_for('farmer_reg'))

        new_farmer = Farmer(
            name=name,
            phone=phone,
            state=state,
            district=district,
            password=password
        )
        db.session.add(new_farmer)
        db.session.commit()
        flash('Request sent successfully!', 'success')
        return redirect(url_for('home'))
    except Exception as e:
        flash(f'An error occurred during registration: {str(e)}', 'danger')
        return redirect(url_for('farmer_reg'))

@app.route('/cust_reg')
def cust_reg():
    return render_template('cust_reg.html')

@app.route('/customer_register', methods=['POST'])
def customer_register():
    try:
        username = request.form.get('username')
        phone = request.form.get('phone')
        password = request.form.get('password')
        house_number = request.form.get('house_number')
        area = request.form.get('area')
        landmark = request.form.get('landmark')
        pincode = request.form.get('pincode')
        state = request.form.get('state')
        district = request.form.get('district')

        if not all([username, phone, password, house_number, area, landmark, pincode, state, district]):
            flash('All fields are required', 'danger')
            return redirect(url_for('cust_reg'))

        # Validate pincode
        if not (pincode.isdigit() and len(pincode) == 6):
            flash('Pincode must be a 6-digit number.', 'danger')
            return redirect(url_for('cust_reg'))

        # Check for existing username or phone
        existing_username = Customer.query.filter_by(username=username).first()
        if existing_username:
            flash('Username already exists!', 'danger')
            return redirect(url_for('cust_reg'))

        existing_phone = Customer.query.filter_by(phone=phone).first()
        if existing_phone:
            flash('Phone number already exists!', 'danger')
            return redirect(url_for('cust_reg'))

        new_customer = Customer(
            username=username,
            phone=phone,
            password=password
        )
        db.session.add(new_customer)
        db.session.flush()  # Get customer ID before committing

        new_address = Address(
            customer_id=new_customer.id,
            house_number=house_number,
            area=area,
            landmark=landmark,
            pincode=pincode,
            state=state,
            district=district
        )
        db.session.add(new_address)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('home'))
    except Exception as e:
        flash(f'Registration failed. Possible database issue: {str(e)}. Please contact support.', 'danger')
        return redirect(url_for('cust_reg'))

@app.route('/farmer', methods=['GET', 'POST'])
def farmer_dashboard():
    if 'user' not in session or session['role'] != 'farmer':
        flash('Please log in as farmer', 'danger')
        return redirect(url_for('home'))

    farmer_id = session.get('farmer_id')
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            price = request.form.get('price')
            kilo = request.form.get('kilo')
            image = request.files.get('image')

            if not all([name, price, kilo, image]):
                flash('All fields are required', 'danger')
                return redirect(url_for('farmer_dashboard'))

            if not allowed_file(image.filename):
                flash('Invalid image file! Only PNG, JPG, JPEG, or GIF allowed.', 'danger')
                return redirect(url_for('farmer_dashboard'))

            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            image_url = url_for('static', filename='uploads/' + filename)

            new_product = Product(farmer_id=farmer_id, name=name, price=float(price), kilo=float(kilo), image_url=image_url)
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding product: {str(e)}', 'danger')
        return redirect(url_for('farmer_dashboard'))

    products = Product.query.filter_by(farmer_id=farmer_id).all()
    return render_template('farmer_dashboard.html', user=session['user'], product=products)

@app.route('/delete_product/<int:product_id>', methods=['GET'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.farmer_id != session.get('farmer_id'):
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('farmer_dashboard'))
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('farmer_dashboard'))

@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.farmer_id != session.get('farmer_id'):
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('farmer_dashboard'))

    if request.method == 'POST':
        try:
            product.name = request.form.get('name')
            product.price = float(request.form.get('price'))
            product.kilo = float(request.form.get('kilo'))
            image = request.files.get('image')

            if not all([product.name, product.price, product.kilo]):
                flash('All fields are required', 'danger')
                return redirect(url_for('update_product', product_id=product_id))

            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                product.image_url = url_for('static', filename='uploads/' + filename)

            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('farmer_dashboard'))
        except Exception as e:
            flash(f'Error updating product: {str(e)}', 'danger')
            return redirect(url_for('update_product', product_id=product_id))

    return render_template('update_product.html', product=product)

@app.route('/customer')
def customer_dashboard():
    if 'user' not in session or session['role'] != 'customer':
        flash('Please log in as customer', 'danger')
        return redirect(url_for('home'))

    state = request.args.get('state')
    district = request.args.get('district')
    search = request.args.get('search')

    query = Product.query.join(Farmer).filter(Farmer.approved == True)
    if state:
        query = query.filter(Farmer.state == state)
    if district:
        query = query.filter(Farmer.district == district)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    products = query.all()
    cart = session.get('cart', {})
    cart_count = sum(cart.values()) if isinstance(cart, dict) else 0

    customer = Customer.query.filter_by(id=session.get('customer_id')).first()

    states = list(INDIAN_STATES_DISTRICTS.keys())
    state_district_map = INDIAN_STATES_DISTRICTS

    return render_template(
        'customer_dashboard.html',
        user=session['user'],
        product=products,
        cart_count=cart_count,
        states=states,
        selected_state=state,
        selected_district=district,
        search=search,
        state_district_map=json.dumps(state_district_map),
        customer=customer
    )

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'role' not in session or session['role'] != 'customer':
        return redirect(url_for('home'))

    product_id = request.form.get('product_id')
    quantity = float(request.form.get('quantity', 0))
    cart = session.get('cart', {})

    product = Product.query.get(product_id)
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('customer_dashboard'))

    if quantity <= product.kilo:
        product.kilo -= quantity
        db.session.commit()

        if product_id in cart:
            cart[product_id] += quantity
        else:
            cart[product_id] = quantity

        session['cart'] = cart
        flash(f'{quantity} kg Homegrown product added to cart!', 'success')
    else:
        flash(f'Not enough stock. Only {product.kilo} kg available for {product.name}.', 'danger')

    return redirect(url_for('customer_dashboard'))

@app.route('/cart')
def view_cart():
    if 'role' not in session or session['role'] != 'customer':
        return redirect(url_for('home'))

    cart = session.get('cart', {})
    products = []
    total_price = 0.0

    for pid, quantity in cart.items():
        prod = Product.query.get(int(pid))
        if prod:
            product_data = {
                'id': prod.id,
                'name': prod.name,
                'image_url': prod.image_url,
                'price': prod.price,
                'quantity': quantity,
                'subtotal': prod.price * quantity,
                'farmer_state': prod.farmer.state,
                'farmer_district': prod.farmer.district
            }
            products.append(product_data)
            total_price += product_data['subtotal']

    return render_template('cart.html', product=products, total=total_price)

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    pid = str(product_id)

    if pid in cart:
        product = Product.query.get(int(pid))
        if product:
            product.kilo += cart[pid]
            db.session.commit()
        del cart[pid]
        session['cart'] = cart
        flash('Item removed from cart.', 'info')

    return redirect(url_for('view_cart'))

@app.route('/address_confirmation', methods=['GET', 'POST'])
def address_confirmation():
    if 'role' not in session or session['role'] != 'customer':
        return redirect(url_for('home'))

    customer = Customer.query.filter_by(id=session.get('customer_id')).first()
    addresses = Address.query.filter_by(customer_id=customer.id).all()
    cart = session.get('cart', {})

    if not cart:
        flash('Your cart is empty.', 'danger')
        return redirect(url_for('view_cart'))

    # Fetch product data for cart items
    cart_products = []
    for pid, quantity in cart.items():
        product = Product.query.get(int(pid))
        if product:
            cart_products.append({
                'id': product.id,
                'farmer_state': product.farmer.state,
                'farmer_district': product.farmer.district
            })

    # Calculate default delivery time for the first address, if available
    default_delivery_time = 'Not calculated'
    default_address = addresses[0] if addresses else None
    if default_address and cart:
        default_delivery_time = calculate_delivery_time(cart, default_address)

    states = list(INDIAN_STATES_DISTRICTS.keys())
    state_district_map = INDIAN_STATES_DISTRICTS

    return render_template(
        'address_confirmation.html',
        customer=customer,
        addresses=addresses,
        default_address=default_address,
        default_delivery_time=default_delivery_time,
        states=states,
        state_district_map=json.dumps(state_district_map),
        cart_products=cart_products,
        new_address_id=session.get('new_address_id')
    )

@app.route('/add_address', methods=['POST'])
def add_address():
    if 'role' not in session or session['role'] != 'customer':
        return redirect(url_for('home'))

    customer = Customer.query.filter_by(id=session.get('customer_id')).first()

    house_number = request.form.get('house_number')
    area = request.form.get('area')
    landmark = request.form.get('landmark')
    pincode = request.form.get('pincode')
    state = request.form.get('state')
    district = request.form.get('district')

    if not all([house_number, area, landmark, pincode, state, district]):
        flash('All address fields are required.', 'danger')
        logger.error("Missing new address fields")
        return redirect(url_for('address_confirmation'))

    # Validate pincode
    if not (pincode.isdigit() and len(pincode) == 6):
        flash('Pincode must be a 6-digit number.', 'danger')
        logger.error(f"Invalid pincode: {pincode}")
        return redirect(url_for('address_confirmation'))

    # Validate state and district
    if state not in INDIAN_STATES_DISTRICTS or district not in INDIAN_STATES_DISTRICTS[state]:
        flash('Invalid state or district selected.', 'danger')
        logger.error(f"Invalid state: {state} or district: {district}")
        return redirect(url_for('address_confirmation'))

    # Add new address
    new_address = Address(
        customer_id=customer.id,
        house_number=house_number,
        area=area,
        landmark=landmark,
        pincode=pincode,
        state=state,
        district=district
    )
    db.session.add(new_address)
    db.session.commit()
    session['new_address_id'] = new_address.id
    flash('New address added successfully!', 'success')
    logger.info(f"New address added, ID: {new_address.id}")
    return redirect(url_for('address_confirmation'))

@app.route('/confirm_delivery', methods=['POST'])
def confirm_delivery():
    if 'role' not in session or session['role'] != 'customer':
        flash('Please log in as customer', 'danger')
        return redirect(url_for('home'))

    logger.debug(f"Session data: {session}")
    logger.debug(f"Form data: {request.form}")

    address_type = request.form.get('address_type')
    customer = Customer.query.filter_by(id=session.get('customer_id')).first()
    cart = session.get('cart', {})

    if not cart:
        flash('Your cart is empty.', 'danger')
        logger.error("Cart is empty")
        return redirect(url_for('view_cart'))

    # Check stock availability
    for pid, quantity in cart.items():
        product = Product.query.get(int(pid))
        if not product or product.kilo < quantity:
            flash(f'Not enough stock for {product.name}.', 'danger')
            logger.error(f"Not enough stock for product {product.name}, requested: {quantity}, available: {product.kilo}")
            return redirect(url_for('view_cart'))

    try:
        if address_type == 'existing':
            address_id = request.form.get('address_id')
            if not address_id:
                flash('Please select an existing address.', 'danger')
                logger.error("No address_id provided for existing address")
                return redirect(url_for('address_confirmation'))

            selected_address = Address.query.get(address_id)
            if not selected_address:
                flash('Selected address not found.', 'danger')
                logger.error(f"Address ID {address_id} not found")
                return redirect(url_for('address_confirmation'))
            if selected_address.customer_id != customer.id:
                flash('Unauthorized address selection.', 'danger')
                logger.error(f"Address ID {address_id} does not belong to customer {customer.id}")
                return redirect(url_for('address_confirmation'))

        else:
            flash('Invalid address type selected.', 'danger')
            logger.error(f"Invalid address_type: {address_type}")
            return redirect(url_for('address_confirmation'))

        # Calculate estimated delivery time for the selected address
        estimated_delivery = calculate_delivery_time(cart, selected_address)
        logger.info(f"Estimated delivery: {estimated_delivery}")

        # Store delivery details in session for payment page
        session['delivery_address'] = {
            'id': selected_address.id,
            'house_number': selected_address.house_number,
            'area': selected_address.area,
            'landmark': selected_address.landmark,
            'pincode': selected_address.pincode,
            'state': selected_address.state,
            'district': selected_address.district
        }
        session['estimated_delivery'] = estimated_delivery
        session.pop('new_address_id', None)  # Clear new_address_id after confirmation

        flash('Address confirmed successfully!', 'success')
        logger.info("Address confirmed, redirecting to payment")
        return redirect(url_for('payment'))

    except Exception as e:
        flash(f'Error processing address: {str(e)}', 'danger')
        logger.exception(f"Exception in confirm_delivery: {str(e)}")
        return redirect(url_for('address_confirmation'))

@app.route('/payment')
def payment():
    if 'role' not in session or session['role'] != 'customer':
        return redirect(url_for('home'))

    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'danger')
        return redirect(url_for('view_cart'))

    products = []
    total_price = 0.0
    for pid, quantity in cart.items():
        prod = Product.query.get(int(pid))
        if prod:
            product_data = {
                'name': prod.name,
                'price': prod.price,
                'quantity': quantity,
                'subtotal': prod.price * quantity
            }
            products.append(product_data)
            total_price += product_data['subtotal']

    delivery_address = session.get('delivery_address', {})
    estimated_delivery = session.get('estimated_delivery', 'Not calculated')

    return render_template(
        'payment.html',
        products=products,
        total=total_price,
        delivery_address=delivery_address,
        estimated_delivery=estimated_delivery
    )

@app.route('/payment_success', methods=['POST'])
def payment_success():
    if 'role' not in session or session['role'] != 'customer':
        flash('Please log in as customer', 'danger')
        return redirect(url_for('home'))

    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'danger')
        return redirect(url_for('view_cart'))

    payment_method = request.form.get('payment_method')
    if not payment_method:
        flash('Please select a payment method.', 'danger')
        return redirect(url_for('payment'))

    delivery_address_data = session.get('delivery_address', {})
    estimated_delivery = session.get('estimated_delivery', 'Not calculated')

    try:
        # Process payment (mock processing, as actual payment gateway integration is not implemented)
        products = []
        total_price = 0.0
        for pid, quantity in cart.items():
            prod = Product.query.get(int(pid))
            if prod:
                if prod.kilo < quantity:
                    flash(f'Not enough stock for {prod.name}. Please update your cart.', 'danger')
                    return redirect(url_for('view_cart'))
                product_data = {
                    'name': prod.name,
                    'price': prod.price,
                    'quantity': quantity,
                    'subtotal': prod.price * quantity,
                    'image_url': prod.image_url  # Moved inside the loop
                }
                products.append(product_data)
                total_price += product_data['subtotal']

        # Create a delivery address object for the template
        class DeliveryAddress:
            def __init__(self, data):
                self.id = data.get('id')
                self.house_number = data.get('house_number')
                self.area = data.get('area')
                self.landmark = data.get('landmark')
                self.pincode = data.get('pincode')
                self.state = data.get('state')
                self.district = data.get('district')

        delivery_address = DeliveryAddress(delivery_address_data)

        # Clear the cart and session data
        session.pop('cart', None)
        session.pop('delivery_address', None)
        session.pop('estimated_delivery', None)

        flash(f'Payment successful via {payment_method}! Your order has been placed.', 'success')
        return render_template(
            'payment_success.html',
            products=products,
            total=total_price,
            delivery_address=delivery_address,
            estimated_delivery=estimated_delivery,
            payment_method=payment_method
        )

    except Exception as e:
        flash(f'Payment processing failed: {str(e)}', 'danger')
        return redirect(url_for('payment'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
