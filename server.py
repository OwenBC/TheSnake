import os
import random

import cherrypy

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""


class Battlesnake(object):
    @cherrypy.expose
    def index(self):
        # If you open your snake URL in a browser you should see this message.
        return "Your Battlesnake is alive!"

    @cherrypy.expose
    def ping(self):
        # The Battlesnake engine calls this function to make sure your snake is working.
        return "pong"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        data = cherrypy.request.json
        print("START")
        return {"color": "#A06B36", "headType": "safe", "tailType": "freckled"}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        data = cherrypy.request.json

        # Choose a random direction to move in
        possible_moves = ["up", "down", "left", "right"]
        head = data['you']['body'][0]

        print(f"Head pos: {head}")

        #Check for walls
        if(head['x'] == 0):
            possible_moves.remove("left")
        if(head['y'] == 0):
            possible_moves.remove("up")
        if(head['x'] == data["board"]["width"] - 1):
            possible_moves.remove("right")
        if(head['y'] == data["board"]["height"] - 1):
            possible_moves.remove("down")

        #don't hit yourself, dummy
        body = data['you']['body']
        for segment in body:
            if(segment["y"] == head["y"]):
                if(segment["x"] == head["x"] - 1):
                    possible_moves.remove("left")
                elif(segment["x"] == head["x"] + 1):
                    possible_moves.remove("right")
            elif(segment["x"] == head["x"]):
                if(segment["y"] == head["y"] - 1):
                    possible_moves.remove("up")
                elif(segment["y"] == head["y"] + 1):
                    possible_moves.remove("down")

        #Don't hit others either
        enemy_snakes = data["board"]["snakes"]
        for snake in enemy_snakes:
            for segment in snake["body"]:
                if(segment["y"] == head["y"]):
                    if(segment["x"] == head["x"] - 1):
                        possible_moves.remove("left")
                    elif(segment["x"] == head["x"] + 1):
                        possible_moves.remove("right")
                elif(segment["x"] == head["x"]):
                    if(segment["y"] == head["y"] - 1):
                        possible_moves.remove("up")
                    elif(segment["y"] == head["y"] + 1):
                        possible_moves.remove("down")

        if(len(possible_moves)==0):
            print("OH SHIT! Guess I'll just die then.")
            move = "up"
        else:
            move = random.choice(possible_moves)

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
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
