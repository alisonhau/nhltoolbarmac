# alison hau | july 2020

import requests
import rumps
import time

API_URL_BASE = "https://statsapi.web.nhl.com/api/v1/"
PENS_TEAM_ID = 5    # hard-coded
TEAM_URL = "{0}/teams/{1}?expand=team.stats,team.schedule.previous,team.schedule.next'.format(BASE_URL)".format(API_URL_BASE, str(PENS_TEAM_ID))
OVERVIEW_URL = API_URL_BASE + "/game/{0}/feed/live/?site=en_nhl"

@rumps.timer(10)
def update_auto(sender):
    updatescores(None)


def get_home_away_stats():
    with requests.get(TEAM_URL) as teaminfo:
        teamjson = teaminfo.json()
        # CURRENTLY WORKING WITH PREVIOUS GAME BECAUSE OF COVID HAITUS / WEIRD PLAYOFF VIBES
        isWeird = True
        next_game_key = 'nextGameSchedule' if not isWeird else 'previousGameSchedule'
        game_id = teamjson["teams"][0][next_game_key]["dates"][0]["games"][0]["gamePk"]

    with requests.get(OVERVIEW_URL.format(game_id)) as gameinfo:
            gamejson = gameinfo.json()

            gamestate = gamejson["gameData"]["status"]["detailedState"]
            scores = gamejson["liveData"]["boxscore"]["teams"]

            away_scores = scores["away"]
            away_team_name = away_scores["team"]["triCode"]
            away_stats = away_scores["team"]["teamStats"]


            homescores = scores["home"]

            print(gamejson["liveData"]["boxscore"]["teams"]["away"])

@rumps.clicked("Update scores")
def updatescores(sender):
    # get scores from api, send
    updated = time.strftime("%d %b %Y %H:%M:%S", time.localtime())
    stats = get_home_away_stats()

    app.menu.clear()
    app.menu.update([
        rumps.MenuItem("Update Stats", callback=get_home_away_stats),
        rumps.MenuItem("Last Updated: %s" %s (updated)),
        rumps.seperator,
        ])


    score_string = 'TEST'

    app.title = score_string

app = rumps.App('PENS Scores & Standings', quit_button=rumps.MenuItem("Quit", key='q'))
app.menu = [
        ('Check now'),
        ]
app.run()
