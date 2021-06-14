from csv import DictReader

from src.Run.Engine import Engine


class UserEngine:
    def __init__(self, player_id):
        self.player_id = player_id
        self.engine = Engine()

        self.loaded_sessions = []

    def load_sessions(self):
        self.loaded_sessions = []
        camps_path = self.engine.campaigns_info_path
        with open(camps_path, mode='r', newline='', encoding='UTF-8') as camp_file:
            camp_reader = DictReader(camp_file)
            for row in camp_reader:
                self.engine.load_campaign(row['campaign_name'])

                all_sessions = self.engine.get_sessions()

                for sess in all_sessions:
                    sess.load_players()
                    if self.player_id in [player.id for player in sess.loaded_players]:
                        self.loaded_sessions.append(sess)

    def get_all_prev(self):
        self.load_sessions()
        prevs = []
        for session in self.loaded_sessions:
            session.load_players()

            player_id = self.player_id
            prev = {}

            player = [player for player in session.loaded_players if player.id == player_id]
            if len(player):
                player = player[0]
                try:
                    prev['character'] = player.character.name
                except AttributeError:
                    prev['character'] = None
                prev['campaign'] = session.campaign.campaign_name
                prev['date'] = session.session_date
                prev['session_id'] = session.session_id
            prevs.append(prev)
        return prevs

