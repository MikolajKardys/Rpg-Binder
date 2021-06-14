from src.CampaignTools.Character import Character
from src.CampaignTools.Item import Item
from src.CampaignTools.Location import Location
from src.CampaignTools.Spells import Spell


class Campaign:
    def __init__(self, campaign_name, campaign_dir_path):
        self.campaign_name = campaign_name
        self.campaign_dir_path = campaign_dir_path

        self.sessions_info_path = self.campaign_dir_path + "\\sessions.csv"

        self.locations_info_path = self.campaign_dir_path + "\\locations.csv"
        self.characters_info_path = self.campaign_dir_path + "\\characters.csv"
        self.characters_info_path = self.campaign_dir_path + "\\items.csv"
        self.characters_info_path = self.campaign_dir_path + "\\spells.csv"

        self.attributes = {
            "Character": (Character, "Postacie"),
            "Location": (Location, "Lokacje"),
            "Item": (Item, "Przedmioty"),
            "Spell": (Spell, "Zaklęcia")
        }

    def __repr__(self):
        return str(self.campaign_name)

    def get_sessions_info_path(self):
        return self.sessions_info_path


