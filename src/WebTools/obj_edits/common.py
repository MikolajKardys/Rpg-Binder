from flask import request


def get_elements(form, prefix):
    elements = {
        item[0].replace(prefix, ""): item[1] for item in dict(form).items() if item[0].__contains__(prefix)
    }
    return elements


def save_obj(engine, obj_class, obj_id, form):
    obj = None

    if obj_class.__name__ == 'Location':
        obj = obj_class(None)
        obj.name = form['name']
        obj.info = form['info']

    elif obj_class.__name__ == 'Item':
        obj = obj_class(None)
        obj.name = form['name']

        attributes = get_elements(request.form, prefix='atr_')

        info_list = list(attributes.values())
        if len(info_list):
            obj.info = info_list[0]
            for info_el in info_list[1:]:
                obj.info += ";" + info_el
        else:
            obj.info = ""

    elif obj_class.__name__ == 'Spell':
        obj = obj_class(None)
        obj.name = form['name']
        obj.diff = int(form['difficulty'])
        obj.cost = int(form['cost'])

        attributes = get_elements(request.form, prefix='atr_')

        info_list = list(attributes.values())
        if len(info_list):
            obj.info = info_list[0]
            for info_el in info_list[1:]:
                obj.info += ";" + info_el
        else:
            obj.info = ""

    elif obj_class.__name__ == 'Character':
        obj = obj_class(None)

        obj.name = form['name']
        obj.pd = int(form['pd'])

        for key in obj_class.stat_names.keys():
            name = f"stat_key_{key}"
            obj.stats[key] = int(form[name])

        for key in obj_class.tuple_names.keys():
            tuple_value = (int(form[f"tuple_value_{key}"]), int(form[f"tuple_value_{key}_max"]))
            obj.__dict__[key] = tuple_value

        skill_names_tab = get_elements(form, 'skill_name_')
        skill_value_tab = get_elements(form, 'skill_value_')
        while len(skill_names_tab):
            key, name = skill_names_tab.popitem()
            value = int(skill_value_tab.pop(key))

            obj.skills.append((name, value))

    if obj is not None:
        if int(obj_id) != -1:
            obj.id = obj_id
        else:
            obj.id = None
        obj.campaign = engine.loaded_campaign

        obj.save_state()

        obj_id = str(obj.id)

    return obj_id
