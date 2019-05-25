# coding: utf8
import os, sys, sqlite3, hashlib, uuid, io, datetime, random, math
sys.path.append(os.path.dirname(__file__))
from sqlite3 import IntegrityError, Error
from functools import wraps
from smtplib import SMTPException
from flask import g, Flask, make_response, jsonify, session, request
from flask_mail import Mail, Message
from flask_cors import CORS
from src.controllers import room_controller, user_controller, session_controller, reservation_controller
from src.constants.constants import *


app = Flask(__name__)

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
#TODO white list in CORS

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


@app.errorhandler(404)
def page_not_found():
    return make_response(jsonify({'success': False}), 404)


def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated(session):
            return send_unauthorized()
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_admin(session):
            return send_unauthorized()
        return f(*args, **kwargs)
    return decorated    


def is_admin(session):
    admin = session_controller.select_user_by_session_id(session['id'])
    if admin is None : return False
    return True

def is_authenticated(session):
    return 'id' in session


def send_unauthorized():
    return make_response(jsonify({'success': False, 'error': ERR_UNAUTH}))


@app.route('/', methods=['GET'])
def start():
    return make_response(jsonify({"alo": "salut"}), 200)


@app.route('/getuser', methods=['POST'])
def get_user():
    user = session_controller.select_user_by_session_id(session['id'])
    return make_response(jsonify({"user": user}), 200)


@app.route('/search', methods=['POST'])
def search_room():
    data = request.json['data']
    if request_data_is_invalid(query=data):
        return make_response(jsonify({'success': False, 'error': ERR_BLANK})), 204
    rooms = room_controller.select_all()
    return make_response(jsonify({'rooms': rooms})), 200


@app.route('/reservation', methods=['POST'])
def reservation():
    data = request.json['data']
    room = data['room']
    user = data['user']
    begin = data['begin']
    end = data['end']
    begin = begin[:24]
    end = end[:24]
    begin = datetime.datetime.strptime(begin, "%a %b %d %Y %H:%M:%S")
    end = datetime.datetime.strptime(end, "%a %b %d %Y %H:%M:%S")
    user_id = int(user['id'])
    room_id = int(room[0])
    if request_data_is_invalid(query=data):
        return make_response(jsonify({'success': False, 'error': ERR_BLANK})), 204
    reservation_controller.save(user_id, room_id, begin, end)
    return make_response(jsonify({'succes':True })), 201

@app.route('/rooms', methods=['GET'])
def get_rooms():
    rooms = room_controller.room_to_list_of_dict(room_controller.select_all())
    return make_response(jsonify({'rooms': rooms}), 200)

@app.route('/rooms', methods=['POST'])
@admin_required
def create_room():   
    name = request.json['name']
    type = request.json['type']
    capacity = request.json['capacity']
    description = request.json['description']
    reservation_id = request.json['reservation_id']
    equipment_id = request.json['equipment_id']
    new_id = room_controller.create(name,type,capacity,description,reservation_id, equipment_id)
    return make_response(jsonify({'id': new_id}), 200)

@app.route('/rooms/<int:room_id>', methods=['DELETE'])
@admin_required
def delete_room_by_id(room_id):
    rooms = room_controller.select_by_id(room_id)
    if rooms is None:
        return make_response(jsonify({'success': False})), 204
    else:
        room_controller.delete(room_id)
        return make_response(jsonify({'success': True})), 200

@app.route('/rooms/<int:room_id>', methods=['PUT'])
@admin_required
def update_room_by_id(room_id):
    rooms = room_controller.select_by_id(room_id)
    if rooms is None:
        return make_response(jsonify({'success': False})), 204
    else:
        id = request.json['id']
        name = request.json['name']
        type = request.json['type']
        capacity = request.json['capacity']
        description = request.json['description']
        reservation_id = request.json['reservation_id']
        equipment_id = request.json['equipment_id']
        rooms = room_controller.update(id,name,type,capacity,description,reservation_id,equipment_id)
        return make_response(jsonify({'rooms': rooms})), 200

@app.route('/admin/reservations', methods=['GET'])
def admin_select_all_reservations():
    reservations = reservation_controller.select_all()
    return make_response(jsonify({'reservations':reservations})), 200


@app.route('/admin/reservations/<int:id>', methods=['PUT', 'DELETE'])
def admin_manage_reservation(id):
    if request.method == 'DELETE':
        reservation_controller.delete(id)
        return make_response(jsonify({'id': id})), 201
    elif request.method == 'PUT':
        data = request.json[data]
        room = data['room']
        user = data['user']
        begin = data['begin']
        end = data['end']
        begin = begin[:24]
        end = end[:24]
        begin = datetime.datetime.strptime(begin, "%a %b %d %Y %H:%M:%S")
        end = datetime.datetime.strptime(end, "%a %b %d %Y %H:%M:%S")
        user_id = int(user['id'])
        room_id = int(room[0])
        reservation_controller.update(user_id, room_id, begin, end)
        if request_data_is_invalid(query=user_id) and request_data_is_invalid(query=room_id) and request_data_is_invalid(query=id):
            return make_response(jsonify({'success': False, 'error': ERR_BLANK})), 204
        reservation_controller.save(user_id, room_id, begin, end)
        return make_response(jsonify({'succes':True })), 201
    

