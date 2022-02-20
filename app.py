from crypt import methods
from email import message
import os
import urllib.request
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect
from flask_login.utils import login_required, logout_user
from models import db, UserModel, login, Question, Image, Comment
from flask_login import current_user, login_user
from flask import *
from random import *
from flask_mail import *


UPLOAD_FOLDER = 'static/uploads/'

# wrong error for logging in without registering and wrong password
# send error 

app = Flask(__name__)

app.secret_key = 'xyz'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

mail = Mail(app)
app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"]=465
app.config["MAIL_USERNAME"]='mujt434@gmail.com'
app.config['MAIL_PASSWORD']='reqrum-myvnow-6riZfo'
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
mail = Mail(app)

otp=randint(000000,999999)
user = None

db.init_app(app)
login.init_app(app)
login.login_view = 'login'

@app.before_first_request
def create_table():
    db.create_all()

@app.route("/")
@login_required
def index():
    questions = Question.query.order_by(Question.created_on.desc())
    return render_template("sub.html", questions=questions)

@app.route("/log_reg", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        log = request.form.get("login")
        reg = request.form.get("reg")

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        print(log)
        print(reg)

        user = UserModel.query.filter_by(username='muj')
        print(user)

        if log is not None:
            if username != "":
                user = UserModel.query.filter_by(username=username).first()

            elif email != "":
                user = UserModel.query.filter_by(email = email).first()

            if user is not None and user.check_pass_hash(password):
                login_user(user)
                return redirect('/')
                # return render_template('login.html', message='Incorrect Password')
            return render_template('login.html', message='Account does not exist')
        
        else:
            mail_match = re.search("[0-9]+@mjcollege.ac.in", email)
            if mail_match:
                if UserModel.query.filter_by(email=email).first():
                    return render_template('login.html', message="Account already exists! Try logging in instead.")
                
                if email != "" and username !="" and password != "":


                    print(otp)

                    msg=Message('OTP',sender='mujt434@gmail.com',recipients=[email])
                    msg.body=str(otp)
                    mail.send(msg)
                    # login_user(user)
                    return render_template('validate.html', info=[username, email, password])
                return render_template("login.html", message='credentials')
            return render_template("login.html", message="Create with College Mail Only")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')

@app.route('/validate',methods=["GET", "POST"])
def validate():
    if request.method == "POST":
        otpl = request.form.get("otp")
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        print(otp)
        if int(otpl) == otp:
            user = UserModel(email=email, username=username)
            user.set_pass_hash(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect('/')
        return render_template('validate.html', message="Incorrect otp")
    return render_template('validate.html')


@app.route('/<subject>')
def sub(subject):
    questions = Question.query.filter_by(sub=subject.upper()).order_by(Question.created_on.desc())

    for i in questions:
        print(i.title)

    sub_dict = {
        'ai': 'Artificial Intelligence',
        'alc': 'Automata Language and Computation',
        'bct': 'BlockChain Technologies',
        'da': 'Data Analytics',
        'irs': 'Information Retrieval Systems',
        'se': 'Software Engineering',
        'os': 'Operating Systems',
        'wit': 'Web and Internet Technologies'
    }
    if subject in sub_dict.keys():
        return render_template("sub.html", subject=sub_dict[subject], questions=questions)
    return "404 Page not found"

@app.route('/<subject>/<id>')
def discussions(subject, id):
    question = Question.query.filter_by(id=id).first()
    images = Image.query.filter_by(qid=id)
    comments = Comment.query.filter_by(qid=id)

    return render_template('discussions.html', question=question, images=images, comments=comments)

@app.route('/add', methods=["POST", "GET"])
def add():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["desc"]
        subject = request.form["sub"]

        question = Question(username=current_user.username, title=title, 
                    description=description, sub=subject)
        db.session.add(question)
        db.session.commit()
        qid = Question.query.filter_by(title=title).first().id


        if 'file' not in request.files:
            return redirect("/add", message={"No file passed"})
        files = request.files.getlist('file')
        file_names = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_names.append(filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = Image(qid=qid, fname=filename)
                db.session.add(image)
                db.session.commit()
            return redirect(f"/{subject}/{qid}")   
    return render_template("add.html")

@app.route("/<subject>/<id>/comment", methods=["POST"])
def add_comment(subject, id):
    reply = request.form["comment"]
    comment = Comment(qid=id, cmt=reply, username=current_user.username)
    db.session.add(comment)
    db.session.commit()
    return redirect(f"/{subject}/{id}")

@app.route("/search", methods=["POST"])
def search():
    query = request.form["q"]

    query = query.split(' ')
    query = f".*{'.*'.join(query)}.*"
    search_results = []
    rs1 = Question.query
    for i in rs1:
        s = "".join(i.title).lower()
        match = re.findall(query, s)
        if match:
            search_results.append(i)
    return render_template("sub.html", questions=search_results)