from flask import Blueprint, g, render_template, abort, request, redirect, url_for

import csv

from src.Run.Engine import Engine

session_edits = Blueprint('session_edits', __name__, template_folder='templates')
engine = Engine()


@session_edits.route("/gm_home/campaigns/<camp_path>/sess_<session_id>/show_script/edit_segment_<seg_ind>",
                     methods=['POST', 'GET'])
def add_script_seg(camp_path, session_id, seg_ind):
    if g.user_type != 'GM':
        return abort(403)

    engine.load_campaign(camp_path)
    campaign = engine.loaded_campaign
    if campaign is None:
        return abort(404)

    engine.load_session(session_id)
    if engine.loaded_session is None:
        return abort(404)

    if request.method == 'POST':
        if 'save_seg' in request.form.keys():
            seg_text = request.form['text']
            engine.loaded_session.save_act(seg_text, int(seg_ind))
            return redirect(url_for('session_edits.show_sess_script', camp_path=camp_path, session_id=session_id))

    acts = engine.loaded_session.acts

    if int(seg_ind) == -1:
        text = ""
    else:
        text = acts[int(seg_ind)]

    return render_template('sess_add_act.html', camp_path=camp_path, session_id=session_id, text=text, ind=seg_ind)


@session_edits.route("/gm_home/campaigns/<camp_path>/sess_<session_id>/show_script", methods=['POST', 'GET'])
def show_sess_script(camp_path, session_id):
    if g.user_type != 'GM':
        return abort(403)

    engine.load_campaign(camp_path)
    campaign = engine.loaded_campaign
    if campaign is None:
        return abort(404)

    engine.load_session(session_id)
    if engine.loaded_session is None:
        return abort(404)

    acts = engine.loaded_session.acts

    acts = [(i, acts[i].replace("\n", "<br>")) for i in range(len(acts))]

    if request.method == 'POST':
        pressed = [key.replace('edit_', '') for key, ignore in dict(request.form).items() if key.__contains__('edit_')]
        if pressed:
            return redirect(url_for('session_edits.add_script_seg', camp_path=camp_path, session_id=session_id,
                                    seg_ind=pressed[0]))

        pressed = [key.replace('rem_', '') for key, ignore in dict(request.form).items() if key.__contains__('rem_')]
        if pressed:
            act_num = len(engine.loaded_session.acts)
            engine.loaded_session.acts = [engine.loaded_session.acts[i] for i in range(act_num) if i != int(pressed[0])]

            engine.loaded_session.update_csv()

            return redirect(url_for('session_edits.show_sess_script', camp_path=camp_path, session_id=session_id))

        pressed = [key.replace('up_', '') for key, ignore in dict(request.form).items() if key.__contains__('up_')]
        if pressed:
            ind = int(pressed[0])
            engine.loaded_session.acts[ind], engine.loaded_session.acts[ind - 1] = \
                engine.loaded_session.acts[ind - 1], engine.loaded_session.acts[ind]

            engine.loaded_session.update_csv()
            return redirect(url_for('session_edits.show_sess_script', camp_path=camp_path, session_id=session_id))

        pressed = [key.replace('down_', '') for key, ignore in dict(request.form).items() if key.__contains__('down_')]
        if pressed:
            ind = int(pressed[0])
            engine.loaded_session.acts[ind], engine.loaded_session.acts[ind + 1] = \
                engine.loaded_session.acts[ind + 1], engine.loaded_session.acts[ind]

            engine.loaded_session.update_csv()
            return redirect(url_for('session_edits.show_sess_script', camp_path=camp_path, session_id=session_id))

    return render_template('sess_view_acts.html', camp_path=camp_path, session_id=session_id, acts=acts)


@session_edits.route("/gm_home/campaigns/<camp_path>/sess_<session_id>/add_player", methods=['POST', 'GET'])
def add_player_sess(camp_path, session_id):
    if g.user_type != 'GM':
        return abort(403)

    engine.load_campaign(camp_path)
    campaign = engine.loaded_campaign
    if campaign is None:
        return abort(404)

    engine.load_session(session_id)
    if engine.loaded_session is None:
        return abort(404)

    if request.method == 'POST':
        player_id = int(request.form['player_select'])
        engine.loaded_session.add_player(player_id)

    return redirect(url_for('session_edits.sess_select_obj', camp_path=camp_path, session_id=session_id))


