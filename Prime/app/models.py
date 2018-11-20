from datetime import datetime
from app import db,login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(id):
    return users.query.get(int(id))

class users(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(100), nullable=False)
    phoneNo = db.Column(db.Integer, nullable=False)
    dob = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='user.png')
    govtid = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    #otp_rel = db.relationship('otp', backref='user')
    otpuser= db.Column(db.Integer)
    isOTPverified = db.Column(db.Integer,default = 0)


    def __repr__(self):
        return "User('{self.username}')"


class Drivers(db.Model):
    BookingId = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(20))
    Source = db.Column(db.String(60), nullable=False)  
    Destination = db.Column(db.String(60), nullable=False)
    Date = db.Column(db.String(60), nullable=False)
    Time = db.Column(db.String(60), nullable=False)  
    CarModel = db.Column(db.String(60), nullable=False)
    CarNumber = db.Column(db.String(60), nullable=False)
    Cost = db.Column(db.Integer, nullable=False)
    Seats = db.Column(db.Integer, nullable=False)
    Vac_seats=db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "Drivers('{self.BookingId}')"

class Riders(db.Model):
    riderid = db.Column(db.Integer,primary_key=True)   
    driverid = db.Column(db.String(20), nullable=False)
    BookingId = db.Column(db.String(20), nullable=False)
    userid = db.Column(db.String(20), nullable=False)    
    # VacantSeats = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "Riders('{self.riderid}')"


class MyRequests(db.Model):
    Rriderid = db.Column(db.Integer,primary_key=True)   
    Rdriverid = db.Column(db.String(20), nullable=False)
    RBookingId = db.Column(db.String(20), nullable=False)
    Ruserid = db.Column(db.String(20), nullable=False)   

    def __repr__(self):
        return "Request('{self.Rriderid}')"

db.create_all()


