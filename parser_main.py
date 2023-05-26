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

        # Parsing the demo file using the DemoParser from awpy lib
        self.demo_parser = DemoParser(
            demofile=demo_path+demo_file,
            demo_id=demo_file[:-4],
            parse_rate=tick_rate
        )

    def get_player_stats(self, ret_type="json"):
        """
        @ret_type (String): This parameter will decide
        @return (@ret_type): The return type depends on the ret_type parameter (json as default)
        """
        data = self.demo_parser.parse()
        pstats = player_stats(data["gameRounds"], return_type=ret_type)

        return pstats

    def output_json(self, file_path="./output/payload.json"):
        """
        This method will just output the json data

        @data (String): The data to be written
        @file_path (String): The path and name of the file to be written
        """
        json_file = open(file_path, "w")
        json.dump(self.output, json_file, indent=6)
        json_file.close()

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

    def main(self):
        """
        This method will do everything to recover all data and analytical functions
        """
        self.get_player_stats()
        self.output_json()
