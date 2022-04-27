from datetime import datetime
from flask import Flask,render_template,request,session,redirect,url_for,flash
# to connect back end to front end
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import query
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
import json

# MY db connection
local_server= True
app = Flask(__name__)
app.secret_key='kusumachandashwini'


# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# app.config['SQLALCHEMY_DATABASE_URL']='mysql://username:password@localhost/databas_table_name'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/qa'
db=SQLAlchemy(app)

# here we will create db models that is tables--front end tables
class Questions(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    author = db.Column(db.String(100))
    question =db.Column(db.String(100))
    created_at = db.Column(db.DateTime(6))
    updated_at = db.Column(db.DateTime(6))

class Response(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user =db.Column(db.String(100))
    question_no = db.Column(db.String(200))
    body = db.Column(db.String(5000))
    created_at = db.Column(db.Date) 

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))


@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/displayq',methods=['POST','GET'])
def displayq():
    if request.method == "GET":
        teach=db.engine.execute(f"SELECT `questions`.*,`response`.`body`  FROM `questions` left join `response` on `questions`.`id`=`response`.`question_no` ")
    if request.method == "POST":
        flash(request.method,"warning")
        user=current_user.username
        body=request.form.get('body')
        question_no=request.form.get('question_no')
        created_at=datetime.now()
        updated_at=datetime.now()
        query=db.engine.execute(f"INSERT INTO `response` (`user`,`body`,`question_no`,`created_at`,`updated_at`) VALUES ('{user}`,'{body}','{question_no}','{created_at}','{updated_at}')")
        return render_template('displayq.html',teach=teach)
    return render_template('displayq.html',teach=teach) 
	
@app.route('/ask' ,methods=['POST','GET'])
@login_required
def ask(): 
    if request.method == "POST":
        author=current_user.username
        question=request.form.get('question')
        created_at=request.form.get('created_at')
        updated_at=request.form.get('updated_at')
       
        query=db.engine.execute(f"INSERT INTO `questions` (`author`,`question`,`created_at`,`updated_at`) VALUES ('{author}','{question}','{created_at}','{updated_at}')")
        flash("question got created successfully","success")
        return render_template('ask.html')

    return render_template('ask.html') 

@app.route('/answer' ,methods=['POST','GET'])
@login_required
def answer(): 
    if request.method == "POST":
        user=current_user.username
        body=request.form.get('body')
        question_no=request.form.get('question_no')
        created_at=datetime.now()
        query=db.engine.execute(f"INSERT INTO `response` (`user`,`question_no`,`body`,`created_at`) VALUES ('{user}','{question_no}','{body}','{created_at}')")
        return render_template('displayq.html')

    return render_template('displayq.html') 
	
#signup form/page
@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        
        #LHS email is database(model) email and RHS is front-end email 
        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            return render_template('/signup.html')
        encpassword=generate_password_hash(password)

        new_user=db.engine.execute(f"INSERT INTO `user` (`username`,`email`,`password`) VALUES ('{username}','{email}','{encpassword}')")

            
        # this is method 2 to save data in db
        # newuser=User(username=username,email=email,password=encpassword)
        # db.session.add(newuser)
        # db.session.commit()
        flash("Signup Succes Please Login","success")
        return render_template('login.html')
        

    return render_template('signup.html')

#login page
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        #LHS user stores true or false   AND   query.filter_by : checking email is equal, by executing query
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","primary")
            return redirect(url_for('index'))
        else:
            flash("invalid credentials","danger")
            return render_template('login.html')    

    return render_template('login.html')

#logout function
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))


#question page once you click on question
@app.route('/questions',methods=['POST','GET'])
@login_required
def questions():
    return render_template('questions.html')

@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'My database is Connected'
    except:
        return 'My db is not Connected'


app.run(debug=True)    