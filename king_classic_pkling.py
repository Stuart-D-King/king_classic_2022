import pandas as pd
import numpy as np
import sys
import pickle
import pdb
from collections import defaultdict
from scipy.stats import rankdata
import folium
from os import listdir, makedirs
from os.path import isfile, join, exists
import boto3


def past_locations_map():
    m = folium.Map(location=[40, -98], zoom_start=5)

    folium.Marker([33.455350, -83.241400], popup=folium.Popup('2021 - Greensboro, GA - Stuart King', max_width=300), icon=folium.Icon(color='red', icon='asterisk')).add_to(m)
    folium.Marker([28.554899, -82.387863], popup=folium.Popup('2020 - Brooksville, FL - Josh Duckett', max_width=300)).add_to(m)
    folium.Marker([33.494171, -111.926048], popup=folium.Popup('2018 & 2019 - Scottsdale, AZ - Alex King', max_width=300)).add_to(m)
    folium.Marker([36.805531, -114.06719], popup=folium.Popup('2017 - Mesquite, NV - Alex King', max_width=300)).add_to(m)
    folium.Marker([41.878114, -87.629798], popup=folium.Popup('2016 - Chicago, IL - Jerry King', max_width=300)).add_to(m)
    folium.Marker([34.502587, -84.951054], popup=folium.Popup('2015 - Calhoun, GA - Stuart King', max_width=300)).add_to(m)
    folium.Marker([42.331427, -83.045754], popup=folium.Popup('2014 - Detroit, MI - Reggie Sherrill', max_width=300)).add_to(m)
    folium.Marker([39.739236, -104.990251], popup=folium.Popup('2013 - Denver, CO - Stuart King', max_width=300)).add_to(m)
    folium.Marker([47.677683, -116.780466], popup=folium.Popup("2012 - Coeur d'Alene, ID - Jerry King", max_width=300)).add_to(m)
    folium.Marker([37.096528, -113.568416], popup=folium.Popup('2011 - St. George, UT - Reggie Sherrill', max_width=300)).add_to(m)
    folium.Marker([38.291859, -122.458036], popup=folium.Popup('2010 - Northern California - Alex King', max_width=300)).add_to(m)
    folium.Marker([39.237685, -120.02658], popup=folium.Popup('2009 - Lake Tahoe, CA - Alex King', max_width=300)).add_to(m)
    folium.Marker([47.606209, -122.332071], popup=folium.Popup('2008 - Seattle, WA - Alex King', max_width=300)).add_to(m)
    folium.Marker([35.960638, -83.920739], popup=folium.Popup('2007 - Knoxville, TN - Stuart King', max_width=300)).add_to(m)
    folium.Marker([33.520661, -86.80249], popup=folium.Popup('2006 - RTJ, Alabama - Gary Olson', max_width=300)).add_to(m)
    folium.Marker([32.366805, -86.299969], popup=folium.Popup('2005 - RTJ, Alabama - Stuart King', max_width=300)).add_to(m)

    m.save('templates/past_locations.html')


