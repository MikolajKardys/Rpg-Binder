from flask import Flask, render_template, abort, session, redirect, url_for, g, request, flash
from flask_qrcode import QRcode

from datetime import date

from src.Run.Engine import Engine

from src.WebTools.login import login_pages
from src.WebTools.player_view import player_view
from src.WebTools.user import user_pages
from src.WebTools.camp_edits import camp_edits
from src.WebTools.session_edit import session_edits

import socket

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.register_blueprint(login_pages)
app.register_blueprint(user_pages)
app.register_blueprint(camp_edits)
app.register_blueprint(session_edits)
app.register_blueprint(player_view)

QRcode(app)


@app.before_request
def before_request():
    g.user_type = None
    g.user_id = None
    g.user_name = None
    if 'user_type' in session:
        g.user_type = session['user_type']
    if 'user_id' in session:
        g.user_id = session['user_id']
    if 'user_name' in session:
        g.user_name = session['user_name']


@app.route("/")
def base_site():
    if g.user_type is None:
        return redirect(url_for('login_pages.login', hide_header=True))
    if g.user_type == 'GM':
        return redirect(url_for('gm_home'))
    elif g.user_type == 'USER':
        return redirect(url_for('user_pages.user_home'))


@app.route("/gm_home")
def gm_home():
    if g.user_type != 'GM':
        abort(403)

    return render_template('gm_home.html')


@app.route("/gm_home/campaigns", methods=['GET', 'POST'])
def select_campaign():
    if g.user_type != 'GM':
        abort(403)
    names = engine.get_campaign_names()

    if request.method == 'POST':
        if 'add_camp' in request.form.keys():
            new_name = request.form['new_name']

            if new_name in names:
                flash(u'Nazwa kampanii musi być unikalna!')
            else:
                engine.create_new_campaign(new_name)
                names.append(new_name)
        else:
            pressed = [name.replace('Camp_', '') for name, ignore in dict(request.form).items()
                       if name.__contains__('Camp_')]

            if len(pressed):
                return redirect(url_for('select_obj', camp_path=pressed[0]))

            else:
                pressed = [name.replace('X_', '') for name, ignore in dict(request.form).items()
                           if name.__contains__('X_')]

                if len(pressed):
                    del_name = pressed[0]

                    engine.remove_campaign(del_name)

                    names.remove(del_name)

    return render_template('camp_select.html', names=names)


@app.route("/gm_home/campaigns/<camp_path>/create_session", methods=['POST', 'GET'])
def create_session(camp_path):
    if g.user_type != 'GM':
        abort(403)

    engine.load_campaign(camp_path)
    campaign = engine.loaded_campaign
    if campaign is None:
        abort(404)

    if request.method == 'POST':
        if 'submit_button' in request.form.keys():
            if 'Follow_check' in request.form.keys() and 'Follow_select' in request.form.keys():
                engine.create_session(request.form['sess_date'], followup=request.form['Follow_select'])
            else:
                engine.create_session(request.form['sess_date'])

            return redirect(url_for('select_obj', camp_path=camp_path))

    today = date.today()

    sessions = engine.get_sessions()

    return render_template('create_session.html', camp_path=camp_path, today=today, sessions=sessions)


@app.route("/gm_home/campaigns/<camp_path>", methods=['POST', 'GET'])
def select_obj(camp_path):
    if g.user_type != 'GM':
        abort(403)

    engine.load_campaign(camp_path)
    campaign = engine.loaded_campaign
    if campaign is None:
        abort(404)

    if request.method == 'POST':
        if 'dodaj_sesje' in request.form.keys():
            return redirect(url_for('create_session', camp_path=camp_path))

        pressed = [item[0].replace('sess_', '') for item in dict(request.form).items() if item[0].__contains__('sess_')]
        if len(pressed):
            return redirect(url_for('session_edits.sess_select_obj', camp_path=camp_path, session_id=int(pressed[0])))

        pressed = [item[0].replace('X_', '') for item in dict(request.form).items() if item[0].__contains__('X_')]
        if len(pressed):
            engine.remove_session(pressed[0])

    sessions = engine.get_sessions()

    sess_dict = [sess.__dict__ for sess in sessions]

    objects_list = [(obj[1], obj[0].__name__)
                    for obj in campaign.attributes.values()]

    if len(sess_dict):
        return render_template('obj_select.html', sessions=sess_dict, objects=objects_list, camp_path=camp_path)

    return render_template('obj_select.html', objects=objects_list, camp_path=camp_path)


@app.route("/gm_home/campaigns/<camp_path>/<obj_name>", methods=['POST', 'GET'])
def show_obj(obj_name, camp_path):
    if g.user_type != 'GM':
        abort(403)

    engine.load_campaign(camp_path)
    campaign = engine.loaded_campaign
    if campaign is None:
        abort(404)

    try:
        obj_class, header = campaign.attributes[obj_name]
    except KeyError:
        return abort(404)

    obj_tab = None
    if request.method == 'POST':
        str_criteria = request.form['str_criteria']
        obj_tab = obj_class.load_obj(campaign)
        obj_tab = obj_class.get_matching(obj_tab, str_criteria)

    if obj_tab is None:
        obj_tab = obj_class.load_obj(campaign)

    return render_template('obj_show.html', objects=obj_tab, obj_name=header, obj_path=obj_name, camp_path=camp_path)


@app.route("/gm_home/campaigns/<camp_path>/<obj_name>/<obj_id>", methods=['GET', 'POST'])
def handle_obj(camp_path, obj_name, obj_id):
    if request.method == 'POST':
        if request.form['submit_button'] == "Edytuj" or request.form['submit_button'] == "Stwórz nowy":
            return redirect(url_for('camp_edits.edit_obj', camp_path=camp_path, obj_name=obj_name, obj_id=obj_id))
        elif request.form['submit_button'] == "Usuń":
            return redirect(url_for('camp_edits.remove_obj', camp_path=camp_path, obj_name=obj_name, obj_id=obj_id))
    return redirect(url_for('show_obj', obj_name=obj_name, camp_path=camp_path))


@app.route("/gm_home/connect_guide")
def conn_guide():
    if g.user_type != 'GM':
        return abort(403)

    return render_template('connect_guide.html', host_str=f"{host}:{port}")


if __name__ == '__main__':
    engine = Engine()  # database engine

    def get_ip():
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    port = 18000
    host = get_ip()

    app.run(debug=True, port=port, host=host)