@session_edits.route("/gm_home/campaigns/<camp_path>/sess_<session_id>", methods=['POST', 'GET'])
def sess_select_obj(camp_path, session_id):
    if g.user_type != 'GM':
        return abort(403)

    engine.load_campaign(camp_path)
    campaign = engine.loaded_campaign
    if campaign is None:
        return abort(404)

    objects_list = [(obj[1], obj[0].__name__)
                    for obj in campaign.attributes.values()]

    engine.load_session(session_id)
    if engine.loaded_session is None:
        return abort(404)

    if request.method == 'POST':
        pressed = [key.replace("X_", "") for key, ignore in dict(request.form).items() if key.__contains__("X_")]
        if len(pressed):
            player_id = pressed[0]
            engine.loaded_session.remove_player(player_id)

        else:
            pressed = [key.replace("show_", "") for key, ignore in dict(request.form).items()
                       if key.__contains__("show_")]
            if len(pressed):
                player_id = pressed[0]
                return redirect(url_for('player_view.see_player', camp_path=camp_path, session_id=session_id,
                                        player_id=player_id))

    engine.loaded_session.load_players()

    players = engine.loaded_session.loaded_players

    all_players = []
    with open('logins.csv', encoding='UTF-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row['type'] == 'USER':
                new_player = {'id': row['id'], 'name': row['name']}

                new_player['already'] = new_player['id'] in [str(player.id) for player in players]

                all_players.append(new_player)

    return render_template('sess_obj_select.html', session_id=session_id, objects=objects_list, camp_path=camp_path,
                           players=players, all_players=all_players)


@session_edits.route("/gm_home/campaigns/<camp_path>/sess_<session_id>/<obj_name>", methods=['GET', 'POST'])
def sess_show_obj(camp_path, session_id, obj_name):
    if g.user_type != 'GM':
        return abort(403)

    engine.load_campaign(camp_path)
    campaign = engine.loaded_campaign
    if campaign is None:
        return abort(404)

    try:
        obj_class, header = campaign.attributes[obj_name]
    except KeyError:
        return abort(404)

    all_objects = None
    if request.method == 'POST':
        if 'search' not in request.form.keys():
            engine.load_session(session_id)
            engine.loaded_session.load_data()
            obj_name_lower = obj_name.lower() + 's'

            all_sess_obj = engine.loaded_session.__dict__[obj_name_lower]
            all_indexes = [int(str(obj)) for obj in all_sess_obj]

            all_loaded = [int(item[0].replace("Ind_", "")) for item in dict(request.form).items()
                          if item[0].__contains__("Ind_")]

            all_indexes = [ind for ind in all_indexes if ind not in all_loaded]

            new_indexes = [int(item[0].replace("Check_", "")) for item in dict(request.form).items()
                           if item[0].__contains__("Check_")]

            checked = new_indexes + all_indexes

            engine.loaded_session.load_players()

            for player in engine.loaded_session.loaded_players:
                old_obj_list = player.__dict__[obj_name_lower].copy()

                old_obj_list = [int(obj) for obj in old_obj_list if int(obj) not in all_loaded]

                prefix = f"pl_{player.id}_"
                new_obj_list = [int(item[0].replace(prefix, "")) for item in dict(request.form).items()
                                if item[0].__contains__(prefix)]

                player.__dict__[obj_name_lower] = new_obj_list + old_obj_list

            engine.loaded_session.update_all_players()

            engine.loaded_session.__dict__[obj_name_lower] = list(checked)
            engine.loaded_session.update_csv()
        else:
            str_criteria = request.form['str_criteria']
            all_objects = obj_class.load_obj(campaign)
            all_objects = obj_class.get_matching(all_objects, str_criteria)

    if all_objects is None:
        all_objects = obj_class.load_obj(campaign)

    engine.load_session(session_id)

    engine.loaded_session.load_data()

    obj_already = [obj.id for obj in engine.loaded_session.__dict__[obj_name.lower() + 's']]  # already loaded

    objects = []
    for obj in all_objects:
        if obj.id in obj_already:
            objects.append((obj, True))
        else:
            objects.append((obj, False))

    obj_label = engine.loaded_campaign.attributes[obj_name][1]

    engine.loaded_session.load_players()

    players = []
    for player in engine.loaded_session.loaded_players:
        if player.character is not None:
            new_dict = {'player_id': player.id, 'name': player.character.name}

            blocked = player.get_objects(obj_name.lower() + 's')
            new_dict['blocked'] = [str(el) for el in blocked]

            players.append(new_dict)

    return render_template('sess_obj_show.html', objects=objects, camp_path=camp_path, session_id=session_id,
                           obj_name=obj_name, obj_label=obj_label, players=players)
