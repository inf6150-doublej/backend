import sys, os, math, hashlib, uuid, datetime
sys.path.append(os.path.abspath(os.path.join('..', 'inf6150')))
from flask import jsonify, make_response, session, request, Blueprint
from sqlite3 import IntegrityError, Error
from functools import wraps
from src.constants.constants import *
from src.controllers import salles_controller, users_controller, sessions_controller, pictures_controller, reservations_controller

router = Blueprint('router', __name__)


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


@router.route('/')
def start():
    return make_response(jsonify({"alo": "salut"}), 200)


@router.route('/image/<pic_id>.jpeg')
def download_picture(pic_id):
    binary_data = pictures_controller.select(pic_id)
    if binary_data is None:
        return make_response(jsonify({'success': False, 'error': ERR_BLANK})), 204
    else:
        response = make_response(binary_data)
        response.headers.set('Content-Type', 'image/jpeg')
    return response


@router.route('/search', methods=['POST'])
def get_salles_by_types():
    query = request.json['query']
    filter = int(request.json['filter'])

    if request_data_is_invalid(query=query):
        return jsonify({'success': False, 'error': ERR_BLANK}), 204

    redirect_url = GLOBAL_URL + '/search/' + query + '/1' + '?filter=' + filter
    return jsonify({'success': True, 'url': redirect_url, 'filter': filter}), 200


@router.route('/search/<query>/<int:page>', methods=['GET'])
def get_salles_by_page(query, page):
    filter = request.args.get('filter')
    data = salles_controller.select_by_type(filter)

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
    salles = data[start:end]

    return True


@router.route('/salles/<int:salle_id>', methods=['GET'])
def get_salle_by_id(salle_id):
    salles = salles_controller.select_by_id(salle_id)
    if salles is None:
        return make_response(jsonify({'success': False})), 204
    else:
        return make_response(jsonify({'success': True, 'salle': salles})), 200


@router.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        print(request.json)
        username = request.json['username']
        password = request.json['password']

        # data validation
        if request_data_is_invalid(username=username, password=password):
            return make_response(jsonify({'success': False, 'error': ERR_FORM})), 400

        user = users_controller.select_user_hash_by_username(username)
        if user is None:
            redirect_url = GLOBAL_URL + '/login'
            return make_response(jsonify({'success': False, 'url': redirect_url, 'error': ERR_PASSWORD})), 401

        salt = user[0]
        hashed_password = hashlib.sha512(str(password + salt).encode('utf-8')).hexdigest()
        if hashed_password == user[1]:
            id_session = uuid.uuid4().hex
            sessions_controller.save(id_session, username)
            session['id'] = id_session
            redirect_url = GLOBAL_URL + '/myaccount'
            return make_response(jsonify({'success': True, 'url': redirect_url})), 200
        else:
            redirect_url = GLOBAL_URL + '/login'
            return make_response(jsonify({'success': False, 'url': redirect_url, 'error': ERR_PASSWORD})), 401
    else:
        return make_response('user_login.html')


@router.route('/register', methods=['POST'])
def register():
        username = request.json['username']
        name = request.json['name']
        family_name = request.json['family_name']
        phone = request.json['phone']
        address = request.json['address']
        password = request.json['password']
        email = request.json['email']

        # data validation
        if request_data_is_invalid(username=username, name=name, family_name=family_name, phone=phone, address=address, password=password, email=email):
            return make_response(jsonify({'success': False, 'error': ERR_FORM})), 400
        else:
            try:
                salt = uuid.uuid4().hex
                hashed_password = hashlib.sha512(str(password + salt).encode('utf-8')).hexdigest()
                users_controller.create(username, name, family_name, phone, address, email, salt, hashed_password)
                id_session = uuid.uuid4().hex
                sessions_controller.save(id_session, username)
                session['id'] = id_session
                url = GLOBAL_URL + '/myaccount'
                return jsonify({'success': True, 'url': url}), 201
            # Unique constraint must be respected
            except IntegrityError:
                return jsonify({'success': False, 'error': ERR_UNI_USER}), 403


@router.route('/logout')
@authentication_required
def logout():
    if 'id' in session:
        id_session = session['id']
        session.pop('id', None)
        sessions_controller.delete(id_session)
    return make_response({'logout': True})


def request_data_is_invalid(**kwargs):
    for key, value in kwargs.items():
        if value == '':
            return True
    return False


# @router.route('/myreservation', methods=['GET'])
# @authentication_required
# def myreservation():
#     id = users_controller.select_user_id_by_id_session(session['id'])
#     salles = reservations_controller.get_salles_by_owner_id(id)
#     if len(salles) == 0:
#         return make_response('myreservation.html', error=ERR_NOPOST), 400
#     else:
#         return make_response('myreservation.html', id=get_username(), salles=salles), 200


# @router.route('/myreservation/update', methods=['GET', 'UPDATE', 'DELETE'])
# @authentication_required
# def update_myreservation():
#     if request.method == 'GET':
#         id = get_db().get_user_id_by_id_session(session['id'])
#         salles = get_db().get_salles_by_owner_id(id)
#         return make_response('myreservation_update.html', id=get_username(),
#                                salles=salles)
#     elif request.method == 'UPDATE':
#         # get request data
#         name = request.json['name']
#         type = request.json['type']
#         race = request.json['race']
#         age = request.json['age']
#         date = datetime.datetime.now().strftime('%Y-%m-%d')
#         description = request.json['description']
#         img_uri = request.json['img']

#         if request_data_is_invalid(name=name, type=type, race=race, age=age,
#                                    description=description):
#             return jsonify({'success': False, 'error': ERR_FORM}), 400

