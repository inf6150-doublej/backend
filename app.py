# coding: utf8
import os, sys, sqlite3, hashlib, uuid, io, datetime, random, math
sys.path.append(os.path.dirname(__file__))
# print(sys.path)
from src.controllers import room_controller, user_controller, session_controller, reservation_controller
from src.constants.constants import *
from functools import wraps
from sqlite3 import IntegrityError, Error
from smtplib import SMTPException
from flask import g, Flask, make_response, jsonify, session, request
from flask_mail import Mail, Message
from flask_cors import CORS


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
    'https://doublej-frontend.herokuapp.com',  # React
  ],

  'SECRET_KEY': '...'
}
CORS(app, supports_credentials=True)
print(app.config)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


@app.errorhandler(404)
def page_not_found(e):
    return make_response(jsonify({'success': False}), 404)


def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated(session):
            return send_unauthorized()
        return f(*args, **kwargs)
    return decorated


def is_authenticated(session):
    return 'id' in session


def send_unauthorized():
    return make_response(jsonify({'success': False, 'error': ERR_UNAUTH}))


@app.route('/')
def start():
    return make_response(jsonify({"alo": "salut"}), 200)


@app.route('/search', methods=['POST'])
def get_rooms_by_types():
    query = request.json['query']
    filter = int(request.json['filter'])

    if request_data_is_invalid(query=query):
        return jsonify({'success': False, 'error': ERR_BLANK}), 204

    redirect_url = GLOBAL_URL + '/search/' + query + '/1' + '?filter=' + filter
    return jsonify({'success': True, 'url': redirect_url, 'filter': filter}), 200


@app.route('/search/<query>/<int:page>', methods=['GET'])
def get_rooms_by_page(query, page):
    filter = request.args.get('filter')
    data = room_controller.select_by_type(filter)

    # TODO optimize to not fetch all data
    nb_page = math.ceil(len(data) / 5)
    # page number verification
    if page > nb_page:
        page = nb_page
    elif page < 1:
        page = 1

    # 5 images per page
    end = page * 5
    start = end - 5
    rooms = data[start:end]

    return True


@app.route('/rooms/<int:room_id>', methods=['GET'])
def get_room_by_id(room_id):
    rooms = room_controller.select_by_id(room_id)
    if rooms is None:
        return make_response(jsonify({'success': False})), 204
    else:
        return make_response(jsonify({'success': True, 'room': rooms})), 200


@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']

    # data validation
    if request_data_is_invalid(email=email, password=password):
        return make_response(jsonify({'success': False, 'error': ERR_FORM})), 400

    user = user_controller.select_user_hash_by_email(email)
    if user is None:
        return make_response(jsonify({'success': False, 'error': ERR_PASSWORD})), 401

    salt = user[0]
    hashed_password = hashlib.sha512(
        str(password + salt).encode('utf-8')).hexdigest()
    if hashed_password == user[1]:
        id_session = uuid.uuid4().hex
        session_controller.save(id_session)
        session['id'] = id_session
        return make_response(jsonify({'success': True })), 200
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
                username, email, name, last_name, phone, address, salt, hashed_password)
            id_session = uuid.uuid4().hex
            session_controller.save(id_session)
            session['id'] = id_session
            send_email(email, MSG_MAIL_REGISTER_SUCCESS_SUBJECT, MSG_MAIL_REGISTER_SUCCESS_BODY)
            return jsonify({'success': True }), 201
        # Unique constraint must be respected
        except IntegrityError:
            return jsonify({'success': False, 'error': ERR_UNI_USER}), 403


@app.route('/logout')
@authentication_required
def logout():
    if 'id' in session:
        id_session = session['id']
        session.pop('id', None)
        session_controller.delete(id_session)
    return make_response({'logout': True})


def request_data_is_invalid(**kwargs):
    for key, value in kwargs.items():
        if value == '':
            return True
    return False


@app.route('/password_recovery', methods=['POST'])
def password_recovery():
    smtp_response_ok = send_recovery_email()
    if smtp_response_ok:
        return jsonify({'success': True, 'msg': MSG_MAIL_SENT_RECOVERY}), 200
    else:
        return jsonify({'success': False, 'error': ERR_SERVOR}), 500


def send_recovery_email():
    user_email = request.json['email']
    username = user_controller.get_user_username_by_email(user_email)
    if username:
        token = generate_token()
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        user_controller.create(username, user_email, token, date)
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


# @app.route('/password_recovery/validate', methods=['POST'])
# def password_recovery_validate():
#     username = request.json['username']
#     password = request.json['password']
#     token = Database.get_connection().get_account_token_by_username(username)
#     if token is None:
#         redirect_url = GLOBAL_URL + '/password_recovery/validate'
#         return jsonify({'success': False, 'url': redirect_url,
#                         'error': ERR_PASSWORD}), 401

#     if password == token:
#         # update user
#         infos = user_controller.get_user_info_by_username(username)
#         user_id = infos[0]
#         salt = uuid.uuid4().hex
#         hashed_password = hashlib.sha512(
#             str(token + salt).encode('utf-8')).hexdigest()
#         user_controller.update_user_password(user_id, salt, hashed_password)
#         # delete account
#         user_controller.delete_account_by_username(username)
#         # update session
#         id_session = uuid.uuid4().hex
#         session_controller.save_session(id_session, username)
#         session['id'] = id_session
#         redirect_url = GLOBAL_URL + '/myaccount'
#         return jsonify({'success': True, 'url': redirect_url}), 201
#     else:
#         redirect_url = GLOBAL_URL + '/password_recovery/validate'
#         return jsonify({'success': False,
#                         'url': redirect_url,
#                         'error': ERR_PASSWORD}), 401



app.secret_key = '(*&*&322387he738220)(*(*22347657'

if __name__ == '__main__':
    app.run()
