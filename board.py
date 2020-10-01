import astar
import random

'''
0 - empty
0 - tails
3 - my head
4 - my body
5 - larger or equivalent enemy head
6 - big head adjacent/near me
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
		head = (data['you']['body'][0]['x'], data['you']['body'][0]['y'])
		for i in self.__get_adj(head):
			for j in self.__get_adj(i):
				if self.getPos(j) == 5 and self.getPos(i) < 3 and self.getPos(i) != -1:
					self.__setPos(i[0],i[1],6)

	def __get_adj(self, pos):
		x = pos[0]
		y = pos[1]
		return [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]


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

	def __astarPath(self, start, end, allow_danger_moves = False):
		return astar.astar(self.board, start, end, allow_danger_moves)

	#check path for two closest foods and return first move of shortest path 
	#TODO: try to find path that leads to a tail
	def seek_food(self, head, tail, food, starving = False):

		paths = []
		#Look for food with a return path
		for f in food:
			f_pos = (f["x"],f["y"])
			path = self.__astarPath(head,f_pos)
			if path != None and self.__astarPath(f_pos,tail) != None:
				paths.append([len(path),self.__return_first_move(path)])

		#If starving look for any path to food
		if len(paths) == 0 and starving:
			for f in food:
				f_pos = (f["x"],f["y"])
				path = self.__astarPath(head,f_pos)
				if path != None:
					paths.append([len(path),self.__return_first_move(path)])
			if len(paths) == 0:
				return None

		#Return the move of the shortest path
		target = paths[0]
		for f in paths:
			if f[0] < target[0]:
				target = f
		return target[1]

	#tail chase
	def coil(self, head, tail, allow_danger_moves = False):
		path = self.__astarPath(head, tail, allow_danger_moves)
		if path == None:
			return None
		return self.__return_first_move(path)

	#TODO: Coil function for other snakes tails. Note: make sure snake hasn't just eaten

	#pick an empty adjacent move TODO: there's something wrong here, probably here
	def desperation(self,head):
		adj = self.__get_adj(head)
		open_moves = []
		for d in adj:
			val = self.getPos(d)
			if val < 3 and val != -1:
				open_moves.append(d)
		if len(open_moves) == 0:
			for d in adj:
				val = self.getPos(d)
				if val == 6:
					open_moves.append(d)
		if len(open_moves) == 0:
			return None
		return self.__get_move(head, random.choice(open_moves))