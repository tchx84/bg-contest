# -*- coding: utf-8 -*-
import os
import re
import sqlite3

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import send_from_directory
from flask import g
from flask import abort
from flask.ext.login import LoginManager
from flask.ext.login import UserMixin
from flask.ext.login import login_required
from flask.ext.login import login_user
from flask.ext.login import logout_user
from flask.ext.login import current_user

from werkzeug import secure_filename

CARPETA_SUBIDOS = os.path.join(os.path.dirname(__file__), 'media')

# FIXME PROD cambiar
URL_SUBIDOS = "http://0.0.0.0:8000/"

BASE_DE_DATOS = os.path.join(os.path.dirname(__file__), 'contest.db')

PRODUCCION = False

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = CARPETA_SUBIDOS

# FIXME PROD cambiar
# >>> import os
# >>> os.urandom(24)
app.secret_key = "unodostres"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "entrar"

class WebFactionMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = '/el-ventilador'
        return self.app(environ, start_response)

# FIXME solo si el deploy no se hace es un root domain
# if PRODUCCION:
#     app.wsgi_app = WebFactionMiddleware(app.wsgi_app)

class Usuario(UserMixin):
    def __init__(self, id_usuario):
        UserMixin.__init__(self)
        self.id = id_usuario

    def get_id(self):
        return self.id

usuario_admin = Usuario(u'admin')

@login_manager.user_loader
def cargar_usuario(id_usuario):
    return usuario_admin

def se_autoriza(formu):
    # FIXME PROD cambiar
    return formu['username'].strip() == 'admin'

@app.route("/admin/entrar", methods=["GET", "POST"])
def entrar():
    if request.method == 'POST':
        if se_autoriza(request.form):
            # login and validate the user...
            login_user(usuario_admin)
            return redirect(request.args.get("next") or url_for("admin"))

    return render_template("entrar.html", usuario=current_user)

@app.route("/admin/salir")
@login_required
def salir():
    logout_user()
    return redirect(url_for('index'))

# FIXME PROD generar
# >>> from __init__ import init_db
# >>> init_db()
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
            db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(BASE_DE_DATOS)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'contest'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

def es_archivo_permitido(nombre_archivo):
    return '.' in nombre_archivo and \
        nombre_archivo.rsplit('.', 1)[-1].lower() == 'png'

def este_formu_vale(formu, archivos):

    # limpiar entradas

    datos = {
        'person-name': formu['person-name'].strip(),
        'person-email': formu['person-email'].strip(),
        'person-age': formu['person-age'].strip(),
        'person-country': formu['person-country'].strip(),
        'bg-title': formu['bg-title'].strip(),
        'conditions-accepted': formu.get('conditions-accepted', None) == 'on',
        }

    person_photo = archivos.get('person-photo', None)
    if person_photo is None:
        datos['person-photo'] = ''
    else:
        datos['person-photo'] = person_photo.filename

    bg_image = archivos.get('bg-image', None)
    if bg_image is None:
        datos['bg-image'] = ''
    else:
        datos['bg-image'] = bg_image.filename

    # checkear entradas

    errores = {}

    mandatory_fields = ('person-name', 'person-email', 'person-age',
                        'person-country', 'person-photo', 'bg-title',
                        'bg-image')

    for field_name in mandatory_fields:
        if datos[field_name] == "":
            errores[field_name] = u"This field is mandatory."

    file_fields = ('person-photo', 'bg-image')

    for field_name in file_fields:
        if not es_archivo_permitido(datos[field_name]):
            errores[field_name] = True

    email_fields = ('person-email',)

    for field_name in email_fields:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", datos[field_name]):
            errores[field_name] = u"Please write a valid email."

    if not datos['conditions-accepted']:
        errores['conditions-accepted'] = u"You need to agree with this contest's conditions in order to participate."

    return datos, errores

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    datos = {}
    errores = {}
    if request.method == 'POST':
        datos, errores = este_formu_vale(request.form, request.files)
        if not errores:

            # guardar archivos

            # FIXME, needs to check for duplicates
            subdir = os.path.join(app.config['UPLOAD_FOLDER'],
                                  secure_filename(datos['bg-title']))

            if not os.path.exists(subdir):
                os.makedirs(subdir)

            filename_photo = os.path.join(subdir, secure_filename(datos['person-photo']))
            request.files['person-photo'].save(filename_photo)

            url_photo = os.path.join(secure_filename(datos['bg-title']),
                                     secure_filename(datos['person-photo']))

            filename_background = os.path.join(subdir, secure_filename(datos['bg-image']))
            request.files['bg-image'].save(filename_background)

            url_background = os.path.join(secure_filename(datos['bg-title']),
                                  secure_filename(datos['bg-image']))

            # guardar en la base de datos

            cur = get_db().cursor()
            cur.execute('insert into contest values (?,?,?,?,?,?,?,?)',
                        (None,
                         datos['person-name'],
                         datos['person-email'],
                         datos['person-age'],
                         datos['person-country'],
                         url_photo,
                         datos['bg-title'],
                         url_background,
                         ))
            get_db().commit()

            return render_template('thanks.html')

    return render_template('form.html', datos=datos, errores=errores)

@app.route('/admin')
@login_required
def admin():
    cur = get_db().cursor()
    cur.execute("select * from contest")
    datos = cur.fetchall()
    return render_template('admin.html', datos=datos, usuario=current_user,
                           URL_SUBIDOS=URL_SUBIDOS)

@app.route('/admin/<id_entry>')
@login_required
def admin_detail(id_entry):
    cur = get_db().cursor()
    cur.execute("select * from contest where id=?", (id_entry,))
    datos = cur.fetchone()
    if datos is None:
        abort(404)

    return render_template('admin_detail.html', datos=datos, usuario=current_user,
                           URL_SUBIDOS=URL_SUBIDOS)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('ups.html'), 404

if __name__ == '__main__':

    if not PRODUCCION:
        app.debug = True

    app.run()
