import pygame
from settings import *
from support import import_folder
from entity import Entity


class Player(Entity):
    def __init__(self, position, groups, obstacle_sprites, create_attack, destroy_attack,
                 create_magic, destroy_magic=False):

        # add the tile to the group it belongs
        super().__init__(groups)

        # use the player image
        self.image = pygame.image.load(
            "../graphics/test/player.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=position)

        # setup graphics
        self.import_player_assets()

        # status for the animation
        self.status = "down"

        # hitbox (same logic as tile)
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET["player"])

        # * STATS
        self.stats = {"health": 100, "energy": 60,
                      "attack": 10, "magic": 4, "speed": 6}

        # max_stats
        self.max_stats = {"health":300, "energy":140, "attack":20, "magic":10, "speed":10}

        # upgrade costs (in EXP)
        self.upgrade_cost = {"health":100, "energy":100, "attack":100, "magic": 100, "speed":100}
        # current health and energy
        self.health = self.stats["health"] * 0.5
        self.energy = self.stats["energy"] * 0.8
        # current experience and speed
        self.exp = 500
        # set the player's speed
        self.speed = self.stats["speed"]

        # * Damage TIMER
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 500

        # * ATTACKING ATTRIBUTES
        # check if an attack has started
        self.attacking = False
        # cooldown until the next attack in milliseconds
        self.attack_cooldown = 400
        # time that has passed since the attack
        self.attack_time = None

        # pass the obstacles for the collision
        self.obstacle_sprites = obstacle_sprites

        # * WEAPON

        # ability to create a weapon, taken from level.py
        self.create_attack = create_attack
        # know which weapon was selected
        self.weapon_index = 0
        # name of the weapon
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        # ability to destroy a weapon, taken from level.py
        self.destroy_attack = destroy_attack

        # timer for weapon switch
        self.can_switch_weapon = True
        self.weapon_switch_time = None

        self.switch_duration_cooldown = 200

        # * MAGIC
        # same as weapon
        self.create_magic = create_magic
        self.destroy_magic = destroy_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = None

        # sounds
        self.weapon_attack_sound = pygame.mixer.Sound("../audio/sword.wav")
        self.weapon_attack_sound.set_volume(0.4)

    def import_player_assets(self):

        # get all the animations
        character_path = "../graphics/player/"

        self.animations = {"up": [], "down": [],
                           "left": [], "right": [], "right_idle": [], "left_idle": [], "up_idle": [], "down_idle": [],
                           "right_attack": [], "left_attack": [], "up_attack": [], "down_attack": [], }

        # grab the sprites for animations from the matching folder using our method
        for animation in self.animations.keys():
            fullpath = character_path + animation
            self.animations[animation] = import_folder(fullpath)

    def input(self):

        #  * MOVEMENT INPUT

        if not self.attacking:

            # get all the pressed keys, and after that change the status accordingly
            keys = pygame.key.get_pressed()

            # check if the up key if pressed
            if (keys[pygame.K_UP]):
                self.direction.y = -1
                self.status = "up"

            # check if the down key if pressed
            elif (keys[pygame.K_DOWN]):
                self.direction.y = 1
                self.status = "down"

            # reset if neither key is pressed
            else:
                self.direction.y = 0

            # check if the right key if pressed
            if (keys[pygame.K_RIGHT]):
                self.direction.x = 1
                self.status = "right"

            # check if the left key if pressed
            elif (keys[pygame.K_LEFT]):
                self.direction.x = -1
                self.status = "left"

            # reset if neither key is pressed
            else:
                self.direction.x = 0

            # * ATTACK INPUT
            if (keys[pygame.K_SPACE]):
                # start the attack aand set the time it has been started
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()
                self.weapon_attack_sound.play()

            # * MAGIC INPUT
            if (keys[pygame.K_LCTRL]):
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                style = list(magic_data.keys())[self.magic_index]
                strength = list(magic_data.values())[self.magic_index]['strength'] + self.stats['magic']
                cost = list(magic_data.values())[self.magic_index]['cost']
                self.create_magic(style, strength, cost)

            # * SWITCH WEAPON
            if (keys[pygame.K_q]) and self.can_switch_weapon:
                # switch the weapon aand set the time it has been started
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()
                self.weapon_index = (
                                            self.weapon_index + 1) % len(weapon_data.keys())
                self.weapon = list(weapon_data.keys())[self.weapon_index]  # * SWITCH WEAPON

            # * SWITCH MAGIC

            if (keys[pygame.K_p]) and self.can_switch_magic:
                # switch the magic aand set the time it has been started
                self.can_switch_magic = False
                self.magic_switch_time = pygame.time.get_ticks()
                self.magic_index = (
                                           self.magic_index + 1) % len(magic_data.keys())
                self.magic = list(weapon_data.keys())[self.magic_index]

        else:
            self.direction.x = 0
            self.direction.y = 0

    def get_status(self):
        # get the status of the player and set self.status in order for the matching animation to be played

        # * IDLE ANIMATION

        # since idle comes after a direction was occuring, for example up then up_idle, we add _idle to the current status, if we're not currently idle :

        if self.direction.x == 0 and self.direction.y == 0:
            if "idle" not in self.status and "attack" not in self.status:
                self.status = self.status + "_idle"

            # * ATTACK ANIMATION

            # prevent the player from moving while attacking and for aniamtion handle it just like the idle one :
            if self.attacking:
                self.direction.x = 0
                self.direction.y = 0
                if "attack" not in self.status:
                    if "idle" in self.status:
                        # remove idle
                        self.status = self.status.replace("_idle", "_attack")
                    else:
                        self.status = self.status + "_attack"
            else:
                if "attack" in self.status:
                    self.status = self.status.replace("_attack", "_idle")

    def cooldowns(self):

        # get the current time
        current_time = pygame.time.get_ticks()

        # check if an attack has been done and the cooldown has passed, then get self.attacking to False again
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]["cooldown"]:
                self.attacking = False
                self.destroy_attack()

        # check if weapon has been switched and the cooldown has passed, then get self.can_switch_weapon to True again
        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

        # check if magic has been switched and the cooldown has passed, then get self.can_switch_magic to True again
        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
                self.can_switch_magic = True

        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True

    def animate(self):
        # get all the images for the current animation according to the current status
        animation = self.animations[self.status]

        # loop over the frame index to get the image to display
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            # go back to the first frame when the loop is complete
            self.frame_index = 0

        # set the image, then the rect
        self.image = animation[int(self.frame_index)]
        # change the rect (because not all images have the same size)
        self.rect = self.image.get_rect(center=self.hitbox.center)

        # flicker if the player has been hit
        if not self.vulnerable:
            alpha = self.flicker_value()
            # when alpha = 255, the player is displayed
            # when alpha = 0, nothing appears
            # thus creating a flickering effect
            self.image.set_alpha(alpha)
        else:
            # get back to its state
            self.image.set_alpha(255)

    def get_full_weapon_damage(self):
        # return the full damage of the player, their attack + weapon's attack
        base_damage = self.stats["attack"]
        weapon_damage = weapon_data[self.weapon]["damage"]

        return base_damage + weapon_damage

    def get_full_magic_damage(self):
        # return the full damage of the player, their attack + magic's attack
        base_damage = self.stats["magic"]
        if self.magic == "sword":
            self.magic = "flame"
        magic_damage = magic_data[self.magic]["strength"]

        return base_damage + magic_damage

    def get_value_by_index(self, index):
        return list(self.stats.values())[index]

    def get_cost_by_index(self, index):
        return list(self.upgrade_cost.values())[index]

    def energy_recovery(self):
        # recover energy gradually
        if self.energy < self.stats["energy"]:
            self.energy += 0.005 * self.stats["magic"]
        else:
            self.energy = self.stats["energy"]

    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.stats["speed"])
        self.energy_recovery()
