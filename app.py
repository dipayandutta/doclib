'''
	Python Script For Making a Document Library 
	Version - 1.0 
'''

#Importing all required library
from flask import Flask , render_template
from flask import redirect , url_for ,request
from flask import g , session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField , PasswordField, BooleanField
from wtforms.validators import InputRequired, Email , Length
from flask_sqlalchemy import SQLAlchemy 
from werkzeug.security import generate_password_hash , check_password_hash
from flask_login import LoginManager , UserMixin, login_user, login_required,logout_user,current_user
import os
from uuid import uuid4
import subprocess
from flask import send_file
from io import BytesIO
from urlparse import urlparse

#Declearing all configurations
app = Flask(__name__)
app.config['SECRET_KEY']= 'Thisisasecretkey123@332das23#$%'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite://///work/python/flask_application/doclib/database.db'

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Getting the root directory 
APP_ROOT =os.path.dirname(os.path.abspath(__file__))

#Declearing User Class for User Registration 
class User(UserMixin,db.Model):
	#Declearing all fields in the database
	id = db.Column(db.Integer,primary_key=True) #id Field Primary Key
	username = db.Column(db.String(15),unique=True) #username 
	password = db.Column(db.String(80)) # password
	email = db.Column(db.String(50),unique=True) #email
	dept  = db.Column(db.String(60)) #Department

#Declearing Admin Class For Admin Registration
class Admin(UserMixin,db.Model):
	id = db.Column(db.Integer,primary_key=True) #id Field Primary key
	username = db.Column(db.String(15),unique=True) #username 
	password = db.Column(db.String(80)) # password

#Getting User ID of the current Login User
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

#Creating The login from using FlaskForm
class LoginForm(FlaskForm):
	username = StringField('username',validators=[InputRequired(),Length(min=4,max=20)])
	password = PasswordField('password',validators=[InputRequired(),Length(min=6,max=80)])
	remember = BooleanField('remember me')

#Createing The Registration From using FlaskForm
class RegistrationForm(FlaskForm):
	username = StringField('username',validators=[InputRequired(),Length(min=4,max=20)])
	password = PasswordField('password',validators=[InputRequired(),Length(min=6,max=80)])
	email = StringField('email',validators=[InputRequired(),Email(message='Invalid Email-Id'),Length(max=50)])
	dept = StringField('Deptartment',validators=[InputRequired(),Length(min=2,max=30)])

#Creating AdminLogin Form using FlaskForm 
class AdminLogin(FlaskForm):
	username = StringField('username',validators=[InputRequired(),Length(min=4,max=26)])
	password = PasswordField('password',validators=[InputRequired(),Length(min=4,max=80)])
	remember = BooleanField('remember me')


#The Login URL Declearation
@app.route('/login',methods=['GET','POST'])
def login():
	form = LoginForm() #Initializing the LoginForm 
	#Checking the Form input Validation
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first() #Fetching User from the database
		if user:
			if check_password_hash(user.password,form.password.data): #Checking password hash
				login_user(user,remember=form.remember.data)
				#If everything works then Redirect the user to his Dashboard
				return redirect(url_for('dashboard'))
		#return '<h1>'+form.username.data + ' '+form.password.data+' '+'</h1>'
		return '<p>Invalid Username or Password</p>'
	return render_template('index.html',form=form)


#The Sign up URL Declearation
@app.route('/signup',methods=['GET','POST'])
def signup():
	form = RegistrationForm()
	if form.validate_on_submit():
		#Generating Password hash
		hashed_password = generate_password_hash(form.password.data,method='sha256')
		#Getting all the value 
		new_user = User(username=form.username.data,password=hashed_password,email=form.email.data,dept=form.dept.data)
		#Inserting the data in the database
		db.session.add(new_user)
		#Commit the database
		db.session.commit()
		return '<p>New User has been created</p>'
		#return '<h1>'+form.username.data+''+form.password.data+''+form.email.data+''+form.dept.data+''+'</h1>'
	return render_template('signup.html',form=form)

#The Admin Signup URL Declearation
@app.route('/adminsignup',methods=['GET','POST'])
def adminsignup():
	form = AdminLogin()
	if form.validate_on_submit():
		hashed_password = generate_password_hash(form.password.data,method='sha256')
		new_admin = Admin(username=form.username.data,password=hashed_password)
		db.session.add(new_admin)
		db.session.commit()
		return '<p>New Admin Created </p>'
	return render_template('adminsignup.html',form=form)

