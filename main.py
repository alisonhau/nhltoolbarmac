# alison hau | july 2020

import requests
import rumps
import time
from datetime import datetime
import pytz

rumps.debug_mode(True)

API_URL_BASE = "https://statsapi.web.nhl.com/api/v1"
PENS_TEAM_ID = 5    # hard-coded
TEAM_URL = "{0}/teams/{1}?expand=team.stats,team.schedule.next,team.schedule.previous'.format(BASE_URL)".format(API_URL_BASE, str(PENS_TEAM_ID))
OVERVIEW_URL = API_URL_BASE + "/game/{0}/feed/live/?site=en_nhl"

def toggle_updates(sender):
    sender.state = not sender.state
    if auto.is_alive(): auto.stop()
    else: auto.start()

def get_home_away_stats(_):
    with requests.get(TEAM_URL) as teaminfo:
        teamjson = teaminfo.json()
        # CURRENTLY WORKING WITH PREVIOUS GAME BECAUSE OF COVID HAITUS / WEIRD PLAYOFF VIBES
        isWeird = False 
        next_game_key = "nextGameSchedule" if not isWeird else "previousGameSchedule"
        game_id = teamjson["teams"][0][next_game_key]["dates"][0]["games"][0]["gamePk"]

    with requests.get(OVERVIEW_URL.format(game_id)) as gameinfo:
        gamejson = gameinfo.json()

        gamestate = gamejson["gameData"]["status"]["detailedState"]
        scores = gamejson["liveData"]["boxscore"]["teams"]

        away_scores = scores["away"]
        away_team_name = away_scores["team"]["triCode"]
        away_stats = away_scores["teamStats"]["teamSkaterStats"]


        home_scores = scores["home"]
        home_team_name = home_scores["team"]["triCode"]
        home_stats = home_scores["teamStats"]["teamSkaterStats"]

        gamedt = gamejson["gameData"]["datetime"]["dateTime"]
        local_tz = pytz.timezone(gamejson["gameData"]["teams"]["home"]["venue"]["timeZone"]["id"])
        # utc to local (make sep function)
        dtime = datetime.strptime(gamedt, "%Y-%m-%dT%H:%M:%SZ")
        local_dt = dtime.replace(tzinfo=pytz.utc).astimezone(local_tz)
        timeuntil = dtime - datetime.now()
        timeuntil_s = "{0} day{1} from now".format(timeuntil.days, "s" if timeuntil.days != 1 else "")
        dtime_s = datetime.strftime(local_dt, "%-m/%-d %-I:%M%p %Z") 

        linescore = gamejson["liveData"]["linescore"]
        curr_pd = linescore["currentPeriod"]
        if curr_pd > 0:
            curr_pd_ordinal = linescore["currentPeriodOrdinal"] + " Period"
            curr_pd_rem = linescore["currentPeriodTimeRemaining"]
        else:
            curr_pd_ordinal = dtime_s
            curr_pd_rem = timeuntil_s
        icetime = "{0} | {1}".format(curr_pd_ordinal, curr_pd_rem)
    
    return [[away_team_name, away_stats], [home_team_name, home_stats]], icetime

@rumps.clicked("Update!")
def updatescores(sender):
    # get scores from api, send
    updated = time.strftime("%b %d %Y %H:%M:%S", time.localtime())
    gamelst, timeleft = get_home_away_stats(None)

    app.menu.clear()
    app.menu.update([
        rumps.MenuItem("Update!", callback=get_home_away_stats),
        rumps.MenuItem("Last Updated: %s" % (updated)),
        rumps.separator,
        ])

    # find a nicer way to do this?? without hardcoded dictionary keys
    gameheaderitem = rumps.MenuItem("{0} vs {1}".format(gamelst[0][0], gamelst[1][0]))
    print("break1")
    app.menu.update(gameheaderitem)

    timeleftitem = rumps.MenuItem(timeleft)
    app.menu.update(timeleftitem)
    for team in gamelst:
        teamstring = "{0}: {1} ({2} SOG)".format(team[0], team[1]["goals"], team[1]["shots"])
        teamitem = rumps.MenuItem(teamstring)
        app.menu.update(teamitem)

    autoupdates = rumps.MenuItem("AutoUpdates (10 sec)", callback=toggle_updates)
    app.menu.update(autoupdates)
    app.menu.update([rumps.MenuItem("Quit",callback=rumps.quit_application, key='q')])
    app.title = "{0}: {1} vs {2}: {3}".format(gamelst[0][0], gamelst[0][1]["goals"], gamelst[1][0], gamelst[1][1]["goals"], )

app = rumps.App('PENS Scores!', quit_button=rumps.MenuItem("Quit", key='q'))
app.menu = [
        ('Check now'),
        ]

def update_auto(sender):
    updatescores(None)

auto = rumps.Timer(update_auto, 10)

app.run()

