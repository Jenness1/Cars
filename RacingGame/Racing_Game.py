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

RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.35)
GREEN_CAR = scale_image(pygame.image.load("imgs/green-car.png"), 0.35)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

FPS = 60

#Mutex lock
position_lock = threading.Lock()

#Binary semaphore for checking the winner
winner_semaphore = threading.Semaphore(1)
winner_declared = False

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
        self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)
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
        global winner_declared
        winner_declared = False

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

def check_winner(car_number):
    global winner_declared

    #First thread to get here aquires the semaphore and can move on; the other thread cannot access the code until it is released
    if winner_semaphore.acquire(blocking=False):
        if not winner_declared:  
            winner_declared = True
            print(f"Car {car_number} wins the race!")
        winner_semaphore.release()


#Still need to add speed being random
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
    if keys[pygame.K_r]:
        car1.reset()

    if not moved:
        car.reduce_speed()

def move_player2(car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_LEFT]:
        car.rotate(left=True)
    if keys[pygame.K_RIGHT]:
        car.rotate(right=True)
    if keys[pygame.K_UP]:
        moved = True
        car.move_forward()
    if keys[pygame.K_DOWN]:
        moved = True
        car.move_backward()
    if keys[pygame.K_l]:
        car2.reset()

    if not moved:
        car.reduce_speed()

# Controls car movement
def car_controller(car1, car2):
    while run1:
        move_player(car1)

        #After the car moves, checks to see if it is colliding with the other car
        #Critical section; Only the first thread to reach this part will get position_lock. Only that thread can access this part
        #Only one car will check for collison instead of both
        with position_lock:
            # Check if car1 collides with car2
            if car1.collide(pygame.mask.from_surface(car2.img), car2.x, car2.y):
                car1.bounce()
            
        if car1.collide(TRACK_BORDER_MASK) != None:
            car1.bounce()

        finish_poi_collide = car1.collide(FINISH_MASK, *FINISH_POSITION)
        if finish_poi_collide != None:
            if finish_poi_collide[1] == 0:
                car1.bounce()
            else:
                check_winner(1)
                car1.reset()
                car2.reset()
        

        time.sleep(1 / FPS) 

def car_controller2(car1, car2):
    while run2:
        #Move car
        move_player2(car1)

        #Check to see if car is colliding with track or car

        #After the car moves, checks to see if it is colliding with the other car
        #Critical section; Only the first thread to reach this part will get the position_lock. Only that thread can access this part
        #Only one car will check for collison instead of both
        with position_lock:
            # Check if car1 collides with car2
            if car1.collide(pygame.mask.from_surface(car2.img), car2.x, car2.y):
                car1.bounce()
        
        #Checks if car is collideing with track 
        if car1.collide(TRACK_BORDER_MASK) != None:
            car1.bounce()

        finish_poi_collide = car1.collide(FINISH_MASK, *FINISH_POSITION)
        if finish_poi_collide != None:
            if finish_poi_collide[1] == 0:
                car1.bounce()
            else:
                check_winner(2)
                car1.reset()
                car2.reset()

        time.sleep(1 / FPS) 

#Game information
run1 = True
run2 = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)),
          (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
queue = []

# Create the two car
car1 = PlayerCar(8, 8, (490, 100))
car2 = PlayerCar(8, 8, (510, 100))

#Create threads to contol the car's movements
car1_thread = threading.Thread(target=car_controller, args=(car1, car2))
car2_thread = threading.Thread(target=car_controller2, args=(car2, car1))
car1_thread.start()
car2_thread.start()

# Main game loop
while run1 and run2:
    clock.tick(FPS)

    draw(WIN, images, car1, car2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run1 = False
            break


# Ending the game
pygame.quit()
car1_thread.join()  
car2_thread.join()