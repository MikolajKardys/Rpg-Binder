from src.CampaignTools.CampObject import CampObject


class Spell(CampObject):
    OBJ_PATH = "\\spells.csv"

    def __init__(self, campaign):
        super().__init__(campaign)
        self.name = ""
        self.diff = 0
        self.cost = 0
        self.info = ""

    def __eq__(self, other):
        return (self.name.lower == other.name.lower and self.info.lower == other.info.lower
                and self.cost == other.cost and self.diff == other.diff)

    def __repr__(self):
        return str(self.id)

    @classmethod
    def get_matching(cls, obj_in_tab, str_criteria):
        obj_tab = super().get_matching(obj_in_tab, str_criteria)
        ids = [str(obj) for obj in obj_tab]

        info_tab = cls.check_obj(obj_in_tab, f"info~{str_criteria}")
        obj_tab += [obj for obj in info_tab if str(obj) not in ids]

        return obj_tab

    def to_string(self, new_line='\n'):
        str_out = f'''
        <h3 style="margin-bottom: 5px; font-family: \'Book Antiqua\', serif;">{self.name}  ---  Poziom {self.diff}</h3>
        <h4 style="margin-top: 5px; font-family: \'Book Antiqua\', serif;">Koszt: {self.cost} PM
</h4> '''

        info_tab = self.info.split(';')
        if len(info_tab[0]):
            for info in info_tab:
                str_out += '<p style="font-family: \'Book Antiqua\', serif; font-size: 100%; margin-top: 0;">'
                info = info.replace('\n', new_line)
                str_out += f">  {info}  <"
                str_out += '</p>'

        return str_out

    def to_render(self):  # taki to_string, tylko do ekranu edycji
        info_lines = []
        if len(self.info):
            info_lines = self.info.split(";")

        attributes = {}
        ind = 0
        for info_row in info_lines:
            attributes[str(ind)] = info_row
            ind += 1

        render_dict = {'name': self.name, 'difficulty': self.diff, 'cost': self.cost, 'attributes': attributes}

        return render_dict
