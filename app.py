# coding: utf8
import os, sys, sqlite3, hashlib, uuid, io, datetime, random, math
sys.path.append(os.path.dirname(__file__))
from flask import g, Flask, make_response, jsonify
from flask_mail import Mail, Message
from flask_cors import CORS
from src.routes.routes import router


app = Flask(__name__)
app.register_blueprint(router)


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
cors = CORS(app)
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


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


@app.errorhandler(404)
def page_not_found(e):
    print('alo 404')
    return make_response(jsonify({'success': False}), 404)


app.secret_key = '(*&*&322387he738220)(*(*22347657'

if __name__ == '__main__':
    app.run()
