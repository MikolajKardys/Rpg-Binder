from flask import Blueprint, g, render_template, abort, request, redirect, url_for

from src.Run.Engine import Engine

player_view = Blueprint('player_view', __name__, template_folder='templates')
engine = Engine()


def get_obj(obj_class, tab_id, campaign=engine.loaded_campaign):
    all_obj = obj_class.load_obj(campaign)
    return [obj for obj in all_obj if obj.id in tab_id]


@player_view.route("/gm_home/campaigns/<camp_path>/sess_<session_id>/player_<player_id>", methods=['POST', 'GET'])
def see_player(camp_path, session_id, player_id):
    if request.method == 'POST':
        if request.form['submit_button'] == 'Edytuj ekwipunek':
            return redirect(url_for('player_view.see_inventory', camp_path=camp_path, session_id=session_id,
                                    player_id=player_id))

        elif request.form['submit_button'] == 'Edytuj czary':
            return redirect(url_for('player_view.see_spells', camp_path=camp_path, session_id=session_id,
                                    player_id=player_id))

        elif request.form['submit_button'] == 'Zmień postać':
            return redirect(url_for('player_view.see_character', camp_path=camp_path, session_id=session_id,
                                    player_id=player_id))

    if g.user_type != 'GM':
        return abort(403)

    engine.load_campaign(camp_path)
    campaign = engine.loaded_campaign
    if campaign is None:
        return abort(404)

    engine.load_session(str(session_id))
    if engine.loaded_session is None:
        return abort(404)

    engine.loaded_session.load_players()

    match = [player for player in engine.loaded_session.loaded_players if str(player.id) == player_id]
    if not len(match):
        return abort(404)
    player = match[0]

    item_class = engine.loaded_campaign.attributes['Item'][0]
    inventory = get_obj(item_class, [ind for ind, num in player.inventory], engine.loaded_campaign)
    inventory = [(item, [number for ind, number in player.inventory if str(ind) == str(item)][0]) for item in inventory]

    spell_class = engine.loaded_campaign.attributes['Spell'][0]
    spell_book = get_obj(spell_class, player.spell_book, engine.loaded_campaign)

    return render_template('view_player.html', camp_path=camp_path, session_id=session_id, player=player,
                           inventory=inventory, spell_book=spell_book)


@player_view.route("/gm_home/campaigns/<camp_path>/sess_<session_id>/player_<player_id>/character",
                   methods=['POST', 'GET'])
def see_character(camp_path, session_id, player_id):
    if g.user_type != 'GM':
        return abort(403)

    engine.load_campaign(camp_path)
    campaign = engine.loaded_campaign
    if campaign is None:
        return abort(404)

    engine.load_session(str(session_id))
    if engine.loaded_session is None:
        return abort(404)

    engine.loaded_session.load_players()

    match = [player for player in engine.loaded_session.loaded_players if str(player.id) == player_id]
    if not len(match):
        return abort(404)
    player = match[0]

    character_class = engine.loaded_campaign.attributes['Character'][0]

    characters = None

    if request.method == 'POST':
        if request.form['submit_button'] in 'character_search':
            characters = character_class.load_obj(engine.loaded_campaign)
            characters = {str(character.id): (character, False) for character in characters}

            if player.character is not None:
                characters[str(player.character.id)] = (characters[str(player.character.id)][0], True)

            characters = list(characters.values())

            permitted = None
            criteria = request.form['character_str_criteria']
            if len(criteria):
                permitted = character_class.get_matching([character for character, active in characters], criteria)
                permitted = [str(character) for character in permitted]

            if permitted is not None:
                characters = [(character, active) for character, active in characters if str(character.id) in permitted]

        elif request.form['submit_button'] == 'Zapisz wybór':
            selected = [character.replace('Check_', "") for character, ignore in dict(request.form).items()
                        if character.__contains__('Check_')]

            if len(selected):
                player.character = character_class.get(campaign, f"id={selected[0]}")
            else:
                all_loaded = [character.replace('ind_', "") for character, ign in dict(request.form).items()
                              if character.__contains__('ind_')]

                if str(player.character) in all_loaded:
                    player.character = None
                else:
                    player.character = character_class.get(campaign, f"id={player.character.id}")

            engine.loaded_session.update_player_csv(int(player_id))

            return redirect(url_for('player_view.see_player', camp_path=camp_path, session_id=session_id,
                                    player_id=player_id))

    if characters is None:
        characters = character_class.load_obj(engine.loaded_campaign)
        characters = {str(character.id): (character, False) for character in characters}

        if player.character is not None:
            characters[str(player.character.id)] = (characters[str(player.character.id)][0], True)

        characters = list(characters.values())

    return render_template('player_edit/character_edit.html', characters=characters, camp_path=camp_path,
                           session_id=session_id, player=player)


@player_view.route("/gm_home/campaigns/<camp_path>/sess_<session_id>/player_<player_id>/inventory",
                   methods=['POST', 'GET'])