class Player(object):

    def __init__(self, name, hdcp, courses, tees, skins=True):
        self.name = name
        self.skins = skins
        self.hdcp = hdcp
        self.scores = dict()
        self.net_scores = dict()
        self.skins_scores = dict()
        self.courses = courses
        self.tees = tees

        for course in self.courses.keys():
            self.create_scorecard(course)


    def create_scorecard(self, course):
        self.scores[course] = dict((x,0) for x in range(1,19))
        self.net_scores[course] = dict((x,0) for x in range(1,19))
        self.skins_scores[course] = dict((x,0) for x in range(1,19))


    def post_score(self, course, hole, score, hdcp):
        self.scores[course][hole] = score

        course_dct = self.courses[course]
        par = course_dct['par']
        hdcps = course_dct['hdcps']
        hole_hdcp = hdcps[hole - 1]

        if 'The National' in course:
            if (hdcp % 2) == 0:
                hdcp = hdcp / 2
                if hole_hdcp <= hdcp:
                    self.skins_scores[course][hole] = score - 1
                elif hdcp < 0 and hole_hdcp <= abs(hdcp):
                    self.skins_scores[course][hole] = score + 1
                else:
                    self.skins_scores[course][hole] = score

                if hdcp > 18:
                    super_hdcp = hdcp - 18
                    if hole_hdcp <= super_hdcp:
                        self.net_scores[course][hole] = score - 2
                    else:
                        self.net_scores[course][hole] = score - 1
                elif hole_hdcp <= hdcp:
                    self.net_scores[course][hole] = score - 1
                elif hdcp < 0 and hole_hdcp <= abs(hdcp):
                    self.net_scores[course][hole] = score + 1
                else:
                    self.net_scores[course][hole] = score
            else:
                hdcp = round(hdcp / 2)
                if hole <= 9:
                    if hole_hdcp <= hdcp:
                        self.skins_scores[course][hole] = score - 1
                    elif hdcp < 0 and hole_hdcp <= abs(hdcp):
                        self.skins_scores[course][hole] = score + 1
                    else:
                        self.skins_scores[course][hole] = score

                    if hdcp > 18:
                        super_hdcp = hdcp - 18
                        if hole_hdcp <= super_hdcp:
                            self.net_scores[course][hole] = score - 2
                        else:
                            self.net_scores[course][hole] = score - 1
                    elif hole_hdcp <= hdcp:
                        self.net_scores[course][hole] = score - 1
                    elif hdcp < 0 and hole_hdcp <= abs(hdcp):
                        self.net_scores[course][hole] = score + 1
                    else:
                        self.net_scores[course][hole] = score
                else:
                    hdcp -= 1
                    if hole_hdcp <= hdcp:
                        self.skins_scores[course][hole] = score - 1
                    elif hdcp < 0 and hole_hdcp <= abs(hdcp):
                        self.skins_scores[course][hole] = score + 1
                    else:
                        self.skins_scores[course][hole] = score

                    if hdcp > 18:
                        super_hdcp = hdcp - 18
                        if hole_hdcp <= super_hdcp:
                            self.net_scores[course][hole] = score - 2
                        else:
                            self.net_scores[course][hole] = score - 1
                    elif hole_hdcp <= hdcp:
                        self.net_scores[course][hole] = score - 1
                    elif hdcp < 0 and hole_hdcp <= abs(hdcp):
                        self.net_scores[course][hole] = score + 1
                    else:
                        self.net_scores[course][hole] = score

        if hole_hdcp <= hdcp:
            self.skins_scores[course][hole] = score - 1
        elif hdcp < 0 and hole_hdcp <= abs(hdcp):
            self.skins_scores[course][hole] = score + 1
        else:
            self.skins_scores[course][hole] = score

        if hdcp > 18:
            super_hdcp = hdcp - 18
            if hole_hdcp <= super_hdcp:
                self.net_scores[course][hole] = score - 2
            else:
                self.net_scores[course][hole] = score - 1
        elif hole_hdcp <= hdcp:
            self.net_scores[course][hole] = score - 1
        elif hdcp < 0 and hole_hdcp <= abs(hdcp):
            self.net_scores[course][hole] = score + 1
        else:
            self.net_scores[course][hole] = score


    def show_scorecard(self, course, net=False):
        if net:
            return self.net_scores[course]

        return self.scores[course]


    def front_nine(self, course, net=False, skins=False):
        if net:
            front = [v for k, v in self.net_scores[course].items()][:9]
            return front

        if skins:
            front = [v for k, v in self.skins_scores[course].items()][:9]
            return front

        front = [v for k, v in self.scores[course].items()][:9]
        return front


    def back_nine(self, course, net=False, skins=False):
        if net:
            back = [v for k,v in self.net_scores[course].items()][9:]
            return back

        if skins:
            back = [v for k,v in self.skins_scores[course].items()][9:]
            return back

        back = [v for k, v in self.scores[course].items()][9:]
        return back


    def calc_course_score(self, course, net=False, skins=False, only_score=False):
        if net:
            score = sum(self.net_scores[course].values())
        elif skins:
            score = sum(self.skins_scores[course].values())
        else:
            score = sum(self.scores[course].values())

        thru = sum([1 for x in self.scores[course].values() if x > 0])

        course_dct = self.courses[course]
        par = sum(course_dct['par'][:thru])
        to_par = score - par

        if only_score:
            return score
        else:
            return score, to_par, thru


    def calc_total_score(self, net=False):
        total = 0
        for course in self.scores.keys():
            if net:
                total += sum(self.net_scores[course].values())
            else:
                total += sum(self.scores[course].values())

        return total


