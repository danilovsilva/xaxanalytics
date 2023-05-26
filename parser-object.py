from awpy import DemoParser
from awpy.analytics.stats import player_stats
import json

# Set the parse_rate equal to the tick rate at which you would like to parse the frames of the demo.
# This parameter only matters if parse_frames=True ()
# For reference, MM demos are usually 64 ticks, and pro/FACEIT demos are usually 128 ticks.
demo_parser = DemoParser(
    demofile="demos/003604372192294338675_1473557262.dem", demo_id="demotest1", parse_rate=128)


# Parse the demofile, output results to dictionary with df name as key
data = demo_parser.parse()


# There are a variety of top level keys
# You can view game rounds and events in 'gameRounds']
data["matchID"]
data["clientName"]
data["mapName"]
data["tickRate"]
data["playbackTicks"]
data["playbackFramesCount"]
data["parsedToFrameIdx"]
data["parserParameters"]
data["serverVars"]
data["matchPhases"]
data["matchmakingRanks"]
data["playerConnections"]
# From this value, you can extract player events via: data['gameRounds'][i]['kills'], etc.
data["gameRounds"]

df_stats = player_stats(data["gameRounds"])

json_file = open("./output/payload.json", "w")
json.dump(df_stats, json_file, indent=6)
json_file.close()
# You can also parse the data into dataframes using
data_df = demo_parser.parse(return_type="df")
