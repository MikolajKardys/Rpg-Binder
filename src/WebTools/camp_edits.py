from flask import Blueprint, abort, g, request, redirect, url_for, render_template

from src.Run.Engine import Engine

from src.WebTools.obj_edits.character_edit_stats import edit_character
from src.WebTools.obj_edits.item_edit import edit_item
from src.WebTools.obj_edits.location_edit import edit_location
from src.WebTools.obj_edits.spell_edit import edit_spell

camp_edits = Blueprint('camp_edits', __name__, template_folder='templates')
engine = Engine()


@camp_edits.route("/gm_home/campaigns/<camp_path>/<obj_name>/remove_<obj_id>")
def remove_obj(camp_path, obj_name, obj_id):
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

    obj = obj_class.get(campaign, f"id={obj_id}")

    obj.remove_obj()

    sess_obj_name = obj_name.lower() + 's'
    camp_sessions = engine.get_sessions()

    for session in camp_sessions:
        session.load_players()

        old_sess_list = session.__dict__[sess_obj_name]
        session.__dict__[sess_obj_name] = [ind for ind in old_sess_list if int(ind) != int(obj_id)]

        for player in session.loaded_players:
            old_obj_list = player.__dict__[sess_obj_name]
            player.__dict__[sess_obj_name] = [ind for ind in old_obj_list if int(ind) != int(obj_id)]

            if obj_name == 'Spell':
                player.spell_book = [ind for ind in player.spell_book if int(ind) != int(obj_id)]
            elif obj_name == 'Item':
                player.inventory = [(ind, number) for ind, number in player.inventory if int(ind) != int(obj_id)]
            elif obj_name == 'Character':
                if int(str(player.character)) == int(obj_id):
                    player.character = None

        session.update_all_players()
        session.update_csv()

    return redirect(url_for('show_obj', obj_name=obj_name, camp_path=camp_path))


@camp_edits.route("/gm_home/campaigns/<camp_path>/<obj_name>/edit_<obj_id>", methods=['GET', 'POST'])
def edit_obj(camp_path, obj_name, obj_id):
    if g.user_type != 'GM':
        abort(403)

    engine.load_campaign(camp_path)
    campaign = engine.loaded_campaign
    if campaign is None:
        abort(404)
    try:
        obj_class, obj_label = campaign.attributes[obj_name]
    except KeyError:
        return abort(404)

    class_dict = {'Item': edit_item, 'Location': edit_location, 'Spell': edit_spell, 'Character': edit_character}

    edit_func = class_dict[obj_name]

    if request.method == 'POST' and 'submit_button' in request.form.keys() and \
            request.form['submit_button'] == 'Zapisz':
        obj_id, render_dict, form_name = edit_func(request, engine, obj_class, obj_id)
        return redirect(url_for('camp_edits.edit_obj', camp_path=camp_path, obj_name=obj_name, obj_id=obj_id))

    obj_id, render_dict, form_name = edit_func(request, engine, obj_class, obj_id)
    return render_template('obj_forms/' + form_name, render_dict=render_dict,
                           camp_path=camp_path, obj_name=obj_name, obj_id=obj_id, obj_label=obj_label)
