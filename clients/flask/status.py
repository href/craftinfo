#!/usr/local/bin/python
# -*- coding: utf-8 -*-

"""Minecraft server status page.

Connects to the server-socket which handles caching and renders the
result using flask.

If the script is executed directly, the flask dev-server is started.

"""

from flask import Flask
from flask import render_template
from craftinfoserver import get_serverinfo


app = Flask(__name__)


@app.route("/")
def status():
    """Handles the webapp root."""
    info = get_serverinfo("localhost", 5001)

    MAXUPDATES = 4 # that's all the current template can handle

    online = info["online"]
    players = info["players"]
    updates = info["updates"][:MAXUPDATES]

    return render_template('status.html', online=online, players=players, 
        updates=updates, playercount = len(players))


if __name__ == "__main__":
    """Start flask dev-server."""
    app.debug = True
    app.run()
