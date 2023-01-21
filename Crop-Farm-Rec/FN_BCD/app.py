from flask import Flask, render_template, request, url_for, redirect, session
import pymongo
import bcrypt
import pickle
import pandas as pd
import numpy as np

# set app as a Flask instance
app = Flask(__name__)
app.secret_key = "testing"
# connoct to your Mongo DB database
client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
mydb = client["farmDB"]

farm = client.get_database('farmDB')
record = farm.register
# get the database name
db = client.get_database('total_records')
db_S = client.get_database('Students')
# get the particular collection that contains the data
records = db.register
Student_records = db_S.register

# ---------------------- Numeric MODEL -------------------------------#
model_numeric = pickle.load(open('C:/Users/dhruv/Desktop/crop farming recommendation/RandomForest.pkl', 'rb'))
upload_files = 'C:\\Users\\admin\\Desktop\\pythonProject\\FN_BCD\\static'

# assign URLs to have a particular route
@app.route("/", methods=['post', 'get'])
def index():
    message = ''
    # if method post in index
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        # if found in database showcase that it's found
        user_found = record.find_one({"name": user})
        email_found = record.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            # hash the password and encode it
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            # assing them in a dictionary in key value pairs
            fName = user
            fage = ""
            fid = email
            password = hashed
            nitrogen = ""
            phosprous = ""
            potassium = ""
            temp = ""
            humidity = ""
            ph = ""
            rainfall = ""
            predicted_result = ""
            data_input = {'fName': fName, 'fage': fage, 'email': fid, 'password': password, 'nitrogen': nitrogen,
                          'phosprous': phosprous,
                          'potassium': potassium, 'temp': temp, 'humidity': humidity, 'ph': ph, 'rainfall': rainfall,
                          'prediction': predicted_result}
            record.insert_one(data_input)

            # find the new created account and its email
            user_data = record.find_one({"email": email})
            new_email = user_data['email']
            # if registered redirect to logged in as the registered user
            return render_template('logged_in.html', email=new_email)
    return render_template('index.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # check if email exists in database
        email_found = record.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            # encode the password and check if it matches
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))


@app.route('/information')
def insertinfo():
    if "email" in session:
        email = session["email"]
    return render_template('information.html')


# ---------------------- Patient information -------------------------------#
@app.route('/info', methods=["GET", "POST"])
def info():
    if request.method == "POST":
        info.Name = request.form['Name']
        info.Age = request.form['Age']
        info.Id = request.form['Id']
        seperator = '_'
        info.concat = info.Name + seperator + info.Id
        return render_template('Crop_pred.html')


# ---------------------- Calls the Numeric based Html Page -------------------------------#
@app.route('/Crop_pred')
def BCD_Numeric():
    return render_template('Crop_pred.html')


# ---------------------- Function for Prediction on Numeric based Model -------------------------------#
@app.route('/predict_numeric', methods=['POST'])
def predict():
    input_features = [float(x) for x in request.form.values()]
    features_value = [np.array(input_features)]
    features_name = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']

    df = pd.DataFrame(features_value, columns=features_name)
    output = model_numeric.predict(df)

    fName = info.Name
    fage = info.Age
    email = info.Id
    nitrogen = input_features[0]
    phosprous = input_features[1]
    potassium = input_features[2]
    temp = input_features[3]
    humidity = input_features[4]
    ph = input_features[5]
    rainfall = input_features[6]
    predicted_result = output[0]

    record.update({"email": email}, {
        '$set': {'fName': fName, 'fage': fage, 'email': email, 'nitrogen': nitrogen, 'phosprous': phosprous,
                 'potassium': potassium, 'temp': temp, 'humidity': humidity, 'ph': ph, 'rainfall': rainfall,
                 'prediction': predicted_result}})

    return render_template('result_numeric.html', prediction_text=output, Name=info.Name, Age=info.Age, Id=info.Id,
                           concat=info.concat)  # Name=Name,Age=Age,Id=Id


# ---------------------- Function for returning to main Index Page -------------------------------#
@app.route('/vmd_timestamp')
def vmd_timestamp():
    return render_template('logged_in.html')


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)