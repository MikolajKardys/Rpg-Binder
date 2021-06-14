import ast
import csv

from src.CampaignTools.CsvManipulator import update_csv
from src.Run.Player import Player


class Session:
    def __init__(self, campaign, session_id, session_dir_path, session_date, acts=None, locations=None, characters=None,
                 items=None, spells=None):
        if acts is None:
            acts = []
        if items is None:
            items = []
        if locations is None:
            locations = []
        if spells is None:
            spells = []
        if characters is None:
            characters = []

        self.campaign = campaign
        self.session_id = session_id
        self.session_dir_path = session_dir_path
        self.session_date = session_date
        self.acts = acts

        self.characters = characters
        self.locations = locations
        self.items = items
        self.spells = spells

        self.loaded_players = None

    def update_csv(self):
        update_csv(self.campaign.get_sessions_info_path(), self.session_id, [self.session_id, self.session_dir_path,
                                                                             self.session_date, self.acts,
                                                                             self.locations, self.characters,
                                                                             self.items, self.spells])

    def save_act(self, text, ind):
        if int(ind) == -1:
            self.acts.append(text)
        else:
            self.acts[ind] = text

        self.update_csv()

    def add_player(self, player_id, character_id=None):
        self.load_players()

        new_player = Player(player_id)
        if new_player is None:
            raise IndexError(f"No player with this index: {player_id}")

        if character_id is not None:
            character = self.campaign.attributes['Character'][0].get(self.campaign, f"id={character_id}")
            new_player.__dict__['character'] = character

        cols = list(new_player.__dict__.keys())
        cols.remove('attributes')
        cols.remove('name')

        path = self.session_dir_path + "\\players.csv"
        with open(path, mode='a', newline='', encoding='UTF-8') as file:
            writer = csv.DictWriter(file, cols)

            play_dict = new_player.__dict__.copy()
            play_dict.pop('attributes')
            play_dict.pop('name')
            writer.writerow(play_dict)

    def remove_player(self, player_id):
        self.load_players()

        self.loaded_players = [player for player in self.loaded_players if player.id != int(player_id)]

        self.update_all_players()

    def load_players(self):
        self.loaded_players = []
        path = self.session_dir_path + "\\players.csv"
        with open(path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                player = Player.from_dict(self, row)

                self.loaded_players.append(player)

    def update_player_csv(self, player_id):
        player = [player for player in self.loaded_players if int(player.id) == int(player_id)][0]

        path = self.session_dir_path + "\\players.csv"

        update_csv(path, player.id, [player.id, player.locations, player.characters,
                                     player.items, player.spells, player.character,
                                     player.inventory, player.spell_book])

    def update_all_players(self):
        tmp = Player(-1)
        cols = list(tmp.__dict__.keys())
        cols.remove('attributes')
        cols.remove('name')

        path = self.session_dir_path + "\\players.csv"
        with open(path, mode='w', newline='', encoding='UTF-8') as file:
            writer = csv.DictWriter(file, cols)
            writer.writeheader()

            for player in self.loaded_players:
                play_dict = player.__dict__.copy()
                play_dict.pop('attributes')
                play_dict.pop('name')
                writer.writerow(play_dict)

    def load_data(self):
        sess_dict = None

        path = self.campaign.get_sessions_info_path()
        with open(path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row['session_id']) == self.session_id:
                    sess_dict = row
                    break

        for item in self.campaign.attributes.items():
            attribute = item[0].lower() + 's'

            allowed_tab = ast.literal_eval(sess_dict[attribute])

            obj_tab = item[1][0].load_obj(self.campaign)

            obj_tab = [obj for obj in obj_tab if int(obj.id) in allowed_tab]

            self.__dict__[attribute] = obj_tab

    def get_player_obj(self, player_id, obj_name):
        self.load_data()

        self.load_players()
        player = [player for player in self.loaded_players if player.id == int(player_id)]

        if not player:
            return None

        player = player[0]

        player_obj_tab = player.get_objects(obj_name)

        obj_tab = self.__dict__[obj_name]

        str_tab = [str(o) for o in obj_tab]
        for player_obj in player_obj_tab:
            if str(player_obj) in str_tab:
                obj_tab = [o for o in obj_tab if str(o) != str(player_obj)]
                str_tab.remove(str(player_obj))

        return player.attributes[obj_name], obj_tab

    def get_attr(self):  # :((
        return [(obj[1], obj[0].__name__.lower() + 's')
                for obj in self.campaign.attributes.values() if obj[1] != 'Postacie']
