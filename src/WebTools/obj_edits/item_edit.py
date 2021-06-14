from src.WebTools.obj_edits.common import save_obj, get_elements

form_name = "item_form.html"


def edit_item(request, engine, obj_class, obj_id):
    if request.method == 'POST':
        if 'submit_button' in request.form.keys():
            if request.form['submit_button'] == 'Dodaj atrybut':

                attributes = get_elements(request.form, prefix='atr_')

                if len(attributes):
                    ids = [int(item[0]) for item in attributes.items()]
                    new_ind = max(ids) + 1
                else:
                    new_ind = 1

                attributes[str(new_ind)] = ""

                render_dict = {'name': request.form['name'], 'attributes': attributes}
                return obj_id, render_dict, form_name

            elif request.form['submit_button'] == 'Zapisz':
                obj_id = save_obj(engine, obj_class, obj_id, request.form)

        else:
            button_id = list(get_elements(request.form, prefix='X_').keys()).pop(0)

            attributes = get_elements(request.form, prefix='atr_')
            attributes.pop(button_id)

            render_dict = {'name': request.form['name'], 'attributes': attributes}
            return obj_id, render_dict, form_name

    if int(obj_id) == -1:
        obj = obj_class(engine.loaded_campaign)
    else:
        obj = obj_class.get(engine.loaded_campaign, f"id={obj_id}")

    return obj_id, obj.to_render(), form_name
