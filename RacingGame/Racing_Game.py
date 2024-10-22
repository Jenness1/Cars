import pygame
import time
import math
import threading  # Import threading module
from utils import scale_image, blit_rotate_center

# Images and other game assets (unchanged)
GRASS = scale_image(pygame.image.load("imgs/grass.png"), 2.5)
TRACK = scale_image(pygame.image.load("imgs/track-2.png"), 0.55)
TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border-2.png"), 0.55)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = pygame.image.load("imgs/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (465, 155)

RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.45)
GREEN_CAR = scale_image(pygame.image.load("imgs/green-car.png"), 0.55)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

FPS = 60

#Here have stuff for shared variables 







#--------------------------------------------------

class AbstractCar:
    def __init__(self, max_vel, rotation_vel, START_POS):
        self.START_POS = START_POS
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0

class PlayerCar(AbstractCar):
    IMG = RED_CAR

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = 0.5 * -self.vel
        self.move()

def draw(win, images, car1, car2):
    for img, pos in images:
        win.blit(img, pos)

    car1.draw(win)
    car2.draw(win)
    pygame.display.update()

#Instead of player controlling, it is determined by threading and stuff 
def move_player(car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        car.rotate(left=True)
    if keys[pygame.K_d]:
        car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        car.move_backward()

    if not moved:
        car.reduce_speed()

# This function will be run in a thread to control the car
def car_controller(car):
    while run:
        move_player(car)
        time.sleep(1 / FPS)  # Maintain the frame rate timing

run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)),
          (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]

# Create the two car threads
car1 = PlayerCar(8, 8, (490,100))
car1_thread = threading.Thread(target=car_controller, args=(car1,))
car1_thread.start()

car2 = PlayerCar(8, 8, (510,100))
car2_thread = threading.Thread(target=car_controller, args=(car2,))
car2_thread.start()

# Main game loop
while run:
    clock.tick(FPS)

    draw(WIN, images, car1, car2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
    
    # Car1 collison 
    if car1.collide(TRACK_BORDER_MASK) != None:
        car1.bounce()

    finish_poi_collide = car1.collide(FINISH_MASK, *FINISH_POSITION)
    if finish_poi_collide != None:
        if finish_poi_collide[1] == 0:
            car1.bounce()
        else:
            car1.reset()
            print("finish")

    #Car2 collison
    if car2.collide(TRACK_BORDER_MASK) != None:
        car2.bounce()
    
    finish_poi_collide2 = car2.collide(FINISH_MASK, *FINISH_POSITION)
    if finish_poi_collide2 != None:
        if finish_poi_collide2[1] == 0:
            car2.bounce()
        else:
            car2.reset()
            print("finish")

#Ending the game
pygame.quit()
run = False  # Stop the thread
car1_thread.join()  # Ensure the thread stops gracefully
car1_thread.join()