@app.route('/admin/reservations/create', methods=['POST'])
def admin_create_reservation():
    data = request.json['data']
    room = data['room']
    user = data['user']
    begin = data['begin']
    end = data['end']
    begin = begin[:24]
    end = end[:24]
    begin = datetime.datetime.strptime(begin, "%a %b %d %Y %H:%M:%S")
    end = datetime.datetime.strptime(end, "%a %b %d %Y %H:%M:%S")
    user_id = int(user['id'])
    room_id = int(room[0])
    reservation_controller.save(user_id, room_id, begin, end)
    if request_data_is_invalid(query=user_id) and request_data_is_invalid(query=room_id):
        return make_response(jsonify({'success': False, 'error': ERR_BLANK})), 204
    reservation_controller.save(user_id, room_id, begin, end)
    return make_response(jsonify({'succes':True })), 201
     


@app.route('/rooms/<int:room_id>', methods=['GET'])
def get_room_by_id(room_id):
    rooms = room_controller.select_by_id(room_id)
    if rooms is None:
        return make_response(jsonify({'success': False})), 204
    else:
        return make_response(jsonify({'rooms': rooms})), 200


@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']

    # data validation
    if request_data_is_invalid(email=email, password=password):
        return make_response(jsonify({'success': False, 'error': ERR_FORM})), 400

    user = user_controller.select_user_by_email(email)
    if user is None:
        return make_response(jsonify({'success': False, 'error': ERR_PASSWORD})), 401
   
    salt = user_controller.get_id_salt(user['id'])
    
    hashed_password = hashlib.sha512(str(password + salt).encode('utf-8')).hexdigest()
    if hashed_password == user_controller.get_id_hash(user['id']):
        id_session = uuid.uuid4().hex
        session_controller.save(id_session, email)
        session['id'] = id_session
        return make_response(jsonify({'success': True})), 200
    else:
        return make_response(jsonify({'success': False, 'error': ERR_PASSWORD})), 401


@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    name = request.json['name']
    last_name = request.json['last_name']
    phone = request.json['phone']
    address = request.json['address']
    password = request.json['password']
    email = request.json['email']

    # data validation
    if request_data_is_invalid(username=username, name=name, last_name=last_name, phone=phone, address=address, password=password, email=email):
        return make_response(jsonify({'success': False, 'error': ERR_FORM})), 400
    else:
        try:
            salt = uuid.uuid4().hex
            hashed_password = hashlib.sha512(
                str(password + salt).encode('utf-8')).hexdigest()
            user_controller.create(
                username, email, name, last_name, phone, address, salt, hashed_password, False)
            id_session = uuid.uuid4().hex
            session_controller.save(id_session, email)
            session['id'] = id_session
            send_email(email, MSG_MAIL_REGISTER_SUCCESS_SUBJECT, MSG_MAIL_REGISTER_SUCCESS_BODY)
            return jsonify({'success': True }), 201
        # Unique constraint must be respected
        except IntegrityError:
            return jsonify({'success': False, 'error': ERR_UNI_USER}), 403


@app.route('/logout', methods=['POST'])
@authentication_required
def logout():
    if 'id' in session:
        id_session = session['id']
        session.pop('id', None)
        session_controller.delete(id_session)
    return make_response(jsonify({'success': True})), 200


def request_data_is_invalid(**kwargs):
    for value in kwargs.items():
        if value == '':
            return True
    return False


@app.route('/password_recovery', methods=['POST'])
def password_recovery():
    smtp_response_ok = send_recovery_email(request.json['email'])
    if smtp_response_ok:
        return jsonify({'success': True, 'msg': MSG_MAIL_SENT_RECOVERY}), 200
    else:
        return jsonify({'success': False, 'error': ERR_SERVOR}), 500


def send_recovery_email(user_email):
    user = user_controller.select_user_info_by_email(user_email)
    if user:
        token = generate_token()
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        user_controller.update_password(user, user_email, token, date)
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

def send_email(recipient, subject, message):
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    msg = Message(subject, recipients=[recipient])
    msg.body = message
    try:
        mail.send(msg)
    except SMTPException:
        return False
    return True


def generate_token():
    # generate 5 random number
    list_of_ints = random.sample(range(1, 10), 5)
    new_password = ''.join(str(x) for x in list_of_ints)
    return new_password


@app.route('/admin/users/<int:id>', methods=['DELETE', 'PUT'])
def admin_manage_user(id):
    if request.method == 'DELETE':
        user_controller.delete(id)
        return make_response(jsonify({'id': id})), 201
    elif request.method == 'PUT':
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
        user_controller.update(id, username, email, name, family_name, phone, address, salt, hash, admin)
        return make_response(jsonify({'user': user})), 201
   

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
    user = user_controller.select_user_by_email(email)
    return make_response(jsonify({'user': user})), 201      


@app.route('/admin/users', methods=['GET'])
def admin_select_all_users():
    users = user_controller.select_all()
    return make_response(jsonify({'users':users})), 200


@app.route('/password_recovery/validate', methods=['POST'])
def password_recovery_validate():
    username = request.json['username']
    password = request.json['password']
    token = Database.get_connection().get_account_token_by_username(username)
    if token is None:
        redirect_url = GLOBAL_URL + '/password_recovery/validate'
        return jsonify({'success': False, 'url': redirect_url,
                        'error': ERR_PASSWORD}), 401

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
        return jsonify({'success': True, 'url': redirect_url}), 201
    else:
        redirect_url = GLOBAL_URL + '/password_recovery/validate'
        return jsonify({'success': False,
                        'url': redirect_url,
                        'error': ERR_PASSWORD}), 401



app.secret_key = '(*&*&322387he738220)(*(*22347657'

if __name__ == '__main__':
    app.run()