class PlayGolf(object):

    def __init__(self):
        self.courses = {
            'The Oconee' : {
                'par': [5,4,4,4,3,4,5,3,4,5,4,4,3,4,3,4,5,4],
                'hdcps': [9,11,1,17,15,7,5,13,3,14,8,10,12,6,18,2,16,4],
                'tees': {
                    'One': (73.8, 139),
                    'Two': (72.8, 136),
                    'Tournament': (71.4, 134),
                    'Three': (70.5, 130),
                    'Three/Four': (68.8, 126),
                    'Four': (67.5, 121),
                    'Four/Five': (65.9, 118)
                }
            },
            'The National - Ridge/Bluff' : {
                'par': [4,4,3,4,3,5,4,5,4,4,4,5,3,4,5,3,4,4],
                'hdcps': [5,7,9,2,4,3,6,8,1,8,3,7,9,6,5,4,1,2],
                'tees': {
                    'One': (74.2, 143),
                    'Two': (72.5, 141),
                    'Tournament': (71.4, 136),
                    'Three': (70.4, 133),
                    'Four': (68.8, 128),
                    'Four/Five': (67.6, 127),
                    'Five': (66.9, 122)
                }
            },
            'The National - Ridge/Cove' : {
                'par': [4,4,3,4,3,5,4,5,4,4,4,3,5,4,5,3,4,4],
                'hdcps': [5,7,9,2,4,3,6,8,1,6,2,9,5,4,7,8,1,3],
                'tees': {
                    'One': (74.6, 143),
                    'Two': (72.5, 141),
                    'Tournament': (71.7, 136),
                    'Three': (70.4, 132),
                    'Four': (68.8, 127),
                    'Four/Five': (67.3, 125),
                    'Five': (66.6, 120)
                }
            },
            'The National - Bluff/Ridge' : {
                'par': [4,4,5,3,4,5,3,4,4,4,4,3,4,3,5,4,5,4],
                'hdcps': [8,3,7,9,6,5,4,1,2,5,7,9,2,4,3,6,8,1],
                'tees': {
                    'One': (74.2, 143),
                    'Two': (72.5, 141),
                    'Tournament': (71.4, 136),
                    'Three': (70.4, 133),
                    'Four': (68.8, 128),
                    'Four/Five': (67.6, 127),
                    'Five': (66.9, 122)
                }
            },
            'The National - Bluff/Cove' : {
                'par': [4,4,5,3,4,5,3,4,4,4,4,3,5,4,5,3,4,4],
                'hdcps': [8,3,7,9,6,5,4,1,2,6,2,9,5,4,7,8,1,3],
                'tees': {
                    'One': (74.4, 143),
                    'Two': (72.4, 141),
                    'Tournament': (71.5, 137),
                    'Three': (70.4, 134),
                    'Four': (69, 127),
                    'Four/Five': (67.7, 128)
                }
            },
            'The National - Cove/Bluff' : {
                'par': [4,4,3,5,4,5,3,4,4,4,4,5,3,4,5,3,4,4],
                'hdcps': [6,2,9,5,4,7,8,1,3,8,3,7,9,6,5,4,1,2],
                'tees': {
                    'One': (74.4, 143),
                    'Two': (72.4, 141),
                    'Tournament': (71.5, 137),
                    'Three': (70.4, 134),
                    'Four': (69, 127),
                    'Four/Five': (67.7, 128)
                }
            },
            'The National - Cove/Ridge' : {
                'par': [4,4,3,5,4,5,3,4,4,4,4,3,4,3,5,4,5,4],
                'hdcps': [6,2,9,5,4,7,8,1,3,5,7,9,2,4,3,6,8,1],
                'tees': {
                    'One': (74.6, 143),
                    'Two': (72.5, 141),
                    'Tournament': (71.7, 136),
                    'Three': (70.4, 132),
                    'Four': (68.8, 127),
                    'Four/Five': (67.3, 125),
                    'Five': (66.6, 120)
                }
            },
            'The Landing' : {
                'par': [4,5,3,4,4,5,3,4,4,4,3,4,4,5,4,5,3,4],
                'hdcps': [3,13,15,1,11,9,17,5,7,6,8,2,10,12,4,14,18,16],
                'tees': {
                    'One': (74.5, 138),
                    'Two': (71.7, 131),
                    'Tournament': (70.6, 129),
                    'Three': (69.9, 127),
                    'Three/Four': (68.6, 124),
                    'Four': (67.3, 121)
                }
            },
            'The Landing Replay' : {
                'par': [4,5,3,4,4,5,3,4,4,4,3,4,4,5,4,5,3,4],
                'hdcps': [3,13,15,1,11,9,17,5,7,6,8,2,10,12,4,14,18,16],
                'tees': {
                    'One': (74.5, 138),
                    'Two': (71.7, 131),
                    'Tournament': (70.6, 129),
                    'Three': (69.9, 127),
                    'Three/Four': (68.6, 124),
                    'Four': (67.3, 121)
                }
            },
            'Great Waters' : {
                'par': [4,5,4,3,4,5,4,3,4,4,4,5,4,3,4,4,3,5],
                'hdcps': [11,17,3,13,1,9,7,15,5,4,16,10,6,18,8,2,14,12],
                'tees': {
                    'Golden Bear': (75.7, 143),
                    'One': (73.3, 138),
                    'One/Two': (72, 135),
                    'Two': (70.8, 132),
                    'Two/Three': (69.6, 128),
                    'Three': (68.1, 125),
                    'Three/Four': (66.5, 121)
                }
            },
            'Great Waters Replay' : {
                'par': [4,5,4,3,4,5,4,3,4,4,4,5,4,3,4,4,3,5],
                'hdcps': [11,17,3,13,1,9,7,15,5,4,16,10,6,18,8,2,14,12],
                'tees': {
                    'Golden Bear': (75.7, 143),
                    'One': (73.3, 138),
                    'One/Two': (72, 135),
                    'Two': (70.8, 132),
                    'Two/Three': (69.6, 128),
                    'Three': (68.1, 125),
                    'Three/Four': (66.5, 121)
                }
            }
        }
        self.pkl_path = 'pkl_files/'
        self.rc_team1_pts = 0
        self.rc_team2_pts = 0


    def to_bucket(self, f_name):
        '''
        Write file to s3 bucket

        INPUT: f - file to write
        '''
        # Specify the service
        s3 = boto3.resource('s3')
        write_name = f_name.replace('_','-')
        s3.Bucket('king-classic-2022').upload_file(f_name, write_name)


    def add_player(self, name, hdcp, tees, skins=True):
        if not exists(self.pkl_path):
            makedirs(self.pkl_path)

        if not isfile(self.pkl_path + name.strip().lower().replace(' ','_')):
            golfer = Player(name, hdcp, self.courses, tees, skins)
            f_name = '{}{}.pkl'.format(self.pkl_path, name.strip().lower().replace(' ','_'))
            with open(f_name, 'wb') as f:
                pickle.dump(golfer, f)

            # self.to_bucket(f_name)


    def add_score(self, player, course, hole, score):
        hdcp = self.calc_handicap(player, course)
        f_name = '{}{}.pkl'.format(self.pkl_path, player.strip().lower().replace(' ','_'))
        with open(f_name, 'rb') as f:
            golfer = pickle.load(f)

        golfer.post_score(course, hole, score, hdcp)

        with open(f_name, 'wb') as f:
            pickle.dump(golfer, f)

        # self.to_bucket(f_name)


    def show_player_course_score(self, player, course, net=False):
        with open('{}{}.pkl'.format(self.pkl_path, player.strip().lower().replace(' ','_')), 'rb') as f:
            golfer = pickle.load(f)
        score  = golfer.calc_course_score(course, net, only_score=True)
        return score


    def show_player_total_score(self, player, net=False):
        with open('{}{}.pkl'.format(self.pkl_path, player.strip().lower().replace(' ','_')), 'rb') as f:
            golfer = pickle.load(f)
        total_score = golfer.calc_total_score(net)
        return total_score


    def leaderboard(self, net=True):
        allfiles = [f for f in listdir(self.pkl_path) if isfile(join(self.pkl_path, f))]

        golfers = []
        for pf in allfiles:
            with open('{}'.format(self.pkl_path) + pf, 'rb') as f:
                golfers.append(pickle.load(f))

        names = []
        scores = []
        to_par = []
        thru = []
        for golfer in golfers:
            names.append(golfer.name)
            total = 0
            tp = 0
            tr = 0
            # for course in golfer.scores.keys():
            for course in [
                    # 'The National - Ridge/Bluff',
                    # 'The National - Ridge/Cove',
                    # 'The National - Bluff/Cove',
                    # 'The National - Bluff/Ridge',
                    # 'The National - Cove/Ridge',
                    # 'The National - Cove/Bluff',
                    'The Oconee',
                    'Great Waters',
                    'The Landing Replay',
                    'Great Waters Replay']:
                score, p, hp = golfer.calc_course_score(course, net)
                total += score
                tp += p
                tr += hp
            scores.append(total)
            to_par.append(tp)
            thru.append(tr)

        # rank = list(rankdata(scores, method='min'))
        rank = list(rankdata(to_par, method='min'))
        # rank = list(np.unique(scores, return_inverse=True)[1])
        results = list(zip(rank, names, to_par, thru, scores))
        sorted_results = sorted(results, key=lambda x: x[0])

        df = pd.DataFrame(sorted_results, columns=['Position', 'Name', 'To Par', 'Thru', 'Net Total'])
        # df.set_index('Position', inplace=True)

        return df


    def calc_skins(self, course, net=True):
        allfiles = [f for f in listdir(self.pkl_path) if isfile(join(self.pkl_path, f))]
        golfers = []
        for pf in allfiles:
            with open('{}'.format(self.pkl_path) + pf, 'rb') as f:
                golfers.append(pickle.load(f))

        players = [golfer for golfer in golfers if golfer.skins == True]
        names = [golfer.name for golfer in golfers]

        pot = len(names) * 5
        cols = [str(x) for x in range(1, 19)]

        scores = []
        if net:
            for player in players:
                scores.append(list(player.skins_scores[course].values()))
        else:
            for player in players:
                scores.append(list(player.scores[course].values()))

        df = pd.DataFrame(data=scores, index=names, columns=cols)
        low_scores = df.min(axis=0)
        # skins = []
        skins_dct = defaultdict(list)
        for hole, low_score in zip(range(1, 19), low_scores):
            if low_score == 0:
                continue
            scores = list(df[str(hole)].values)
            if scores.count(low_score) == 1:
                # skins.append((hole, df[str(hole)].idxmin()))
                skins_dct[df[str(hole)].idxmin()].append(str(hole))

        results = []
        for name in names:
            results.append((name, skins_dct[name], len(skins_dct[name])))
            # results.append((name, skins.count(name)))

        results = [(name, ', '.join(holes), n_skins) for name, holes, n_skins in results]
        sorted_results = sorted(results, key=lambda x: x[2], reverse=True)

        total_skins = sum(n for _, _, n in sorted_results)
        skin_value = pot / total_skins

        final_results = [(name, holes, skins * skin_value) for name, holes, skins in sorted_results]

        df_results = [(name, holes, round(winnings/skin_value), float(winnings)) for name, holes, winnings in final_results]

        df_skins = pd.DataFrame(df_results, columns=['Player', 'Holes Won', 'Skins', 'Winnings'])
        df_skins['Winnings'] = df_skins['Winnings'].map('${:,.2f}'.format)

        return df_skins


    def calc_teams(self, teams, course):
        allfiles = [f for f in listdir(self.pkl_path) if isfile(join(self.pkl_path, f))]
        golfers = []
        for pf in allfiles:
            with open('{}'.format(self.pkl_path) + pf, 'rb') as f:
                golfers.append(pickle.load(f))

        names = [golfer.name for golfer in golfers]
        dct = dict(zip(names, golfers))
        # pot = len(teams) * 20
        team_scores = []
        for (p1, p2) in teams:
            g1 = dct[p1]
            g2 = dct[p2]
            s1 = g1.calc_course_score(course, net=True, only_score=True)
            s2 = g2.calc_course_score(course, net=True, only_score=True)
            team_score = s1 + s2
            team_scores.append(team_score)

        team_nums = [idx+1 for idx, _ in enumerate(range(len(teams)))]
        rank = list(rankdata(team_scores, method='min'))
        results = list(zip(rank, team_nums, team_scores))
        sorted_results = sorted(results, key=lambda x: x[0])

        clean_teams = [p1 + ' / ' + p2 for p1, p2 in teams]
        final_results = [(r, clean_teams[i-1], s) for r,i,s in sorted_results]

        df = pd.DataFrame(final_results, columns=['Position', 'Team', 'Score'])
        df['Winnings'] = 0

        first = [t for r,t,s in final_results if r == 1]
        second = [t for r,t,s in final_results if r == 2]
        third = [t for r,t,s in final_results if r == 3]

        if len(first) == 1 and len(second) == 1:
            f_winnings = 60
            s_winnings = 40
            t_winnings = 20 / len(third)
            df['Winnings'] = np.where(df['Position'] == 1, f_winnings, df['Winnings'])
            df['Winnings'] = np.where(df['Position'] == 2, s_winnings, df['Winnings'])
            df['Winnings'] = np.where(df['Position'] == 3, t_winnings, df['Winnings'])
        elif len(first) == 2:
            f_winnings = (60 + 40) / 2
            s_winnings = 20 / len(third)
            df['Winnings'] = np.where(df['Position'] == 1, f_winnings, df['Winnings'])
            df['Winnings'] = np.where(df['Position'] == 3, s_winnings, df['Winnings'])
        elif len(first) == 1  and len(second) > 1:
            f_winnings = 60
            s_winnings = (40 + 20) / len(second)
            df['Winnings'] = np.where(df['Position'] == 1, f_winnings, df['Winnings'])
            df['Winnings'] = np.where(df['Position'] == 2, s_winnings, df['Winnings'])
        elif len(first) > 2:
            f_winnings = (60 + 40 + 20) / len(first)
            df['Winnings'] = np.where(df['Position'] == 1, f_winnings, df['Winnings'])

        df['Winnings'] = df['Winnings'].map('${:,.2f}'.format)

        return df


    def player_scorecards(self, players, course, net=False, skins=False):
        course_dct = self.courses[course]
        course_par = course_dct['par']
        course_hdcps = course_dct['hdcps']

        front_par = sum(course_par[:9])
        back_par = sum(course_par[9:])
        total_par = sum(course_par)
        par = course_par[:9] + [front_par] + course_par[9:] + [back_par, total_par, 0, 0]
        hdcp = course_hdcps[:9] + [0] + course_hdcps[9:] + [0,0,0,0]
        scores = [par, hdcp]

        allfiles = [f for f in listdir(self.pkl_path) if isfile(join(self.pkl_path, f))]
        golfers = []
        for pf in allfiles:
            with open('{}'.format(self.pkl_path) + pf, 'rb') as f:
                golfers.append(pickle.load(f))

        names = [golfer.name for golfer in golfers]
        dct = dict(zip(names, golfers))

        for player in players:
            golfer = dct[player]

            if net:
                front = golfer.front_nine(course, net=True)
                front_tot = sum(front)
                back = golfer.back_nine(course, net=True)
                back_tot = sum(back)
                total = golfer.calc_course_score(course, net=True, only_score=True)
                net_total = golfer.calc_course_score(course, net=True, only_score=True)
            elif skins:
                front = golfer.front_nine(course, skins=True)
                front_tot = sum(front)
                back = golfer.back_nine(course, skins=True)
                back_tot = sum(back)
                total = golfer.calc_course_score(course, skins=True, only_score=True)
                net_total = golfer.calc_course_score(course, skins=True, only_score=True)
            else:
                front = golfer.front_nine(course)
                front_tot = sum(front)
                back = golfer.back_nine(course)
                back_tot = sum(back)
                total = golfer.calc_course_score(course, only_score=True)
                net_total = golfer.calc_course_score(course, net=True, only_score=True)
            hdcp = self.calc_handicap(player, course)
            score = front + [front_tot] + back + [back_tot, total, hdcp, net_total]
            scores.append(score)

        idx = ['Par', 'Hdcp'] + players.copy()

        cols = [str(x) for x in range(1, 19)]
        all_cols = cols[:9] + ['Front'] + cols[9:] + ['Back', 'Total', 'Hdcp', 'Net']

        df = pd.DataFrame(data=scores, index=idx, columns=all_cols)
        for col in df.columns:
            df[col] = df[col].astype(str)
        df.loc['Par'] = df.loc['Par'].replace(['0'],'')
        df.loc['Hdcp'] = df.loc['Hdcp'].replace(['0'],'')
        return df


    def calc_handicap(self, player, course):
        allfiles = [f for f in listdir(self.pkl_path) if isfile(join(self.pkl_path, f))]
        golfers = []
        for pf in allfiles:
            with open('{}'.format(self.pkl_path) + pf, 'rb') as f:
                golfers.append(pickle.load(f))

        names = [golfer.name for golfer in golfers]
        dct = dict(zip(names, golfers))

        golfer = dct[player]

        course_dct = self.courses[course]
        course_par = sum(course_dct['par'])
        golfer_tees = golfer.tees[course]
        rating, slope = course_dct['tees'][golfer_tees]
        calc_hdcp = round((golfer.hdcp * (slope / 113)) + (rating - course_par))

        return calc_hdcp


    def show_handicaps(self, course):
        allfiles = [f for f in listdir(self.pkl_path) if isfile(join(self.pkl_path, f))]
        golfers = []
        for pf in allfiles:
            with open('{}'.format(self.pkl_path) + pf, 'rb') as f:
                golfers.append(pickle.load(f))

        names = [golfer.name for golfer in golfers]
        hdcps = [golfer.hdcp for golfer in golfers]
        tees = [golfer.tees[course] for golfer in golfers]
        course_hdcps = [self.calc_handicap(name, course) for name in names]
        results = list(zip(names, tees, hdcps, course_hdcps))
        sorted_results = sorted(results, key=lambda x: x[0])

        df_hdcps = pd.DataFrame(sorted_results, columns=['Player', 'Tee', 'Handicap', 'Course Handicap'])

        return df_hdcps


    def calc_ryder_cup(self):
        allfiles = [f for f in listdir(self.pkl_path) if isfile(join(self.pkl_path, f))]
        golfers = []
        for pf in allfiles:
            with open('{}'.format(self.pkl_path) + pf, 'rb') as f:
                golfers.append(pickle.load(f))

        players = [golfer for golfer in golfers]
        names = [golfer.name for golfer in golfers]
        dct = dict(zip(names, golfers))

        matchups1 = [('Alex King', 'Stuart King'),
                 ('Jeff Veness', 'Zach Taylor'),
                 ('Jerry King', 'Josh Duckett'),
                 ('Reggie Sherrill', 'Bobby Jovanov'),
                 ('Rob Matiko', 'Andy Tapper'),
                 ('Chris Marsh', 'Patrick Hannahan')]

        matchups2 = [('Jerry King', 'Stuart King'),
                 ('Alex King', 'Andy Tapper'),
                 ('Chris Marsh', 'Bobby Jovanov'),
                 ('Rob Matiko', 'Zach Taylor'),
                 ('Reggie Sherrill', 'Patrick Hannahan'),
                 ('Jeff Veness', 'Josh Duckett')]

        team1_pts = 0.0
        team2_pts = 0.0

        matchup1_results = []
        matchup2_results = []

        for (p1, p2) in matchups1:
            course = 'The National - Cove/Ridge'
            matchup_vs = p1.split()[0] + ' vs ' + p2.split()[0]
            try:
                g1 = dct[p1]
                g2 = dct[p2]
                h1 = self.calc_handicap(p1, course)
                h2 = self.calc_handicap(p2, course)

                gets_strokes = 'equal'
                if h1 > h2:
                    diff = h1 - h2
                    gets_strokes = 'team1'
                elif h2 > h1:
                    diff = h2 - h1
                    gets_strokes = 'team2'

                g1_scores = list(g1.scores[course].values())
                g2_scores = list(g2.scores[course].values())

                if g1_scores[17] > 0 and g2_scores[17] > 0: # only calculate if both golfers have finished
                    team1_wins = 0
                    team2_wins = 0

                    course_hdcps = self.courses[course]['hdcps']
                    s1 = course_hdcps[:9] # odd stroke differences mean golfer gets more strokes on front side since each nine has the same 1-9 handicaps
                    s1 = [x*2-1 for x in s1]
                    s2 = course_hdcps[9:]
                    s2 = [x*2 for x in s2]
                    course_hdcps = s1 + s2

                    for i, h in enumerate(course_hdcps):
                        if gets_strokes == 'team1' and h <= diff:
                            if g1_scores[i] - 1 < g2_scores[i]:
                                team1_wins += 1
                            elif g1_scores[i] - 1 > g2_scores[i]:
                                team2_wins += 1
                        elif gets_strokes == 'team2' and h <= diff:
                            if g2_scores[i] - 1 < g1_scores[i]:
                                team2_wins += 1
                            elif g2_scores[i] - 1 > g1_scores[i]:
                                team1_wins += 1
                        else:
                            if g1_scores[i] < g2_scores[i]:
                                team1_wins += 1
                            elif g1_scores[i] > g2_scores[i]:
                                team2_wins += 1

                        if (team1_wins - team2_wins) > 0 and (18 - (i+1)) < (team1_wins - team2_wins):
                            team1_pts += 1
                            if 18 - (i+1) == 0:
                                result_str = '{} up'.format(team1_wins - team2_wins)
                            else:
                                result_str = '{} and {}'.format(team1_wins - team2_wins, 18-(i+1))
                            matchup_result = p1.split()[0] + ' wins: ' + result_str
                            break
                        elif (team2_wins - team1_wins) > 0 and (18 - (i+1)) < (team2_wins - team1_wins):
                            team2_pts += 1
                            if 18 - (i+1) == 0:
                                result_str = '{} up'.format(team2_wins - team1_wins)
                            else:
                                result_str = '{} and {}'.format(team2_wins - team1_wins, 18-(i+1))
                            matchup_result = p2.split()[0] + ' wins: ' + result_str
                            break
                        elif (team1_wins - team2_wins) == 0 and (18 - (i+1)) == 0:
                            team1_pts += 0.5
                            team2_pts += 0.5
                            result_str = 'halved'
                            matchup_result = result_str
                            break

                matchup1_results.append((matchup_vs, matchup_result))
            except:
                matchup1_results.append((matchup_vs, 'TBD'))

        for (p1, p2) in matchups2:
            course = 'The Landing'
            matchup_vs = p1.split()[0] + ' vs ' + p2.split()[0]
            try:
                g1 = dct[p1]
                g2 = dct[p2]
                h1 = self.calc_handicap(p1, course)
                h2 = self.calc_handicap(p2, course)

                gets_strokes = 'equal'
                if h1 > h2:
                    diff = h1 - h2
                    gets_strokes = 'team1'
                elif h2 > h1:
                    diff = h2 - h1
                    gets_strokes = 'team2'

                g1_scores = list(g1.scores[course].values())
                g2_scores = list(g2.scores[course].values())

                if g1_scores[17] > 0 and g2_scores[17] > 0: # only calculate if both golfers have finished
                    team1_wins = 0
                    team2_wins = 0
                    course_hdcps = self.courses[course]['hdcps']
                    for i, h in enumerate(course_hdcps):
                        if gets_strokes == 'team1' and h <= diff:
                            if g1_scores[i] - 1 < g2_scores[i]:
                                team1_wins += 1
                            elif g1_scores[i] - 1 > g2_scores[i]:
                                team2_wins += 1
                        elif gets_strokes == 'team2' and h <= diff:
                            if g2_scores[i] - 1 < g1_scores[i]:
                                team2_wins += 1
                            elif g2_scores[i] - 1 > g1_scores[i]:
                                team1_wins += 1
                        else:
                            if g1_scores[i] < g2_scores[i]:
                                team1_wins += 1
                            elif g1_scores[i] > g2_scores[i]:
                                team2_wins += 1

                        if (team1_wins - team2_wins) > 0 and (18 - (i+1)) < (team1_wins - team2_wins):
                            team1_pts += 1
                            if 18 - (i+1) == 0:
                                result_str = '{} up'.format(team1_wins - team2_wins)
                            else:
                                result_str = '{} and {}'.format(team1_wins - team2_wins, 18-(i+1))
                            matchup_result = p1.split()[0] + ' wins: ' + result_str
                            break
                        elif (team2_wins - team1_wins) > 0 and (18 - (i+1)) < (team2_wins - team1_wins):
                            team2_pts += 1
                            if 18 - (i+1) == 0:
                                result_str = '{} up'.format(team2_wins - team1_wins)
                            else:
                                result_str = '{} and {}'.format(team2_wins - team1_wins, 18-(i+1))
                            matchup_result = p2.split()[0] + ' wins: ' + result_str
                            break
                        elif (team1_wins - team2_wins) == 0 and (18 - (i+1)) == 0:
                            team1_pts += 0.5
                            team2_pts += 0.5
                            result_str = 'halved'
                            matchup_result = result_str
                            break

                matchup2_results.append((matchup_vs, matchup_result))
            except:
                matchup2_results.append((matchup_vs, 'TBD'))

        df1 = pd.DataFrame(matchup1_results, columns=['Matchup', 'Result'])
        df2 = pd.DataFrame(matchup2_results, columns=['Matchup', 'Result'])

        if team1_pts + team2_pts == 12.0:
            if team1_pts > team2_pts:
                final_result_str = 'Team 1 Wins!'
            elif team2_pts > team1_pts:
                final_result_str = 'Team 2 Wins!'
            else:
                final_result_str = "It's a tie!"
        elif team1_pts + team2_pts > 0:
            final_result_str = 'In Progress'
        else:
            final_result_str = 'Play has yet to begin'

        return df1, df2, team1_pts, team2_pts, final_result_str


