import pygame as pg
import threading
import time

from src.scenes.scene import Scene
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.core.services import sound_manager, scene_manager, input_manager
from src.interface.components import Button
from src.sprites import BackgroundSprite
from src.sprites import Sprite
from typing import override
from src.utils.definition import Monster, Item

class BattleScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Sprite

    attack_button: Button
    run_button: Button
    items_button: Button
    heal_potion_button: Button
    strength_potion_button: Button
    defense_potion_button: Button
    evolve_button: Button


    
    def __init__(self, game_manager: GameManager):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background2.png")
        
        self.game_manager = game_manager
        
        # Online Manager
        if GameSettings.IS_ONLINE:
            self.online_manager = OnlineManager()
        else:
            self.online_manager = None
        self.sprite_online = Sprite("ingame_ui/options1.png", (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
        

        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT * 3 // 4
        
        self.font = pg.font.Font("assets/fonts/Pokemon Solid.ttf", 28)
        
        self.white_overlay = pg.Surface((360, 100))
        self.pokemon = self.game_manager.bag._monsters_data[0]
        self.pokemon_pic = pg.image.load(f"assets/images/{self.pokemon['sprite_path']}")
        self.pokemon_pic = pg.transform.scale(self.pokemon_pic, (150, 150))
        self.pokemon_name = self.font.render(f"{self.pokemon['name']}", True, (0, 0, 0))
        self.pokemon_level = self.font.render(f"Lv {self.pokemon['level']}", True, (0, 0, 0))
        self.pokemon_hp = self.font.render(f"HP: {self.pokemon['hp']}/{self.pokemon['max_hp']}", True, (0, 0, 0))
        self.pokemon_max_blood = pg.image.load("assets/images/UI/raw/UI_Flat_BarFill01c.png")
        self.pokemon_max_blood = pg.transform.scale(self.pokemon_max_blood, (200, 20))
        self.pokemon_current_blood_img = pg.image.load("assets/images/UI/raw/UI_Flat_BarFill01a.png")
        self.pokemon_current_blood_img = pg.transform.scale(self.pokemon_current_blood_img, (200, 20))
        self.pokemon_current_blood = pg.transform.scale(self.pokemon_current_blood_img, (200 * self.pokemon["hp"] // self.pokemon["max_hp"], 20))
        self.pokemon_element = self.font.render(f"({self.pokemon['elements']})", True, (0, 0, 0))


        self.enemy_pokemon = self.game_manager.bag._monsters_data[3]
        self.enemy_pic = pg.image.load(f"assets/images/{self.enemy_pokemon['sprite_path']}")
        self.enemy_pic = pg.transform.scale(self.enemy_pic, (150, 150))
        self.enemy_name = self.font.render(f"{self.enemy_pokemon['name']}", True, (0, 0, 0))
        self.enemy_level = self.font.render(f"Lv {self.enemy_pokemon['level']}", True, (0, 0, 0))
        self.enemy_pokemon["hp"] = self.enemy_pokemon["max_hp"]
        self.enemy_hp = self.font.render(f"HP: {self.enemy_pokemon['hp']}/{self.enemy_pokemon['max_hp']}", True, (0, 0, 0))
        self.enemy_max_blood = pg.image.load("assets/images/UI/raw/UI_Flat_BarFill01c.png")
        self.enemy_max_blood = pg.transform.scale(self.enemy_max_blood, (200, 20))
        self.enemy_current_blood_img = pg.image.load("assets/images/UI/raw/UI_Flat_BarFill01a.png")
        self.enemy_current_blood_img = pg.transform.scale(self.enemy_current_blood_img, (200, 20))
        self.enemy_current_blood = pg.transform.scale(self.enemy_current_blood_img, (200 * self.enemy_pokemon["hp"] // self.enemy_pokemon["max_hp"], 20))
        self.enemy_element = self.font.render(f"({self.enemy_pokemon['elements']})", True, (0, 0, 0))


        self.message_system = MessageSystem(
            self.font,
            pg.Rect(0, GameSettings.SCREEN_HEIGHT * 5 // 6, GameSettings.SCREEN_WIDTH, 120),
            duration_per_message = 200,
            auto_advance = False,
            require_key_after_duration = True
            )

        self.turn = True
        self.use_potion = False
        self.add_atk = 0
        self.add_def = 0

        self.can_evolve = True
        

        self.attack_button = Button(
            "ingame_ui/options5.png", "ingame_ui/options5.png",
            px - 400, 600, 80, 80,
            lambda: self.attack(self.pokemon, self.enemy_pokemon)
            )

        self.items_button = Button(
            "UI/button_backpack_hover.png", "UI/button_backpack_hover.png",
            px - 100, 600, 80, 80,
            lambda: self.use_items()
            )
        
        self.run_button = Button(
            "ingame_ui/baricon1.png", "ingame_ui/baricon1.png",
            px + 200, 600, 80, 80,
            lambda: self.run(self.pokemon)
            )
        
        self.heal_potion_button = Button(
            "ingame_ui/potion.png", "ingame_ui/potion.png",
            px - 400, 600, 80, 80,
            lambda: self.heal(self.pokemon)
            )

        self.strength_potion_button = Button(
            "ingame_ui/options1.png", "ingame_ui/options1.png",
            px - 100, 600, 80, 80,
            lambda: self.increase_strength(self.pokemon)
            )
        
        self.defense_potion_button = Button(
            "ingame_ui/options2.png", "ingame_ui/options2.png",
            px + 200, 600, 80, 80,
            lambda: self.increase_defense(self.pokemon)
            )
        
        self.evolve_button = Button(
            "UI/raw/UI_Flat_ButtonArrow01a.png", "UI/raw/UI_Flat_ButtonArrow01a.png",
            px + 500, 600, 80, 80,
            lambda: self.evolve(self.pokemon)
            )


    def attack(self, attacker, defender):
        damage = 30 + self.add_atk
        if (attacker["elements"] == "Fire" and defender["elements"] == "Grass") or (attacker["elements"] == "Grass" and defender["elements"] == "Water") or (attacker["elements"] == "Water" and defender["elements"] == "Fire"):
            damage = int(damage * 1.5)
            defender["hp"] = max(0, defender["hp"] - damage)
            messages = [
                f"{attacker['name']} attacked!",
                "very effective!",
                f"{defender['name']} lost {damage} HP!"
                ]
        else:
            defender["hp"] = max(0, defender["hp"] - damage)
            messages = [
                f"{attacker['name']} attacked!",
                f"{defender['name']} lost {damage} HP!"
                ]

        if defender["hp"] <= 0:
            messages.append(f"{defender['name']} fainted!")
            self.message_system.show_messages(messages)
            self.defer_scene_change = True
        else:    
            self.message_system.show_messages(messages)
            self.turn = False

    
    def enemy_turn(self):
        attacker = self.enemy_pokemon
        defender = self.pokemon

        damage = 10 - self.add_def
        if (attacker["elements"] == "Fire" and defender["elements"] == "Grass") or (attacker["elements"] == "Grass" and defender["elements"] == "Water") or (attacker["elements"] == "Water" and defender["elements"] == "Fire"):
            damage = int(damage * 1.5)
            defender["hp"] = max(0, defender["hp"] - damage)
            messages = [
                f"{attacker['name']} attacked!",
                "very effective!",
                f"{defender['name']} lost {damage} HP!"
                ]
        else:
            defender["hp"] = max(0, defender["hp"] - damage)
            messages = [
                f"{attacker['name']} attacked!",
                f"{defender['name']} lost {damage} HP!"
                ]
        
        if defender["hp"] <= 0:
            messages.append(f"{defender['name']} fainted!")
            self.message_system.show_messages(messages)
            self.defer_scene_change = True
        else:
            self.message_system.show_messages(messages)
            self.turn = True  


    def run(self, attacker):
        messages = [f"{attacker["name"]} ran away!"]
        self.message_system.show_messages(messages)
        self.defer_scene_change = True


    def use_items(self):
        self.use_potion = True

    def heal(self, pokemon):
        pokemon['hp'] = min(pokemon['max_hp'], pokemon['hp'] + 20)
        messages = [f"{pokemon['name']} uses heal potion!"]
        self.game_manager.bag._items_data[0]["count"] -= 1
        self.message_system.show_messages(messages)
        self.use_potion = False
        self.turn = False
    
    def increase_strength(self, pokemon):
        self.add_atk += 20
        messages = [f"{pokemon['name']} uses strength potion!"]
        self.game_manager.bag._items_data[1]["count"] -= 1
        self.message_system.show_messages(messages)
        self.use_potion = False
        self.turn = False

    def increase_defense(self, pokemon):
        self.add_def += 2
        messages = [f"{pokemon['name']} uses defense potion!"]
        self.game_manager.bag._items_data[2]["count"] -= 1
        self.message_system.show_messages(messages)
        self.use_potion = False
        self.turn = False

    def evolve(self, pokemon):
        messages = [f"{pokemon["name"]} evolves!"]
        if pokemon["name"] == "Pikachu":
            self.pokemon = {"name": "Raichu", "hp": pokemon["hp"] + 60, "max_hp": 160, "level": pokemon["level"],
                "sprite_path": "menu_sprites/menusprite3.png", "elements": pokemon["elements"]}
            self.game_manager.bag._monsters_data[0] = self.pokemon
        self.message_system.show_messages(messages)
        self.can_evolve = False
        self.turn = False



    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 103 Pallet Town.ogg")
        if self.online_manager:
            self.online_manager.enter()        


    @override
    def exit(self) -> None:
        if self.online_manager:
            self.online_manager.exit()
        
    @override
    def update(self, dt: float):
        # Check if there is assigned next scene
        self.game_manager.try_switch_map()
        
        # Update player and other data
        if self.game_manager.player:
            self.game_manager.player.update(dt)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.update(dt)

        if self.turn and not self.message_system.is_showing():
            if not self.use_potion:
                self.attack_button.update(dt)
                self.items_button.update(dt)
                self.run_button.update(dt)
                if self.can_evolve and self.pokemon["name"] != "Raichu":
                    self.evolve_button.update(dt)
            else:
                self.heal_potion_button.update(dt)
                self.strength_potion_button.update(dt)
                self.defense_potion_button.update(dt)

        self.message_system.update()

        if not self.message_system.is_showing() and not self.turn:
            self.enemy_turn()

        self.pokemon = self.game_manager.bag._monsters_data[0]
        self.pokemon_pic = pg.image.load(f"assets/images/{self.pokemon['sprite_path']}")
        self.pokemon_pic = pg.transform.scale(self.pokemon_pic, (150, 150))
        self.pokemon_name = self.font.render(f"{self.pokemon['name']}", True, (0, 0, 0))
        self.pokemon_level = self.font.render(f"Lv {self.pokemon['level']}", True, (0, 0, 0))
        
        self.pokemon_hp = self.font.render(f"HP: {self.pokemon['hp']}/{self.pokemon['max_hp']}", True, (0, 0, 0))
        self.pokemon_current_blood = pg.transform.scale(
            self.pokemon_current_blood_img,
            (200 * self.pokemon["hp"] // self.pokemon["max_hp"], 20)
            )   

        self.enemy_hp = self.font.render(f"HP: {self.enemy_pokemon['hp']}/{self.enemy_pokemon['max_hp']}", True, (0, 0, 0))
        self.enemy_current_blood = pg.transform.scale(
            self.enemy_current_blood_img,
            (200 * self.enemy_pokemon["hp"] // self.enemy_pokemon["max_hp"], 20)
            )
            
        
        if hasattr(self, "defer_scene_change") and self.defer_scene_change:
            if not self.message_system.is_showing():
                scene_manager.change_scene("game")
                self.defer_scene_change = False

        self.game_manager.bag.update(dt)
        
        if self.game_manager.player is not None and self.online_manager is not None:
            _ = self.online_manager.update(
                self.game_manager.player.position.x, 
                self.game_manager.player.position.y,
                self.game_manager.current_map.path_name
            )

    
        
    @override
    def draw(self, screen: pg.Surface):        
        self.background.draw(screen)
        screen.blit(self.pokemon_pic, (400, 350))
        self.white_overlay.fill((255, 255, 255))
        screen.blit(self.white_overlay, (50, 400))
        screen.blit(self.pokemon_name, (70, 410))
        screen.blit(self.pokemon_level, (200, 410))
        screen.blit(self.pokemon_hp, (70, 450))
        screen.blit(self.pokemon_max_blood, (70, 480))
        screen.blit(self.pokemon_current_blood, (70, 480))
        screen.blit(self.pokemon_element, (300, 410))

        screen.blit(self.enemy_pic, (750, 50))
        self.white_overlay.fill((255, 255, 255))
        screen.blit(self.white_overlay, (900, 100))
        screen.blit(self.enemy_name, (920, 110))
        screen.blit(self.enemy_level, (1050, 110))
        screen.blit(self.enemy_hp, (920, 150))
        screen.blit(self.enemy_max_blood, (920, 180))
        screen.blit(self.enemy_current_blood, (920, 180))
        screen.blit(self.enemy_element, (1150, 110))

            
        if self.turn:
            if not self.use_potion:    
                self.attack_button.draw(screen)
                self.items_button.draw(screen)
                self.run_button.draw(screen)
                if self.can_evolve and self.pokemon["name"] != "Raichu":
                    self.evolve_button.draw(screen)
            else:
                self.heal_potion_button.draw(screen)
                self.strength_potion_button.draw(screen)
                self.defense_potion_button.draw(screen)
        
        self.message_system.draw(screen)


        
            


class MessageSystem:
    def __init__(self, font: pg.font.Font, box_rect: pg.Rect, advance_keys = None,
                 duration_per_message = 500, auto_advance = False, require_key_after_duration = True):
        self.font = font
        self.box_rect = box_rect
        self.messages = []
        self.current_message = None
        self.visible = False
        self.duration_per_message = duration_per_message
        self.auto_advance = auto_advance
        self.require_key_after_duration = require_key_after_duration

        self.message_start_time = 0

        self.advance_keys = advance_keys or [pg.K_SPACE]

        self.text_color = (255, 255, 255)
        self.box_color = (0, 0, 0)
        self.box_surface = pg.Surface((box_rect.width, box_rect.height))

    def show_messages(self, messages: list[str]):
        self.messages = messages
        self.current_message = self.messages.pop(0)
        self.visible = True
        self.message_start_time = pg.time.get_ticks()

    def update(self):
        if not self.visible:
            return

        elapsed = pg.time.get_ticks() - self.message_start_time
        allow_key = (not self.require_key_after_duration) or (elapsed >= self.duration_per_message)


        keys = pg.key.get_pressed()
        if allow_key and any(keys[k] for k in self.advance_keys):
            if self.messages:
                self.current_message = self.messages.pop(0)
                self.message_start_time = pg.time.get_ticks()
            else:
                self.visible = False
                self.current_message = None
                return
            
        if self.auto_advance and elapsed >= self.duration_per_message:
            if self.messages:
                self.current_message = self.messages.pop(0)
                self.message_start_time = pg.time.get_ticks()
            else:
                self.visible = False
                self.current_message = None

    def draw(self, screen: pg.Surface):
        if not self.visible:
            return
        
        self.box_surface.fill(self.box_color)
        screen.blit(self.box_surface, (self.box_rect.x, self.box_rect.y))

        text_surface = self.font.render(self.current_message, True, self.text_color)
        screen.blit(text_surface, (self.box_rect.x + 20,
                                   self.box_rect.y + 20))

    def is_showing(self):
        return self.visible