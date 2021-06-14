from flask import render_template, Blueprint, abort, g, request

from src.Run.UserEngine import UserEngine
from src.WebTools.player_view import get_obj

user_pages = Blueprint('user_pages', __name__, template_folder='templates')


@user_pages.route("/user_home")
def user_home():
    if g.user_type != 'USER' or g.user_id is None:
        abort(403)

    usr_engine = UserEngine(int(g.user_id))
    prev_list = usr_engine.get_all_prev()

    return render_template('usr_files/usr_home.html', prev_list=prev_list)


@user_pages.route("/user_home/session_<session_id>_character")
def user_character(session_id):
    if g.user_type != 'USER' or g.user_id is None:
        abort(403)

    usr_engine = UserEngine(int(g.user_id))
    usr_engine.load_sessions()
    sess = [sess for sess in usr_engine.loaded_sessions if [sess.session_id == int(session_id)]]
    if not len(sess):
        return abort(404)

    sess = sess[0]
    sess.load_players()

    match = [player for player in sess.loaded_players if player.id == int(g.user_id)]
    try:
        player = match[0]
    except IndexError:
        return abort(404)

    item_class = sess.campaign.attributes['Item'][0]
    inventory = get_obj(item_class, [ind for ind, num in player.inventory], campaign=sess.campaign)
    inventory = [(item, [number for ind, number in player.inventory if str(ind) == str(item)][0]) for item in inventory]

    spell_class = sess.campaign.attributes['Spell'][0]
    spell_book = get_obj(spell_class, player.spell_book, campaign=sess.campaign)

    return render_template('usr_files/usr_view_player.html', session_id=session_id, player=player, inventory=inventory,
                           spell_book=spell_book)


@user_pages.route("/user_home/session_<session_id>_enc")
def user_session(session_id):
    if g.user_type != 'USER' or g.user_id is None:
        abort(403)

    usr_engine = UserEngine(int(g.user_id))
    usr_engine.load_sessions()
    sess = [sess for sess in usr_engine.loaded_sessions if [sess.session_id == int(session_id)]]
    if not len(sess):
        abort(404)

    sess = sess[0]
    sess.load_players()

    match = [player for player in sess.loaded_players if player.id == int(g.user_id)]
    try:
        character = match[0]
    except IndexError:
        character = None

    object_list = sess.get_attr()

    return render_template('usr_files/usr_session.html', objects=object_list, session_id=session_id,
                           character=character)


@user_pages.route("/user_home/session_<session_id>/<obj_name>", methods=['POST', 'GET'])
def user_show_obj(obj_name, session_id):
    if g.user_type != 'USER' or g.user_id is None:
        abort(403)

    usr_engine = UserEngine(int(g.user_id))
    usr_engine.load_sessions()
    sess = [sess for sess in usr_engine.loaded_sessions if [sess.session_id == int(session_id)]]
    if not len(sess):
        abort(404)

    obj_label = None
    objects = None
    if request.method == 'POST':
        str_criteria = request.form['str_criteria']
        obj_label, objects = sess[0].get_player_obj(g.user_id, obj_name)

        if len(objects):
            objects = objects[0].get_matching(objects, str_criteria)

    if obj_label is None or objects is None:
        obj_label, objects = sess[0].get_player_obj(g.user_id, obj_name)

    return render_template('usr_files/usr_show.html', session_id=session_id, objects=objects, obj_name=obj_label,
                           obj_path=obj_name, edit=None)
