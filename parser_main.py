from awpy import DemoParser
from lib.custom_stats import player_stats
import pandas as pd
import numpy as np
import json
import os

# Set the parse_rate equal to the tick rate at which you would like to parse the frames of the demo.
# This parameter only matters if parse_frames=True ()
# For reference, MM demos are usually 64 ticks, and pro/FACEIT demos are usually 128 ticks.


class CsGoDemoParser():

    def __init__(self,  demo_file, output, demo_path="", tick_rate=128):
        """
        Retrieves player stats and match information.

        @ret_type (str): The return type of player stats ('json' as default).
        @return (dict or str): Player stats in the specified return type.
        """
        self.output = {}
        self.match_date = self.get_date_from_demofile(demo_path+demo_file)
        self.match_id = self.calculate_file_hash(demo_path+demo_file)
        self.file_name = demo_file[6:]
        self.output_path = output
        if not os.path.exists(output):
            os.makedirs(output)

        # Parsing the demo file using the DemoParser from awpy lib
        self.demo_parser = DemoParser(
            demofile=demo_path+demo_file,
            demo_id=self.match_id,
            parse_rate=tick_rate,
            log=True,
            outpath=self.output_path
        )

    def get_player_stats(self, ret_type="json"):
        """
        @ret_type (String): This parameter will decide
        @return (@ret_type): The return type depends on the ret_type parameter (json as default)
        """
        self.data = self.demo_parser.parse()
        self.data = self.cast_steamID_to_str(self.data)
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

        first_kills_side = self.get_first_kills_sides(self.data)

        self.match_stats = {
            "teamWinnerName": team_winner_name,
            "teamWinnerSide": team_winner_side,
            "teamWinnerScore": team_winner_score,
            "teamWinnerPlayers": team_winner_players,
            "teamLoserName": team_loser_name,
            "teamLoserSide": team_loser_side,
            "teamLoserScore": team_loser_score,
            "teamLoserPlayers": team_loser_players,
            "firstKills": first_kills_side
        }

        self.match_duration = self.get_match_duration(
            int(self.data['playbackTicks'])/int(self.data['tickRate']))

        pstats = player_stats(self.data["gameRounds"], return_type=ret_type)
        # list with dicts with all stats from players
        self.lstats = list(pstats.values())
        for p in range(len(self.lstats)):
            self.lstats[p]['steamID'] = str(self.lstats[p]['steamID'])

        grenade_damage = self.get_grenade_damage(self.data)
        hs_deaths = self.get_headshot_deaths(self.data)
        first_kills = self.get_first_kills(self.data)
        weapon_kills = self.get_weapon_kills(self.data)
        weapon_deaths = self.get_weapon_deaths(self.data)
        player_kills = self.get_player_kills(self.data)
        player_deaths = self.get_player_deaths(self.data)
        player_flashed = self.get_player_flashed(self.data)
        flashed_by = self.get_flashed_by(self.data)
        rws = self.calculate_rws(self.data)

        self.lstats = self.add_value_by_steamID(self.lstats, grenade_damage)
        self.lstats = self.add_value_by_steamID(self.lstats, hs_deaths)
        self.lstats = self.add_value_by_steamID(self.lstats, first_kills)
        self.lstats = self.add_value_by_steamID(self.lstats, weapon_kills)
        self.lstats = self.add_value_by_steamID(self.lstats, weapon_deaths)
        self.lstats = self.add_value_by_steamID(self.lstats, player_kills)
        self.lstats = self.add_value_by_steamID(self.lstats, player_deaths)
        self.lstats = self.add_value_by_steamID(self.lstats, player_flashed)
        self.lstats = self.add_value_by_steamID(self.lstats, flashed_by)
        self.lstats = self.add_value_by_steamID(self.lstats, rws)

        self.validate_tags(self.lstats)

        if ret_type == "json":
            result = {
                "matchID": self.data["matchID"],
                "matchDate": self.match_date,
                "mapName": self.data["mapName"],
                "matchStats": self.match_stats,
                "playersStats": self.lstats
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

        file_path = self.output_path+self.match_date+"_payload_"+self.match_id+".json"
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

    def criar_json(self, file_name, match_id, match_date, map_name, match_duration, match_stats, player_stats):
        data = {
            "fileName": file_name,
            "matchID": match_id,
            "matchDate": match_date,
            "mapName": map_name,
            "matchDuration": match_duration,
            "matchStats": match_stats,
            "playersStats": player_stats
        }

        return data

    def add_value_by_steamID(self, lstats, records):
        """
        This method will add key and value to a dict, using the steamID as filter.

        @lstats (list): List of player stats.
        @records (Dict): Dict of keys and values to add in lstats.
        Example:
            {'steamID': '76561198061035335',
            'key': 'heDamage',
            'value': 405}
        """
        for record in records:
            for player in lstats:
                if player['steamID'] == record['steamID']:
                    player[record['key']] = record['value']
                    break
        return lstats

    def get_grenade_damage(self, data):
        dmg = pd.DataFrame()

        for game_round in data['gameRounds']:
            df = pd.DataFrame(game_round['damages'])
            df = df.loc[df['weaponClass'] == 'Grenade', [
                'attackerSteamID', 'weapon', 'hpDamageTaken']]
            df['weapon'] = np.where(df['weapon'].isin(
                ['Incendiary Grenade', 'Molotov']), 'fireDamage', df['weapon'])
            df['weapon'] = np.where(
                df['weapon'] == 'HE Grenade', 'heDamage', df['weapon'])
            df['weapon'] = np.where(
                df['weapon'] == 'Smoke Grenade', 'smokeDamage', df['weapon'])
            df['weapon'] = np.where(
                df['weapon'] == 'Flash Grenade', 'flashDamage', df['weapon'])
            dmg = pd.concat([dmg, df])

        dmg = dmg.groupby(['attackerSteamID', 'weapon'])[
            'hpDamageTaken'].sum().reset_index(name="hpDamageTaken")

        dmg = self.pivoting_unpivoting(
            dmg, ['attackerSteamID', 'weapon', 'hpDamageTaken'])

        return dmg.to_dict('records')

    def pivoting_unpivoting(self, df, columns=[]):
        """
        Renamed, Pivoting and filling NA values and unpivoting to set values

        @df (pandas dataframe): Dataframe to be changed
        @columns (list): list with columns to be renamed
            Example: ['attackerSteamID', 'weapon', 'hpDamageTaken']

        @return (pandas dataframe): unpivoted and filled NA values
            Example: df['steamID', 'key', 'value']
        """
        df = df.rename(
            columns={columns[0]: 'steamID',
                     columns[1]: 'key',
                     columns[2]: 'value'})

        df = df.pivot(index='steamID',
                      columns='key',
                      values='value').fillna(0)

        df = df.reset_index().melt(id_vars='steamID',
                                   var_name='key',
                                   value_name='value')

        return df

    def get_headshot_deaths(self, data):
        headshot_deaths = pd.DataFrame()
        for game_round in data['gameRounds']:
            df = pd.DataFrame(game_round['kills'])
            df = df.loc[df['isHeadshot'] == True,
                        ['isHeadshot', 'victimSteamID']]
            headshot_deaths = pd.concat([headshot_deaths, df])

        headshot_deaths = headshot_deaths.groupby(
            'victimSteamID')['isHeadshot'].count().reset_index(name="isHeadshot")
        headshot_deaths['hsDeaths'] = "hsDeaths"

        headshot_deaths = self.pivoting_unpivoting(
            headshot_deaths,
            ['victimSteamID', 'hsDeaths', 'isHeadshot']
        )
        return headshot_deaths.to_dict('records')

    def get_first_kills(self, data):
        first_kills = pd.DataFrame()
        for game_round in data['gameRounds']:
            df = pd.DataFrame(game_round['kills'])
            df = df.loc[df['isFirstKill'] == True, [
                'attackerSteamID', 'attackerSide', 'victimSteamID', 'victimSide', 'isFirstKill']]
            first_kills = pd.concat([first_kills, df])

        first_kills_agg = first_kills.groupby(['attackerSteamID', 'attackerSide'])[
            'isFirstKill'].count().reset_index(name="isFirstKill")
        first_kills_agg['attackerSide'] = np.where(
            first_kills_agg['attackerSide'] == 'CT', 'firstKillsCt', 'firstKillsTr')
        first_kills_agg = first_kills_agg.rename(
            columns={'attackerSteamID': 'steamID', 'attackerSide': 'key', 'isFirstKill': 'value'})

        first_deaths_agg = first_kills.groupby(['victimSteamID', 'victimSide'])[
            'isFirstKill'].count().reset_index(name="isFirstKill")
        first_deaths_agg['victimSide'] = np.where(
            first_deaths_agg['victimSide'] == 'CT', 'firstDeathsCt', 'firstDeathsTr')
        first_deaths_agg = first_deaths_agg.rename(
            columns={'victimSteamID': 'steamID', 'victimSide': 'key', 'isFirstKill': 'value'})

        first_kills = pd.concat([first_kills_agg, first_deaths_agg])
        first_kills = self.pivoting_unpivoting(
            first_kills, ['steamID', 'key', 'value'])
        return first_kills.to_dict('records')

    def get_weapon_kills(self, data):
        weapon_kill = pd.DataFrame()

        for game_round in data['gameRounds']:
            df = pd.DataFrame(game_round['kills'])
            weapon_kill = pd.concat([weapon_kill, df])

        weapon_kill = weapon_kill.groupby(['attackerSteamID', 'weapon'])[
            'weapon'].count().reset_index(name="weaponKills")
        grouped_dict = {}
        for attacker, group in weapon_kill.groupby('attackerSteamID'):
            weapons = group[['weapon', 'weaponKills']].to_dict(orient='list')
            grouped_dict[attacker] = dict(
                zip(weapons['weapon'], weapons['weaponKills']))

        weapon_kill = pd.DataFrame(grouped_dict.items(), columns=[
                                   'attackerSteamID', 'weaponKills'])
        weapon_kill['key'] = 'weaponKills'

        weapon_kill = self.pivoting_unpivoting(
            weapon_kill, ['attackerSteamID', 'key', 'weaponKills'])
        return weapon_kill.to_dict('records')

    def get_first_kills_sides(self, data):
        first_kills = []

        for r in data['gameRounds']:
            if 'kills' in r:
                kill = r['kills'][0]
                first_kill = {
                    'roundNum': r['roundNum'],
                    'winningSide': r['winningSide'],
                    'attackerSteamID': kill['attackerSteamID'],
                    'attackerSide': kill['attackerSide'],
                    'victimSteamID': kill['victimSteamID'],
                    'victimSide': kill['victimSide'],
                    'seconds': kill['seconds']
                }
                first_kills.append(first_kill)

        return first_kills

    def get_weapon_deaths(self, data):
        weapon_death = pd.DataFrame()

        for game_round in data['gameRounds']:
            df = pd.DataFrame(game_round['kills'])
            weapon_death = pd.concat([weapon_death, df])

        weapon_death = weapon_death.groupby(['victimSteamID', 'weapon'])[
            'weapon'].count().reset_index(name="weaponKills")
        grouped_dict = {}
        for victim, group in weapon_death.groupby('victimSteamID'):
            weapons = group[['weapon', 'weaponKills']].to_dict(orient='list')
            grouped_dict[victim] = dict(
                zip(weapons['weapon'], weapons['weaponKills']))

        weapon_death = pd.DataFrame(grouped_dict.items(), columns=[
                                    'victimSteamID', 'weaponKills'])
        weapon_death['key'] = 'weaponDeaths'

        weapon_death = self.pivoting_unpivoting(
            weapon_death, ['victimSteamID', 'key', 'weaponKills'])
        return weapon_death.to_dict('records')

    def get_player_kills(self, data):
        player_kill = pd.DataFrame()

        for game_round in data['gameRounds']:
            df = pd.DataFrame(game_round['kills'])
            player_kill = pd.concat([player_kill, df])

        player_kill = player_kill.groupby(['attackerSteamID', 'victimSteamID'])[
            'victimSteamID'].count().reset_index(name="playerKills")
        grouped_dict = {}
        for attacker, group in player_kill.groupby('attackerSteamID'):
            players = group[['victimSteamID', 'playerKills']
                            ].to_dict(orient='list')
            grouped_dict[attacker] = dict(
                zip(players['victimSteamID'], players['playerKills']))

        player_kill = pd.DataFrame(grouped_dict.items(), columns=[
                                   'attackerSteamID', 'playerKills'])
        player_kill['key'] = 'playerKills'

        player_kill = self.pivoting_unpivoting(
            player_kill, ['attackerSteamID', 'key', 'playerKills'])
        return player_kill.to_dict('records')

    def get_player_deaths(self, data):
        player_death = pd.DataFrame()

        for game_round in data['gameRounds']:
            df = pd.DataFrame(game_round['kills'])
            player_death = pd.concat([player_death, df])

        player_death = player_death.groupby(['victimSteamID', 'attackerSteamID'])[
            'attackerSteamID'].count().reset_index(name="playerDeaths")
        for p in range(len(player_death)):
            player_death.loc[p, 'attackerSteamID'] = player_death.loc[p, 'attackerSteamID'] if player_death.loc[p,
                                                                                                                'attackerSteamID'] != 'None' else player_death.loc[p, 'victimSteamID']
        grouped_dict = {}
        for attacker, group in player_death.groupby('victimSteamID'):
            players = group[['attackerSteamID', 'playerDeaths']
                            ].to_dict(orient='list')
            grouped_dict[attacker] = dict(
                zip(players['attackerSteamID'], players['playerDeaths']))

        player_death = pd.DataFrame(grouped_dict.items(), columns=[
                                    'victimSteamID', 'playerDeaths'])
        player_death['key'] = 'playerDeaths'

        player_death = self.pivoting_unpivoting(
            player_death, ['victimSteamID', 'key', 'playerDeaths'])
        return player_death.to_dict('records')

    def get_player_flashed(self, data):
        player_flashed = pd.DataFrame()

        for game_round in data['gameRounds']:
            df = pd.DataFrame(game_round['flashes'])
            player_flashed = pd.concat([player_flashed, df])

        player_flashed = player_flashed.groupby(['attackerSteamID', 'playerSteamID'])[
            'flashDuration'].sum().reset_index(name="playerFlashed")
        player_flashed['playerFlashed'] = round(
            player_flashed['playerFlashed'], 2)
        grouped_dict = {}
        for attacker, group in player_flashed.groupby('attackerSteamID'):
            players = group[['playerSteamID', 'playerFlashed']
                            ].to_dict(orient='list')
            grouped_dict[attacker] = dict(
                zip(players['playerSteamID'], players['playerFlashed']))

        player_flashed = pd.DataFrame(grouped_dict.items(), columns=[
                                      'attackerSteamID', 'playerFlashed'])
        player_flashed['key'] = 'playerFlashed'

        player_flashed = self.pivoting_unpivoting(
            player_flashed, ['attackerSteamID', 'key', 'playerFlashed'])
        return player_flashed.to_dict('records')

    def get_flashed_by(self, data):
        flashed_by = pd.DataFrame()

        for game_round in data['gameRounds']:
            df = pd.DataFrame(game_round['flashes'])
            flashed_by = pd.concat([flashed_by, df])

        flashed_by = flashed_by.groupby(['playerSteamID', 'attackerSteamID'])[
            'flashDuration'].sum().reset_index(name="flashedByPlayer")
        flashed_by['flashedByPlayer'] = round(flashed_by['flashedByPlayer'], 2)
        grouped_dict = {}
        for attacker, group in flashed_by.groupby('playerSteamID'):
            players = group[['attackerSteamID', 'flashedByPlayer']].to_dict(
                orient='list')
            grouped_dict[attacker] = dict(
                zip(players['attackerSteamID'], players['flashedByPlayer']))

        flashed_by = pd.DataFrame(grouped_dict.items(), columns=[
                                  'playerSteamID', 'flashedByPlayer'])
        flashed_by['key'] = 'flashedByPlayer'

        flashed_by = self.pivoting_unpivoting(
            flashed_by, ['playerSteamID', 'key', 'flashedByPlayer'])
        return flashed_by.to_dict('records')

    def get_match_duration(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def validate_tags(self, lstats):
        for player_stats in lstats:
            player_stats['firstDeathsCt'] = int(
                player_stats.get('firstDeathsCt', 0))
            player_stats['firstDeathsTr'] = int(
                player_stats.get('firstDeathsTr', 0))
            player_stats['firstKillsCt'] = int(
                player_stats.get('firstKillsCt', 0))
            player_stats['firstKillsTr'] = int(
                player_stats.get('firstKillsTr', 0))
            player_stats['hsDeaths'] = int(player_stats.get('hsDeaths', 0))
            player_stats['heDamage'] = int(player_stats.get('heDamage', 0))
            player_stats['fireDamage'] = int(player_stats.get('fireDamage', 0))
            player_stats['weaponKills'] = player_stats.get('weaponKills', {})
            player_stats['weaponDeaths'] = player_stats.get('weaponDeaths', {})
            player_stats['playerKills'] = player_stats.get('playerKills', {})
            player_stats['playerDeaths'] = player_stats.get('playerDeaths', {})
            player_stats['playerFlashed'] = player_stats.get(
                'playerFlashed', {})
            player_stats['flashedByPlayer'] = player_stats.get(
                'flashedByPlayer', {})
            player_stats['rws'] = round(player_stats.get('rws', 0), 2)

        return lstats

    def calculate_rws(self, data):
        rws = pd.DataFrame()

        for game_round in data['gameRounds']:
            for damage in game_round['damages']:
                if game_round['winningSide'] == damage['attackerSide'] and \
                   damage['attackerSide'] != damage['victimSide']:
                    df = pd.DataFrame(damage, index=[0])
                    if game_round['roundEndReason'] in ('BombDefused', 'TargetBombed'):
                        df['playerReason'] = game_round['bombEvents'][-1]['playerSteamID']
                    else:
                        df['playerReason'] = 'None'
                    df['roundEndReason'] = game_round['roundEndReason']
                    df['round'] = game_round['roundNum']
                    rws = pd.concat([rws, df])

        rws = rws.groupby(['round', 'attackerSteamID', 'attackerTeam', 'roundEndReason', 'playerReason'])[
            'hpDamageTaken'].sum().reset_index(name="totDamageRound")
        rws['sumDamageRound'] = rws.groupby(
            'round')['totDamageRound'].transform('sum')
        rws['rws'] = (rws['totDamageRound'] / rws['sumDamageRound']) * 100

        new_df = pd.DataFrame(columns=rws.columns)

        added_rounds = set()
        for index, row in rws.iterrows():
            if row['playerReason'] != 'None' and row['round'] not in added_rounds:
                current_round_rows = rws.loc[rws['round']
                                             == row['round'], 'rws']
                for idx, value in current_round_rows.items():
                    rws.at[idx, 'rws'] = rws.at[idx, 'rws'] * 0.7

                new_row = {
                    'round': row['round'],
                    'attackerSteamID': row['playerReason'],
                    'attackerTeam': row['attackerTeam'],
                    'roundEndReason': row['roundEndReason'],
                    'playerReason': row['playerReason'],
                    'totDamageRound': 0,
                    'sumDamageRound': row['sumDamageRound'],
                    'rws': 30.0
                }
                new_df = pd.concat([new_df, pd.DataFrame(
                    new_row, index=[0])], ignore_index=True)
                added_rounds.add(row['round'])

        rws = pd.concat([rws, new_df])

        rws = rws.groupby(['attackerSteamID'])[
            'rws'].sum().reset_index(name="rws")
        rws['rws'] = rws['rws'] / len(data['gameRounds'])
        rws['rws'] = round(rws['rws'], 2)
        rws['key'] = 'rws'

        rws = self.pivoting_unpivoting(rws, ['attackerSteamID', 'key', 'rws'])
        return rws.to_dict('records')

    def cast_steamID_to_str(self, data):
        for round_data in data['gameRounds']:
            ct_players = round_data['ctSide']['players']
            t_players = round_data['tSide']['players']
            kills = round_data['kills']
            damages = round_data['damages']
            grenades = round_data['grenades']
            bomb_events = round_data['bombEvents']
            flashes = round_data['flashes']

            for player in ct_players:
                player['steamID'] = str(player['steamID'])
            for player in t_players:
                player['steamID'] = str(player['steamID'])
            for kill in kills:
                kill['attackerSteamID'] = str(kill['attackerSteamID'])
                kill['victimSteamID'] = str(kill['victimSteamID'])
                kill['assisterSteamID'] = str(kill['assisterSteamID'])
                kill['flashThrowerSteamID'] = str(kill['flashThrowerSteamID'])
                kill['playerTradedSteamID'] = str(kill['playerTradedSteamID'])
            for damage in damages:
                damage['attackerSteamID'] = str(damage['attackerSteamID'])
                damage['victimSteamID'] = str(damage['victimSteamID'])
            for grenade in grenades:
                grenade['throwerSteamID'] = str(grenade['throwerSteamID'])
            for bomb_event in bomb_events:
                bomb_event['playerSteamID'] = str(bomb_event['playerSteamID'])
            for flash in flashes:
                flash['attackerSteamID'] = str(flash['attackerSteamID'])
                flash['playerSteamID'] = str(flash['playerSteamID'])

        return data

    def main(self):
        """
        This method will do everything to recover all data and analytical functions
        """
        self.get_player_stats()
        self.output_json(self.criar_json(self.file_name,
                                         self.match_id,
                                         self.match_date,
                                         self.data["mapName"],
                                         self.match_duration,
                                         self.match_stats,
                                         self.lstats))
