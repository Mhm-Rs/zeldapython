import pygame
from settings import *
from entity import Entity
from support import *


class Enemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player, trigger_death_particles, add_xp):
        # * general setup
        super().__init__(groups)
        # another sprite type, not the same as the tile one
        self.sprite_type = "enemy"

        # Graphics setup
        # get the animations for the monster
        self.import_graphics(monster_name)
        # set the current status
        self.status = "idle"
        # set the image
        self.image = self.animations[self.status][self.frame_index]

        # * Movement
        # place the enemy on the given position
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -10)
        # an enemy knows the obstacle
        self.obstacle_sprites = obstacle_sprites

        # * Stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        # health
        self.health = monster_info["health"]
        # exp given when defeated
        self.exp = monster_info["exp"]
        # speed
        self.speed = monster_info["speed"]
        # damage
        self.attack_damage = monster_info["damage"]
        # knockback when attacked
        self.resistance = monster_info["resistance"]
        # radius where it can attack
        self.attack_radius = monster_info["attack_radius"]
        # radius where it can detect player
        self.notice_radius = monster_info["notice_radius"]
        # particle to use after attack
        self.attack_type = monster_info["attack_type"]

        # * player interaction
        self.can_attack = True
        self.attack_cooldown = 1000
        self.attack_time = None
        self.damage_player = damage_player

        # * invicibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invicibility_duration = 300

        # show death particles
        self.trigger_death_particles = trigger_death_particles

        # add xp of player
        self.add_exp = add_xp

        # sounds
        self.death_sound = pygame.mixer.Sound("../audio/death.wav")
        self.hit_sound = pygame.mixer.Sound("../audio/hit.wav")
        self.attack_sound = pygame.mixer.Sound(monster_info["attack_sound"])
        self.death_sound.set_volume(0.2)
        self.hit_sound.set_volume(0.2)
        self.attack_sound.set_volume(0.3)

    def import_graphics(self,name):
        # almost the same as import_player_assets from player

        # animations of each monster
        self.animations = {"idle":[], "move":[], "attack":[]}
        # path to the animation of the enemy
        main_path = f"../graphics/monsters/{name}/"

        # load the animations
        for animation in self.animations.keys():
            fullpath = main_path + animation
            # eg : graphics/monster/racoon/idle
            self.animations[animation] = import_folder(fullpath)

    def get_player_distance_direction(self,player):
        # convert the center of the entities as vectors
        enemy_vector = pygame.math.Vector2(self.rect.center)
        player_vector = pygame.math.Vector2(player.rect.center)

        # get the module of the vector which is the difference of the two vectors
        distance = (player_vector - enemy_vector).magnitude()
        # get the angle of that vector
        direction = (player_vector - enemy_vector).normalize() if distance > 0 else pygame.math.Vector2(0, 0)

        return distance, direction

    def get_status(self,player):
        # move towards the player if possible

        # get the distance to the player
        distance = self.get_player_distance_direction(player)[0]

        if distance <= self.attack_radius and self.can_attack:
            if self.status != "attack":
                self.frame_index = 0
            self.status = "attack"
        elif distance <= self.notice_radius:
            self.status = "move"
        else:
            self.status = "idle"

    def actions(self, player):
        if self.status == "attack":
            self.damage_player(self.attack_damage, self.attack_type)
            self.attack_time = pygame.time.get_ticks()
            self.attack_sound.play()
        elif self.status == "move":
            # move towards the player if possible

            # set the direction in which the enemy should move so that they can attack the player
            self.direction = self.get_player_distance_direction(player)[1]

        else:
            # if the enemy does not notice the player, the enemy should stop moving
            self.direction = pygame.math.Vector2()

    def animate(self):
        # get all the images for the current animation according to the current status
        animation = self.animations[self.status]

        # loop over the frame index to get the image to display
        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            # go back to the first frame when the loop is complete
            if self.status == "attack":
                self.can_attack = False
            self.frame_index = 0

        # set the image, then the rect
        self.image = animation[int(self.frame_index)]
        # change the rect (because not all images have the same size)
        self.rect = self.image.get_rect(center=self.hitbox.center)


        # flicker if the enemy has been hit
        if not self.vulnerable:
            alpha = self.flicker_value()
            # when alpha = 255, the enemy is displayed
            # when alpha = 0, nothing appears
            # thus creating a flickering effect
            self.image.set_alpha(alpha)
        else:
            # get back to its state
            self.image.set_alpha(255)

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True

        if not self.vulnerable:
            if current_time - self.hit_time >= self.invicibility_duration:
                self.vulnerable = True

    def get_damage(self, player, attack_type):
        if self.vulnerable:
            self.hit_sound.play()
            # get the direction in which the enemy has been hit
            self.direction = self.get_player_distance_direction(player)[1]
            if attack_type == "weapon":
                # lower the health of the enemy
                self.health -= player.get_full_weapon_damage()
            else:
                # magic damage
                self.health -= player.get_full_magic_damage()
            self.vulnerable = False
            self.hit_time = pygame.time.get_ticks()

    def check_death(self):
        # kill an enemy if its health is null
        if self.health <= 0:
            self.trigger_death_particles(self.rect.center, self.monster_name)
            self.add_exp(self.exp)
            self.death_sound.play()
            self.kill()

    def knockback(self):
        # if the enemy has just been hit
        if not self.vulnerable:
            # change the direction
            self.direction *= - self.resistance

    def update(self):
        self.knockback()
        self.move(self.speed)
        self.animate()
        self.cooldowns()

    def enemy_update(self, player):
        self.get_status(player)
        self.actions(player)
        self.check_death()