from src.CampaignTools.CampObject import CampObject


class Location(CampObject):
    OBJ_PATH = "\\locations.csv"

    def __init__(self, campaign):
        super().__init__(campaign)
        self.name = ""
        self.info = ""

    def __eq__(self, other):
        return self.name.lower == other.name.lower and self.info.lower == other.info.lower

    def to_string(self, new_line='\n'):
        str_out = ""

        str_out += f'<h2 style="margin: 0;">{self.name}</h2>' + new_line

        str_out += '<p style="font-family: \'Book Antiqua\', serif; font-size: 110%;">'
        str_out += self.info.replace('\n', '<br/>')
        str_out += '</p>'
        return str_out

    def to_render(self):  # taki to_string, tylko do ekranu edycji
        render_dict = {'name': self.name, 'info': self.info}
        return render_dict
