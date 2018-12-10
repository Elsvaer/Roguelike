import libtcodpy as libtcod
#Parameters for screen size & FPS
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20
#Defines the size of the map.
MAP_WIDTH = 80
MAP_HEIGHT = 45

class Tile: 
	#class for the tiles that will form the map
	def __init__(self, blocked, block_sight):
		self.blocked = blocked

		#If tile blocks movement it also blocks sight
		if block_sight is None: block_sight = blocked
		self.block_sight = block_sight


class Object:
	#creates a broad object-class usable for most things
	#represented by character on screen always
	def __init__(self, x, y, char, color):
		self.x = x
		self.y = y
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

#Defines the colors that the walls will have.
color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)

#Checks for keypresses & changes player coordinate
def handle_keys():
	global playerx, playery
 
	key = libtcod.console_wait_for_keypress(True)  #waits for input; turn-based

	#Fullscreen and quit function    
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		#Alt+Enter: toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
	elif key.vk == libtcod.KEY_ESCAPE:
		return True  #exit game

	#movement keys
	if libtcod.console_is_key_pressed(libtcod.KEY_UP):
		playery -= 1
 
	elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
		playery += 1
 
	elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
		playerx -= 1
 
	elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
		playerx += 1

def make_map():
	global map
 
	#fill map with "unblocked" tiles
	map = [[ Tile(False)
		for y in range(MAP_HEIGHT) ]
			for x in range(MAP_WIDTH) ]

	#Test pillars		
	map[30][22].blocked = True
	map[30][22].block_sight = True
	map[50][22].blocked = True
	map[50][22].block_sight = True

#Defines function that render all objects.
def render_all():
	#draw all objects in the list
	for object in objects:
		object.draw()
	#Goes through all tiles and prints them in color
	for y in range(MAP_HEIGHT):
		for x in range(MAP_WIDTH):
			wall = map[x][y].block_sight
			if wall:
				libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET )
			else:
				libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET )

#Defines all objects used in game.
player = Object(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', libtcod.white)
npc = Object(SCREEN_WIDTH/2 - 5, SCREEN_HEIGHT/2, '@', libtcod.yellow)
objects = [npc, player]


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

#Defines variables of player position
playerx = SCREEN_WIDTH/2
playery = SCREEN_HEIGHT/2

#Draws the map on screen
make_map()

###########################
##!!!!Main game loop!!!!###
###########################

while not libtcod.console_is_window_closed():
	#Prints background
	libtcod.console_set_default_foreground(0, libtcod.white)
	#Prints character to screen
	libtcod.console_put_char(0, playerx, playery, '@', libtcod.BKGND_NONE)
	#Renders the screen
	render_all()
	#draws all objects
	for object in objects:
		object.draw()
	#Flushes screen
	libtcod.console_flush()

	#removes all objects former positions before they move
	for object in objects:
		object.clear()
	#Initializes other console
	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
	#Removes trail of character-signs
	libtcod.console_put_char(0, playerx, playery, ' ', libtcod.BKGND_NONE)

	#handle keys and exit game if needed
	exit = handle_keys()
	if exit:
		break
