import json
import os
import firebase_admin
from firebase_admin import credentials, db

firebase_key = json.loads(os.environ["FIREBASE_KEY"])

cred = credentials.Certificate(firebase_key)

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://bloodbank-4d2e3-default-rtdb.asia-southeast1.firebasedatabase.app/"
})
ref = db.reference('/')
app = Flask(__name__)
app.secret_key = "mysecretkey"  



@app.route('/')
def login():
    return render_template('login.html')



@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')



@app.route('/checkuser', methods=['POST'])
def check():
    try:
        username = request.form['username']
        password = request.form['password']

        user_info_ref = db.reference(f'user/{username}')
        user_info = user_info_ref.get()

        
        if user_info and user_info['password'] == password:
            session['username'] = username  
            return redirect('/homepage')
        else:
            flash("❌ Invalid username or password!", "danger")
            return redirect('/')

    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
        return redirect('/')



@app.route('/newuser', methods=['POST'])
def newuser():
    try:
        username = request.form['username']
        email = request.form['email']
        phone_number = request.form['phone']
        password = request.form['password']

        user_ref = db.reference(f'user/{username}')
        user_ref.set({
            'username': username,
            'email': email,
            'phone': phone_number,
            'password': password
        })

        flash("✅ Registration successful! Please login.", "success")
        return redirect('/')

    except Exception as e:
        flash(f"Registration Error: {e}", "danger")
        return redirect('/register')



@app.route('/homepage')
def homepage():
    if 'username' not in session:
        return redirect('/')
    return render_template('home_page.html')



@app.route('/add_donar')
def add_donar():
    return render_template('Add_Donsar.html')



@app.route('/insertdonor', methods=['POST'])
def insertdonar():
    try:
        username = request.form.get('donorName')
        user_ref = db.reference(f'donors/{username}')

        user_ref.set({
            "name": request.form.get('donorName'),
            "gender": request.form.get('Gender'),
            "blood_type": request.form.get('bloodType'),
            "phone_number": request.form.get('phoneNumber'),
            "email": request.form.get('Email'),
            "primary_location": request.form.get('pLocation'),
            "secondary_location": request.form.get('sLocation')
        })

        flash("✅ Donor added successfully!", "success")
        return redirect('/add_donar')

    except Exception as e:
        flash(f"Error adding donor: {e}", "danger")
        return redirect('/add_donar')



@app.route('/finddonar')
def finddonar():
    return render_template('find_donar.html')


@app.route('/displaydonor', methods=['POST'])
def displaydonor():
    try:
        bloodtype = request.form.get('bloodtype', '').strip().lower()
        location = request.form.get('location', '').strip().lower()

        if not bloodtype or not location:
            flash("⚠ Blood type and location are required!", "warning")
            return redirect('/finddonar')

        ref = db.reference('donors')
        all_donors = ref.get() or {}

        matching_donors = {
            key: donor for key, donor in all_donors.items()
            if donor.get("blood_type", "").lower() == bloodtype and
               location in [donor.get("primary_location", "").lower(),
                            donor.get("secondary_location", "").lower()]
        }

        return render_template('find_donar.html', donors=matching_donors)

    except Exception as e:
        flash(f"❌ Error retrieving donor data: {e}", "danger")
        return redirect('/finddonar')



@app.route('/listofall')
def listofall():
    try:
        ref = db.reference('donors')
        all_donors = ref.get() or {}
        return render_template('listofall.html', donors=all_donors)

    except Exception as e:
        flash(f"Error fetching donors: {e}", "danger")
        return redirect('/homepage')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
