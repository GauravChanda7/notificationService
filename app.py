from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from pytz import timezone as pytz_timezone
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import Client
from dotenv import load_dotenv
import math
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notificationService.db'
db = SQLAlchemy(app)

class UserBase(db.Model):
    __tablename__ = 'user_base'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), unique = True, nullable = False)
    mailId = db.Column(db.String(50), unique = True, nullable = False)
    phoneNumber = db.Column(db.String(15), unique = True, nullable = False)
    password = db.Column(db.String(128), nullable = False)
    createdAt = db.Column(db.DateTime, default = lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<User id={self.id}, name={self.name}>'
    


class Messages(db.Model):
    __tablename__ = 'messages'

    sno = db.Column(db.Integer, primary_key = True)
    toId = db.Column(db.Integer, db.ForeignKey('user_base.id'), nullable = False)
    fromId = db.Column(db.Integer, db.ForeignKey('user_base.id'), nullable = False)
    name = db.Column(db.String(50), nullable = False)
    subject = db.Column(db.String(100), nullable = False)
    body = db.Column(db.Text, nullable = False)
    sentAt = db.Column(db.DateTime, default = lambda: datetime.now(timezone.utc))

    sender = db.relationship('UserBase', foreign_keys = [fromId], backref = 'sent_messages')
    receiver = db.relationship('UserBase', foreign_keys = [toId], backref = 'received_messages') 

    def __repr__(self):
        return f'<User {self.sno}>'




@app.route('/')
def index():
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
                return redirect(f'/homepage/{user.id}')
            else:
                flash('Incorrect password', 'error')
                return redirect('/login')
        else:
            flash('Email not registered', 'error')
            return redirect('/login')
        
    else:
        return render_template('login.html')
    


@app.route('/homepage/<int:id>')
def homepage(id):
    return render_template('homepage.html', id = id)



@app.route('/notifications/send/<int:id>', methods = ['GET', 'POST'])
def send(id):
    if request.method == 'POST':
        name = request.form.get('name').strip()
        subject = request.form.get('subject').strip()
        body = request.form.get('message').strip()

        action = request.form.get('action')


        if action == 'Submit Email':
            recpname = request.form.get('recpmail')



        elif action == 'Submit Message':
            accountSID = os.getenv('ACCOUNT_SID')
            authToken = os.getenv('AUTH_TOKEN')
            twilioPhone = os.getenv('TWILIO_PHONE')
            recpPhone = request.form.get('recpnum')

            body = f'From: {name}' + '\n' + f'Subject: {subject}' + '\n' + body

            client = Client(accountSID, authToken)
            message = client.messages.create(to = recpPhone,
                                             from_ = twilioPhone,
                                             body = body)
            
            print(f'Message sent! SID: {message.sid}')
            return redirect(f'/homepage/{id}')


        elif action == 'Submit Notification':
            recpname = request.form.get('recpname')
            toUser = UserBase.query.filter_by(name = recpname).first()

            newMessage = Messages(toId = toUser.id, 
                                  fromId = id, 
                                  name = name,
                                  subject = subject,
                                  body = body)
            
            try:
                db.session.add(newMessage)
                db.session.commit()
                return redirect(f'/homepage/{id}')
            except Exception as e:
                return f'Error while adding message to db: {e}'

    else:
        return render_template('sendnotif.html', id = id)   
    


@app.route('/notifications/inbox/<int:id>/<int:pageNo>', methods = ['GET', 'POST'])
def inbox(id, pageNo):
    notifPerPage = 10
    offset = (pageNo - 1) * notifPerPage
    totalNotif = Messages.query.filter_by(toId = id).count()
    totalPage = math.ceil( totalNotif / notifPerPage ) 

    notificationList = Messages.query.filter_by(toId = id).order_by(Messages.sentAt).offset(offset).limit(notifPerPage).all()
    ist = pytz_timezone('Asia/Kolkata')

    for notification in notificationList:
        if notification.sentAt.tzinfo is None:
            notification.sentAt = notification.sentAt.replace(tzinfo = timezone.utc)
        notification.sentAt = notification.sentAt.astimezone(ist)

    return render_template('inbox.html', userId = id, notificationList = notificationList, pageNo = pageNo, totalPage = totalPage)
    


@app.route('/delete/<int:userId>/<int:deleteId>', methods = ['POST'])
def delete(userId, deleteId):
    if request.method == 'POST':
        notifToDelete = Messages.query.get(deleteId)

        try:
            db.session.delete(notifToDelete)
            db.session.commit()
            return redirect(f'/notifications/inbox/{userId}/1')
        except Exception as e:
            return f'Error while deleting message: {e}'



@app.route('/view/<int:id>/<int:messageSno>')
def view(id, messageSno):
    message = Messages.query.get(messageSno)
    ist = pytz_timezone('Asia/Kolkata')
    if message.sentAt.tzinfo is None:
        message.sentAt = message.sentAt.replace(tzinfo = timezone.utc)
    message.sentAt = message.sentAt.astimezone(ist)
    
    return render_template('view.html', message = message)
    





if __name__ == '__main__':

    with app.app_context():
        db.create_all()
        print("Database ready")

    app.run(debug = True)