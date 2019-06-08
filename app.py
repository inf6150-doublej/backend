# coding: utf8
import os, sys, sqlite3, hashlib, uuid, io, datetime, random, math
sys.path.append(os.path.dirname(__file__))
from datetime import datetime
from datetime import timedelta  
from sqlite3 import IntegrityError, Error
from apscheduler.schedulers.background import BackgroundScheduler
from db.database import Database
from functools import wraps
from smtplib import SMTPException
from flask import g, Flask, jsonify, session, request
from flask_mail import Mail, Message
from flask_cors import CORS
from src.controllers import room_controller, user_controller, session_controller, reservation_controller, feedback_controller
from src.constants.constants import *
from flask import abort


app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

# Load e-mail configuration
def config_mail():
    config_list = []
    current_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(current_path, 'src/config/conf.txt')
    with open(path) as c:
        for i in range(2):
            line = c.readline()
            options = line.split(':')
            # remove trailing '\n'
            option = options[1]
            option = option.rstrip()
            # list[0] = mail, list[1] = password
            config_list.append(option)
    return config_list


config_list = config_mail()
mail_default_sender = config_list[0]
mail_username = config_list[0]
mail_password = config_list[1]
CORS(app)
app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=mail_username,
    MAIL_DEFAULT_SENDER=mail_default_sender,
    MAIL_PASSWORD=mail_password
)
mail = Mail(app)
app.config['CORS_HEADERS'] = 'Content-Type'
config = {
    'ORIGINS': [
        'http://localhost:3000',  # React
        'https://bookingexpert.herokuapp.com',  # React
    ],
    'SECRET_KEY': '...'
}
CORS(app, supports_credentials=True)

@app.route('/', methods=['GET'])
def start():
    return jsonify({"Allo": "salut"}), 200

#############################
# AUTHENTICATION

# Validate if user is authenticated
def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated(session):
            return send_unauthorized()
        return f(*args, **kwargs)
    return decorated


# Validate if user is an administrator.  Return unauthorized error if not
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        #if not is_admin(session):
           #return send_unauthorized()
        return f(*args, **kwargs)
    return decorated 


# Validate if user is an administrator
def is_admin(session):
    user = session_controller.select_user_by_session_id(session['id'])
    if user is None : return False
    is_admin = user['admin']
    if is_admin: return True 
    return False

# Validate if user is authenticated
def is_authenticated(session):
    return 'id' in session

# Return unauthorized error
def send_unauthorized():
    return jsonify({'error': ERR_UNAUTH}), 401

# User login
@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']

    # data validation
    if request_data_is_invalid(email=email, password=password):
        return jsonify({'error': ERR_FORM}), 400

    user = user_controller.to_dict(user_controller.select_user_by_email(email))

    if user is None:
        return jsonify({'error': ERR_PASSWORD}), 401

    salt = user_controller.get_id_salt(user['id'])
    hashed_password = hashlib.sha512(str(password + salt).encode('utf-8')).hexdigest()
    if hashed_password == user_controller.get_id_hash(user['id']):
        id_session = uuid.uuid4().hex
        session_controller.save(id_session, email)
        session['id'] = id_session
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': ERR_PASSWORD}), 401

# Register a user
@app.route('/register', methods=['POST'])
def register():
    user = request.json['user']
    username = user['username']
    name = user['name']
    last_name = user['last_name']
    phone = user['phone']
    address = user['address']
    password = user['password']
    email = user['email']

    # data validation
    if request_data_is_invalid(username=username, name=name, last_name=last_name, phone=phone, address=address, password=password, email=email):
        return jsonify({'error': ERR_FORM}), 400
    else:
        try:
            salt = uuid.uuid4().hex
            hashed_password = hashlib.sha512(
                str(password + salt).encode('utf-8')).hexdigest()
            user_controller.create(
                username, email, name, last_name, phone, address, salt, hashed_password, False)
            send_email(email, MSG_MAIL_REGISTER_SUCCESS_SUBJECT, MSG_MAIL_REGISTER_SUCCESS_BODY)
            id_session = uuid.uuid4().hex
            session_controller.save(id_session, email)
            session['id'] = id_session
            new_user = user_controller.to_dict(user_controller.select_user_by_email(email))
            return jsonify({'user':new_user}), 201
        # Unique constraint must be respected
        except IntegrityError:
            print('unique user')
            return jsonify({'error': ERR_UNI_USER}), 403
        except SMTPException:
            print('error email')
            # return jsonify({'error': ERR_EMAIL}), 400
            # TODO remove that when testing is over
            id_session = uuid.uuid4().hex
            session_controller.save(id_session, email)
            session['id'] = id_session
            return jsonify({'user':user}), 201

