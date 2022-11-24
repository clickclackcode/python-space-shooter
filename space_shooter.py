import pygame
from pygame.locals import *
import random

pygame.init()

# create the window
game_width = 500
game_height = 500
screen_size = (game_width, game_height)
game_window = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Space Shooter')

# colors
red = (200, 0, 0)
white = (255, 255, 255)

class Player(pygame.sprite.Sprite):
	
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.x = x
		self.y = y
		
		self.lives = 3
		self.score = 0
		
		# spaceship image
		image = pygame.image.load('images/spaceship.png')
		image_scale = 40 / image.get_rect().width
		new_width = image.get_rect().width * image_scale
		new_height = image.get_rect().height * image_scale
		scaled_size = (new_width, new_height)
		self.image = pygame.transform.scale(image, scaled_size)
		
		self.rect = self.image.get_rect()
		
		# for displaying damage
		self.invincibility_frames = 0
		damage_image = pygame.image.load('images/damage.png')
		image_scale = 80 / damage_image.get_rect().width
		new_width = damage_image.get_rect().width * image_scale
		new_height = damage_image.get_rect().height * image_scale
		scaled_size = (new_width, new_height)
		self.damage_image = pygame.transform.scale(damage_image, scaled_size)
		
	def update(self):
		self.rect.x = self.x
		self.rect.y = self.y
		
		if self.invincibility_frames > 0:
			self.invincibility_frames -= 1
			
	def draw_damage(self):
		
		if self.invincibility_frames > 0:
			
			damage_x = self.x - self.image.get_width() / 3
			damage_y = self.y - self.image.get_height() / 2
			game_window.blit(self.damage_image, (damage_x, damage_y))
	
class Meteor(pygame.sprite.Sprite):
	
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.x = x
		self.y = y
		
		# select a random color, size, and number for the image
		color = random.choice(['brown', 'grey'])
		size = random.choice(['big', 'medium', 'small', 'tiny'])
		num = random.randint(1, 2)
		self.image = pygame.image.load(f'images/meteors/{color}_{size}_{num}.png')
		
		# set number of hits required to destroy meteor
		# and the points added to score if destroyed
		if size == 'big':
			self.hits = 4
			self.points = 4
		elif size == 'medium':
			self.hits = 3
			self.points = 3
		elif size == 'small':
			self.hits = 2
			self.points = 2
		elif size == 'tiny':
			self.hits = 1
			self.points = 1
			
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		
	def update(self):
		
		# move meteor down
		self.rect.y += 1
		
		# rotate the image
		if self.rect.y % 20 == 0:
			self.image = pygame.transform.rotate(self.image, 90)
			
		# check for collision with player
		if pygame.sprite.spritecollide(self, player_group, False):
			self.kill()
			
			# decrease player life unless player just recently got hit
			if player.invincibility_frames == 0:
				player.lives -= 1
				
				# display the damage image for 50 frames
				player.invincibility_frames = 50
				
		# check for collision with missile
		if pygame.sprite.spritecollide(self, missile_group, True):
			self.hits -= 1
			
			# add to score if meteor is destroyed
			if self.hits == 0:
				player.score += self.points
				
		# remove meteor when it goes off screen or it's been destroyed
		if self.rect.top > game_height or self.hits == 0:
			self.kill()
	
class Missile(pygame.sprite.Sprite):
	
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.rect = Rect(x - 2, y, 4, 8)
		
	def draw(self):
		for w in range(self.rect.width):
			for h in range(self.rect.height):
				game_window.set_at((self.rect.x + w, self.rect.y - h), white)
				
	def update(self):
		
		# missile shoots up the screen
		self.rect.y -= 5
		
		# display the missile or remove it when it goes off screen
		if self.rect.bottom > 0:
			self.draw()
		else:
			self.kill()
	
# create the sprite groups
player_group = pygame.sprite.Group()
meteor_group = pygame.sprite.Group()
missile_group = pygame.sprite.Group()

# load background image
bg = pygame.image.load('images/background.png')

# create the player
player_x = 250
player_y = 450
player = Player(player_x, player_y)
player_group.add(player)

# missile cooldown
missile_cooldown = 200
last_missile = pygame.time.get_ticks() - missile_cooldown

# helper function for displaying text on the screen
def write_text(str, color, x, y):
	font = pygame.font.Font(pygame.font.get_default_font(), 16)
	text = font.render(str, True, color)
	text_rect = text.get_rect()
	text_rect.center = (x, y)
	game_window.blit(text, text_rect)

# create a new meteor
def create_meteor():
	
	# set a random x coordinate
	meteor_x = random.randint(50, game_width - 50)
	
	# start the meteor at the top of the screen
	meteor_y = 0
	
	meteor = Meteor(meteor_x, meteor_y)
	meteor_group.add(meteor)
	
# create the first meteor
create_meteor()

# game loop
clock = pygame.time.Clock()
fps = 120
running = True
loop_ctr = 0
while running:
	
	loop_ctr += 1
	
	clock.tick(fps)
	
	for event in pygame.event.get():
		if event.type == QUIT:
			running = False
			
	keys = pygame.key.get_pressed()
	
	# move the spaceship using the left/right arrow keys
	if keys[K_LEFT] and player.rect.left > 0:
		player.x -= 2
	elif keys[K_RIGHT] and player.rect.right < game_width:
		player.x += 2
		
	# shoot missile with space bar
	if keys[K_SPACE]:
		
		# wait for some time before firing another missile
		current_time = pygame.time.get_ticks()
		if current_time - last_missile > missile_cooldown:
			
			missile = Missile(player.rect.centerx, player.rect.y)
			missile_group.add(missile)
			
			last_missile = current_time
			
	# draw the background
	for bg_x in range(0, game_width, bg.get_width()):
		for bg_y in range(0, game_height, bg.get_height()):
			game_window.blit(bg, (bg_x, bg_y))
			
	# move and draw the player's spaceship
	player_group.update()
	player_group.draw(game_window)
	
	# draw damage if player is hit
	player.draw_damage()
	
	# move and draw the missiles
	missile_group.update()
	
	# create additional meteors every 100th iteration of the game loop
	if loop_ctr == 100:
		
		create_meteor()
		
		# reset the counter
		loop_ctr = 0
		
	# move and draw the meteors
	meteor_group.update()
	meteor_group.draw(game_window)
	
	# display score and remaining lives
	write_text(f'Lives: {player.lives}', white, game_width / 8, 20)
	write_text(f'Score: {player.score}', white, game_width * 7 / 8, 20)
			
	pygame.display.update()
	
	# check if game is over
	gameover = player.lives == 0
	while gameover:
		
		clock.tick(fps)
		
		for event in pygame.event.get():
			
			if event.type == QUIT:
				pygame.quit()
				
		gameover_str = f'Game over. Do you want to play again? (y or n)'
		write_text(gameover_str, red, game_width / 2, game_height / 2)
		
		keys = pygame.key.get_pressed()
		if keys[K_y]:
			
			# clear the sprite groups
			player_group.empty()
			meteor_group.empty()
			missile_group.empty()
			
			# add a meteor
			create_meteor()
			
			# reset the player
			player = Player(player_x, player_y)
			player_group.add(player)
			
			gameover = False
			
		elif keys[K_n]:
			running = False
			break
			
		pygame.display.update()
	
pygame.quit()