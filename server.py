#!/usr/bin/env python

# Run guide
# 1. go to server.py's directory i.e. cd P1
# 2. now run cmd "ls", you should see server.py, venv and templates
# 3. run cmd ". venv/bin/activate"
# 4. run "python server.py"
# 5. click link in terminal or on your browser type "http://0.0.0.0:8111/"
#

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@104.196.152.219/proj1part2
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.152.219/proj1part2"
#
DATABASEURI = "postgresql://nd2705:12345678@35.227.37.35/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
# );""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request 
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
    return render_template("index.html")

#
#                 League part
#
# Defualt page for leagues, waiting for user's query


@app.route('/league', methods=['GET'])
def league():
    return render_template("league.html")

# Method to handle user's query on league


@app.route('/checkLeague')
def checkLeague():
    # Get user's input
    name = request.form['name']
    country = request.form['country']
    rank = request.form['rank']
    avg = request.form['avg']
    response = []
    title = ()

    # When league name is not empty
    if name != '':
        if country == '' and rank == '' and avg == '':
            if name == 'all':
                query = "select * from leagues"
                result = engine.connect().execute(query)
            else:
                query = "select * from leagues where league_name='%s'" % (name)
                result = engine.connect().execute(query)
            title = ('League Name', 'Country', 'Number of Teams', 'Sport Type')
        elif rank != '' and avg == '':
            if rank == 'all':
                query = "select team_season_performance.team_name, team_season_performance.rank, join_in.league_name, join_in.seasons_in_league from team_season_performance join join_in on team_season_performance.team_name = join_in.team_name where join_in.league_name = '%s' order by rank" % (
                    name)
                result = engine.connect().execute(query)
            else:
                query = "select team_season_performance.team_name, team_season_performance.rank, join_in.league_name, join_in.seasons_in_league from team_season_performance join join_in on team_season_performance.team_name = join_in.team_name where join_in.league_name = '%s' and rank %s order by rank" % (
                    name, rank)
                result = engine.connect().execute(query)
            title = ('Teams', 'Rank', 'League', 'Season')
    # When user wants to see  the average goals
    elif avg != '':
        if name == 'all' or name == '':
            query = "select * from (select league_name, seasons_in_league, AVG(goal_scored) as avg from team_season_performance inner join join_in on team_season_performance.team_name = join_in.team_name group by(join_in.league_name, join_in.seasons_in_league)) as avggoals where avg %s" % (avg)
            result = engine.connect().execute(query)
        else:
            query = "select * from (select league_name, seasons_in_league, AVG(goal_scored) as avg from team_season_performance inner join join_in on team_season_performance.team_name = join_in.team_name where league_name = '%s' group by(join_in.league_name, join_in.seasons_in_league)) as avggoals where avg %s" % (name, avg)
            result = engine.connect().execute(query)
        title = ('League', 'Season', 'Average Goals')
    else:
        return render_template("league.html")

    response.append(title)
    for row in result:
        response.append(row)
    context = dict(data=response)
    return render_template("league.html", **context)


#
#             Team part
#
@app.route('/team', methods=['GET'])
def team():
    return render_template("team.html")

# Method to handle user's query on teams and performance


