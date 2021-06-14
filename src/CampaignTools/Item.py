from src.CampaignTools.CampObject import CampObject


class Item(CampObject):
    OBJ_PATH = "\\items.csv"

    def __init__(self, campaign):
        super().__init__(campaign)
        self.name = ""
        self.info = ""

    def __eq__(self, other):
        return self.name.lower == other.name.lower and self.info.lower == other.info.lower

    def to_string(self, number=1, new_line='\n'):
        str_out = f'''
        <h3 style="margin-bottom: 5px; font-family: \'Book Antiqua\', serif;">{self.name}'''

        if number == 1:
            str_out += "</h3>\n"
        else:
            str_out += f" ---  Sztuk: x{number}</h3\n>"

        str_out += new_line

        info_tab = self.info.split(';')
        if len(info_tab[0]):
            for info in info_tab:
                str_out += '<p style="font-family: \'Book Antiqua\', serif; font-size: 100%; margin-top: 0;">'
                info = info.replace('\n', new_line)
                str_out += f">  {info}  <"
                str_out += '</p>'

        return str_out

    @classmethod
    def get_matching(cls, obj_in_tab, str_criteria):
        obj_tab = super().get_matching(obj_in_tab, str_criteria)
        ids = [str(obj) for obj in obj_tab]

        info_tab = cls.check_obj(obj_in_tab, f"info~{str_criteria}")
        obj_tab += [obj for obj in info_tab if str(obj) not in ids]

        return obj_tab

    def to_render(self):  # taki to_string, tylko do ekranu edycji
        info_lines = []
        if len(self.info):
            info_lines = self.info.split(";")

        attributes = {}
        ind = 0
        for info_row in info_lines:
            attributes[str(ind)] = info_row
            ind += 1

        render_dict = {'name': self.name, 'attributes': attributes}

        return render_dict
