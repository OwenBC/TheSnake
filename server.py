import os
import random
import enum

import cherrypy
from board import *

class direction(enum.Enum): 
    left = 0
    right = 1
    up = 2
    down = 3

class Battlesnake(object):
    @cherrypy.expose
    def index(self):
        # If you open your snake URL in a browser you should see this message.
        return "If you're reading this it's working"

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
        return {"color": "#F1F1F1", "headType": "dead", "tailType": "block-bum"}

    def collision_check(self, points, x, y, width, height, board, pt_change):
        #Check for walls
        if(x == 0):
            points[direction.left.value] += pt_change
        if(y == 0):
            points[direction.up.value] += pt_change
        if(x == width - 1):
            points[direction.right.value] += pt_change
        if(y == height - 1):
            points[direction.down.value] += pt_change

        #Don't hit snakes, including youself
        if(board.getPos(x-1,y) != 'x'):
            points[direction.left.value] += pt_change
        if(board.getPos(x+1,y) != 'x'):
            points[direction.right.value] += pt_change
        if(board.getPos(x,y-1) != 'x'):
            points[direction.up.value] += pt_change
        if(board.getPos(x,y+1) != 'x'):
            points[direction.down.value] += pt_change

    def adj_heads(self, points, x, y, board, pt_change_prey, pt_change_pred):
        #avoid predators, seek prey
        pts = [['H',pt_change_pred],['h',pt_change_prey]]
        for target in pts:
            if(board.getPos(x-2,y) == target[0]):   #left 2
                points[direction.left.value] += target[1]
            if(board.getPos(x+2,y) == target[0]):   #right 2
                points[direction.right.value] += target[1]
            if(board.getPos(x,y-2) == target[0]):   #up 2
                points[direction.up.value] += target[1]
            if(board.getPos(x,y+2) == target[0]):   #down 2
                points[direction.down.value] += target[1]
            if(board.getPos(x-1,y-1) == target[0]):   #left 1 up 1
                points[direction.left.value] += target[1]
                points[direction.up.value] += target[1]
            if(board.getPos(x-1,y+1) == target[0]):   #left 1 down 1
                points[direction.left.value] += target[1]
                points[direction.down.value] += target[1]
            if(board.getPos(x+1,y-1) == target[0]):   #right 1 up 1
                points[direction.right.value] += target[1]
                points[direction.up.value] += target[1]
            if(board.getPos(x+1,y+1) == target[0]):   #right 1 down 1
                points[direction.right.value] += target[1]
                points[direction.down.value] += target[1]

    def outer_tiles(self, points, x, y, width, height, pt_change):
        #Preference for the middle
        if(x==1):
            points[direction.left.value] += pt_change
        elif(x == width - 2):
            points[direction.right.value] += pt_change
        elif(x == 0 or x == width - 1):
            points[direction.up.value] += pt_change/2
            points[direction.down.value] += pt_change/2
        if(y == 1):
            points[direction.up.value] += pt_change
        elif(y == height - 2):
            points[direction.down.value] += pt_change
        elif(y == 0 or y == height - 1):
            points[direction.left.value] += pt_change/2
            points[direction.right.value] += pt_change/2

    def adjacent_food(self, points, x, y, board, pt_change):
        #point bonus for nearby food
        if(board.getPos(x-1,y) == 'F'):
            points[direction.left.value] += pt_change
        if(board.getPos(x+1,y) == 'F'):
            points[direction.right.value] += pt_change
        if(board.getPos(x,y-1) == 'F'):
            points[direction.up.value] += pt_change
        if(board.getPos(x,y+1) == 'F'):
            points[direction.down.value] += pt_change

    def seek_food(self, points, food, x, y, width, height, pt_change):
        #favour closest food
        min_dist = width + height
        indices = []
        for i in range(len(food)):
            dist = abs(x-food[i]["x"]) + abs(y-food[i]["y"])
            if(dist < min_dist):
                min_dist = dist
                indices = [i]
            elif(dist == min_dist):
                indices.append(i)
        if(min_dist < (width + height)/2):
            target_food = food[random.choice(indices)]
            if(target_food["x"]<x):
                points[direction.left.value] += pt_change
            elif(target_food["x"]>x):
                points[direction.right.value] += pt_change
            if(target_food["y"]<y):
                points[direction.up.value] += pt_change
            elif(target_food["y"]>y):
                points[direction.down.value] += pt_change

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        data = cherrypy.request.json

        #create Board object
        gameboard = Board(data)

        #left right up down
        points = [0]*4

        #get stuff from data
        x,y = data['you']['body'][0]['x'],data['you']['body'][0]['y']
        width,height = data["board"]["width"],data["board"]["height"]

        #check for definite collisions
        self.collision_check(points, x, y, width, height, gameboard, -1000)
        #chase smaller snakes, avoid bigger ones
        self.adj_heads(points, x, y, gameboard, 3, -9)
        #preference to stay away from walls
        self.outer_tiles(points, x, y, width, height, -1)
        #food grabbing
        if(True): #active
            self.seek_food(points, data["board"]["food"], x, y, width, height, 2)
        else: #passive
            self.adjacent_food(points, x, y, gameboard, 2)

        #get moves with most points
        
        move_choices = []
        max_pts = max(points)
        for i in range(4):
            if(points[i] == max_pts):
                move_choices.append(direction(i).name)
        print(f"points: {points}")   
        print(f"move choices: {move_choices}")

        #choose
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
