import libtcodpy as libtcod
#Parameters for screen size & FPS
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20
#Defines the size of the map.
MAP_WIDTH = 80
MAP_HEIGHT = 45
#Defines a few constants relevant to dungeon generator
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
#Defines the colors that the walls will have.
color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)


class Tile: 
	#class for the tiles that will form the map
	def __init__(self, blocked, block_sight):
		self.blocked = blocked
		#If tile blocks movement, it also blocks sight
		if block_sight is None: block_sight = blocked
		self.block_sight = block_sight

class Rect:
	#a rectangle on the map. used to characterize a room.
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h
	def center(self):
		center_x = (self.x1 + self.x2) / 2
		center_y = (self.y1 + self.y2) / 2
		return (center_x, center_y)
 
	def intersect(self, other):
		#returns true if this rectangle intersects with another one
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
				self.y1 <= other.y2 and self.y2 >= other.y1)


def create_room(room):
	global map
	#go through the tiles in the rectangle and make them passable
	for x in range(room.x1 + 1, room.x2):
		for y in range(room.y1 + 1, room.y2):
			map[x][y].blocked = False
			map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
	#function that creates horizontal tunnels
	global map
	for x in range(min(x1, x2), max(x1, x2) + 1):
		map[x][y].blocked = False
		map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
	#function that creates vertical tunnels
	global map
	for y in range(min(y1, y2), max(y1, y2) + 1):
		map[x][y].blocked = False
		map[x][y].block_sight = False

class Object:
	#creates a broad object-class usable for most things
	#represented by character on screen always
	def __init__(self, x, y, char, color):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
	def move(self, dx, dy):
		#Ensures you cannot walk over blocked tiles
		if not map[self.x + dx][self.y + dy].blocked:
			self.x += dx
			self.y += dy
	def draw(self):
		#sets the color & then draws the character that represents this object at position
		libtcod.console_set_default_foreground(con, self.color)
		libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
	def clear(self):
		#erase the character that represents this object
		libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

#Checks for keypresses & changes player coordinate
def handle_keys():
	key = libtcod.console_wait_for_keypress(True)  #turn-based
 
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		#Alt+Enter: toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
 
	elif key.vk == libtcod.KEY_ESCAPE:
		return True  #exit game command
 
	#movement keys
	if libtcod.console_is_key_pressed(libtcod.KEY_UP):
		player.move(0, -1)
 
	elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
		player.move(0, 1)
 
	elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
		player.move(-1, 0)
 
	elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
		player.move(1, 0)

def make_map():
	global map
 
	#fill map with "unblocked" tiles
	map = [[ Tile(True, True)
		for y in range(MAP_HEIGHT) ]
			for x in range(MAP_WIDTH) ]
	#dungeon generator
	rooms = []
	num_rooms = 0
	for r in range(MAX_ROOMS):
		#random height and width
		w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
		h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
		#creates random position without going outside the map
		x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
		y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

		#create new rooms with 'rect' class
		new_room = Rect(y, x, w, h)

		#check for intersections between other rooms
		failed = False
		for other_room in rooms:
			if new_room.intersect(other_room):
				failed = True
				break
		if not failed:
			#^ = no intersections; room is valid
			
			#renders room
			create_room(new_room)

			#gets coordinates of center
			(new_x, new_y) = new_room.center()

			if num_rooms == 0:
				#this means that this is the first room; therefore player starting
				#coordinates should be in this room
				player.y = new_x
				player.y = new_y
		else:
			#all rooms after the first should be connected
			#to the previous room with a tunnel

			#center coordinates on previous room
			(prev_x, prev_y) =room[num_rooms-1].center()

			#get random number between 0 and 1 in order to decide tunneling
			if libtcod.random_get_int(0, 0 , 1) == 1:
				#first move horizontally, then vertically
				create_h_tunnel(prev_x, new_x, prev_y)
				create_v_tunnel(prev_y, new_y, prev_x)
			else:
				create_v_tunnel(prev_y, new_y, prev_x)
				create_h_tunnel(prev_x, new_x, prev_y)
		#append new room to list
		rooms.append(new_room)
		num_rooms += 1

#Defines function that render all objects.
def render_all():
	global color_dark_ground
	global color_dark_wall 

	#Goes through all tiles and prints them in color
	for y in range(MAP_HEIGHT):
		for x in range(MAP_WIDTH):
			wall = map[x][y].block_sight
			if wall:
				libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET )
			else:
				libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET )
	#draw all objects in the list
	for object in objects:
		object.draw()




############################
####!!!Initialization!!!####
############################

#Defining what font we use
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
#Initializes screen.
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Roguelike', False)
#Defines other console
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
#Limits FPS
libtcod.sys_set_fps(LIMIT_FPS)

player = Object(23, 25, "@", libtcod.white)
#Defines all objects used in game.
objects = [player]


#Draws the map on screen
make_map()

###########################
##!!!!Main game loop!!!!###
###########################

while not libtcod.console_is_window_closed():
	#Renders the screen
	render_all()
	#draws all objects
	for object in objects:
		object.draw()
	
	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)	
	#Flushes screen
	libtcod.console_flush()

	#removes all objects former positions before they move
	for object in objects:
		object.clear()
	#Initializes other console


	#handle keys and exit game if needed
	exit = handle_keys()
	if exit:
		break
