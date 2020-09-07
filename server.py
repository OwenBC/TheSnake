import os
import random

import cherrypy
from board import Board

class Battlesnake(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # If you open your snake URL in a browser you should see this message.
        return {
            "apiversion": "1",
            "author": "owenc",
            "color": "#F1F1F1",  
            "head": "dead",  
            "tail": "block-bum",  
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        # TODO: Use this function to decide how your snake is going to look on the board.
        data = cherrypy.request.json

        print("START")
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        data = cherrypy.request.json

        #create Board object
        gameboard = Board(data)

        #get stuff from data
        head = (data['you']['body'][0]['x'], data['you']['body'][0]['y'])
        tail = (data['you']['body'][-1]['x'], data['you']['body'][-1]['y'])
        
        move = None

        #hungr, look for food
        if(data["you"]["health"] < 20):
            move = gameboard.seek_food(head, data["board"]["food"])

        #chase tail
        if(move == None):
            move = gameboard.coil(head, tail)
        if(move == None):
            move = gameboard.desperation(head)
        if(move == None):
            move = "down"

        print(f"MOVE: {move}")
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json
        print("END")
        return "ok"


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": 80}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
