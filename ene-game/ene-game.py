import pygame
import numpy
import random
import os

path = __file__
path = path.replace("ene-game.py", "")
os.chdir(path)

coloroptions = ["Blue", "Red", "Green", "Yellow", "Purple"]

global ColorScheme
while True:
                ColorScheme = str(input("What color, Blue, Red, Green, Yellow or Purple: "))
                ColorScheme = ColorScheme.capitalize()
                if ColorScheme in coloroptions:
                    ColorScheme = ColorScheme + "-"
                    break
                else:
                    print("Try Again")

def main():
    #variables
    ScreenWidth = 800
    ScreenHeight = 600
    global CameraX, WorldPositionX, PlayerHealth, DamageTaken, DamageHealed, gameon, running, gameover, directory
    BackgroundImage = pygame.image.load("images\Background.png")
    gameon = True
    running = False 
    gameover = False
    CameraX = 0
    WorldPositionX = 0
    PlayerHealth = 3
    DamageTaken = False
    DamageHealed = False

    #sprites        
    class Player(pygame.sprite.Sprite):
        def __init__(self, startx, starty):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load(f"images\{ColorScheme}ene-float-1.png")
            self.rect = self.image.get_rect()
            self.rect = self.rect.inflate(-5, -5)
            self.rect.center = [(startx), starty]
            self.imagelist = [(pygame.image.load(f"images\{ColorScheme}ene-float-1.png")), (pygame.image.load(f"images\{ColorScheme}ene-float-2.png"))]
            self.currentframe = 0
            self.prevkey = pygame.key.get_pressed()
            self.speed = 0.75
            self.minspeed = -8
            self.maxspeed = 8
            self.jumpspeed = 12
            self.gravity = 0.5
            self.animation_index = 0
            self.animation_tick = 0
            self.facing_left = False
            self.h_momentum = 0
            self.v_momentum = 0
            self.doublejump = True
            self.doublejumptick = 0
            self.safepointx = startx
            self.safepointy = starty

        def check_fall(self):
            if self.rect.y > 600:
                global PlayerHealth, DamageTaken
                if PlayerHealth == 1:
                    DamageTaken = True
                    return
                global CameraX, WorldPositionX
                CameraX = self.safepointx - WorldPositionX
                objects.update(self)
                WorldPositionX = self.safepointx
                self.rect.y = self.safepointy
                DamageTaken = True
                self.h_momentum = 0

        def check_collision(self, x, y, objects):
            self.rect.move_ip([x, y])
            collide = pygame.sprite.spritecollideany(self, objects)
            self.rect.move_ip([-x,-y])
            return collide

        def player_animation(self):
            self.image = self.imagelist[self.currentframe]
            if self.facing_left == True:
                self.image = pygame.transform.flip(self.image, True, False)

            if self.animation_tick == 40:
                self.animation_tick = 0
                if self.animation_index == 0:
                    self.currentframe = 0
                    self.animation_index = 1
                else:
                    self.currentframe = 1
                    self.animation_tick = -20
                    self.animation_index = 0
            else:
                self.animation_tick += 1

        def update(self, objects):
            self.player_animation()
            key = pygame.key.get_pressed()
            self.check_fall()
            onground = self.check_collision(0, 1, objects)

            if numpy.sign(self.h_momentum) != 0:
                speedtype = numpy.sign(self.h_momentum)
                if speedtype > 0:
                    self.h_momentum += -(self.speed/2)
                else:
                    self.h_momentum += (self.speed/2)

            if self.doublejumptick > 0:
                self.doublejumptick -= 1

            if key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
                if self.h_momentum > self.minspeed:
                    self.h_momentum += -self.speed
                self.facing_left = True

            elif key[pygame.K_RIGHT] and not key[pygame.K_LEFT]:
                if self.h_momentum < self.maxspeed:
                    self.h_momentum += self.speed
                self.facing_left = False

            if onground:
                global WorldPositionX
                self.safepointx = WorldPositionX
                self.safepointy = self.rect.y
                self.v_momentum = 0
                self.doublejump = True

            if key[pygame.K_UP] and onground:
                self.v_momentum = -self.jumpspeed
                self.doublejumptick = 15

            elif key[pygame.K_UP] and self.doublejump and self.doublejumptick == 0:
                self.v_momentum = -self.jumpspeed
                self.doublejump = False

            if self.v_momentum < 10 and not onground:
                self.v_momentum += self.gravity

            self.move(self.h_momentum, self.v_momentum, objects)

        def move(self, x, y, objects):
            dx = x
            dy = y
            i = 0
            while self.check_collision(0, dy, objects) and i < (20):
                dy -= numpy.sign(dy)
                i += 1
            i = 0
            while self.check_collision(dx, 0, objects) and i < (20):
                dx -= numpy.sign(dx)
                i += 1
            i = 0
            global CameraX, WorldPositionX
            CameraX = dx
            WorldPositionX += dx
            self.rect.move_ip([0, dy])

        def draw(self, screen):
            screen.blit(self.image, self.rect)

    class HealthBar(pygame.sprite.Sprite):
        def __init__(self, startx, starty):
            pygame.sprite.Sprite.__init__(self)

            self.image = pygame.image.load("images\ene-health-full.png")
            self.rect = self.image.get_rect()
            self.rect.center = [(startx), starty]
            self.full = True

        def damage(self):
            self.image = pygame.image.load("images\ene-health-empty.png")
            self.full = False
            global PlayerHealth
            PlayerHealth -= 1

        def healed(self):
            self.image = pygame.image.load("images\ene-health-full.png")
            self.full = True
            global PlayerHealth
            PlayerHealth += 1

    class Health1(HealthBar):
        def __init__(self, startx, starty):
            HealthBar.__init__(self, startx, starty)

        def update(self):
            global DamageTaken, DamageHealed, PlayerHealth
            if DamageTaken == True and PlayerHealth == 1:
                self.damage()
                DamageTaken = False
                Gameover()
            if DamageHealed == True:
                self.healed()
                DamageHealed = False
    class Health2(HealthBar):
        def __init__(self, startx, starty):
            HealthBar.__init__(self, startx, starty)

        def update(self):
            global DamageTaken, DamageHealed, PlayerHealth

            if DamageTaken == True and PlayerHealth == 2:
                self.damage()
                DamageTaken = False
            if DamageHealed == True:
                self.healed()
                DamageHealed = False
    class Health3(HealthBar):
        def __init__(self, startx, starty):
            HealthBar.__init__(self, startx, starty)

        def update(self):
            global DamageTaken, DamageHealed, PlayerHealth

            if DamageTaken == True and PlayerHealth == 3:
                self.damage()
                DamageTaken = False
            if DamageHealed == True:
                self.healed()
                DamageHealed = False

    class FloorTile(pygame.sprite.Sprite):
        def __init__(self, startx, starty):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load("images\Floor.png")
            self.rect = self.image.get_rect()
            self.rect.center = [(startx), starty]
            self.immune = True

        def update(self, player):
            self.distance = (player.rect.x - self.rect.x)
            if self.distance < 2000 and self.distance > -2000:
                self.immune = False
            if self.distance > 4000 or self.distance < -10000 and not self.immune:
                self.kill()
            self.rect.move_ip([-CameraX, 0])

    def Gameover():
        global running, gameover
        running = False
        gameover = True

    icon = pygame.image.load("images\ene-health-full.png")
    pygame.display.set_caption("Ene Game")
    pygame.display.set_icon(icon)
    screen = pygame.display.set_mode((ScreenWidth, ScreenHeight))
    Gameoverimage = pygame.image.load("images\Gameover-screen.png").convert_alpha()
    clock = pygame.time.Clock()
    global objects, player_sprites
    objects = pygame.sprite.Group()
    enemys = pygame.sprite.Group()
    player_sprites = pygame.sprite.Group()

    player = Player((ScreenWidth / 2) - 35, 0)
    health1 = Health1(35, 30)
    health2 = Health2(95, 30)
    health3 = Health3(155, 30)
    player_sprites.add(health1, health2, health3)

    font = pygame.font.Font('freesansbold.ttf', 32)
    score = 0
    Scoredisplay = font.render(str(score), True, (0, 0, 0))
    scoreloc = Scoredisplay.get_rect()
    scoreloc.topright = (760, 30)
    scoreend = Scoredisplay.get_rect()
    scoreend.center = (30, 30)

    floor1 = FloorTile((-50), 530)
    objects.add(floor1)

    for i in range(0, 1050, 100):
        floor = FloorTile((i), 530)
        objects.add(floor)

    floorrand = 0
    floorrandy = 0
    lastfloory = 530
    floorpos = 0
    nbt = 0

    #gameloop
    running = True
    alpha = 0
    gameovertick = 0
    while gameon:
        while running:
            pygame.event.pump()
            player.update(objects)
            enemys.update()
            objects.update(player)
            player_sprites.update()
            score = max(round(WorldPositionX / 100), score)
            Scoredisplay = font.render(str(score), True, (0, 0, 0))

            if (WorldPositionX) > nbt:
                floorrand = random.randint(250, 400)
                floorrandy = random.randint(250, 550)
                floorpos = floorrand + 1000
                floor = FloorTile(floorpos, floorrandy)
                nbt += floorrand
                objects.add(floor)


            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False
                    gameon = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        gameon = False

            screen.blit(BackgroundImage, (0, 0))
            enemys.draw(screen)
            player.draw(screen)
            objects.draw(screen)
            player_sprites.draw(screen)
            screen.blit(Scoredisplay, scoreloc)
            pygame.display.flip()
            clock.tick(60)
        if gameover == True:
            if alpha < 255:
                if gameovertick > 10:
                    alpha += 2
                    gameovertick = 0
                else:
                    gameovertick += 1
            
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False
                    gameon = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        gameon = False

                    if event.key == pygame.K_SPACE:
                        return main()
            
            Gameoverimage.set_alpha(alpha)
            screen.blit(Gameoverimage, (0, 0))
            screen.blit(Scoredisplay, scoreend)
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    pygame.init()
    main()