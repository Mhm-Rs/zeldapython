import pygame

from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade


class Level:

    def __init__(self):

        # get the display surface from main
        self.display_surface = pygame.display.get_surface()

        # sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # is the game paused ?
        self.game_paused = False

        # attack sprites
        self.current_attack = None
        # will contain : magic, weapon
        self.attack_sprites = pygame.sprite.Group()
        # will contain : anything that can be attacked
        self.attackable_sprites = pygame.sprite.Group()

        # sprite setup
        self.create_map()

        # user interface
        self.ui = UI()
        self.upgrade = Upgrade(self.player)

        # particles
        self.animation_player = AnimationPlayer()

        # magic
        self.magic_player = MagicPlayer(self.animation_player)

    def create_map(self):

        # layouts of the map
        layouts = {
            "boundary": import_csv_layout("../map/map_FloorBlocks.csv"),
            "grass": import_csv_layout("../map/map_Grass.csv"),
            "object": import_csv_layout("../map/map_LargeObjects.csv"),
            "entity": import_csv_layout("../map/map_Entities.csv")
        }

        graphics = {
            "grass": import_folder("../graphics/Grass"),
            "object": import_folder("../graphics/objects")
        }

        # .items() returns a set-like object containing keys and values
        for style, layout in layouts.items():

            # # ** enumerate returns a list containing an index and the object that was passed in

            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != "-1":
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE

                        # add a boundary to the group
                        if style == "boundary":
                            Tile((x, y), [self.obstacle_sprites], 'invisible')

                        # add a grass tile with a random image
                        if style == "grass":
                            random_image = choice(graphics["grass"])
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites],
                                 "grass", random_image)

                        # add an object tile
                        if style == "object":
                            image = graphics["object"][int(col)]
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites], "object", image)

                        # add an entity
                        if style == "entity":
                            # place the player :
                            if col == "394":
                                # the player "knows" the obstacle sprites but isn't inside of that group
                                self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites,
                                                     self.create_attack, self.destroy_attack, self.create_magic)
                            else:
                                # create an enemy with the correct name
                                if col == "390":
                                    monster_name = "bamboo"
                                elif col == "391":
                                    monster_name = "spirit"
                                elif col == "392":
                                    monster_name = "raccoon"
                                else:
                                    monster_name = "squid"

                                Enemy(monster_name, (x, y), [self.visible_sprites, self.attackable_sprites],
                                      self.obstacle_sprites, self.damage_player, self.trigger_death_particles,
                                      self.add_exp)

    def destroy_attack(self):
        # if there's a weapon, destroy it after is has served its purpose
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def create_attack(self):
        # create a weapon
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def create_magic(self, style, strength, cost):
        if style == "heal":
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])

        if style == "flame":
            self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])

    def player_attack_logic(self):
        # check if any attack sprite collide with any attackable sprite
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                # get all the sprites that collide with the current attack_sprite
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                if collision_sprites:
                    # if there are sprites that collide
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == "grass":
                            # get the position of the grass
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0, 55)
                            # spawn grass particles : 3 to 6 particles
                            for particle in range(randint(3, 6)):
                                self.animation_player.create_grass_particles(pos-offset, [self.visible_sprites])
                            # destroy grass
                            target_sprite.kill()
                        else:
                            # deal damage based on the stats
                            target_sprite.get_damage(self.player, attack_sprite.sprite_type)

    def damage_player(self, amount, attack_type):
        # remove health from player if hit
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()

            # generate particles
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])

    def trigger_death_particles(self, pos, particle_type):
        # trigger death particles, will be used by enemy
        self.animation_player.create_particles(particle_type, pos, [self.visible_sprites])

    def add_exp(self, amount):
        self.player.exp += amount

    def toggle_upgrade_menu(self):
        self.game_paused = not self.game_paused

    def run(self):
        # draw all the visible sprites
        self.visible_sprites.custom_draw(self.player)

        # display the data from the player using ui
        self.ui.display(self.player)

        if self.game_paused:
            # display the upgrade menu
            self.upgrade.display()
        else:
            # update and draw the game

            # call the update method of every visible_sprite
            self.visible_sprites.update()

            # update all monsters
            self.visible_sprites.enemy_update(self.player)

            # check for enemies and apply our logic
            self.player_attack_logic()


# group for the camera
class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        # general setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # getting half the width and half the height of the screen
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2

        # set a vector for the camera (an offset coming from the player's movement)
        self.offset = pygame.math.Vector2()

        # creating the floor
        self.floor_surface = pygame.image.load("../graphics/tilemap/ground.png").convert()
        self.floor_rect = self.floor_surface.get_rect(topleft=(0, 0))

    # * overwriting the draw method of a group
    def custom_draw(self, player):
        # getting the offset from the player's position
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # drawing the floor

        # removing the offset from the floor to figure out where to draw it
        floor_offset_position = self.floor_rect.topleft - self.offset

        self.display_surface.blit(self.floor_surface, floor_offset_position)

        # for every sprite inside the sprite group
        # we sort the sprites with their y coordinates 
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            # removing the offset from each sprite to figure out where to draw the sprites
            offset_position = sprite.rect.topleft - self.offset

            # draw the sprite 
            self.display_surface.blit(sprite.image, offset_position)

    def enemy_update(self, player):
        # update the status of every enemy
        enemy_sprites = []
        # get the sprites of all enemies
        for sprite in self.sprites():
            if hasattr(sprite, "sprite_type"):
                if sprite.sprite_type == "enemy":
                    enemy_sprites.append(sprite)
        for enemy in enemy_sprites:
            # update enemies
            enemy.enemy_update(player)
