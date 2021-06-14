from src.WebTools.obj_edits.common import save_obj

form_name = "location_form.html"


def edit_location(request, engine, obj_class, obj_id):
    if request.method == 'POST':
        if request.form['submit_button'] == 'Zapisz':
            obj_id = save_obj(engine, obj_class, obj_id, request.form)

    if int(obj_id) == -1:     # czy dodajemy nowy czy updatujemy stary
        obj = obj_class(engine.loaded_campaign)
    else:
        obj = obj_class.get(engine.loaded_campaign, f"id={obj_id}")

    return obj_id, obj.to_render(), form_name
