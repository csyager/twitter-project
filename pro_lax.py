from main import *

def update_data():

    followers_of_pll = api.GetFollowers(screen_name="PremierLacrosse")
    followers_of_mll = api.GetFollowers(screen_name="MLL_Lacrosse")

    for f in followers_of_mll:
        SQL = "INSERT INTO mll_followers (screen_name, twitter_id) VALUES (%s, %s)"
        VALUES = (f.screen_name, f.id)
        cur.execute(SQL, VALUES)
        SQL = "INSERT INTO both_followers (screen_name, twitter_id) VALUES (%s, %s)"
        cur.execute(SQL, VALUES)
    
    for f in followers_of_pll:
        SQL = "INSERT INTO pll_followers (screen_name, twitter_id) VALUES (%s, %s)"
        VALUES = (f.screen_name, f.id)
        cur.execute(SQL, VALUES)
        SQL = "INSERT INTO both_followers (screen_name, twitter_id) VALUES (%s, %s)"
        cur.execute(SQL, VALUES)


def print_data():
    cur.execute("select * from mll_followers")
    results = cur.fetchall()
    print("MLL")
    for r in results:
        print(r)
    cur.execute("select * from pll_followers")
    results = cur.fetchall()
    print(">>>>>>>>>>")
    print("PLL")
    for r in results:
        print(r)
    cur.execute("select * from both_followers")
    results = cur.fetchall()
    print(">>>>>>>>>>")
    for r in results:
        print(r)


def main():
    while True:
        command = input("Press u to update data, press p to print, press q to quit\n")
        if command == "u":
            update_data()
            logging.info("Starting update_data thread")
        if command == "p":
            print_data()
        if command == "q":
            quit()

if __name__ == "__main__":
    main()