#         # front end send data_uri as data:image/base64,XXX
#         # where xxx is the blob in string format
#         listed_img_uri = img_uri.split(',')
#         img_base64_tostring = listed_img_uri[1]

#         # will not be updated if empty
#         pic_id = ''
#         user_id = get_db().get_user_id_by_id_session(session['id'])
#         # the photo has been updated
#         if len(img_base64_tostring) > 0:
#             # TODO add image extention possibilities
#             pic_id = get_username()
#             get_db().update_pictures(pic_id, img_uri)

#         get_db().update_salle(name, type, race, age, date, description,
#                                pic_id, user_id)
#         return_url = GLOBAL_URL + '/myreservation'
#         return jsonify({'success': True, 'url': return_url}), 201

#     elif request.method == 'DELETE':
#         user_id = get_db().get_user_id_by_id_session(session['id'])
#         pic_id = get_username()
#         try:
#             get_db().delete_salle(user_id, pic_id)
#             return jsonify({'success': True, 'msg': INFO_DEL}), 201
#         except Error:
#             return jsonify({'success': False, 'error': ERR_SERVOR}), 500


# def save_image_on_disc(**kwargs):
#     user_id = kwargs['user_id']
#     img_uri = kwargs['img_uri']
#     name = kwargs['name']
#     img_name = name + '_' + str(user_id)

#     # front end send data_uri as data:image/base64,XXX
#     # where xxx is the blob in string format
#     listed_img_uri = img_uri.split(',')
#     img_base64_tostring = listed_img_uri[1]

#     # convert string to binary data for writing purpose
#     binary_data = a2b_base64(img_base64_tostring)

#     # allow to run on other machine thus we dont know the root path
#     my_path = os.path.abspath(os.path.dirname(__file__))
#     # TODO add image extention possibilities
#     img_url = 'static/img/%s.jpeg' % (img_name,)
#     path = os.path.join(my_path, img_url)

#     # create/save image
#     with open(path, 'wb+') as fh:
#         fh.write(binary_data)
#     return path


# @router.route('/password_recovery', methods=['POST', 'GET'])
# def password_recovery():
#     if request.method == 'POST':
#         smtp_response_ok = send_recovery_email()
#         if smtp_response_ok:
#             return jsonify({'success': True, 'msg': INFO_MSG_SENT_RECOVERY}), \
#                    200
#         else:
#             return jsonify({'success': False, 'error': ERR_SERVOR}), 500
#     elif request.method == 'GET':
#         return make_response('password_recovery.html')


# def send_recovery_email():
#     user_email = request.json['email']
#     username = get_db().get_user_username_by_email(user_email)
#     if username:
#         token = generate_token()
#         date = datetime.datetime.now().strftime('%Y-%m-%d')
#         get_db().create_account(username, user_email, token, date)
#         subject = INFO_MAIL_RECOVER_SUBJECT
#         msg = Message(subject, recipients=[user_email])
#         msg.body = INFO_MAIL_RECOVER_BODY + token
#         try:
#             mail.send(msg)
#         except SMTPException:
#             return False
#         return True
#     # return true even if email was not sent
#     return True


# def generate_token():
#     # generate 5 random number
#     list_of_ints = random.sample(range(1, 10), 5)
#     new_password = ''.join(str(x) for x in list_of_ints)
#     return new_password


# @router.route('/password_recovery/validate', methods=['POST', 'GET'])
# def password_recovery_validate():
#     if request.method == 'POST':
#         username = request.json['username']
#         password = request.json['password']
#         token = get_db().get_account_token_by_username(username)
#         if token is None:
#             redirect_url = GLOBAL_URL + '/password_recovery/validate'
#             return jsonify({'success': False, 'url': redirect_url,
#                             'error': ERR_PASSWORD}), 401

#         if password == token:
#             # update user
#             infos = get_db().get_user_info_by_username(username)
#             user_id = infos[0]
#             salt = uuid.uuid4().hex
#             hashed_password = hashlib.sha512(
#                 str(token + salt).encode('utf-8')).hexdigest()
#             get_db().update_user_password(user_id, salt, hashed_password)
#             # delete account
#             get_db().delete_account_by_username(username)
#             # update session
#             id_session = uuid.uuid4().hex
#             get_db().save_session(id_session, username)
#             session['id'] = id_session
#             redirect_url = GLOBAL_URL + '/myaccount'
#             return jsonify({'success': True, 'url': redirect_url}), 201
#         else:
#             redirect_url = GLOBAL_URL + '/password_recovery/validate'
#             return jsonify({'success': False,
#                             'url': redirect_url,
#                             'error': ERR_PASSWORD}), 401
#     else:
#         return make_response('password_recovery_validate.html')


# @router.route('/send_email', methods=['POST'])
# def send_email():
#     sender_email = request.json['email']
#     msg_body = request.json['message']
#     salle_id = request.json['salle_id']
#     subject = INFO_MAIL_SUBJECT + sender_email

#     if request_data_is_invalid(sender_email=sender_email, salle_id=salle_id):
#         return jsonify({'success': False, 'error': ERR_FORM}), 400

#     recipient = get_db().get_user_email_by_salle_id(salle_id)
#     msg = Message(subject, recipients=[recipient])
#     msg.body = msg_body
#     try:
#         mail.send(msg)
#     except SMTPException:
#         return jsonify({'success': False, 'error': ERR_SERVOR}), 500
#     return jsonify({'success': True, 'msg': INFO_MSG_SENT_ADOPTION}), 200