@app.route('/checkTeam')
def checkTeam():
    name = request.form['name']
    city = request.form['city']
    season = request.form['season']
    league = request.form['league']
    rank = request.form['rank']
    win = request.form['win']
    loss = request.form['loss']
    response = []
    title = ()

    if name != '' and league == '' and season == '':
        if city == '' and rank == '' and win == '' and loss == '':
            if name == 'all':
                query = "select * from teams"
                result = engine.connect().execute(query)
            else:
                query = "select * from teams where team_name = '%s'" % (name)
                result = engine.connect().execute(query)
            title = ('Team', 'City', 'Stadium')
    elif league != '' and season == '':
        if name == 'all' or name == '':
            if league == 'all':
                query = "select * from join_in order by league_name"
                result = engine.connect().execute(query)
            else:
                query = "select * from join_in where league_name = '%s'" % (
                    league)
                result = engine.connect().execute(query)
        else:
            query = "select * from join_in where team_name = '%s'" % (name)
            result = engine.connect().execute(query)
        title = ('Season', 'Team', 'League')
    elif season != '':
        if (name == 'all' or name == '') and win == '' and loss == '':
            query = "select * from team_season_performance"
            result = engine.connect().execute(query)
        elif name != '' and win == '' and loss == '':
            query = "select * from team_season_performance where team_name = '%s'" % (
                name)
            result = engine.connect().execute(query)
        elif win != '':
            if league == '':
                query = "select * from team_season_performance where wins %s" % (
                    win)
                result = engine.connect().execute(query)
            else:
                query = "select * from team_season_performance where wins %s and team_name in (select team_name from join_in where league_name = '%s')" % (
                    win, league)
                result = engine.connect().execute(query)
        elif loss != '':
            if league == '':
                query = "select * from team_season_performance where losses %s" % (
                    loss)
                result = engine.connect().execute(query)
            else:
                query = "select * from team_season_performance where loss %s and team_name in (select team_name from join_in where league_name = '%s')" % (
                    win, league)
                result = engine.connect().execute(query)
        title = ('Team', 'Season', 'Rank', 'Wins', 'Losses',
                 'Goal Scored', 'Goal Conceded', 'Goal Difference', 'Cards')
    else:
        return render_template("team.html")

    response.append(title)
    for row in result:
        response.append(row)
    context = dict(data=response)
    return render_template("team.html", **context)


#
#             Player part
#
@app.route('/player', methods=['GET'])
def player():
    return render_template("player.html")

# Method to handle user's query on players and performance


