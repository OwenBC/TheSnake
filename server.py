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

    def remove(self, input_list, remove):
        try:
            input_list.remove(remove)
        except:
            pass
        return input_list

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
        favourable_moves = ["up", "down", "left", "right"]
        
        head = data['you']['body'][0]
        body = data['you']['body']

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

        #Don't hit snakes
        snakes = data["board"]["snakes"]
        for snake in snakes:
            for i in range(len(snake["body"])-1):
                segment = snake["body"][i]
                if(segment["y"] == head["y"]):
                    if(segment["x"] == head["x"] - 1):
                        possible_moves = self.remove(possible_moves, "left")
                    elif(segment["x"] == head["x"] + 1):
                        possible_moves = self.remove(possible_moves, "right")
                elif(segment["x"] == head["x"]):
                    if(segment["y"] == head["y"] - 1):
                        possible_moves = self.remove(possible_moves, "up")
                    elif(segment["y"] == head["y"] + 1):
                        possible_moves = self.remove(possible_moves, "down")

        #Big snake evasion
        for snake in snakes:
            if(len(snake["body"]) < len(body) or snake["id"] == data['you']['id']):
                continue
            enemy_head = snake["body"][0]
            if(enemy_head["x"] == head["x"] - 2 and enemy_head["y"] == head["y"]):   #left 2
                favourable_moves = self.remove(favourable_moves, "left")
            elif(enemy_head["x"] == head["x"] + 2 and enemy_head["y"] == head["y"]):   #right 2
                favourable_moves = self.remove(favourable_moves, "right")
            elif(enemy_head["x"] == head["x"] and enemy_head["y"] == head["y"] - 2):   #up 2
                favourable_moves = self.remove(favourable_moves, "up")
            elif(enemy_head["x"] == head["x"] and enemy_head["y"] == head["y"] + 2):   #down 2
                favourable_moves = self.remove(favourable_moves, "down")
            elif(enemy_head["x"] == head["x"] - 1 and enemy_head["y"] == head["y"] - 1):   #left 1 up 1
                favourable_moves = self.remove(favourable_moves, "left")
                favourable_moves = self.remove(favourable_moves, "up")
            elif(enemy_head["x"] == head["x"] - 1 and enemy_head["y"] == head["y"] + 1):   #left 1 down 1
                favourable_moves = self.remove(favourable_moves, "left")
                favourable_moves = self.remove(favourable_moves, "down")
            elif(enemy_head["x"] == head["x"] + 1 and enemy_head["y"] == head["y"] - 1):   #right 1 up 1
                favourable_moves = self.remove(favourable_moves, "right")
                favourable_moves = self.remove(favourable_moves, "up")
            elif(enemy_head["x"] == head["x"] + 1 and enemy_head["y"] == head["y"] + 1):   #right 1 down 1
                favourable_moves = self.remove(favourable_moves, "right")
                favourable_moves = self.remove(favourable_moves, "down")

        #Preference for the middle
        if(head['x'] == 1):
            favourable_moves = self.remove(favourable_moves, "left")
        if(head['y'] == 1):
            favourable_moves = self.remove(favourable_moves, "up")
        if(head['x'] == data["board"]["width"] - 2):
            favourable_moves = self.remove(favourable_moves, "right")
        if(head['y'] == data["board"]["height"] - 2):
            favourable_moves = self.remove(favourable_moves, "down")

        #handle favourable, yet non-possible moves
        directions = copy(favourable_moves)
        for direction in directions:
            if(direction not in possible_moves):
                favourable_moves.remove(direction)

        #choose
        if(len(possible_moves)==0):
            print("OH SHIT! Guess I'll just die then.")
            move = "up"
        elif(len(favourable_moves)==0):
            move = random.choice(possible_moves)
        else:
            move = random.choice(favourable_moves)

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
