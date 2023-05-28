from awpy import DemoParser
from awpy.analytics.stats import player_stats
import json

# Set the parse_rate equal to the tick rate at which you would like to parse the frames of the demo.
# This parameter only matters if parse_frames=True ()
# For reference, MM demos are usually 64 ticks, and pro/FACEIT demos are usually 128 ticks.


class CsGoDemoParser():

    def __init__(self,  demo_file, demo_path="demos/", tick_rate=128):
        """
        @demo_path (String): The path of the file to be analyzed (e.g. "C:/Program Files (x86)/Steam/steamapps/common/Counter-Strike Global Offensive/csgo/")
        @demo_file (String): The file name (e.g. "pug_de_overpass_2023-05-26_17.dem")
        @tick_rate (Integer): Server tick rate of the demo
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
        pstats = player_stats(self.data["gameRounds"], return_type=ret_type)

        if self.data['gameRounds'][len(self.data['gameRounds'])-1]['winningSide'] == 'CT':
            self.match_stats = {
                "teamWinnerName": self.data['gameRounds'][len(self.data['gameRounds'])-1]['ctTeam'],
                "teamWinnerSide": 'CT',
                "teamWinnerScore": self.data['gameRounds'][len(self.data['gameRounds'])-1]['endCTScore'],
                "teamWinnerPlayers": self.data['gameRounds'][len(self.data['gameRounds'])-1]['ctSide']['players'],
                "teamLoserName": self.data['gameRounds'][len(self.data['gameRounds'])-1]['tTeam'],
                "teamLoserSide": 'T',
                "teamLoserScore": self.data['gameRounds'][len(self.data['gameRounds'])-1]['endTScore'],
                "teamLoserPlayers": self.data['gameRounds'][len(self.data['gameRounds'])-1]['tSide']['players'],
            }
        else:
            self.match_stats = {
                "teamWinnerName": self.data['gameRounds'][len(self.data['gameRounds'])-1]['tTeam'],
                "teamWinnerSide": 'T',
                "teamWinnerScore": self.data['gameRounds'][len(self.data['gameRounds'])-1]['endTScore'],
                "teamWinnerPlayers": self.data['gameRounds'][len(self.data['gameRounds'])-1]['tSide']['players'],
                "teamLoserName": self.data['gameRounds'][len(self.data['gameRounds'])-1]['ctTeam'],
                "teamLoserSide": 'CT',
                "teamLoserScore": self.data['gameRounds'][len(self.data['gameRounds'])-1]['endCTScore'],
                "teamLoserPlayers": self.data['gameRounds'][len(self.data['gameRounds'])-1]['ctSide']['players'],
            }

        self.lstats = list(pstats.values()) # list with dicts with all stats from players
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


    def main(self):
        """
        This method will do everything to recover all data and analytical functions
        """
        self.get_player_stats()
        self.output_json(self.criar_json(self.match_id,self.match_date,self.data["mapName"],self.match_stats,self.lstats))
