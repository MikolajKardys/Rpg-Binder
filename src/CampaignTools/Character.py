import ast

from src.CampaignTools.CampObject import CampObject


class Character(CampObject):
    OBJ_PATH = "\\characters.csv"
    stat_names = {"strength": "Siła", "agility": "Zręczność", "endurance": "Kondycja",
                  "perception": "Spostrzegawczość", "intelligence": "Inteligencja", "will": "Wola"}

    tuple_names = {"health": "Punkty życia", "armor": "Pancerz", "mana": "Punkty magii",
                   "pw": "PW", "pkp": "PKP"}

    def __init__(self, campaign):
        super().__init__(campaign)

        self.name = ""
        self.pd = 0

        self.stats = {"strength": 0, "agility": 0, "endurance": 0, "perception": 0, "intelligence": 0, "will": 0}

        self.health = (0, 0)
        self.armor = (0, 0)
        self.mana = (0, 0)
        self.pw = (0, 0)
        self.pkp = (0, 0)

        self.skills = []

    def obj_from_dict(self, row):
        keys = list(row.keys())
        keys.remove("name")
        keys.remove("id")
        self.id = row["id"]
        self.name = row["name"]
        for atr in keys:
            self.__dict__[atr] = ast.literal_eval(row[atr])

    def to_string(self, new_line='\n'):
        def print_table(title, content):
            str_tmp = ""
            if title is not None:
                str_tmp += f'<h2>{title}</h2>'
            str_tmp += '<table style="border-collapse: collapse; ; width: 50%;">\n'
            for tmp_label, tmp_value in content:
                str_tmp += f'''
               <tr>
                   <td style="border: solid 1px white;">
                       <p style="font-size: 110%; margin: 0; font-family: 'Book Antiqua', serif;">{tmp_label}</p> 
                   </td>
                   <td style="border: solid 1px white;">
                       <p style="font-size: 110%; margin: 0; font-family: 'Book Antiqua', serif;">{tmp_value}</p>
                   </td>
               </tr>
               '''
            str_tmp += "</table>\n"
            return str_tmp

        str_out = f'''
        <h2 style="font-family: 'Book Antiqua', serif;">{self.name}</h2>
        <h3 style="display: inline;">Punkty doświadczenia: {self.pd}</h3>
        {new_line}
        {new_line}'''

        tuple_content = []
        for key, value in self.tuple_names.items():
            label = value
            tuple_value = self.__dict__[key]
            if tuple_value[1] > 0:
                tuple_content.append((label, f"{tuple_value[0]}/{tuple_value[1]}"))
        str_out += print_table(None, tuple_content)

        stat_content = []
        for key, value in self.stats.items():
            label = self.stat_names[key]
            stat_content.append((label, value))
        str_out += print_table('Statystyki', stat_content)

        skill_content = []
        for skill in self.skills:
            skill_content.append(skill)

        str_out += print_table('Umiejętności', skill_content)

        return str_out

    def to_render(self):  # taki to_string, tylko do ekranu edycji
        render_dict = self.__dict__.copy()
        render_dict.pop('campaign')
        render_dict.pop('id')

        stat_dict = {}
        for key, stat in render_dict['stats'].items():
            stat_dict[key] = (self.stat_names[key], stat)

        render_dict['stats'] = stat_dict

        tuple_keys = [key for key in self.__dict__.keys() if type(self.__dict__[key]) == tuple]

        tuples = [(key, self.tuple_names[key], self.__dict__[key]) for key in tuple_keys]

        render_dict['tuples'] = tuples

        render_dict = {key: value for key, value in render_dict.items() if key not in self.tuple_names.keys()}

        render_dict['skills'] = {str(i): self.skills[i] for i in range(len(self.skills))}

        return render_dict
