from flask import render_template, request, session, redirect, url_for, Blueprint, flash, abort, g
import csv

from src.Run.Engine import Engine

login_pages = Blueprint('login_pages', __name__, template_folder='templates')

engine = Engine()


@login_pages.route("/gm_home/edit_players", methods=['POST', 'GET'])
def edit_players():
    def load_players(get_all=False):
        loaded_players = {}
        with open('logins.csv', 'r', newline='', encoding='UTF-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if get_all:
                    loaded_players[row['id']] = {'type': row['type'], 'id': row['id'], 'code': row['code'],
                                                 'name': row['name']}
                elif row['type'] == 'USER':
                    loaded_players[row['id']] = {'name': row['name'], 'code': row['code']}

        if get_all:
            return reader.fieldnames, loaded_players
        return loaded_players

    if g.user_type != 'GM':
        return abort(403)

    players = {}

    if request.method == 'POST':
        current_players = [name.replace('Name_', '') for name, ignore in dict(request.form).items()
                           if name.__contains__('Name_')]

        for key in current_players:
            players[key] = {'name': request.form[f'Name_{key}'], 'code': request.form[f'Code_{key}']}

        if 'submit_button' in request.form.keys():
            if request.form['submit_button'] == 'Dodaj gracza':
                keys = [int(name.replace('Name_', '')) for name, ignore in dict(request.form).items()
                        if name.__contains__('Name_')]
                if len(keys):
                    new_id = max(keys) + 1
                else:
                    new_id = 1

                players[str(new_id)] = {'name': '', 'code': ''}

            elif request.form['submit_button'] == 'Zapisz stan':
                names = [player['name'] for player in players.values()]
                codes = [player['code'] for player in players.values()]

                if names.__contains__('') or codes.__contains__(''):
                    flash(u'Oba pola muszą być zapełnione!')

                elif len(names) != len(set(names)) or len(codes) != len(set(codes)):
                    flash(u'Wszystkie nazwy i kody muszą być unikalne!')

                else:
                    cols, old_players = load_players(get_all=True)

                    deleted = [key for key, value in old_players.items() if key not in players.keys()
                               and int(key) != -1]  # kod MG
                    if len(deleted):
                        names = engine.get_campaign_names()
                        for name in names:
                            engine.load_campaign(name)

                            sessions = engine.get_sessions()
                            for sess in sessions:
                                sess.load_players()

                                sess.loaded_players = [player for player in sess.loaded_players if str(player.id) not in deleted]

                                sess.update_all_players()

                    for key in deleted:
                        old_players.pop(key)

                    for key, values in players.items():
                        if key in old_players.keys():
                            old_players[key]['name'] = values['name']
                            old_players[key]['code'] = values['code']
                        else:
                            old_players[key] = values
                            old_players[key]['type'] = 'USER'
                            old_players[key]['id'] = key

                    with open('logins.csv', 'w', newline='', encoding='UTF-8') as file:
                        writer = csv.DictWriter(file, cols)
                        writer.writeheader()

                        for row_dict in old_players.values():
                            writer.writerow(row_dict)

                    players = load_players()

            elif request.form['submit_button'] == 'Wczytaj ponownie':
                return redirect(url_for('login_pages.edit_players'))
        else:
            pressed = [name.replace('X_', '') for name, ignore in dict(request.form).items()
                       if name.__contains__('X_')]

            if len(pressed):
                players.pop(str(pressed[0]))

    else:
        players = load_players()

    return render_template('edit_players.html', players=players)


@login_pages.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        code = request.form['submit_text']

        session.pop('user_type', None)
        session.pop('user_id', None)
        if request.form['submit_button'] == "Mistrz gry":
            if not verify('GM', code):
                flash(u'Nie istnieje użytkownik o tym kodzie!')
                return redirect(url_for('login_pages.login'))

            session['user_type'] = 'GM'

        elif request.form['submit_button'] == "Gracz":
            if not verify('USER', code):
                flash(u'Nie istnieje użytkownik o tym kodzie!')
                return redirect(url_for('login_pages.login'))

            session['user_type'] = 'USER'

        return redirect(url_for('base_site'))

    return render_template('login.html', hide_header=True)


@login_pages.route('/logout')
def logout():
    session.pop('user_type', None)
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('base_site'))


def verify(usr_type, code):  # also sets user id
    file_path = 'logins.csv'

    with open(file_path, encoding='UTF-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row['type'] == usr_type and row['code'] == code:
                session['user_id'] = row['id']
                session['user_name'] = row['name']
                return True
        return False
