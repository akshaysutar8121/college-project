# natural laungugage processing libraries
from firebase_admin import firestore
from firebase_admin import credentials
import firebase_admin
import pyrebase
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import pytz
import requests
import json
import gc
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import WordNetLemmatizer
import warnings
import string
import random
import nltk
nltk.download('punkt')
nltk.download('omw-1.4')
warnings.filterwarnings('ignore')
nltk.download('punkt')
nltk.download('wordnet')
# api related packages


app = Flask(__name__, template_folder='./template')


# time stamp for user creation
def getTime():
    now = datetime.now()
    time_zone = pytz.timezone('Asia/Kolkata')
    mynow = now.astimezone(time_zone)
    mynow = str(mynow.hour)+":"+str(mynow.minute)
    return mynow


# all greetings
greetings = ("hi", "hello", "whatsup", "hey", "greetings")
greeting_response = ["hi sir this is your personal AI assistant, i can help you to solve your problems",
                     "hey", "hello", "whatsup buddy", "i am glad to helping you"]


def greeting(inp):
    for word in inp.split():
        if word.lower() in greetings:
            return random.choice(greeting_response)


# ***********
f = open('./lucia.txt', 'r', errors='ignore')
raw = f.read()
raw = raw.lower()
raw

sent_tokens = nltk.sent_tokenize(raw)
words = nltk.word_tokenize(raw)

lametizer = WordNetLemmatizer()


def leme_token(tokens):
    return [lametizer.lemmatize(token) for token in tokens]


remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)


def lemeNormalize(text):
    return leme_token(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


# *************************

# databse apis to show data of cars
response1 = requests.get('http://akshay8860.pythonanywhere.com')

data1 = response1.json()

# simplifing the data
record1 = []
for i in data1['data']:
    arr = [str(i['img']), i['manufacturer'], i['model'], i['price'], str(i['wiki']),
           ]

    record1.append(arr)
result1 = record1

# ***********
response2 = requests.get('http://sutar12345.pythonanywhere.com/')
data2 = response2.json()
record2 = []
for i in data2['data']:
    arr = [str(i['name']), str(i['adress']), str(i["image"])]
    record2.append(arr)
result2 = record2
# database to get shorooms database

# **************
# firebase authenticatin

appconfig = {"apiKey": "AIzaSyCykB-zhe_Dl5dwNp-vUPTvqwS4Gx6w7vQ",

             "authDomain": "college-project-b119a.firebaseapp.com",

             "projectId": "college-project-b119a",

             "storageBucket": "college-project-b119a.appspot.com",

             "messagingSenderId": "141734861464",

             "appId": "1:141734861464:web:a301b74e1685ffc9e00eed",

             "measurementId": "G-MTWH7CZF8T",
             "databaseURL": ''


             }
firebase = pyrebase.initialize_app(appconfig)
auth = firebase.auth()

# credintials
cred = credentials.Certificate('./firestorekey.json')
try:
    firebase_admin.initialize_app(cred)

except:
    print("you have alreday intialized you dont need to run again")
db = firestore.client()
# ***********

app = Flask(__name__, template_folder='./template')
app.secret_key = "super secret key"
@app.route('/')
def home():
    return render_template('homepage.html')


# chat route


@app.route('/chatbot')
def chatbot():
    return render_template('chatbotfile.html')


@app.route('/lucia', methods=['POST', 'GET'])
def lucia():
    def response(user_response):

        chatbot_res = ''
        sent_tokens.append(user_response)
        tfidfvect = TfidfVectorizer(
            tokenizer=lemeNormalize, stop_words='english')
        tfidf = tfidfvect.fit_transform(sent_tokens)
        val = cosine_similarity(tfidf[-1], tfidf)
        idx = val.argsort()[0][-2]
        flat = val.flatten()
        flat.sort()
        req_tfidf = flat[-2]
        if req_tfidf == 0:
            chatbot_res = chatbot_res+"sorry i couldn't understand"
            return chatbot_res
        else:
            chatbot_res = chatbot_res+sent_tokens[idx]
            return chatbot_res

    inp_time = ''

    # time when input is given by user
    inp_time = getTime()
    final_response = ''
    user_input = ''

    output_time = ''

    if request.method == 'POST':

        user_response = request.form['messege']
        # input given by user
        user_input = user_response

        user_response = user_response.lower()
        if(user_response != 'bye'):
            # if(user_response=="thanks" or user_response=="thank you"):
            if("thank" in list(user_response.split()) or "thanks" in list(user_response.split())):

                print("lucia:welcome sir...")
                output_time = getTime()
                final_response = "lucia:welcome sir..."

            else:
                if(greeting(user_response) != None):
                    output_time = getTime()
                    final_response = greeting(user_response)
                else:

                    final_response = response(str(user_response))
                    output_time = getTime()
                    sent_tokens.remove(user_response)
        else:
            final_response = "lucia:bye have a nice day sir"

            output_time = getTime()

    return render_template('chatbotfile.html', result=final_response, user_input=user_input, inp_time=inp_time, output_time=output_time)


@app.route('/cars')
def mycars():
    return render_template('carspage.html', result=result1)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    messege = ''
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']
        dob = request.form['date']
        phone = request.form['phone']
        country = request.form['country']
        try:
          user=auth.create_user_with_email_and_password(email,password)
          auth.send_email_verification(user['idToken'])
          messege='succsesfully created account please cheack email'
          db.collection('users').document(str(email)).set(
            {
            'dob':str(dob),
            'phone':str(phone),
            'country':str(country),
            'time':str(getTime())
            }
           )
        except:
          messege='user already exist!'
        
    return render_template('signuppage.html', result=messege)


@app.route('/login', methods=['POST', 'GET'])
def login():
    messege = ''
    validate = ''
    email = ''
    nickn = ''
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        # try:
        #     user = auth.sign_in_with_email_and_password(email, password)
        #     messege = 'succesfully loged in!'
        #     session["key"] = 'akshay@123'
        #     vals = str(email).split('@')
        #     nickn = vals[0]
        #     session["email"] = str(email)

        #     session["email"] = email

        #     return redirect(url_for("userpage", email=email, name=nickn))
        #     useremail = email

        #     info = auth.get_account_info(user['idToken'])
        #     val = info['users'][0]['emailVerified']
        #     if val == False:
        #         validate = 'your email is not verified please verify'
        # except:
        #     messege = 'invalid credintials!' 

        
        user = auth.sign_in_with_email_and_password(email, password)
        messege = 'succesfully loged in!'
        session["key"] = 'akshay@123'
        vals = str(email).split('@')
        nickn = vals[0]
        session["email"] = str(email)

        session["email"] = email

        return redirect(url_for("userpage", email=email, name=nickn))
        useremail = email

        info = auth.get_account_info(user['idToken'])
        val = info['users'][0]['emailVerified']
        if val == False:
            validate = 'your email is not verified please verify'
        
        messege = 'invalid credintials!'
        

    return render_template('signinpage.html', result=messege)


@app.route('/resetpass', methods=['POST', 'GET'])
def resetpass():
    messege = ''

    if request.method == 'POST':
        try:
            email = request.form['email']
            auth.send_password_reset_email(email)
            messege = 'email sent please cheack '
        except:
            messege = 'user not exist'

    return render_template('resetpass.html', result=messege)


@app.route('/user/<name>%<email>')
def userpage(email, name):
    if "email" in session:
        return render_template("userprofile.html", name=name, email=email, result2=result2)

    else:
        return render_template('signinpage.html')


@app.route('/logout')
def logout():
    session.pop("email", None)
    return redirect(url_for("login"))


app.run(debug=True)