@app.route('/checkPlayer')
def checkPlayer():
    name = request.form['name']
    age = request.form['age']
    pos = request.form['pos']
    nation = request.form['nation']
    team = request.form['team']
    season = request.form['season']
    goal = request.form['g']
    asis = request.form['a']
    response = []
    title = ()

    if name != '' and team == '' and season == '':
        if name == 'all':
            query = "select * from players"
            result = engine.connect().execute(query)
        else:
            query = "select * from players where player_fullname = '%s'" % (
                name)
            result = engine.connect().execute(query)
        title = ('Player', 'Age', 'Position', 'Nationality')
    elif age != '' and goal == '' and asis == '' and pos == '' and nation == '':
        query = "select * from players where player_age %s" % (age)
        result = engine.connect().execute(query)
        title = ('Player', 'Age', 'Position', 'Nationality')
    elif nation != '' and goal == '' and asis == '' and pos == '':
        if age != '':
            query = "select * from players where player_age %s and player_nationality = '%s'" % (
                age, nation)
            result = engine.connect().execute(query)
        else:
            query = "select * from players where player_nationality = '%s'" % (
                nation)
            result = engine.connect().execute(query)
        title = ('Player', 'Age', 'Position', 'Nationality')
    elif pos != '' and goal == '' and asis == '':
        if age == '' and nation == '':
            query = "select * from players where player_position  = '%s'" % (
                pos)
            result = engine.connect().execute(query)
        elif age == '' and nation != '':
            query = "select * from players where player_position  = '%s' and player_age %s" % (
                pos, age)
            result = engine.connect().execute(query)
        elif age != '' and nation != '':
            query = "select * from players where player_position  = '%s' and player_age%s and player_nationality = '%s'" % (
                pos, age, nation)
            result = engine.connect().execute(query)
        elif age != '' and nation == '':
            query = "select * from players where player_position  = '%s' and player_age%s" % (
                pos, age)
            result = engine.connect().execute(query)
        title = ('Player', 'Age', 'Position', 'Nationality')
    elif season != '' and team == '' and goal == '' and asis == '':
        if name == '' or name == 'all':
            query = "select * from player_season_performance"
            result = engine.connect().execute(query)
        elif name != '' and name != 'all':
            query = "select * from player_season_performance where player_fullname = '%s'" % (
                name)
            result = engine.connect().execute(query)
        title = ('Player', 'Team', 'Seson', 'Appearance', 'Goals', 'Assists',
                 'Penatly Goals', 'Conceded', 'Yellow Cards', 'Red Cards')
    elif season != '' and team != '' and goal == '' and asis == '':
        query = "select * from player_season_performance where player_team  = '%s'" % (
            team)
        result = engine.connect().execute(query)
        title = ('Player', 'Team', 'Seson', 'Appearance', 'Goals', 'Assists',
                 'Penatly Goals', 'Conceded', 'Yellow Cards', 'Red Cards')
    elif goal != '' and asis != '':
        if age == '' and pos == '' and nation == '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and player_season_performance.assists %s" % (
                goal, asis)
            result = engine.connect().execute(query)
        elif age != '' and pos == '' and nation == '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and player_season_performance.assists %s and players.player_age %s" % (
                goal, asis, age)
            result = engine.connect().execute(query)
        elif age != '' and pos != '' and nation == '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and player_season_performance.assists %s and players.player_age %s and players.player_position = '%s'" % (
                goal, asis, age, pos)
            result = engine.connect().execute(query)
        elif age != '' and pos != '' and nation != '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and player_season_performance.assists %s and players.player_age %s and players.player_position = '%s' and players.player_nationality  = '%s'" % (
                goal, asis, age, pos, nation)
            result = engine.connect().execute(query)
        elif age != '' and pos != '' and nation != '' and team != '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and player_season_performance.assists %s and players.player_age %s and players.player_position = '%s' and players.player_nationality  = '%s' and player_season_performance.player_team = '%s'" % (
                goal, asis, age, pos, nation, team)
            result = engine.connect().execute(query)
        elif age == '' and pos != '' and nation == '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and player_season_performance.assists %s and players.player_position = '%s'" % (
                goal, asis, pos)
            result = engine.connect().execute(query)
        elif age == '' and pos != '' and nation != '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and player_season_performance.assists %s and players.player_position = '%s' and players.player_nationality  = '%s'" % (
                goal, asis, pos, nation)
            result = engine.connect().execute(query)
        elif age == '' and pos != '' and nation != '' and team != '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and player_season_performance.assists %s and players.player_position = '%s' and players.player_nationality  = '%s' and player_season_performance.player_team = '%s'" % (
                goal, asis, pos, nation, team)
            result = engine.connect().execute(query)
        elif age == '' and pos == '' and nation != '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and player_season_performance.assists %s and players.player_nationality  = '%s'" % (
                goal, asis, nation)
            result = engine.connect().execute(query)
        elif age == '' and pos == '' and nation != '' and team != '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and player_season_performance.assists %s and players.player_nationality  = '%s' and player_season_performance.player_team = '%s'" % (
                goal, asis, nation, team)
            result = engine.connect().execute(query)
        elif age == '' and pos == '' and nation == '' and team != '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and player_season_performance.assists %s and player_season_performance.player_team = '%s'" % (
                goal, asis, team)
            result = engine.connect().execute(query)
        title = ('Player', 'Age', 'Position',
                 'Nationality', 'Team', 'Goals', 'Assists')
    elif goal != '':
        if age == '' and pos == '' and nation == '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s" % (
                goal)
            result = engine.connect().execute(query)
        elif age != '' and pos == '' and nation == '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and players.player_age %s" % (
                goal, age)
            result = engine.connect().execute(query)
        elif age != '' and pos != '' and nation == '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and players.player_age %s and players.player_position = '%s'" % (
                goal, age, pos)
            result = engine.connect().execute(query)
        elif age != '' and pos != '' and nation != '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and players.player_age %s and players.player_position = '%s' and players.player_nationality  = '%s'" % (
                goal, age, pos, nation)
            result = engine.connect().execute(query)
        elif age != '' and pos != '' and nation != '' and team != '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and players.player_age %s and players.player_position = '%s' and players.player_nationality  = '%s' and player_season_performance.player_team = '%s'" % (
                goal, age, pos, nation, team)
            result = engine.connect().execute(query)
        elif age == '' and pos != '' and nation == '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and players.player_position = '%s'" % (
                goal, pos)
            result = engine.connect().execute(query)
        elif age == '' and pos != '' and nation != '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and players.player_position = '%s' and players.player_nationality  = '%s'" % (
                goal, pos, nation)
            result = engine.connect().execute(query)
        elif age == '' and pos != '' and nation != '' and team != '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and players.player_position = '%s' and players.player_nationality  = '%s' and player_season_performance.player_team = '%s'" % (
                goal, pos, nation, team)
            result = engine.connect().execute(query)
        elif age == '' and pos == '' and nation != '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and players.player_nationality  = '%s'" % (
                goal, nation)
            result = engine.connect().execute(query)
        elif age == '' and pos == '' and nation != '' and team != '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and players.player_nationality  = '%s' and player_season_performance.player_team = '%s'" % (
                goal, nation, team)
            result = engine.connect().execute(query)
        elif age == '' and pos == '' and nation == '' and team != '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.goals from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.goals %s and player_season_performance.player_team = '%s'" % (
                goal, team)
            result = engine.connect().execute(query)
        title = ('Player', 'Age', 'Position', 'Nationality', 'Team', 'Goals')
    elif asis != '':
        if age == '' and pos == '' and nation == '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.assists %s" % (
                asis)
            result = engine.connect().execute(query)
        elif age != '' and pos == '' and nation == '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.assists %s and players.player_age %s" % (
                asis, age)
            result = engine.connect().execute(query)
        elif age != '' and pos != '' and nation == '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.assists %s and players.player_age %s and players.player_position = '%s'" % (
                asis, age, pos)
            result = engine.connect().execute(query)
        elif age != '' and pos != '' and nation != '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.assists %s and players.player_age %s and players.player_position = '%s' and players.player_nationality  = '%s'" % (
                asis, age, pos, nation)
            result = engine.connect().execute(query)
        elif age != '' and pos != '' and nation != '' and team != '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.assists %s and players.player_age %s and players.player_position = '%s' and players.player_nationality  = '%s' and player_season_performance.player_team = '%s'" % (
                asis, age, pos, nation, team)
            result = engine.connect().execute(query)
        elif age == '' and pos != '' and nation == '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.assists %s and players.player_position = '%s'" % (
                asis, pos)
            result = engine.connect().execute(query)
        elif age == '' and pos != '' and nation != '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.assists %s and players.player_position = '%s' and players.player_nationality  = '%s'" % (
                asis, pos, nation)
            result = engine.connect().execute(query)
        elif age == '' and pos != '' and nation != '' and team != '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.assists %s and players.player_position = '%s' and players.player_nationality  = '%s' and player_season_performance.player_team = '%s'" % (
                asis, pos, nation, team)
            result = engine.connect().execute(query)
        elif age == '' and pos == '' and nation != '' and team == '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.assists %s and players.player_nationality  = '%s'" % (
                asis, nation)
            result = engine.connect().execute(query)
        elif age == '' and pos == '' and nation != '' and team != '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.assists %s and players.player_nationality  = '%s' and player_season_performance.player_team = '%s'" % (
                asis, nation, team)
            result = engine.connect().execute(query)
        elif age == '' and pos == '' and nation == '' and team != '':
            query = "select players.player_fullname, players.player_age, players.player_position, players.player_nationality, player_season_performance.player_team, player_season_performance.assists from players join player_season_performance on players.player_fullname = player_season_performance.player_fullname where player_season_performance.assists %s and player_season_performance.player_team = '%s'" % (
                asis, team)
            result = engine.connect().execute(query)
        title = ('Player', 'Age', 'Position', 'Nationality', 'Team', 'Assists')
    else:
        return render_template("player.html")

    response.append(title)
    for row in result:
        response.append(row)
    context = dict(data=response)
    return render_template("player.html", **context)


