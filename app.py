from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'devsecretkey123'            #use random later to assign key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notificationService.db'
db = SQLAlchemy(app)

class UserBase(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    mailId = db.Column(db.String(50), unique = True, nullable = False)
    phoneNumber = db.Column(db.String(15), unique = True, nullable = False)
    password = db.Column(db.String(128), nullable = False)
    createdAt = db.Column(db.DateTime, default = lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<User {self.id}>'




@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'Sign-in':
            return redirect('/signin')
        elif action == 'Login':
            return redirect('/login')
        
    else:
        return render_template('index.html')



@app.route('/signin', methods = ['GET', 'POST'])
def signin():
    if request.method == 'POST':
        name = request.form.get('name')
        mailId = request.form.get('mailId')
        phoneNumber = request.form.get('phoneNumber')
        password = request.form.get('password')

        hashedPassword = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        newUser = UserBase(name = name, 
                        mailId = mailId, 
                        phoneNumber = phoneNumber, 
                        password = hashedPassword)
        
        try:
            db.session.add(newUser)
            db.session.commit()
            return redirect('/login')
        except Exception as e:
            return f'Error while sign-up: {e}'
        
    else:
        return render_template('signin.html')
    

    
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        mailId = request.form.get('mailId').strip()
        password = request.form.get('password').strip()

        user = UserBase.query.filter_by(mailId = mailId).first()
        if user:
            if check_password_hash(user.password, password):
                return redirect('/homepage')
            else:
                flash('Incorrect password', 'error')
                return redirect('/login')
        else:
            flash('Email not registered', 'error')
            return redirect('/login')
        
    else:
        return render_template('login.html')
    


@app.route('/homepage', methods = ['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        pass
    else:
        return render_template('homepage.html')




if __name__ == '__main__':
    app.run(debug = True)