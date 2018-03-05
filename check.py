from flask import Flask , render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField , PasswordField , BooleanField
from wtforms.validators import InputRequired,Email,Length 

app = Flask(__name__)
app.config['SECRET_KEY']='123qdase23@@#asda123'
Bootstrap(app)

class LoginForm(FlaskForm):
	username = StringField('username',validators=[InputRequired(),Length(min=4,max=20)])
	password = PasswordField('username',validators=[InputRequired(),Length(min=6,max=80)])
	remember = BooleanField('remember me')

class RegistrationForm(FlaskForm):
	username = StringField('username',validators=[InputRequired(),Length(min=4,max=20)])
	password = PasswordField('password',validators=[InputRequired(),Length(min=6,max=80)])
	email = StringField('email',validators=[InputRequired(),Email(message='Invalid Email-Id'),Length(max=50)])
	dept = StringField('Deptartment',validators=[InputRequired(),Length(min=2,max=30)])


@app.route('/',methods=['GET','POST'])
def login():
	form = LoginForm()

	return render_template('index.html',form=form)

if __name__ == '__main__':
	app.run(debug=True)