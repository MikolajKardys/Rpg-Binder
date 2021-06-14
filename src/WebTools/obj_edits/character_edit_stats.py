from src.WebTools.obj_edits.common import save_obj, get_elements

form_name = "character_form.html"

same_keys = ['name']


def dict_from_form(obj_class, form):
    new_dict = {'name': form['name'], 'pd': int(form['pd'])}

    stats = get_elements(form, prefix="stat_key_")
    for key, value in stats.items():
        stats[key] = (obj_class.stat_names[key], int(value))
    new_dict['stats'] = stats

    skill_keys = get_elements(form, prefix="skill_name_")
    skills = {}
    for key, name in skill_keys.items():
        skills[key] = (name, int(form[f"skill_value_{key}"]))
    new_dict['skills'] = skills

    tuple_keys = get_elements(form, prefix="tuple_value_")
    tuples = []
    for key, value in tuple_keys.items():
        if not key.__contains__("_max"):
            values = (int(value), int(form[f"tuple_value_{key}_max"]))
            new_tuple = (key, obj_class.tuple_names[key], values)
            tuples.append(new_tuple)
    new_dict['tuples'] = tuples

    return new_dict


def edit_character(request, engine, obj_class, obj_id):
    if request.method == 'POST':
        if 'submit_button' in request.form.keys():
            if request.form['submit_button'] == 'Dodaj umiejętność':
                render_dict = dict_from_form(obj_class, request.form)

                skill_indexes = [int(key) for key in render_dict['skills'].keys()]

                if len(skill_indexes):
                    new_index = str(max(skill_indexes) + 1)
                else:
                    new_index = 0

                render_dict['skills'][new_index] = ("", 0)

                return obj_id, render_dict, form_name

            elif request.form['submit_button'] == 'Zapisz':
                obj_id = save_obj(engine, obj_class, obj_id, request.form)

        else:
            render_dict = dict_from_form(obj_class, request.form)

            pressed = [item[0] for item in dict(request.form).items() if item[0].__contains__('X_')].pop(0)

            if pressed.__contains__('skill'):
                index = pressed.replace("X_skill_", "")
                render_dict['skills'].pop(index)

            return obj_id, render_dict, form_name

    if int(obj_id) == -1:
        obj = obj_class(engine.loaded_campaign)
    else:
        obj = obj_class.get(engine.loaded_campaign, f"id={obj_id}")

    return obj_id, obj.to_render(), form_name
