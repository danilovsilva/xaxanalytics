from awpy import DemoParser
from lib.custom_stats import player_stats
import pandas as pd
import numpy as np
import json

# Set the parse_rate equal to the tick rate at which you would like to parse the frames of the demo.
# This parameter only matters if parse_frames=True ()
# For reference, MM demos are usually 64 ticks, and pro/FACEIT demos are usually 128 ticks.


class CsGoDemoParser():

    def __init__(self,  demo_file, demo_path="", tick_rate=128):
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
            team_winner_name = last_round['ctTeam'] if last_round['ctTeam'] != '' else 'Team 1'
            team_winner_side = 'CT'
            team_winner_score = last_round['endCTScore']
            team_winner_players = last_round['ctSide']['players']
            team_loser_name = last_round['tTeam'] if last_round['tTeam'] != '' else 'Team 2'
            team_loser_side = 'T'
            team_loser_score = last_round['endTScore']
            team_loser_players = last_round['tSide']['players']
        else:
            team_winner_name = last_round['tTeam'] if last_round['tTeam'] != '' else 'Team 1'
            team_winner_side = 'T'
            team_winner_score = last_round['endTScore']
            team_winner_players = last_round['tSide']['players']
            team_loser_name = last_round['ctTeam'] if last_round['ctTeam'] != '' else 'Team 2'
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

        self.match_duration = self.get_match_duration(
            int(self.data['playbackTicks'])/int(self.data['tickRate']))

        pstats = player_stats(self.data["gameRounds"], return_type=ret_type)
        # list with dicts with all stats from players
        self.lstats = list(pstats.values())

        grenade_damage = self.get_grenade_damage(self.data)
        hsDeaths = self.get_headshot_deaths(self.data)
        first_kills = self.get_first_kills(self.data)
        weapon_kills = self.get_weapon_kills(self.data)
        weapon_deaths = self.get_weapon_deaths(self.data)

        self.lstats = self.add_value_by_steamName(self.lstats, grenade_damage)
        self.lstats = self.add_value_by_steamName(self.lstats, hsDeaths)
        self.lstats = self.add_value_by_steamName(self.lstats, first_kills)
        self.lstats = self.add_value_by_steamName(self.lstats, weapon_kills)
        self.lstats = self.add_value_by_steamName(self.lstats, weapon_deaths)

        self.validate_tags(self.lstats)

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
        file_path = "./output/payload_"+self.match_id+".json"
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

    def criar_json(self, match_id, match_date, map_name, match_duration, match_stats, player_stats):
        data = {
            "matchID": match_id,
            "matchDate": match_date,
            "mapName": map_name,
            "matchDuration": match_duration,
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
            df = df.loc[df['weaponClass'] == 'Grenade', [
                'attackerName', 'weapon', 'hpDamageTaken']]
            df['weapon'] = np.where(df['weapon'].isin(
                ['Incendiary Grenade', 'Molotov']), 'fireDamage', df['weapon'])
            df['weapon'] = np.where(
                df['weapon'] == 'HE Grenade', 'heDamage', df['weapon'])
            df['weapon'] = np.where(
                df['weapon'] == 'Smoke Grenade', 'smokeDamage', df['weapon'])
            df['weapon'] = np.where(
                df['weapon'] == 'Flash Grenade', 'flashDamage', df['weapon'])
            dmg = pd.concat([dmg, df])

        dmg = dmg.groupby(['attackerName', 'weapon'])[
            'hpDamageTaken'].sum().reset_index(name="hpDamageTaken")

        dmg = self.pivoting_unpivoting(
            dmg, ['attackerName', 'weapon', 'hpDamageTaken'])

        return dmg.to_dict('records')

    def pivoting_unpivoting(self, df, columns=[]):
        """
        Renamed, Pivoting and filling NA values and unpivoting to set values

        @df (pandas dataframe): Dataframe to be changed
        @columns (list): list with columns to be renamed
            Example: ['attackerName', 'weapon', 'hpDamageTaken']

        @return (pandas dataframe): unpivoted and filled NA values
            Example: df['playerName', 'key', 'value']
        """
        df = df.rename(
            columns={columns[0]: 'playerName',
                     columns[1]: 'key',
                     columns[2]: 'value'})

        df = df.pivot(index='playerName',
                      columns='key',
                      values='value').fillna(0)

        df = df.reset_index().melt(id_vars='playerName',
                                   var_name='key',
                                   value_name='value')

        return df

    def get_headshot_deaths(self, data):
        headshot_deaths = pd.DataFrame()
        for r in range(len(data['gameRounds'])):
            df = pd.DataFrame(data['gameRounds'][r]['kills'])
            df = df.loc[df['isHeadshot'] == True, ['isHeadshot', 'victimName']]
            headshot_deaths = pd.concat([headshot_deaths, df])

        headshot_deaths = headshot_deaths.groupby(
            'victimName')['isHeadshot'].count().reset_index(name="isHeadshot")
        headshot_deaths['hsDeaths'] = "hsDeaths"

        headshot_deaths = self.pivoting_unpivoting(
            headshot_deaths,
            ['victimName', 'hsDeaths', 'isHeadshot']
        )
        return headshot_deaths.to_dict('records')

    def get_first_kills(self, data):
        first_kills = pd.DataFrame()
        for r in range(len(data['gameRounds'])):
            df = pd.DataFrame(data['gameRounds'][r]['kills'])
            df = df.loc[df['isFirstKill'] == True, [
                'attackerName', 'attackerSide', 'victimName', 'victimSide', 'isFirstKill']]
            first_kills = pd.concat([first_kills, df])

        first_kills_agg = first_kills.groupby(['attackerName', 'attackerSide'])[
            'isFirstKill'].count().reset_index(name="isFirstKill")
        first_kills_agg['attackerSide'] = np.where(
            first_kills_agg['attackerSide'] == 'CT', 'firstKillsCt', 'firstKillsTr')
        first_kills_agg = first_kills_agg.rename(
            columns={'attackerName': 'playerName', 'attackerSide': 'key', 'isFirstKill': 'value'})

        first_deaths_agg = first_kills.groupby(['victimName', 'victimSide'])[
            'isFirstKill'].count().reset_index(name="isFirstKill")
        first_deaths_agg['victimSide'] = np.where(
            first_deaths_agg['victimSide'] == 'CT', 'firstDeathsCt', 'firstDeathsTr')
        first_deaths_agg = first_deaths_agg.rename(
            columns={'victimName': 'playerName', 'victimSide': 'key', 'isFirstKill': 'value'})

        first_kills = pd.concat([first_kills_agg, first_deaths_agg])
        first_kills = self.pivoting_unpivoting(
            first_kills, ['playerName', 'key', 'value'])
        return first_kills.to_dict('records')

    def get_weapon_kills(self, data):
        weapon_kill = pd.DataFrame()

        for r in range(len(data['gameRounds'])):
            df = pd.DataFrame(data['gameRounds'][r]['kills'])
            weapon_kill = pd.concat([weapon_kill, df])

        weapon_kill = weapon_kill.groupby(['attackerName', 'weapon'])[
            'weapon'].count().reset_index(name="weaponKills")
        grouped_dict = {}
        for attacker, group in weapon_kill.groupby('attackerName'):
            weapons = group[['weapon', 'weaponKills']].to_dict(orient='list')
            grouped_dict[attacker] = dict(
                zip(weapons['weapon'], weapons['weaponKills']))

        weapon_kill = pd.DataFrame(grouped_dict.items(), columns=[
                                   'attackerName', 'weaponKills'])
        weapon_kill['key'] = 'weaponKills'

        weapon_kill = self.pivoting_unpivoting(
            weapon_kill, ['attackerName', 'key', 'weaponKills'])
        return weapon_kill.to_dict('records')

    def get_weapon_deaths(self, data):
        weapon_death = pd.DataFrame()

        for r in range(len(data['gameRounds'])):
            df = pd.DataFrame(data['gameRounds'][r]['kills'])
            weapon_death = pd.concat([weapon_death, df])

        weapon_death = weapon_death.groupby(['victimName', 'weapon'])[
            'weapon'].count().reset_index(name="weaponKills")
        grouped_dict = {}
        for victim, group in weapon_death.groupby('victimName'):
            weapons = group[['weapon', 'weaponKills']].to_dict(orient='list')
            grouped_dict[victim] = dict(
                zip(weapons['weapon'], weapons['weaponKills']))

        weapon_death = pd.DataFrame(grouped_dict.items(), columns=[
                                    'victimName', 'weaponKills'])
        weapon_death['key'] = 'weaponDeaths'

        weapon_death = self.pivoting_unpivoting(
            weapon_death, ['victimName', 'key', 'weaponKills'])
        return weapon_death.to_dict('records')

    def get_match_duration(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def validate_tags(self, lstats):
        for p in range(len(lstats)):
            lstats[p]['firstDeathsCt'] = int(lstats[p].get('firstDeathsCt', '0'))
            lstats[p]['firstDeathsTr'] = int(lstats[p].get('firstDeathsTr', '0'))
            lstats[p]['firstKillsCt'] = int(lstats[p].get('firstKillsCt', '0'))
            lstats[p]['firstKillsTr'] = int(lstats[p].get('firstKillsTr', '0'))
            lstats[p]['hsDeaths'] = int(lstats[p].get('hsDeaths', '0'))
            lstats[p]['heDamage'] = int(lstats[p].get('heDamage', '0'))
            lstats[p]['fireDamage'] = int(lstats[p].get('fireDamage', '0'))
            lstats[p]['weaponKills'] = lstats[p].get('weaponKills', '{}')
            lstats[p]['weaponDeaths'] = lstats[p].get('weaponDeaths', '{}')
        return lstats

    def main(self):
        """
        This method will do everything to recover all data and analytical functions
        """
        self.get_player_stats()
        self.output_json(self.criar_json(self.match_id,
                                         self.match_date,
                                         self.data["mapName"],
                                         self.match_duration,
                                         self.match_stats,
                                         self.lstats))