# End user session
@app.route('/logout', methods=['POST'])
def logout():
    if 'id' in session:
        id_session = session['id']
        session.pop('id', None)
        session_controller.delete(id_session)
    return jsonify({'success': True}), 200

# Check if data eis invalid
def request_data_is_invalid(**kwargs):
    for value in kwargs.items():
        if value == '' or value is None:
            return True
    return False

#############################
# USER

# Get user information
@app.route('/getuser', methods=['POST'])
def get_user():
    if not is_authenticated(session):
        return jsonify({'user': None}), 200   
    user = session_controller.select_user_by_session_id(session['id'])
    return jsonify({'user': user}), 200

# Generate password
def generate_token():
    # generate 5 random number
    list_of_ints = random.sample(range(1, 10), 5)
    new_password = ''.join(str(x) for x in list_of_ints)
    return new_password

# Update of delete one user
@app.route('/admin/users/<int:id>', methods=['DELETE', 'PUT'])
def admin_manage_user(id):
    if request.method == 'DELETE':
        user_controller.delete(id)
        return jsonify({'id': id}), 201
    elif request.method == 'PUT':
        user = request.json['user']
        username = user['username']
        name = user['name']
        family_name = user['family_name']
        phone = user['phone']
        address = user['address']
        #password = user['password']
        email = user['email']
        admin = user['admin']
        #salt = uuid.uuid4().hex
        #hash = hashlib.sha512(str(password + salt).encode('utf-8')).hexdigest()
        user_controller.update(id, username, email, name, family_name, phone, address, admin)
        return jsonify({'user': user}), 201
   
# Create a user
@app.route('/admin/users/create', methods=['POST'])
def admin_create_user():
    user = request.json['user']
    username = user['username']
    name = user['name']
    family_name = user['family_name']
    phone = user['phone']
    address = user['address']
    password = user['password']
    email = user['email']
    admin = user['admin']
    salt = uuid.uuid4().hex
    hash = hashlib.sha512(str(password + salt).encode('utf-8')).hexdigest()
    user_controller.create(username, email, name, family_name, phone, address, salt, hash, admin)
    user = user_controller.to_dict(user_controller.select_user_by_email(email))
    return jsonify({'user': user}), 201


# Get all users list
@app.route('/admin/users', methods=['GET'])
def admin_select_all_users():
    users = user_controller.select_all()
    return jsonify({'users':users}), 200

# Recover password
@app.route('/password_recovery/validate', methods=['POST'])
def password_recovery_validate():
    username = request.json['username']
    password = request.json['password']
    token = Database.get_connection().get_account_token_by_username(username)
    if token is None:
        return jsonify({'error': ERR_PASSWORD}), 401

    if password == token:
        # update user
        infos = user_controller.get_user_info_by_username(username)
        user_id = infos[0]
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(
            str(token + salt).encode('utf-8')).hexdigest()
        user_controller.update_user_password(user_id, salt, hashed_password)
        # delete account
        user_controller.delete_account_by_username(username)
        # update session
        id_session = uuid.uuid4().hex
        session_controller.save_session(id_session, username)
        session['id'] = id_session
        redirect_url = GLOBAL_URL + '/myaccount'
        return jsonify({'url': redirect_url}), 201
    else:
        redirect_url = GLOBAL_URL + '/password_recovery/validate'
        return jsonify({'error': ERR_PASSWORD}), 401