if __name__ == '__main__':
    # past_locations_map()
    golf = PlayGolf()

    print('Adding players...')
    tees = {
        # 'The National - Ridge/Bluff': 'One',
        # 'The National - Ridge/Cove': 'One',
        # 'The National - Bluff/Cove': 'One',
        # 'The National - Bluff/Ridge': 'One',
        'The National - Cove/Ridge': 'One',
        # 'The National - Cove/Bluff': 'One',
        'The Oconee': 'One',
        'Great Waters': 'Golden Bear',
        'The Landing': 'One',
        'The Landing Replay': 'One',
        'Great Waters Replay': 'Golden Bear'
    }

    tees_ = {
        # 'The National - Ridge/Bluff': 'Two',
        # 'The National - Ridge/Cove': 'One',
        # 'The National - Bluff/Cove': 'One',
        # 'The National - Bluff/Ridge': 'One',
        'The National - Cove/Ridge': 'One',
        # 'The National - Cove/Bluff': 'One',
        'The Oconee': 'Two',
        'Great Waters': 'One/Two',
        'The Landing': 'Tournament',
        'The Landing Replay': 'Tournament',
        'Great Waters Replay': 'One/Two'
    }

    golf.add_player('Stuart King', 2.4, tees, True)
    print("Adding Stuart's scores...")
    for idx, _ in enumerate(range(18)):
        golf.add_score('Stuart King', 'The National - Cove/Ridge', idx+1, np.random.randint(3,7))
        golf.add_score('Stuart King', 'The Oconee', idx+1, np.random.randint(3,7))
        golf.add_score('Stuart King', 'Great Waters', idx+1, np.random.randint(3,7))
        golf.add_score('Stuart King', 'The Landing', idx+1, np.random.randint(3,7))
        golf.add_score('Stuart King', 'The Landing Replay', idx+1, np.random.randint(3,7))
        golf.add_score('Stuart King', 'Great Waters Replay', idx+1, np.random.randint(3,7))

    golf.add_player('Alex King', 0.3, tees, True)
    print("Adding Alex's scores...")
    for idx, _ in enumerate(range(18)):
        golf.add_score('Alex King', 'The National - Cove/Ridge', idx+1, np.random.randint(3,7))
        golf.add_score('Alex King', 'The Oconee', idx+1, np.random.randint(3,7))
        golf.add_score('Alex King', 'Great Waters', idx+1, np.random.randint(3,7))
        golf.add_score('Alex King', 'The Landing', idx+1, np.random.randint(3,7))
        golf.add_score('Alex King', 'The Landing Replay', idx+1, np.random.randint(3,7))
        golf.add_score('Alex King', 'Great Waters Replay', idx+1, np.random.randint(3,7))

    golf.add_player('Jerry King', 9.5, tees_, True)
    print("Adding Jerry's scores...")
    for idx, _ in enumerate(range(18)):
        golf.add_score('Jerry King', 'The National - Cove/Ridge', idx+1, np.random.randint(3,8))
        golf.add_score('Jerry King', 'The Oconee', idx+1, np.random.randint(3,8))
        golf.add_score('Jerry King', 'Great Waters', idx+1, np.random.randint(3,8))
        golf.add_score('Jerry King', 'The Landing', idx+1, np.random.randint(3,8))
        golf.add_score('Jerry King', 'The Landing Replay', idx+1, np.random.randint(3,8))
        golf.add_score('Jerry King', 'Great Waters Replay', idx+1, np.random.randint(3,8))

    golf.add_player('Reggie Sherrill', 8.0, tees_, True)
    print("Adding Reggie's scores...")
    for idx, _ in enumerate(range(18)):
        golf.add_score('Reggie Sherrill', 'The National - Cove/Ridge', idx+1, np.random.randint(3,8))
        golf.add_score('Reggie Sherrill', 'The Oconee', idx+1, np.random.randint(3,8))
        golf.add_score('Reggie Sherrill', 'Great Waters', idx+1, np.random.randint(3,8))
        golf.add_score('Reggie Sherrill', 'The Landing', idx+1, np.random.randint(3,8))
        golf.add_score('Reggie Sherrill', 'The Landing Replay', idx+1, np.random.randint(3,8))
        golf.add_score('Reggie Sherrill', 'Great Waters Replay', idx+1, np.random.randint(3,8))

    golf.add_player('Jeff Veness', 13.6, tees_, True)
    print("Adding Jeff's scores...")
    for idx, _ in enumerate(range(18)):
        golf.add_score('Jeff Veness', 'The National - Cove/Ridge', idx+1, np.random.randint(3,8))
        golf.add_score('Jeff Veness', 'The Oconee', idx+1, np.random.randint(3,8))
        golf.add_score('Jeff Veness', 'Great Waters', idx+1, np.random.randint(3,8))
        golf.add_score('Jeff Veness', 'The Landing', idx+1, np.random.randint(3,8))
        golf.add_score('Jeff Veness', 'The Landing Replay', idx+1, np.random.randint(3,8))
        golf.add_score('Jeff Veness', 'Great Waters Replay', idx+1, np.random.randint(3,8))

    golf.add_player('Patrick Hannahan', 8.6, tees, True)
    print("Adding Patrick's scores...")
    for idx, _ in enumerate(range(18)):
        golf.add_score('Patrick Hannahan', 'The National - Cove/Ridge', idx+1, np.random.randint(3,8))
        golf.add_score('Patrick Hannahan', 'The Oconee', idx+1, np.random.randint(3,8))
        golf.add_score('Patrick Hannahan', 'Great Waters', idx+1, np.random.randint(3,8))
        golf.add_score('Patrick Hannahan', 'The Landing', idx+1, np.random.randint(3,8))
        golf.add_score('Patrick Hannahan', 'The Landing Replay', idx+1, np.random.randint(3,8))
        golf.add_score('Patrick Hannahan', 'Great Waters Replay', idx+1, np.random.randint(3,8))

    golf.add_player('Andy Tapper', 2.1, tees, True)
    print("Adding Andy's scores...")
    for idx, _ in enumerate(range(18)):
        golf.add_score('Andy Tapper', 'The National - Cove/Ridge', idx+1, np.random.randint(3,7))
        golf.add_score('Andy Tapper', 'The Oconee', idx+1, np.random.randint(3,7))
        golf.add_score('Andy Tapper', 'Great Waters', idx+1, np.random.randint(3,7))
        golf.add_score('Andy Tapper', 'The Landing', idx+1, np.random.randint(3,7))
        golf.add_score('Andy Tapper', 'The Landing Replay', idx+1, np.random.randint(3,7))
        golf.add_score('Andy Tapper', 'Great Waters Replay', idx+1, np.random.randint(3,7))

    golf.add_player('Zach Taylor', 5.8, tees_, True)
    print("Adding Zach's scores...")
    for idx, _ in enumerate(range(18)):
        golf.add_score('Zach Taylor', 'The National - Cove/Ridge', idx+1, np.random.randint(3,8))
        golf.add_score('Zach Taylor', 'The Oconee', idx+1, np.random.randint(3,8))
        golf.add_score('Zach Taylor', 'Great Waters', idx+1, np.random.randint(3,8))
        golf.add_score('Zach Taylor', 'The Landing', idx+1, np.random.randint(3,8))
        golf.add_score('Zach Taylor', 'The Landing Replay', idx+1, np.random.randint(3,8))
        golf.add_score('Zach Taylor', 'Great Waters Replay', idx+1, np.random.randint(3,8))

    golf.add_player('Josh Duckett', 13.2, tees_, True)
    print("Adding Josh's scores...")
    for idx, _ in enumerate(range(18)):
        golf.add_score('Josh Duckett', 'The National - Cove/Ridge', idx+1, np.random.randint(3,8))
        golf.add_score('Josh Duckett', 'The Oconee', idx+1, np.random.randint(3,8))
        golf.add_score('Josh Duckett', 'Great Waters', idx+1, np.random.randint(3,8))
        golf.add_score('Josh Duckett', 'The Landing', idx+1, np.random.randint(3,8))
        golf.add_score('Josh Duckett', 'The Landing Replay', idx+1, np.random.randint(3,8))
        golf.add_score('Josh Duckett', 'Great Waters Replay', idx+1, np.random.randint(3,8))

    golf.add_player('Bobby Jovanov', 10.7, tees, True)
    print("Adding Bobby's scores...")
    for idx, _ in enumerate(range(18)):
        golf.add_score('Bobby Jovanov', 'The National - Cove/Ridge', idx+1, np.random.randint(3,8))
        golf.add_score('Bobby Jovanov', 'The Oconee', idx+1, np.random.randint(3,8))
        golf.add_score('Bobby Jovanov', 'Great Waters', idx+1, np.random.randint(3,8))
        golf.add_score('Bobby Jovanov', 'The Landing', idx+1, np.random.randint(3,8))
        golf.add_score('Bobby Jovanov', 'The Landing Replay', idx+1, np.random.randint(3,8))
        golf.add_score('Bobby Jovanov', 'Great Waters Replay', idx+1, np.random.randint(3,8))

    golf.add_player('Chris Marsh', 14.1, tees_, True)
    print("Adding Chris's scores...")
    for idx, _ in enumerate(range(18)):
        golf.add_score('Chris Marsh', 'The National - Cove/Ridge', idx+1, np.random.randint(3,8))
        golf.add_score('Chris Marsh', 'The Oconee', idx+1, np.random.randint(3,8))
        golf.add_score('Chris Marsh', 'Great Waters', idx+1, np.random.randint(3,8))
        golf.add_score('Chris Marsh', 'The Landing', idx+1, np.random.randint(3,8))
        golf.add_score('Chris Marsh', 'The Landing Replay', idx+1, np.random.randint(3,8))
        golf.add_score('Chris Marsh', 'Great Waters Replay', idx+1, np.random.randint(3,8))

    golf.add_player('Rob Matiko', 12.0, tees_, True)
    print("Adding Rob's scores...")
    for idx, _ in enumerate(range(18)):
        golf.add_score('Rob Matiko', 'The National - Cove/Ridge', idx+1, np.random.randint(3,8))
        golf.add_score('Rob Matiko', 'The Oconee', idx+1, np.random.randint(3,8))
        golf.add_score('Rob Matiko', 'Great Waters', idx+1, np.random.randint(3,8))
        golf.add_score('Rob Matiko', 'The Landing', idx+1, np.random.randint(3,8))
        golf.add_score('Rob Matiko', 'The Landing Replay', idx+1, np.random.randint(3,8))
        golf.add_score('Rob Matiko', 'Great Waters Replay', idx+1, np.random.randint(3,8))
