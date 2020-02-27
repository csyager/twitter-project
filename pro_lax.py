from main import *

followers_of_pll = []
followers_of_mll = []
followers_of_both = []

def reload_data():
    followers_of_pll = api.GetFollowerIDs(screen_name="PremierLacrosse")
    followers_of_mll = api.GetFollowerIDs(screen_name="MLL_Lacrosse")
    followers_of_both.clear
    for follower in followers_of_pll:
        if follower in followers_of_mll:
            followers_of_both.append(follower)


def print_data():
    print("PLL: " + str(len(followers_of_pll)))
    print("MLL: " + str(len(followers_of_mll)))
    print("BOTH: " + str(len(followers_of_both)))