import csv
import os
import ast
from shutil import copyfile, rmtree

from src.CampaignTools.Campaign import Campaign
from src.CampaignTools.CsvManipulator import create_csv_file, count_csv_rows

from src.CampaignTools.Location import Location
from src.CampaignTools.Character import Character
from src.CampaignTools.Item import Item
from src.CampaignTools.Spells import Spell

from src.Run.Session import Session


class Engine:
    def __init__(self):
        self.user_data_path = os.path.abspath(__file__)[:-len("\\src\\Run\\Engine.py")] + "\\UserData"

        if not os.path.exists(self.user_data_path):
            os.mkdir(self.user_data_path)

        self.campaigns_info_path = self.user_data_path + "\\campaigns.csv"
        create_csv_file(self.campaigns_info_path, "campaign_name,dir_path")

        self.loaded_campaign = None
        self.loaded_session = None

        self.camp_objects = {
            "Location": (Location, "Lokacje"),
            "Character": (Character, "Postacie"),
            "Item": (Item, "Przedmioty"),
            "Spell": (Spell, "Zaklęcia")
        }

    def create_new_campaign(self, campaign_name):
        campaign_dir_path = os.path.abspath(__file__)[:-len("\\src\\Run\\Engine.py")] + "\\UserData\\" + str(
            campaign_name)

        with open(self.campaigns_info_path, mode='a', newline='', encoding='UTF-8') as info_file:
            writer = csv.writer(info_file)
            writer.writerow([campaign_name, campaign_dir_path])

        os.mkdir(campaign_dir_path)
        create_csv_file(campaign_dir_path + "\\sessions.csv", "session_id,dir_path,session_date,acts,locations,"
                                                              "characters,items,spells")

        create_csv_file(campaign_dir_path + "\\characters.csv", "id,name,pd,stats,health,armor,mana,pw,pkp,skills")

        create_csv_file(campaign_dir_path + "\\locations.csv", "id,name,info")

        create_csv_file(campaign_dir_path + "\\items.csv", "id,name,info")

        create_csv_file(campaign_dir_path + "\\spells.csv", "id,name,diff,cost,info")

        self.loaded_campaign = Campaign(campaign_name, campaign_dir_path)

    def remove_campaign(self, campaign_name):
        with open(self.campaigns_info_path, mode='r', newline='', encoding='UTF-8') as file:
            reader = csv.DictReader(file)
            cols = reader.fieldnames

            new_rows = []
            directory = None
            for row in reader:
                if row['campaign_name'] != campaign_name:
                    new_rows.append(row)
                else:
                    directory = row['dir_path']

        with open(self.campaigns_info_path, mode='w', newline='', encoding='UTF-8') as file:
            writer = csv.DictWriter(file, cols)

            writer.writeheader()
            for row in new_rows:
                writer.writerow(row)

        if directory is not None:
            rmtree(directory)

    def campaign_name_exists(self, campaign_name):
        with open(self.campaigns_info_path, mode='r', newline='', encoding='UTF-8') as info_file:
            reader = csv.reader(info_file)
            next(reader)
            for row in reader:
                if row[0] == campaign_name:
                    return True
        return False

    def load_campaign(self, campaign_name):
        while not self.campaign_name_exists(campaign_name):
            raise NameError("There isn't campaign with this name!")

        campaign_dir_path = os.path.abspath(__file__)[:-len("\\src\\Run\\Engine.py")] + "\\UserData\\"
        campaign_dir_path += str(campaign_name)
        self.loaded_campaign = Campaign(campaign_name, campaign_dir_path)

    def get_campaign_names(self):
        names = []
        with open(self.campaigns_info_path, mode='r', newline='', encoding='UTF-8') as info_file:
            reader = csv.reader(info_file)
            next(reader)
            for row in reader:
                names.append(row[0])
        return names

    def create_session(self, session_date, followup=None):
        row_num = count_csv_rows(self.loaded_campaign.sessions_info_path)
        session_id = row_num + 1
        session_dir_path = self.loaded_campaign.campaign_dir_path + "\\session" + str(session_id)

        os.mkdir(session_dir_path)

        if followup is not None:
            self.load_session(int(followup))

            copyfile(self.loaded_session.session_dir_path + "\\players.csv",
                     session_dir_path + "\\players.csv")

            self.loaded_session.session_id = session_id
            self.loaded_session.session_dir_path = session_dir_path
            self.loaded_session.session_date = session_date
            self.loaded_session.acts = []
        else:
            self.loaded_session = Session(self.loaded_campaign, session_id, session_dir_path, session_date)
            create_csv_file(session_dir_path + "\\players.csv",
                            "id,locations,characters,items,spells,character,inventory,spell_book")

        with open(self.loaded_campaign.sessions_info_path, mode='a', newline='') as info_file:
            sess_dict = self.loaded_session.__dict__.copy()
            sess_dict.pop("campaign")
            sess_dict.pop("loaded_players")

            writer = csv.DictWriter(info_file, sess_dict.keys())
            writer.writerow(sess_dict)

    def remove_session(self, session_id):
        session_dir = None
        new_rows = []
        with open(self.loaded_campaign.get_sessions_info_path(), "r") as file:
            reader = csv.DictReader(file)
            cols = reader.fieldnames
            for row in reader:
                if row['session_id'] == str(session_id):
                    session_dir = row['dir_path']
                else:
                    new_rows.append(row)

        with open(self.loaded_campaign.get_sessions_info_path(), "w", newline='') as file:
            writer = csv.DictWriter(file, cols)

            writer.writeheader()
            for row in new_rows:
                writer.writerow(row)

        if session_dir is not None:
            rmtree(session_dir)

    def get_sessions(self):
        path = self.loaded_campaign.sessions_info_path
        all_sessions = []
        with open(path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                new_session = Session(self.loaded_campaign, int(row['session_id']), row['dir_path'],
                                      row['session_date'], ast.literal_eval(row['acts']))

                all_sessions.append(new_session)

        all_sessions.sort(key=lambda sess: sess.session_date)

        return all_sessions

    def load_session(self, session_id):
        all_sessions = self.get_sessions()

        match = [sess for sess in all_sessions if sess.session_id == int(session_id)]

        if match:
            self.loaded_session = match[0]
        else:
            self.loaded_session = None

    def camp_add_obj(self, obj_class_name, obj_dict):
        obj_class = self.camp_objects[obj_class_name][0]

        new_obj = obj_class(self.loaded_campaign)
        obj_dict['id'] = None
        new_obj.obj_from_dict(obj_dict)

        new_obj.save_state()

    def sess_add_obj(self, obj_class_name, obj_id):
        key = obj_class_name.lower() + 's'

        obj_class = self.camp_objects[obj_class_name][0]

        obj = obj_class.get(self.loaded_campaign, f"id={obj_id}")

        if obj is None:
            raise NameError("Non-existent object id!")

        self.loaded_session.__dict__[key].append(obj)

        self.loaded_session.update_csv()
