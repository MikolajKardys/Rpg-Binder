import csv
import ast


class Player:
    PLAYER_FILE = "logins.csv"

    def __init__(self, player_id, character=None):
        self.id = player_id

        with open(self.PLAYER_FILE, "r", encoding='UTF-8') as file:
            reader = csv.DictReader(file)
            names = [row['name'] for row in reader if row['type'] == 'USER' and row['id'] == str(self.id)]
            if names:
                self.name = names[0]
            else:
                self.name = ""

        self.locations = []   # Tu są wyjątkowo liczby; rzeczy, do których NIE MA dostępu
        self.characters = []
        self.items = []
        self.spells = []

        self.attributes = {
            'locations': 'Lokacje', 'characters': 'Postacie', 'items': 'Przedmioty', 'spells': 'Zaklęcia'
        }

        self.character = character

        self.inventory = []
        self.spell_book = []

    def get_objects(self, obj_name):
        return self.__dict__[obj_name]

    def __repr__(self):
        return str(self.__dict__)

    @classmethod
    def from_dict(cls, session, row):
        player = Player(int(row['id']))
        for key, value in row.items():
            if key != 'character':
                player.__dict__[key] = ast.literal_eval(value)
            else:
                player.__dict__[key] = value

        player.character = session.campaign.attributes['Character'][0].get(session.campaign,
                                                                           f"id={player.character}")

        return player
