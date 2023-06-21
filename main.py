import pygame
import os
import time
import random

pygame.init()

#IMAGES AND SPRITES
ENEMY_GREEN = pygame.transform.scale(pygame.image.load(os.path.join("assets", "AlienGreen.png")), (50, 50))
ENEMY_RED = pygame.transform.scale(pygame.image.load(os.path.join("assets", "AlienRed.png")), (50, 50))
ENEMY_BLUE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "AlienBlue.png")), (50, 50))
PLAYER_SPACESHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "SpaceShipAnimation1.png")), (80, 80))
LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Laser.png")), (5, 20))

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)
    

class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = LASER
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, position):
        screen.blit(self.ship_type, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(screen)

    def move_lasers(self, vel, objects):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(SCREEN_HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(objects):
                objects.health -= 10
                self.lasers.remove(laser)
    
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def Shoot(self):
        if self.cooldown == 0:
            laser = Laser(self.x, self.y, LASER)
            self.lasers.append(laser)
            self.cooldown = 1

class player(Ship):

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_type = PLAYER_SPACESHIP
        self.laser = LASER
        self.mask = pygame.mask.from_surface(self.ship_type)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(SCREEN_HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + 80 + 10, 80, 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + 80 + 10, 80 * (self.health/self.max_health), 10))

class Enemy(Ship):
    COLOURS = {
        "red": (ENEMY_RED),
        "green": (ENEMY_GREEN),
        "blue": (ENEMY_BLUE)
    }

    def __init__(self, x, y, colour, health=100):
        super().__init__(x, y, health)
        self.ship_type = self.COLOURS[colour]
        self.lasers
        self.mask = pygame.mask.from_surface(self.ship_type)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 30
    clock = pygame.time.Clock()
    score = 0
    lives = 5
    velocity = 8
    font = pygame.font.SysFont("sanserif", 22)
    defeat_font = pygame.font.SysFont("sanserif", 82)

    enemies = []
    enemies_quantity = 5
    enemy_vel = 3
    laser_vel = 3

    defeat = False
    defeat_timer = 0

    Player = player(300, SCREEN_HEIGHT - 80)

    def redraw_window():
        screen.fill((0, 0, 0))
        score_label = font.render(f"SCORE: {score}", 1, (255, 255, 255))
        lives_label = font.render(f"LIVES: {lives}", 1, (255, 255, 255))

        screen.blit(lives_label, (10, 10))
        screen.blit(score_label, (SCREEN_WIDTH - score_label.get_width() - 10 , 10))

        for enemy in enemies:
            enemy.draw(screen)

        Player.draw(screen)   

        if defeat:
            defeat_label = defeat_font.render("Defeated", 1, (255, 0, 0))
            screen.blit(defeat_label, (SCREEN_WIDTH/2 - defeat_label.get_width()/2, SCREEN_HEIGHT/2)) 

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or Player.health <= 0:
            defeat = True
            defeat_timer += 1

        if defeat:
            if defeat_timer > FPS * 5:
                run = False
            else:
                continue 

        if len(enemies) == 0:
            score += 1
            enemies_quantity += 2
            for i in range(enemies_quantity):
                enemy = Enemy(random.randrange(50, SCREEN_WIDTH - 100), random.randrange(-1000, -800), random.choice(["red", "green", "blue"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and Player.x > 0:
            Player.x -= velocity
        if keys[pygame.K_RIGHT] and Player.x + 80 < SCREEN_WIDTH:
            Player.x += velocity
        if keys[pygame.K_UP] and Player.y > 0:
            Player.y -= velocity
        if keys[pygame.K_DOWN] and Player.y + 80 < SCREEN_HEIGHT:
            Player.y += velocity
        if keys[pygame.K_SPACE]:
            Player.Shoot()
        
        if random.randrange(0, 2*60) == 1:
            enemy.shoot()

        if collide(enemy, Player):
            Player.health -= 10
            enemies.remove(enemy)

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            if enemy.y + 50 > SCREEN_HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        Player.move_lasers(-laser_vel, enemies)


main()
