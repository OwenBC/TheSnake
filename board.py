'''
x - empty
M - my head
B - my body
H - larger or equivalent enemy head
h - smaller enemy head
b - enemy body
x - tails
F - food
'''

class Board:

	def __init__(self, data):
		self.board = [['x' for y in range(data['board']['height'])] for x in range(data['board']['width'])]
		for snake in data['board']['snakes']:
			if(snake['id']==data['you']['id']):
				self.__addSnakeToBoard(snake, 'M','B')
			elif(snake['length'] < data['you']['length']):
				self.__addSnakeToBoard(snake, 'h','b')
			else:
				self.__addSnakeToBoard(snake, 'H','b')
		for food in data['board']['food']:
			self.__setPos(food[x],food[y],'F')


	def __addSnakeToBoard(self, snake, head, body):
		i = 1
		length = snake['length']
		for segment in snake['body']:
			x = segment['x']
			y = segment['y']
			if(i == 1):
				self.__setPos(x,y,head)
			elif(i <= length):
				self.__setPos(x,y,body)
			i++;


	def __setPos(self, x, y, val):
		board[x][y] = val

	def getPos(self, x, y):
		if(x<0||y<0||x==data['board']['width']||y==data['board']['height']):
			return 'W'
		else:
			return board[x][y]