from main import *
from bs4 import BeautifulSoup

# parse org codes into dictionary
org_codes = {}
org_code_file = open('org_codes.txt', 'r')
for line in org_code_file:
    school = line.split(maxsplit=1)[1].strip()
    code = line.split(maxsplit=1)[0].strip()
    org_codes[school] = code

# parses data line-by-line from file provided in filepath and updates the postgres database
def update_database(filepath: str, table_name: str):
    player_file = open(filepath, 'r')
    num_players = 0
    for line in player_file:
        num_players += 1
    print("Updating database with " + str(num_players) + " entries...")
    num_finished = 0
    player_file.seek(0)
    for player_line in player_file:
        year = player_line.split(maxsplit=3)[0].strip()
        firstname = player_line.split(maxsplit=3)[1].strip()
        lastname = player_line.split(maxsplit=3)[2].strip()
        school = player_line.split(maxsplit=3)[3].strip()
        org_code = org_codes[school]
        URL = "https://web1.ncaa.org/stats/StatsSrv/careersearch"
        PARAMS = {
            'doWhat': 'playerCoachSearch',
            'lastName': lastname,
            'firstName': firstname,
            'searchSport': 'MLA',
            'playerCoach': 1
        }
        r = requests.get(url=URL, params=PARAMS)
        for line in r.iter_lines():
            if '<a href="javascript:showCareer' in str(line) and str(org_code) in str(line):
                player_id=int(str(line).split('(')[1].split(',')[0])
                academic_year = int(str(line).split(',')[1][1:].split(',')[0])
                division = int(str(line).split(',')[3][1:].split(',')[0])

        URL = "https://web1.ncaa.org/stats/StatsSrv/careerplayer"
        PARAMS = {
            'sortOn': 0,
            'doWhat': 'display',
            'playerId': player_id,
            'coachId': player_id,
            'orgId': org_code,
            'academicYear': academic_year,  
            'division': division,
            'sportCode': 'MLA',
            'idx': '' 
        }
        r = requests.get(url=URL, params=PARAMS)

        # parse player stat page
        soup = BeautifulSoup(r.content, 'html.parser')
        
        this_row = None     # will store the row containing the desired academic year
        attr = []           # stores list of attributes parsed from player stat page

        # parses Career Stats table
        for row in soup.findAll('table', class_='statstable')[0].findAll('tr'):
            for col in row.findAll('td'):
                if "-" + year[2:] in str(col.contents):
                # this row represents the year that we're looking for
                    this_row = row
        
        if this_row is None:
            logging.error("Career Stats Row corresponding to year not found")
        else:
            # tracks number of currently viewed column
            count = 0
            # adds data sequentially from row into attr[]
            for col in this_row.findAll('td'):
                # if numerical stats have a "-", replace with a 0 and append
                if count > 3 and col.string.strip() == "-":
                    attr.append("0")
                # otherwise, just append raw data
                else:
                    attr.append(col.string.strip())
                count += 1

        goalie_row = None
        # parses Goalkeepers table
        for row in soup.findAll('table', class_='statstable')[1].findAll('tr'):
            for col in row.findAll('td'):
                if "-" + year[2:] in str(col.contents):
                    goalie_row = row
        
        if goalie_row is None:
            logging.error("Goalkeeper Row corresponding to year not found")
        else:
            count = 0
            for col in goalie_row.findAll('td'):
                if count < 4:
                    count += 1
                elif col.string.strip() == "-":
                    attr.append("0")
                    count += 1
                else:
                    attr.append(col.string.strip())
                    count += 1
        
        ranking_rows = []
        # parse ranking table
        try:
            for row in soup.findAll('table', {"cellpadding": "4"})[0].findAll('tr'):
                col = row.find('td').contents[0].string.strip()
                if "-" + year[2:] in col:
                    ranking_rows.append(row)
        except IndexError:
            continue
        

        rankings = {}
        if len(ranking_rows) != 0:
            for ranking_row in ranking_rows:
                count = 0
                cols = ranking_row.findAll('td')
                category = cols[1].a.string.strip()
                category_code = ""
                if category == "Points Per Game":
                    category_code = "ppg_rank"
                elif category == "Goals Per Game":
                    category_code = "gpg_rank"
                elif category == "Assists Per Game":
                    category_code = "apg_rank"
                elif category == "Save Percentage":
                    category_code = "save_pct_rank"
                elif category == "Goals-Against Average":
                    category_code = "goals_against_average_rank"
                elif category == "Saves Per Game":
                    category_code = "saves_per_game_rank"
                elif category == "Ground Balls Per Game":
                    category_code = "gb_per_game_ranking"
                elif category == "Caused Turnovers Per Game":
                    category_code = "caused_turnover_per_game_ranking"
                elif category == "Shot Percentage":
                    category_code = "shot_pct_rank"
                elif category == "Individual Man-up Goals":
                    category_code = "man_up_goals_rank"
                else:
                    logging.error("No category code exists for category '" + category + "'")
                    continue
                rank = cols[2].string.strip()
                rankings[category_code] = rank


        # query the database table for the player and year to see if data already exists
        SQL = ("SELECT * FROM " + table_name + " WHERE name = %s AND academic_year = %s;")
        VALUES = (attr[0], attr[2])
        cur.execute(SQL, VALUES)

        # new_record is true if no data matching player for this year exists
        if len(cur.fetchall()) == 0:
            new_record = True
        else:
            new_record = False

        # record for this name and academic year doesn't exist - add to table
        if new_record:
            SQL = ("INSERT INTO " + table_name + " "
                    "(name, school, class, academic_year, position, gp, goals, gpg, assists, apg, tp, ppg, ground_balls, gbpg, fo_wins, fo_losses, fo_pct, goalie_ga, goalie_ga_avg, goalie_saves, goalie_save_pct) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")
            VALUES = (attr[0], school, attr[1], attr[2], attr[3], int(attr[4]), int(attr[5]), float(attr[6]), int(attr[7]), float(attr[8]), int(attr[9]), float(attr[10]), int(attr[11]), float(attr[12]), int(attr[13]), int(attr[14]), float(attr[15]), int(attr[16]), float(attr[17]), int(attr[18]), float(attr[19]))
            cur.execute(SQL, VALUES)
            conn.commit()

        # record does exist - update record
        else:
            SQL = ("UPDATE " + table_name + " "
                    "SET gp = %s, goals = %s, gpg = %s, assists = %s, apg = %s, tp = %s, ppg = %s, ground_balls = %s, gbpg = %s, fo_wins = %s, fo_losses = %s, fo_pct = %s, goalie_ga = %s, goalie_ga_avg = %s, goalie_saves = %s, goalie_save_pct = %s "
                    "WHERE name = %s AND academic_year = %s;")
            VALUES = (int(attr[4]), int(attr[5]), float(attr[6]), int(attr[7]), float(attr[8]), int(attr[9]), float(attr[10]), int(attr[11]), float(attr[12]), int(attr[13]), int(attr[14]), float(attr[15]), int(attr[16]), float(attr[17]), int(attr[18]), float(attr[19]), attr[0], attr[2])
            cur.execute(SQL, VALUES)
            conn.commit()

        # update records with rankings    
        for key in rankings:
            SQL = ("UPDATE " + table_name + " "
                    "SET %s = %s "
                    "WHERE name = %s AND academic_year = %s")
            VALUES = (AsIs(key), int(rankings[key]), attr[0], attr[2])
            cur.execute(SQL, VALUES)
        num_finished += 1
        pct = int(float(num_finished)/float(num_players) * 100)
        print(str(pct) + "%", end='\r')
    print("Done.")

if __name__ == "__main__":
    update_database('winners.txt', 'tewaaraton_winners')