# Send recovery e-mail and return error if send does not work
@app.route('/recoverpassword', methods=['POST'])
def password_recovery():
    smtp_response_ok = send_recovery_email(request.json['email'])
    if smtp_response_ok:
        return jsonify({'msg': MSG_MAIL_SENT_RECOVERY}), 200
    else:
        return jsonify({'error': ERR_SERVOR}), 500

# Send recovery e-mail
def send_recovery_email(user_email):
    user = user_controller.select_user_by_email(user_email)
    if user:
        token = generate_token()
        salt = user[7]
        hash_password = hashlib.sha512(str(token + salt).encode('utf-8')).hexdigest()
        user_controller.update_password(int(user[0]), hash_password)
        subject = MSG_MAIL_RECOVER_SUBJECT
        msg = Message(subject, recipients=[user_email])
        msg.body = MSG_MAIL_RECOVER_BODY + token
        try:
            mail.send(msg)
        except SMTPException:
            return False
        return True
    # return true even if email was not sent
    return True




#############################
# FEEDBACK
@app.route('/feedback', methods=['POST'])
def feedback():
    feedback = request.json['feedback']
    email = feedback['email']
    name = feedback['name']
    comment = feedback['comment']
    feedback_controller.create(email, name, comment)
    return jsonify({'feedback': feedback}), 201



#############################
# SEARCH AND RESERVATION

# Search a room
@app.route('/search', methods=['POST'])
def search_rooms():
    data = request.json['data']    
    print((str)(data))
    begin = data['begin']
    end = data['end']
    capacity = data['capacity']
    equipment = data['equipment']
    location = data['location'] if data['location'] != 'everywhere' else ''
    location = '%' + location + '%' 
    room_type = int(data['type'])
    if request_data_is_invalid(query=data):
        return jsonify({'error': ERR_BLANK}), 204
    begin = begin[:24]
    end = end[:24]
    begin = datetime.strptime(begin, "%a %b %d %Y %H:%M:%S")
    end = datetime.strptime(end, "%a %b %d %Y %H:%M:%S")
    rooms = room_controller.room_to_list_of_dict(room_controller.select_all_available(location,capacity, begin, end, equipment, room_type))
    nothingFound = False

    if len(rooms) == 0:
        rooms = room_controller.room_to_list_of_dict(room_controller.select_all_available_capacityexceeded(location,capacity, begin, end, equipment, room_type))
        nothingFound = True

    return jsonify({'rooms': rooms, 'nothingFound': nothingFound}), 200

# Make a reservation
@app.route('/reservation', methods=['POST'])
def reservation():
    data = request.json['data']
    room = data['room']
    user = data['user']
    begin = data['begin']
    end = data['end']
    if(user is None):
        return jsonify({'error': 'Missing User in form'}), 400
    begin = begin[:24]
    end = end[:24]
    begin = datetime.strptime(begin, "%a %b %d %Y %H:%M:%S")
    end = datetime.strptime(end, "%a %b %d %Y %H:%M:%S")
    user_id = int(user['id'])
    room_id = int(room['id'])
    try:
        reservation_id = reservation_controller.save(user_id, room_id, begin, end)
        scheduler.add_job(lambda: reservation_controller.delete(reservation_id), 'cron', hour=end.hour, minute=end.minute)
        send_email(user['email'], MSG_MAIL_RESERVATION_SUCCESS_SUBJECT, MSG_MAIL_RESERVATION_SUCCESS_BODY)
        return jsonify({'success':True}), 201
    except Error:
        return jsonify({'error': 'save reservation error'}), 500

# List of all reservations
@app.route('/admin/reservations', methods=['GET'])
def admin_select_all_reservations():
    reservations = reservation_controller.select_all()
    return jsonify({'reservations':reservations}), 200


@app.route('/admin/reservations/<int:id>', methods=['PUT', 'DELETE'])
def admin_manage_reservation(id):
    if request.method == 'DELETE':
        reservation_controller.delete(id)
        return jsonify({'id': id}), 201
    elif request.method == 'PUT':
        reservation = request.json['reservation']
        room_id = reservation['room_id']
        user_id = reservation['user_id']
        begin = reservation['begin']
        end = reservation['end']
        begin = begin[:24]
        end = end[:24]
        begin = datetime.strptime(begin, "%a %b %d %Y %H:%M:%S")
        end = datetime.strptime(end, "%a %b %d %Y %H:%M:%S")
        user_id = int(user_id)
        room_id = int(room_id)
        reservation_controller.update(id, user_id, room_id, begin, end)
        return jsonify({'reservation': reservation }), 201
    