#
#             Coach Part
#
@app.route('/coach', methods=['GET'])
def coach():
    return render_template("coach.html")

# Method to handle user's query on coach and coach performance


@app.route('/checkCoach')
def checkCoach():
    name = request.form['name']
    nation = request.form['nation']
    age = request.form['age']
    team = request.form['team']
    season = request.form['season']
    rank = request.form['rank']
    win = request.form['win']
    response = []
    title = ()

    if name != '' and team == '' and rank == '':
        if name == 'all':
            query = "select * from coaches"
            result = engine.connect().execute(query)
        else:
            query = "select * from coaches where coach_name == '%s'" % (name)
            result = engine.connect().execute(query)
        title = ('Coach', 'Age', 'Nationality')
    elif name != '' and team != '' and rank == '':
        query = "select * from coaches where coach_name == '%s' and coach_team = '%s'" % (
            name, team)
        result = engine.connect().execute(query)
    elif season != '' and nation == '':
        if name == '' or name == 'all':
            query = "select * from coach_seasons"
            result = engine.connect().execute(query)
        else:
            query = "select * from coach_seasons where coach_name == '%s'" % (
                name)
            result = engine.connect().execute(query)
        title = ('Coach', 'Team', 'Season')
    elif nation != '' and rank == '' and season == '':
        query = "select * from coaches where coach_nationality = '%s'" % (
            nation)
        result = engine.connect().execute(query)
        title = ('Coach', 'Age', 'Nationality')
    elif rank != '':
        if nation == '':
            query = "select coach_seasons.coach_name, team_season_performance.team_name, team_season_performance.rank, team_season_performance.season from team_season_performance join coach_seasons on team_season_performance.team_name = coach_seasons.coach_team where team_season_performance.rank %s" % (
                rank)
            result = engine.connect().execute(query)
        else:
            query = "select coach_seasons.coach_name, team_season_performance.team_name, team_season_performance.rank, team_season_performance.season from team_season_performance join coach_seasons on team_season_performance.team_name = coach_seasons.coach_team where team_season_performance.rank %s and coach_seasons.coach_name in (select coach_name from coaches where coach_nationality = '%s')" % (
                rank, nation)
            result = engine.connect().execute(query)
        title = ('Coach', 'Team', 'Rank', 'Season')
    elif nation != '' and season != '':
        query = "select coach_seasons.coach_name, team_season_performance.team_name, team_season_performance.rank, team_season_performance.wins, team_season_performance.losses, team_season_performance.season from team_season_performance join coach_seasons on team_season_performance.team_name = coach_seasons.coach_team where coach_seasons.coach_name in (select coach_name from coaches where coach_nationality = '%s')" % (
            nation)
        result = engine.connect().execute(query)
        title = ('Coach', 'Team', 'Rank', 'Wins', 'Losses', 'Season')
    elif win != '' and age == '':
        query = "select coach_seasons.coach_name, team_season_performance.team_name, team_season_performance.wins, team_season_performance.season from team_season_performance join coach_seasons on team_season_performance.team_name = coach_seasons.coach_team where team_season_performance.wins %s" % (
            win)
        result = engine.connect().execute(query)
        title = ('Coach', 'Team', 'Wins', 'Season')
    elif age != '':
        if win == '':
            query = "select * from coaches where coach_age %s" % (age)
            result = engine.connect().execute(query)
            title = ('Coach', 'Age', 'Nationality')
        else:
            query = "select coach_seasons.coach_name, team_season_performance.team_name, team_season_performance.wins, team_season_performance.season from team_season_performance join coach_seasons on team_season_performance.team_name = coach_seasons.coach_team where coach_seasons.coach_name in (select coach_name from coaches where coach_age %s)" % (
                age)
            result = engine.connect().execute(query)
            title = ('Coach', 'Team', 'Wins', 'Season')
    else:
        return render_template("coach.html")

    response.append(title)
    for row in result:
        response.append(row)
    context = dict(data=response)
    return render_template("coach.html", **context)

