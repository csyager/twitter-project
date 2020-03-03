from main import *
from bs4 import BeautifulSoup

# parse org codes into dictionary
org_codes = {}
org_code_file = open('org_codes.txt', 'r')
for line in org_code_file:
    school = line.split(maxsplit=1)[1].strip()
    code = line.split(maxsplit=1)[0].strip()
    org_codes[school] = code


winners_file = open('winners.txt', 'r')
for winner_line in winners_file:
    year = winner_line.split(maxsplit=3)[0].strip()
    firstname = winner_line.split(maxsplit=3)[1].strip()
    lastname = winner_line.split(maxsplit=3)[2].strip()
    school = winner_line.split(maxsplit=3)[3].strip()
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
        logging.error("Row corresponding to year not found")
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

    # query the database table for the player and year to see if data already exists
    SQL = ("SELECT * FROM tewaaraton_winners WHERE name = %s AND academic_year = %s;")
    VALUES = (attr[0], attr[2])
    cur.execute(SQL, VALUES)

    # new_record is true if no data matching player for this year exists
    if len(cur.fetchall()) == 0:
        new_record = True
    else:
        new_record = False

    # record for this name and academic year doesn't exist - add to table
    if new_record:
        SQL = ("INSERT INTO tewaaraton_winners "
                "(name, school, class, academic_year, position, gp, goals, gpg, assists, apg, tp, ppg, ground_balls, gbpg, fo_wins, fo_losses, fo_pct) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")
        VALUES = (attr[0], school, attr[1], attr[2], attr[3], int(attr[4]), int(attr[5]), float(attr[6]), int(attr[7]), float(attr[8]), int(attr[9]), float(attr[10]), int(attr[11]), float(attr[12]), int(attr[13]), int(attr[14]), float(attr[15]))
        cur.execute(SQL, VALUES)
        conn.commit()

    # record does exist - update record
    else:
        SQL = ("UPDATE tewaaraton_winners "
                "SET gp = %s, goals = %s, gpg = %s, assists = %s, apg = %s, tp = %s, ppg = %s, ground_balls = %s, gbpg = %s, fo_wins = %s, fo_losses = %s, fo_pct = %s "
                "WHERE name = %s AND academic_year = %s;")
        VALUES = (int(attr[4]), int(attr[5]), float(attr[6]), int(attr[7]), float(attr[8]), int(attr[9]), float(attr[10]), int(attr[11]), float(attr[12]), int(attr[13]), int(attr[14]), float(attr[15]), attr[0], attr[2])
        cur.execute(SQL, VALUES)
        conn.commit()