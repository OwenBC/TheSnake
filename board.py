import astar
import random

'''
0 - empty
0 - tails
3 - my head
4 - my body
5 - larger or equivalent enemy head
2 - smaller enemy head
4 - enemy body
1 - food
-1 - OOB
'''

class Board:
	def __init__(self, data):
		self.width = data['board']['width']
		self.height = data['board']['height']
		self.board = [[0 for y in range(self.height)] for x in range(self.width)]
		for food in data['board']['food']:
			self.__setPos(food['x'],food['y'], 1)
		for snake in data['board']['snakes']:
			if(snake['id']==data['you']['id']):
				self.__addSnakeToBoard(snake, 3)
			elif(snake['length'] < data['you']['length']):
				self.__addSnakeToBoard(snake, 2)
			else:
				self.__addSnakeToBoard(snake, 5)

	def __addSnakeToBoard(self, snake, head):
		i = 1
		length = snake['length']
		for segment in snake['body']:
			x = segment['x']
			y = segment['y']
			if(i == 1):
				self.__setPos(x,y,head)
			elif(i < length):
				self.__setPos(x,y,4)
			i+=1

	def __setPos(self, x, y, val):
		self.board[x][y] = val

	#returns value stored at the given location on the board
	def getPos(self, pos):
		if(pos[0]<0 or pos[1]<0 or pos[0]>self.width-1 or pos[1]>self.height-1):
			return -1
		else:
			return self.board[pos[0]][pos[1]]

	def __get_move(self, start, end):
		if start[0] == end[0]:
			if start[1] > end[1]:
				return "down"
			else:
				return "up"
		else:
			if start[0] > end[0]:
				return "left"
			else:
				return "right"

	def __return_first_move(self, path):
		return self.__get_move(path[0], path[1])

	def __astarPath(self, start, end):
		return astar.astar(self.board, start, end)

	#check path for two closest foods and return first move of shortest path
	def seek_food(self, pos, food):
		food_length = len(food)
		targets = []
		while len(targets) < min(2, food_length):
			temp_targets = []  
			min_dist = self.width + self.height
			for f in food:
				dist = abs(pos[0]-f["x"]) + abs(pos[1]-f["y"])
				if(dist < min_dist):
					min_dist = dist
					temp_targets = [f]
				elif(dist == min_dist):
					temp_targets.append(f)
			for f in temp_targets:
				food.remove(f)
				targets.append(f)
		astarPaths = []
		for f in targets:
			f_pos = (f["x"],f["y"])
			path = self.__astarPath(pos, f_pos)
			if path != None:
				astarPaths.append([len(path), self.__return_first_move(path)])
		if len(astarPaths) == 0:
			return None
		#print(astarPaths)
		target = astarPaths[0]
		for f in astarPaths:
			if f[0] < target[0]:
				target = f
		#print(target)
		return target[1]

	#tell me how to get to back end
	def coil(self, head, tail):
		def coil(self, head, tail):
		path = self.__astarPath(head, tail)
		if path == None:
			return None
		return self.__return_first_move(path)

	#pick an empty adjacent move
	def desperation(self,head):
		x = head[0]
		y = head[1]
		options = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
		open_moves = []
		for d in options:
			val = self.getPos(d)
			if val < 3 and val != -1:
				open_moves.append(d)
		#print(open_moves)
		if len(open_moves) == 0:
			return None
		return self.__get_move(head, random.choice(open_moves))