#
#             Match part
#


@app.route('/match', methods=['GET'])
def match():
    return render_template("match.html")

# Method to handle user's query on mathches


@app.route('/checkMatch')
def checkMatch():
    home = request.form['home']
    away = request.form['away']
    date = request.form['date']
    league = request.form['league']
    season = request.form['season']
    hg = request.form['hg']
    ag = request.form['ag']
    response = []
    title = ()

    if home != '' and hg == '' and ag == '':
        if away != '' and date == '':
            query = "select * from matches where team_home = '%s' and team_away = '%s'" % (
                home, away)
            result = engine.connect().execute(query)
        elif away != '' and date != '':
            query = "select * from matches where team_home = '%s' and team_away = '%s' and date = '%s'" % (
                home, away, date)
            result = engine.connect().execute(query)
        elif away == '' and date != '':
            query = "select * from matches where team_home = '%s' and date = '%s'" % (
                home, date)
            result = engine.connect().execute(query)
        else:
            query = "select * from matches where team_home = '%s'" % (home)
            result = engine.connect().execute(query)
    elif league != '' and home == '' and away == '':
        if date != '':
            query = "select * from matches where match_league = '%s' and date = '%s'" % (
                league, date)
            result = engine.connect().execute(query)
        elif date == '':
            query = "select * from matches where match_league = '%s'" % (
                league)
            result = engine.connect().execute(query)
    elif hg != '':
        if date != '' and league != '':
            query = "select * from matches where date = '%s' and match_league = '%s' and home_goals '%s" % (
                date, league, hg)
            result = engine.connect().execute(query)
        elif home != '':
            query = "select * from matches where date = '%s' and team_home = '%s' and home_goals '%s" % (
                home, hg)
            result = engine.connect().execute(query)
    elif ag != '':
        if date != '' and league != '':
            query = "select * from matches where date = '%s' and match_league = '%s' and away_goals '%s" % (
                date, league, ag)
            result = engine.connect().execute(query)
        elif away != '':
            query = "select * from matches where date = '%s' and team_away = '%s' and away_goals '%s" % (
                away, ag)
            result = engine.connect().execute(query)
    elif date != '':
        query = "select * from matches where date = '%s'" % (date)
        result = engine.connect().execute(query)
    else:
        query = "select * from matches"
        result = engine.connect().execute(query)

    title = ('Home', 'Away', 'Date', 'League', 'Season',
             'Home Goals', 'Away Goals', 'Referee', 'Attendance')
    response.append(title)
    for row in result:
        response.append(row)
    context = dict(data=response)
    return render_template("match.html", **context)

#
# Test part
#


@app.route('/test', methods=['GET'])
def test():
    return render_template('test.html')

# Dammy method to do sql test


@app.route('/testClick', methods=['POST'])
def testClick():
    name = request.form['name']
    names = []
    str = ('name', 'age', 'nationality', )
    names.append(str)
    if name == '':
        result = engine.connect().execute("select team_season_performance.team_name, team_season_performance.rank, join_in.league_name from team_season_performance join join_in on team_season_performance.team_name = join_in.team_name where join_in.league_name = 'Premier League' order by rank")
    for row in result:
        names.append(row)
    context = dict(data=names)
    return render_template("test.html", **context)


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

            python server.py

        Show the help text using:

            python server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()
