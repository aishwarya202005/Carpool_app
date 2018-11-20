import os
import binascii
import random
from flask import render_template
from sqlalchemy import and_, create_engine
from flask import url_for, redirect, request, make_response,flash
# Importing Session Object to use Sessions
from flask import session, logging
from app import app,db,bcrypt
from app.models import Drivers,Riders,MyRequests
from app.models import users
from flask_mail import Mail,Message
from passlib.hash import sha256_crypt
from functools import wraps
import smtplib
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from forms import RegistrationForm, LoginForm, UpdateAccountForm
from flask_login import login_user,current_user,logout_user,login_required
from datetime import datetime, date


app.config.from_pyfile('config.cfg')
 
mail = Mail(app)

s = URLSafeTimedSerializer('Thisisasecret!')

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
	return render_template('index.html')


#Registration Functions
# @app.route('/register')
# def register():
# 	return render_template('register.html')

@app.route('/register', methods = ['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		otp_num = random.randint(1000,9999)
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = users(username = form.username.data,name = form.name.data,gender = form.gender.data,phoneNo = form.phoneNo.data,dob = form.dob.data,
		email = form.email.data,govtid = form.govtId.data,password = hashed_password,otpuser=otp_num)
		email = form.email.data
		user_name= form.username.data
		token = s.dumps(email, salt='email-confirm')
		msg = Message('Confirm Email', sender = 'help.primeriders@gmail.com',recipients=[email])
		link = url_for('confirm_email',token = token, _external = True)
		msg.body = 'Your link is {}'.format(link)
		mail.send(msg)
		#otp_num = random.randint(1000,9999)
		#token1 = s.dumps(otp_num, salt='otp-confirm')
		msg_otp = Message('Confirm OTP', sender = 'help.primeriders@gmail.com',recipients=[email])
		#link_otp = url_for('confirm_otp',token = otp_num, _external = True)
		msg_otp.body = 'Your otp is {}'.format(otp_num)
		mail.send(msg_otp)
		
		#check_otp = url_for('confirm_otp',user=user)
		#otp1 = otp(otp = otp_num)
		#db.session.add(otp1)
		db.session.add(user)
		db.session.commit()
		#flash('Your account has now been created.. You can now log in !!','success')
		#return redirect(url_for('login'))
	
		return render_template('otp.html',user_name=user_name,title = 'Verification',form=form)
	return render_template('register.html',title = 'Register',form=form)	


@app.route('/confirm_email/<token>')
def confirm_email(token):
	try:
		email = s.loads(token,salt = 'email-confirm',max_age=3600)
	except SignatureExpired:
		return '<h1>Your token expired!</h1>'
	return '<h1>Email Id confirmed!</h1>'
@app.route('/confirm_otp_next',methods=['GET','POST'])
def confirm_otp_next():
	print "inside confirm otp"
	name=request.args.get('values')
	print name
	otp_obj=users.query.filter_by(username=name).first()
	otp_num=otp_obj.otpuser
	entered_otp=request.form["otpp"]
	print entered_otp
	print "displayed"
	print otp_num
	print "displaying isOTPverified :"
	print otp_obj.isOTPverified
	if (int(otp_num) == int(entered_otp) and otp_obj.isOTPverified == 0) :
		print "otp verfied"
		otp_obj.isOTPverified = 1
		#db.session.add(users)
		db.session.commit()
		flash('Your account has now been created.. You can now log in !!','success')
		return redirect(url_for('login'))
	else :
		print "Not verfied"
		flash('Please enter your details again to get new OTP','danger')
		db.session.delete(otp_obj)
		db.session.commit()
		# return render_template('register.html',title = 'Register')
		return redirect(url_for('register'))		

#Login Functions

@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = users.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data) :
			if user.isOTPverified == 1:	
				login_user(user, remember=form.remember.data)
				next_page = request.args.get('next')
				return redirect(next_page) if next_page else redirect(url_for('index'))
			else:
				flash('OTP was not verified.. Kindly register again..', 'danger')
				db.session.delete(user)
				db.session.commit()
				return redirect(url_for('register'))
		else:
			flash('Login Unsuccessful. Please check email and password', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('index'))


def save_picture(form_picture):
	#create a random number in random_hex
	#random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	#filename = form_picture.filename
	picture_fn = binascii.hexlify(os.urandom(24)) + f_ext
	#picture_fn = _ + f_ext
	#print ("shafiya")
	print picture_fn
	picture_path = os.path.join(app.root_path,'static/profile_pics',picture_fn)
	#print('path')
	#print picture_path
	#destination = '/'.join(target,filename)
	form_picture.save(picture_path)
	return picture_fn

#Profile of User after login
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	dri_id=current_user.id
	all_req = MyRequests.query.filter_by(Rdriverid=dri_id).all()
	print "testing-------"
	# print all_req[0].Ruserid
	print "done-------"
	as_driver= Drivers.query.filter_by(userid=dri_id).all()
	past_driver=[]
	coming_driver=[]
	for x in as_driver :
		datetime_object = datetime.strptime(x.Date, '%Y-%m-%d')
		print "object datetime"
		print datetime_object
		print "Aj ki date"
		print datetime.now()
		if datetime_object < datetime.now() :
			past_driver.append(x)
			print x.Date
		else :
			coming_driver.append(x)
			print "baad ki date ----"	

	as_rider = Riders.query.filter_by(userid=dri_id).all()
	as_rider_details=[]
	for detail in as_rider :
		as_rider_details.append(Drivers.query.filter_by(BookingId=detail.BookingId).first()) 


	past_rider=[]
	coming_rider=[]	
	for x in as_rider_details :
		datetime_object = datetime.strptime(x.Date, '%Y-%m-%d')
		print "object datetime"
		print datetime_object
		print "Aj ki date"
		print datetime.now()
		if datetime_object < datetime.now() :
			past_rider.append(x)
			print x.Date
		else :
			coming_rider.append(x)
			print "baad ki date ----"	
	return render_template('account.html', title='Account',
						   image_file=image_file, form=form,all_req=all_req,
						   past_driver=past_driver,coming_driver=coming_driver,
						   past_rider=past_rider,coming_rider=coming_rider)



@app.route('/selride', methods=['GET', 'POST'])
def selride():
    name = request.args.get('values')
    #print name
    #print "heeeeeeeeeeeeheeeeeee"
    selected_dri = Drivers.query.filter_by(BookingId=name).first()
    return render_template('select_driver.html',selected_dri=selected_dri)


@app.route('/list_req')
def list_req():
	# driver user id
	# usernam=session["user"]
	#userobj=users.query.filter_by(username=usernam).first()	    
	#dri_id = userobj.id
	dri_id=current_user.id
	all_req = MyRequests.query.filter_by(Rdriverid=dri_id).all()
	return render_template('list_requests.html',all_req=all_req)


@app.route('/accept_req', methods=['GET', 'POST'])
def accept_req():
	userobjid = request.args.get('value1')
	b_id = request.args.get('value2')
	#insertion in booking(riders) table
	# driver user id
	#usernam=session["user"]
	usernam=current_user.username
	userobj=users.query.filter_by(username=usernam).first()	    
	dri_id = userobj.id
	vacant=Drivers.query.filter_by(BookingId=b_id).first()
	vac_seat = vacant.Vac_seats
	if int(vac_seat) == 0 :
		objjaroori=users.query.filter_by(id=userobjid).first()
		emailto=objjaroori.email
		email = 'help.primeriders@gmail.com'
		password = 'Rider@prime1'		
		send_to_email = emailto
		subject = 'Ride notification'
		message = 'Sorry no seats available for requested ride. Please consider other ride options. \n\n Regards, \n PRIME RIDE Team '
		msg = MIMEMultipart()
		msg['From'] = email
		msg['To'] = send_to_email
		msg['Subject'] = subject
		msg.attach(MIMEText(message, 'plain'))
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(email, password)
		text = msg.as_string()
		server.sendmail(email, send_to_email, text)
		server.quit()
		return render_template('noseats.html')
	else :
		vacant.Vac_seats = int(vac_seat) -1
		db.session.commit()
		objname = Drivers()
		insert =Riders(driverid=dri_id,BookingId=b_id,userid=userobjid)
		db.session.add(insert)
		db.session.commit()
		sendto = userobj.email
		email = 'help.primeriders@gmail.com'
		password = 'Rider@prime1'		
		send_to_email = sendto
		subject = 'Ride notification'
		message = 'You have successfully added a rider for your journey. Please visit your profile for further details. \n\n Regards, \n PRIME RIDE Team '
		msg = MIMEMultipart()
		msg['From'] = email
		msg['To'] = send_to_email
		msg['Subject'] = subject
		msg.attach(MIMEText(message, 'plain'))
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(email, password)
		text = msg.as_string()
		server.sendmail(email, send_to_email, text)
		server.quit()
			#inform requester about accepting
		objjaroori=users.query.filter_by(id=userobjid).first()
		emailto=objjaroori.email
		email = 'help.primeriders@gmail.com'
		password = 'Rider@prime1'		
		send_to_email = emailto
		subject = 'Ride notification'
		message = 'Congratulations, your ride is confirmed. Please visit your profile for further details. \n\n Regards, \n PRIME RIDE Team '
		msg = MIMEMultipart()
		msg['From'] = email
		msg['To'] = send_to_email
		msg['Subject'] = subject
		msg.attach(MIMEText(message, 'plain'))
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(email, password)
		text = msg.as_string()
		server.sendmail(email, send_to_email, text)
		server.quit()		
	
	#deletion
	
	obj = MyRequests.query.filter_by(Ruserid=userobjid,RBookingId=b_id).first()
	db.session.delete(obj)
	db.session.commit()


	# redirect to profile page
	return render_template('index.html')

	


@app.route('/delete_req', methods=['GET', 'POST'])
def delete_req():
	print "printing----"
	userobjid = request.args.get('value1')
	b_id = request.args.get('value2')
	print userobjid
	obj = MyRequests.query.filter_by(Ruserid=userobjid,RBookingId=b_id).first()
	db.session.delete(obj)
	db.session.commit()

	#inform requester about rejection
	newobj=users.query.filter_by(id=userobjid).first()
	emailto=newobj.email
	email = 'help.primeriders@gmail.com'
	password = 'Rider@prime1'		
	send_to_email = emailto
	subject = 'Ride notification'
	message = 'Sorry, the driver has declined your request. Kindly consider the other available options. \n\n Regards, \n PrimeRIDE Team '
	msg = MIMEMultipart()
	msg['From'] = email
	msg['To'] = send_to_email
	msg['Subject'] = subject
	msg.attach(MIMEText(message, 'plain'))
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(email, password)
	text = msg.as_string()
	server.sendmail(email, send_to_email, text)
	server.quit()
	# redirect to profile page
	return render_template('index.html')


@app.route('/req_details', methods=['GET', 'POST'])
def req_details():
	print "hii"
	# value1= user id
	u_id = request.args.get('value1')
	b_id = request.args.get('value2')
	userobj=users.query.filter_by(id=u_id).first()	
	# usernam=session["user"]
	# userobj=users.query.filter_by(username=usernam).first()	    
	# dri_id = userobj.id
    # all_req = MyRequests.query.filter_by(Ruserid=dri_id).all()
	return render_template('req_details.html',userobj=userobj,b_id=b_id)

@app.route('/req_ride', methods=['GET', 'POST'])
def req_ride():
    name = request.args.get('values')
    print name
    print "heeeeeeeeeeeeheeeeeee"
    selected_dri = Drivers.query.filter_by(BookingId=name).first()
    return render_template('req_ride.html',selected_dri=selected_dri)



@app.route('/success_booking')
@login_required
def success_booking():
	#get email from session
	name = request.args.get('values')
	print "inside success booking"
	print name
	data=Drivers.query.filter_by(BookingId=name).first()
	print data.CarModel
	available=data.Vac_seats
	print "available seats"
	print available
	# driver user id
	#usernam=session["user"]
	usernam=current_user.username
	userobj=users.query.filter_by(username=usernam).first()	
	if int(available) == 0 :
		
		#userto=userobj.userid
		print "user to"
		#print userto
		#obj=users.query.filter_by(id=userto).first()
		print userobj.email
		emailto=userobj.email
		email = 'help.primeriders@gmail.com'
		password = 'Rider@prime1'		
		send_to_email = emailto
		subject = 'Ride notification'
		message = 'Sorry for inconvenience. No seats are available for the selected ride. We will notify you as soon as rides will be available.\n Regards, \n PRIME RIDE Team '
		msg = MIMEMultipart()
		msg['From'] = email
		msg['To'] = send_to_email
		msg['Subject'] = subject
		msg.attach(MIMEText(message, 'plain'))
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(email, password)
		text = msg.as_string()
		server.sendmail(email, send_to_email, text)
		server.quit()
		return render_template('sorry.html')
	else :
		bookingid=name
		#data is driver object
		driverid=data.userid
		#requester is logged in			
		driverobj=users.query.filter_by(id=driverid).first()
		sendto=driverobj.email
		print "drivers email"
		print sendto
		insert=MyRequests(Rdriverid=driverid,RBookingId=bookingid,Ruserid=userobj.id)
		db.session.add(insert)
		db.session.commit()	
		email = 'help.primeriders@gmail.com'
		password = 'Rider@prime1'		
		send_to_email = sendto
		subject = 'Ride request notification'
		message = 'You have a new request for your ride offer.Please visit your profile to accept or reject request\n Regards, \n PRIME RIDE Team '
		msg = MIMEMultipart()
		msg['From'] = email
		msg['To'] = send_to_email
		msg['Subject'] = subject
		msg.attach(MIMEText(message, 'plain'))
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(email, password)
		text = msg.as_string()
		server.sendmail(email, send_to_email, text)
		server.quit()			
		print "displayed booking id"
		return render_template('success_booking.html')


@app.route('/findride')
def find_ride():
    return render_template('findride.html')



@app.route('/offerride')
def offer_ride():
    return render_template('offerride.html')

@app.route('/findNext',methods = ['GET','POST'])
def findNext():
	startplace=request.form["source"]
	endplace = request.form["destination"]
	date_ = request.form["date"]
	time_ = request.form["time"]
	#idhere=current_user.id
	driverdetails=Drivers.query.filter_by(Source=startplace,Destination=endplace,Date=date_).all()
	#filter_by(Source=startplace,Destination=endplace,Date=date_,Time=time_).first()
	#for drivers in driverdetails
	#print driverdetails.BookingId
	return render_template('gridview.html',driverdetails=driverdetails)



@app.route('/offerNext', methods = ['GET','POST'])
@login_required
def offerNext():
	vac=request.form["noofseats"]
	vac=int(vac)-1
	# idhere=session["user"]

	# details=users.query.filter_by(username=idhere).first()
	booking = Drivers(userid=current_user.id,Source=request.form["source"],  Destination=request.form["destination"], 
	Date=request.form["date"],Time=request.form["time"],
	CarModel=request.form["carmodel"],CarNumber=request.form["carno"],Cost=request.form["cost"],
	Seats=request.form["noofseats"],Vac_seats=vac)
	print request.form["time"]
	print "time-----------"
	db.session.add(booking)
	db.session.commit()
	flash('Congratulations your ride details has been saved and you will be notified via email', 'success')
	email = 'help.primeriders@gmail.com'
	password = 'Rider@prime1'
	# change here accordingly
	
	#
	send_to_email = current_user.email
	subject = 'Ride notification'
	message = 'Congratulations your ride details has been saved and you will get regular updates regarding riders'
	msg = MIMEMultipart()
	msg['From'] = email
	msg['To'] = send_to_email
	msg['Subject'] = subject

	msg.attach(MIMEText(message, 'plain'))

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(email, password)
	text = msg.as_string()
	server.sendmail(email, send_to_email, text)
	server.quit()
	#redirect to profile or home
	# flash('Your ride offer has been successfully published','success')
	return render_template('index.html')

@app.route('/send_useremail', methods=['GET', 'POST'])
def send_useremail():
	bande_ki_email=	request.form['email']
	print bande_ki_email
	bande_ka_naam= request.form["name"]
	print bande_ka_naam
	bande_ka_phone= request.form["phone"]
	print bande_ka_phone
	bande_ka_msg=request.form["message"]
	print bande_ka_msg
	#mail feedback from banda	
	emailto='help.primeriders@gmail.com'
	email = 'help.primeriders@gmail.com'
	password = 'Rider@prime1'		
	send_to_email = emailto
	subject = 'Feedback'
	message = bande_ka_msg +"\nsent by:" + bande_ki_email + "---" +bande_ka_naam + "\n Phone no. "+bande_ka_phone
	print message
	msg = MIMEMultipart()
	msg['From'] = email
	msg['To'] = send_to_email
	msg['Subject'] = subject
	msg.attach(MIMEText(message, 'plain'))
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(email, password)
	text = msg.as_string()
	server.sendmail(email, send_to_email, text)
	server.quit()
	# redirect to profile page
	flash('Thank you for your valuable feedback','success')
	return render_template('index.html')	

@app.route('/del_ride', methods=['GET', 'POST'])
def del_ride():	
	print "deleting"
	b_id = request.args.get('value')
	to_del=MyRequests.query.filter_by(RBookingId=b_id).all()
	for x in to_del :
		requester_email_obj=users.query.filter_by(id=x.Ruserid).first()
		details_obj=Drivers.query.filter_by(BookingId=b_id).first()
		#inform requester about rejection	
		emailto=requester_email_obj.email
		email = 'help.primeriders@gmail.com'
		password = 'Rider@prime1'		
		send_to_email = emailto
		subject = 'Ride notification'
		message = 'Sorry, the driver has cancelled the following ride.\n Source: '+details_obj.Source+' \n Destination: '+details_obj.Destination+'\n Dated:'+details_obj.Date+' Kindly consider the other available options. \n\n Regards, \n PrimeRIDE Team '
		msg = MIMEMultipart()
		msg['From'] = email
		msg['To'] = send_to_email
		msg['Subject'] = subject
		msg.attach(MIMEText(message, 'plain'))
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(email, password)
		text = msg.as_string()
		server.sendmail(email, send_to_email, text)
		server.quit()
		db.session.delete(x)
		db.session.commit()
	new_del=Riders.query.filter_by(BookingId=b_id).all()
	for x in new_del :
		requester_email_obj=users.query.filter_by(id=x.userid).first()
		details_obj=Drivers.query.filter_by(BookingId=b_id).first()
		#inform requester about rejection	
		emailto=requester_email_obj.email
		email = 'help.primeriders@gmail.com'
		password = 'Rider@prime1'		
		send_to_email = emailto
		subject = 'Ride notification'
		message = 'Sorry, the driver has cancelled the following ride.\n Source: '+details_obj.Source+' \n Destination: '+details_obj.Destination+'\n Dated:'+details_obj.Date+' Kindly consider the other available options. \n\n Regards, \n PrimeRIDE Team '
		msg = MIMEMultipart()
		msg['From'] = email
		msg['To'] = send_to_email
		msg['Subject'] = subject
		msg.attach(MIMEText(message, 'plain'))
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(email, password)
		text = msg.as_string()
		server.sendmail(email, send_to_email, text)
		server.quit()
		db.session.delete(x)
		db.session.commit()
	dri_del=Drivers.query.filter_by(BookingId=b_id).first()	
	db.session.delete(dri_del)
	db.session.commit()	
	flash('You have successfully deleted your ride offer','success')
	return render_template('index.html')


	print "printing----"
	

	
	


