import os
import random
import enum

import cherrypy

class direction(enum.Enum): 
    left = 0
    right = 1
    up = 2
    down = 3

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

    def collision_check(self, points, data, pt_change):
        head = data['you']['body'][0]
        snakes = data["board"]["snakes"]

        #Check for walls
        if(head['x'] == 0):
            points[direction.left.value] += pt_change
        if(head['y'] == 0):
            points[direction.up.value] += pt_change
        if(head['x'] == data["board"]["width"] - 1):
            points[direction.right.value] += pt_change
        if(head['y'] == data["board"]["height"] - 1):
            points[direction.down.value] += pt_change

        #Don't hit snakes, including youself
        for snake in snakes:
            for i in range(len(snake["body"])-1):
                segment = snake["body"][i]
                if(segment["y"] == head["y"]):
                    if(segment["x"] == head["x"] - 1):
                        points[direction.left.value] += pt_change
                    elif(segment["x"] == head["x"] + 1):
                        points[direction.right.value] += pt_change
                elif(segment["x"] == head["x"]):
                    if(segment["y"] == head["y"] - 1):
                        points[direction.up.value] += pt_change
                    elif(segment["y"] == head["y"] + 1):
                        points[direction.down.value] += pt_change

    def nearby_heads(self, points, data, pt_change_prey, pt_change_pred):
        head = data['you']['body'][0]
        snakes = data["board"]["snakes"]

        #avoid predators, seek prey
        for snake in snakes:
            if(snake["id"] == data['you']['id']):
                continue
            elif(len(snake["body"]) < len(data['you']['body'])):
                pt_change = pt_change_prey
            else:
                pt_change = pt_change_pred

            enemy_head = snake["body"][0]
            if(enemy_head["x"] == head["x"] - 2 and enemy_head["y"] == head["y"]):   #left 2
                points[direction.left.value] += pt_change
            elif(enemy_head["x"] == head["x"] + 2 and enemy_head["y"] == head["y"]):   #right 2
                points[direction.right.value] += pt_change
            elif(enemy_head["x"] == head["x"] and enemy_head["y"] == head["y"] - 2):   #up 2
                points[direction.up.value] += pt_change
            elif(enemy_head["x"] == head["x"] and enemy_head["y"] == head["y"] + 2):   #down 2
                points[direction.down.value] += pt_change
            elif(enemy_head["x"] == head["x"] - 1 and enemy_head["y"] == head["y"] - 1):   #left 1 up 1
                points[direction.left.value] += pt_change
                points[direction.right.value] += pt_change
            elif(enemy_head["x"] == head["x"] - 1 and enemy_head["y"] == head["y"] + 1):   #left 1 down 1
                points[direction.left.value] += pt_change
                points[direction.down.value] += pt_change
            elif(enemy_head["x"] == head["x"] + 1 and enemy_head["y"] == head["y"] - 1):   #right 1 up 1
                points[direction.right.value] += pt_change
                points[direction.right.value] += pt_change
            elif(enemy_head["x"] == head["x"] + 1 and enemy_head["y"] == head["y"] + 1):   #right 1 down 1
                points[direction.right.value] += pt_change
                points[direction.down.value] += pt_change

    def outer_tiles(self, points, data, pt_change):
        head = data['you']['body'][0]
        #Preference for the middle
        if(head['x'] == 1):
            points[direction.left.value] += pt_change
        if(head['y'] == 1):
            points[direction.up.value] += pt_change
        if(head['x'] == data["board"]["width"] - 2):
            points[direction.right.value] += pt_change
        if(head['y'] == data["board"]["height"] - 2):
            points[direction.down.value] += pt_change

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        data = cherrypy.request.json

        #left right up down
        points = [0]*4

        #check for definite collisions
        self.collision_check(points, data, -1000)

        self.nearby_heads(points, data, 2, -6)

        self.outer_tiles(points, data, -1)

        #choose
        move_choices = []
        max_pts = max(points)
        for i in range(4):
            if(points[i] == max_pts):
                move_choices.append(direction(i).name)
        #choose
        if(len(move_choices)==0):
            print("OH SHIT! Guess I'll just die then.")
            move = "up"
        else:
            move = random.choice(move_choices)

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