def see_inventory(camp_path, session_id, player_id):
    if g.user_type != 'GM':
        return abort(403)

    engine.load_campaign(camp_path)
    campaign = engine.loaded_campaign
    if campaign is None:
        return abort(404)

    engine.load_session(str(session_id))
    if engine.loaded_session is None:
        return abort(404)

    engine.loaded_session.load_players()

    match = [player for player in engine.loaded_session.loaded_players if str(player.id) == player_id]
    if not len(match):
        return abort(404)
    player = match[0]

    item_class = engine.loaded_campaign.attributes['Item'][0]
    inventory = get_obj(item_class, [ind for ind, num in player.inventory], engine.loaded_campaign)
    inventory = [(item, [number for ind, number in player.inventory if str(ind) == str(item)][0]) for item in inventory]

    items = None

    if request.method == 'POST':
        if request.form['submit_button'] in 'item_search':
            items = item_class.load_obj(engine.loaded_campaign)
            items = {str(item.id): (item, 0) for item in items}

            for item_id, number in inventory:
                items[str(item_id)] = (items[str(item_id)][0], number)

            items = list(items.values())

            permitted = None
            criteria = request.form['item_str_criteria']
            if len(criteria):
                permitted = item_class.get_matching([item for item, number in items], criteria)
                permitted = [str(item) for item in permitted]

            if permitted is not None:
                items = [(item, number) for item, number in items if str(item.id) in permitted]

        elif request.form['submit_button'] == 'Zapisz ekwipunek':
            items = item_class.load_obj(engine.loaded_campaign)
            items = {str(item.id): (item, 0) for item in items}

            for item_id, number in inventory:
                items[str(item_id)] = (items[str(item_id)][0], number)

            numbers = {item[0].replace('number_', ""): int(item[1]) for item in dict(request.form).items()
                       if item[0].__contains__('number_')}

            for ind, number in numbers.items():
                items[ind] = (items[ind][0], number)

            items = list(items.values())

            new_inventory = [(str(item), number) for item, number in items if number > 0]
            player.inventory = new_inventory

            for i in range(len(engine.loaded_session.loaded_players)):
                if engine.loaded_session.loaded_players[i] == int(player_id):
                    engine.loaded_session.loaded_players[i] = player
                    break

            engine.loaded_session.update_player_csv(int(player_id))

            return redirect(url_for('player_view.see_player', camp_path=camp_path, session_id=session_id,
                                    player_id=player_id))

    if items is None:
        items = item_class.load_obj(engine.loaded_campaign)
        items = {str(item.id): (item, 0) for item in items}

        for item_id, number in inventory:
            items[str(item_id)] = (items[str(item_id)][0], number)

        items = list(items.values())

    return render_template('player_edit/equip_edit.html', items=items, camp_path=camp_path,
                           session_id=session_id, player=player)


@player_view.route("/gm_home/campaigns/<camp_path>/sess_<session_id>/player_<player_id>/spell_book",
                   methods=['POST', 'GET'])
def see_spells(camp_path, session_id, player_id):
    if g.user_type != 'GM':
        return abort(403)

    engine.load_campaign(camp_path)
    campaign = engine.loaded_campaign
    if campaign is None:
        return abort(404)

    engine.load_session(str(session_id))
    if engine.loaded_session is None:
        return abort(404)

    engine.loaded_session.load_players()

    match = [player for player in engine.loaded_session.loaded_players if str(player.id) == player_id]
    if not len(match):
        return abort(404)
    player = match[0]

    spell_class = engine.loaded_campaign.attributes['Spell'][0]
    spell_book = get_obj(spell_class, player.spell_book, engine.loaded_campaign)

    spells = None

    if request.method == 'POST':
        if request.form['submit_button'] in 'spell_search':
            all_spells = spell_class.load_obj(engine.loaded_campaign)

            criteria = request.form['spell_str_criteria']
            spells = spell_class.get_matching(all_spells, criteria)
            spells = {str(spell.id): (spell, False) for spell in spells}

            for spell in spell_book:
                if str(spell) in spells.keys():
                    spells[str(spell)] = (spells[str(spell)][0], True)

            spells = list(spells.values())

        elif request.form['submit_button'] == 'Zapisz zaklęcia':
            spells = spell_class.load_obj(engine.loaded_campaign)
            spells = {str(spell.id): (spell, False) for spell in spells}

            for spell_id in spell_book:
                spells[str(spell_id)] = (spells[str(spell_id)][0], True)

            all_loaded = [spell.replace('ind_', "") for spell, ign in dict(request.form).items()
                          if spell.__contains__('ind_')]
            for ind in all_loaded:
                spells[ind] = (spells[ind][0], False)

            all_checked = [spell.replace('Check_', "") for spell, ign in dict(request.form).items()
                           if spell.__contains__('Check_')]
            for ind in all_checked:
                spells[ind] = (spells[ind][0], True)

            spells = list(spells.values())

            new_spell_book = [str(spell) for spell, known in spells if known]
            player.spell_book = new_spell_book

            for i in range(len(engine.loaded_session.loaded_players)):
                if engine.loaded_session.loaded_players[i] == int(player_id):
                    engine.loaded_session.loaded_players[i] = player
                    break

            engine.loaded_session.update_player_csv(int(player_id))

            return redirect(url_for('player_view.see_player', camp_path=camp_path, session_id=session_id,
                                    player_id=player_id))

    if spells is None:
        spells = spell_class.load_obj(engine.loaded_campaign)
        spells = {str(spell.id): (spell, 0) for spell in spells}

        for spell in spell_book:
            if str(spell) in spells.keys():
                spells[str(spell)] = (spells[str(spell)][0], True)

        spells = list(spells.values())

    return render_template('player_edit/spells_edit.html', spells=spells, camp_path=camp_path,
                           session_id=session_id, player=player)