#The Admin Login URL Declearation
@app.route('/adminlogin',methods=['GET','POST'])
def adminlogin():
	form = AdminLogin()
	if form.validate_on_submit():
		#Database Fetching
		user = Admin.query.filter_by(username=form.username.data).first()
		if user:
			if check_password_hash(user.password,form.password.data):
				login_user(user)
				return redirect(url_for('admindashboard'))
		return '<p> Invalid username or password </p>'
		
		#return '<p>'+form.username.data+''+form.password.data+''+'</p>'
	return render_template('adminlogin.html',form=form)

#Admin Dashboard
@app.route('/admindashboard')
@login_required
def admindashboard():
	return render_template('admindash.html',name=current_user.username)

#User Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
	return render_template('dashboard.html',name=current_user.username)

#The Private Upload Page
@app.route('/upload')
@login_required
def upload():
	return render_template('upload.html',name=current_user.username)

#Page that will display after private upload
@app.route('/uploaddone',methods=['GET','POST'])
@login_required
def uploaddone():
	dir_name = current_user.username
	target = os.path.join(APP_ROOT,dir_name)
	print target
	if not os.path.isdir(target):
		os.mkdir(target)
	else:
		print "Unable to create upload Directory {}".format(target)
	print request.files.getlist("file")

	for upload in request.files.getlist("file"):
		print upload 
		filename = upload.filename
		destination = "/".join([target,filename])
		upload.save(destination)
	return render_template('complete.html')

#The Search Page Private Search
@app.route('/search',methods=['GET','POST'])
@login_required
def search():
	#Getting the user name To create the dir with the username
	current_dir = current_user.username 
	full_path   = os.path.realpath(current_dir) #Getting the realpath
	string = request.form['search'] #getting the search String
	#Creating the Command 
	cmd = ["sh","search_shell.sh",full_path,string]
	print cmd
	print string
	#Using subprocess to run the script
	results = subprocess.Popen(cmd,stdout=subprocess.PIPE,
									stderr=subprocess.PIPE,
									stdin=subprocess.PIPE)
	out,err = results.communicate()
	store = out
	#Parsing the Output for HTML display
	results_list = store.split("\n")
	pass_list = []
	urls = []
	file_location = []
	for res in results_list:
		pass_list.append(res)
	#return 'Search String is '+string +full_path
	for files in pass_list:
		urls.append(files.split(':')[0])

	for url in urls:
		file_location.append(send_file(BytesIO(url)))
	return render_template("results.html",results=pass_list,file_loc=file_location)

#The Gloabl Upload or Public Upload URL Declearation
@app.route('/globupload')
@login_required
def globupload():

	return render_template('globup.html',name=current_user.username)


#The Page that will display after the global upload done
@app.route('/globupdone',methods=['GET','POST'])
@login_required
def globupdone():
	#Upload on the ROOT directory not on a specific dir
	# So all user can search
	target = APP_ROOT
	for upload in request.files.getlist("file"):
		print upload 
		filename = upload.filename
		destination = "/".join([target,filename])
		upload.save(destination)
	return render_template('globcomplete.html')

#The global search URL
@app.route('/globsearch')
@login_required
def globsearch():
	return render_template('globsearch.html',name=current_user.username)

#The global Search function
@app.route('/globalsearch',methods=['GET','POST'])
@login_required
def globalsearch():
	string = request.form['search']
	print string 
	cmd = ["sh","globalsearch.sh",string]
	print cmd 
	results = subprocess.Popen(cmd,stdout=subprocess.PIPE,
									stderr=subprocess.PIPE,
									stdin=subprocess.PIPE)
	out,err = results.communicate()
	store = out 
	results_list=store.split("\n")
	pass_list = []
	for res in results_list:
		pass_list.append(res)
	return render_template('globresults.html',results=pass_list,name=current_user.username)
'''
@app.route('/return_files',methods=['GET','POST'])
def return_files():
	current_dir = current_user.username 
	full_path   = os.path.realpath(current_dir)
	string = request.form['search']
	cmd = ["sh","search_shell.sh",full_path,string]
	print cmd
	print string
	results = subprocess.Popen(cmd,stdout=subprocess.PIPE,
									stderr=subprocess.PIPE,
									stdin=subprocess.PIPE)
	out,err = results.communicate()
	store = out
	results_list = store.split("\n")
	pass_list = []
	for res in results_list:
		pass_list.append(res)

	for files in pass_list:
		#print files.split(':')[0]
		return send_file(files.split(':')[0])
	#return send_file('/work/python/flask_application/doclib/cnadmin/Doc.doc')
'''
# The File Downloader URL
@app.route('/files-download')
def file_download():
	return render_template('download.html')

#The file Downloader
@app.route('/return-files/',methods=['GET','POST'])
def return_files():
	#path = '/work/python/flask_application/doclib/file.txt'
	location = request.form['path']
	parsepath = urlparse(location).path
	print parsepath
	#return 'Hello World'
	return send_file(parsepath)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.run(debug=True)