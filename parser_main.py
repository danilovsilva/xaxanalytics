from awpy import DemoParser
from awpy.analytics.stats import player_stats
import pandas as pd
import numpy as np
import json

# Set the parse_rate equal to the tick rate at which you would like to parse the frames of the demo.
# This parameter only matters if parse_frames=True ()
# For reference, MM demos are usually 64 ticks, and pro/FACEIT demos are usually 128 ticks.


class CsGoDemoParser():

    def __init__(self,  demo_file, demo_path="demos/", tick_rate=128):
        """
        Retrieves player stats and match information.

        @ret_type (str): The return type of player stats ('json' as default).
        @return (dict or str): Player stats in the specified return type.
        """
        self.output = {}
        self.match_date = self.get_date_from_demofile(demo_path+demo_file)
        self.match_id = self.calculate_file_hash(demo_path+demo_file)

        # Parsing the demo file using the DemoParser from awpy lib
        self.demo_parser = DemoParser(
            demofile=demo_path+demo_file,
            demo_id=self.match_id,
            parse_rate=tick_rate
        )

    def get_player_stats(self, ret_type="json"):
        """
        @ret_type (String): This parameter will decide
        @return (@ret_type): The return type depends on the ret_type parameter (json as default)
        """
        self.data = self.demo_parser.parse()
        last_round = self.data['gameRounds'][-1]

        if last_round['winningSide'] == 'CT':
            team_winner_name = last_round['ctTeam']
            team_winner_side = 'CT'
            team_winner_score = last_round['endCTScore']
            team_winner_players = last_round['ctSide']['players']
            team_loser_name = last_round['tTeam']
            team_loser_side = 'T'
            team_loser_score = last_round['endTScore']
            team_loser_players = last_round['tSide']['players']
        else:
            team_winner_name = last_round['tTeam']
            team_winner_side = 'T'
            team_winner_score = last_round['endTScore']
            team_winner_players = last_round['tSide']['players']
            team_loser_name = last_round['ctTeam']
            team_loser_side = 'CT'
            team_loser_score = last_round['endCTScore']
            team_loser_players = last_round['ctSide']['players']

        self.match_stats = {
            "teamWinnerName": team_winner_name,
            "teamWinnerSide": team_winner_side,
            "teamWinnerScore": team_winner_score,
            "teamWinnerPlayers": team_winner_players,
            "teamLoserName": team_loser_name,
            "teamLoserSide": team_loser_side,
            "teamLoserScore": team_loser_score,
            "teamLoserPlayers": team_loser_players,
        }

        pstats = player_stats(self.data["gameRounds"], return_type=ret_type)
        self.lstats = list(pstats.values()) # list with dicts with all stats from players

        grenade_damage = self.get_grenade_damage(self.data)

        self.lstats = self.add_value_by_steamName(self.lstats, grenade_damage)

        if ret_type == "json":
            result = {
                "matchID": self.data["matchID"],
                "matchDate": self.match_date,
                "mapName": self.data["mapName"],
                "matchStats": self.match_stats,
                "playersStats": pstats
            }
            return json.dumps(result)
        else:
            return pstats

    def output_json(self, data):
        """
        This method will just output the json data

        @data (String): The data to be written
        @file_path (String): The path and name of the file to be written
        """
        file_path="./output/payload_"+self.match_id+".json"
        with open(file_path, "w") as json_file:
            json.dump(data, json_file)

    def build_json_output(self, key, value):
        self.output[key] = value

    @staticmethod
    def get_date_from_demofile(file_path):
        """
        Get the date from the demo file name (e.g. pug_de_overpass_2023-05-26.dem")
        The format should be "xxxxx_YYYY-MM-DD_HH.dem"

        @return (String): the date in string type
        """
        date_string = file_path[len(file_path)-17:-7]
        return date_string

    def calculate_file_hash(self, demo_file):
        import zlib

        # Create a hash object
        hash_object = zlib.crc32(b'')

        # Read the file content
        with open(demo_file, 'rb') as file:
            for block in iter(lambda: file.read(4096), b''):
                # Update the hash object with each block
                hash_object = zlib.crc32(block, hash_object)

        # Get the hash value as a representation
        # hexadecimal de até 8 caracteres
        file_hash = format(hash_object & 0xFFFFFFFF, '08x')

        return file_hash

    def criar_json(self, match_id, match_date, map_name, match_stats, player_stats):
        data = {
            "matchID": match_id,
            "matchDate": match_date,
            "mapName": map_name,
            "matchStats": match_stats,
            "playersStats": player_stats
        }

        return data

    def add_value_by_steamName(self, lstats, records):
        '''
        This method will add key and value to a dict, using the playerName as filter.

        @lstats (list): List of player stats.
        @records (Dict): Dict of keys and values to add in lstats.
        Example:
            {'playerName': 'Aquino.Amt',
            'key': 'heDamage',
            'value': 405}
        '''
        for record in records:
            for player in lstats:
                if player['playerName'] == record['playerName']:
                    player[record['key']] = record['value']
                    break
        return lstats

    def get_grenade_damage(self, data):
        dmg = pd.DataFrame()
        for r in range(len(data['gameRounds'])):
            df = pd.DataFrame(data['gameRounds'][r]['damages'])
            df = df.loc[df['weaponClass'] == 'Grenade', ['attackerName', 'weapon', 'hpDamageTaken']]
            df['weapon'] = np.where(df['weapon'].isin(['Incendiary Grenade', 'Molotov']), 'fireDamage', df['weapon'])
            df['weapon'] = np.where(df['weapon'] == 'HE Grenade', 'heDamage', df['weapon'])
            df['weapon'] = np.where(df['weapon'] == 'Smoke Grenade', 'smokeDamage', df['weapon'])
            df['weapon'] = np.where(df['weapon'] == 'Flash Grenade', 'flashDamage', df['weapon'])
            dmg = pd.concat([dmg, df])

        dmg = dmg.groupby(['attackerName','weapon'])['hpDamageTaken'].sum().reset_index(name="hpDamageTaken")
        dmg = dmg.rename(columns={'attackerName': 'playerName', 'weapon': 'key', 'hpDamageTaken': 'value'})
        return dmg.to_dict('records')

    def main(self):
        """
        This method will do everything to recover all data and analytical functions
        """
        self.get_player_stats()
        self.output_json(self.criar_json(self.match_id,self.match_date,self.data["mapName"],self.match_stats,self.lstats))