@app.route('/admin/reservations/create', methods=['POST'])
def admin_create_reservation():
    reservation = request.json['reservation']
    room_id = reservation['room_id']
    user_id = reservation['user_id']
    begin = reservation['begin']
    end = reservation['end']
    begin = begin[:24]
    end = end[:24]
    begin = datetime.strptime(begin, "%a %b %d %Y %H:%M:%S")
    end = datetime.strptime(end, "%a %b %d %Y %H:%M:%S")
    user_id = int(user_id)
    room_id = int(room_id)
    reservation= reservation_controller.save(user_id, room_id, begin, end)
    return jsonify({'reservation':reservation}), 201   

#############################
# ROOMS

# Get all rooms
@app.route('/admin/rooms', methods=['GET'])
def get_rooms():
    rooms = room_controller.room_to_list_of_dict(room_controller.select_all())   
    return jsonify({'rooms': rooms}), 200

# Create a room
@app.route('/admin/rooms', methods=['POST'])
@admin_required
def create_room():  
    name = request.json['room']['name']
    type = request.json['room']['type']
    capacity = request.json['room']['capacity']
    description = request.json['room']['description']
    equipment = request.json['room']['equipment']
    city = request.json['room']['city']
    postal_code = request.json['room']['postalCode']
    new_id = room_controller.create(name, type, capacity, description, equipment, city, postal_code)
    return jsonify({'id': new_id}), 201

# Delete a room
@app.route('/admin/rooms/<int:room_id>', methods=['DELETE'])
@admin_required
def delete_room_by_id(room_id):
    rooms = room_controller.select_by_id(room_id)
    if rooms is None:
        return jsonify({'error': 'Delete error'}), 400
    else:
        room_controller.delete(room_id)
        return jsonify({'id': room_id}), 201

# Update a room
@app.route('/admin/rooms/<int:room_id>', methods=['PUT'])
@admin_required
def update_room_by_id(room_id):
    rooms = room_controller.select_by_id(room_id)
    if rooms is None:
        return jsonify({'error': 'failed to update this room'}), 204
    else:        
        id = room_id
        room = request.json['room']
        name = room['name']
        type = room['type']
        capacity = room['capacity']
        description = room['description']
        equipment = room['equipment']
        city = room['city']
        postal_code = room['postalCode']
        room_controller.update(id, name, type, capacity, description, equipment, city, postal_code)
        return jsonify({'room': room}), 201

# Get one room
@app.route('/admin/rooms/<int:room_id>', methods=['GET'])
def get_room_by_id(room_id):
    rooms = room_controller.select_by_id(room_id)
    if rooms is None:
        return jsonify({'error': 'failed to get this room'}), 204
    else:
        return jsonify({'rooms': rooms}), 200

# Send an e-mail
def send_email(recipient, subject, message):
    date = datetime.now().strftime('%Y-%m-%d')
    msg = Message(subject, recipients=[recipient])
    msg.body = message
    mail.send(msg)

# Get rooms usage stats
@app.route('/admin/rooms/usage/<selected_date>', methods=['GET'])
def get_rooms_usage(selected_date):
    
    selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    stats = room_controller.usage_to_dict(room_controller.select_usage(selected_date, selected_date + timedelta(days=1) ))   
    return jsonify({'stats': stats}), 200


#############################
# ERROR HANDLER

# For page not found 404 error
@app.errorhandler(404)
def page_not_found():
    return jsonify({'error': ERR_404}), 404

# For page not found 404 error
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': ERR_404}), 404


# For Internal server error 500
@app.errorhandler(500)
def page_not_found(e):
    return jsonify({'error': 'Internal server error'}), 500


app.secret_key = '(*&*&322387he738220)(*(*22347657'


if __name__ == '__main__':
    app.run(debug=True)