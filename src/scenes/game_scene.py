import pygame as pg
import threading
import time

from src.scenes.scene import Scene
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.core.services import sound_manager, scene_manager, input_manager
from src.interface.components import Button, Slider
from src.sprites import Sprite
from typing import override, Dict, Tuple
from src.interface.components.chat_overlay import ChatOverlay
from src.maps.map import MiniMap
from src.maps.navigation import Navigation



class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Sprite

    setting_button: Button
    backpack_button: Button
    setting_back_button: Button
    backpack_back_button: Button
    save_button: Button
    load_button: Button
    mute_button: Button
    volume_slider: Slider
    buy_ui_button: Button
    sell_ui_button: Button
    buy_heal_potion_button: Button
    buy_strength_potion_button: Button
    buy_defense_potion_button: Button
    buy_ball_button: Button
    sell_heal_potion_button: Button
    sell_strength_potion_button: Button
    sell_defense_potion_button: Button
    sell_ball_button: Button
    navigation_button: Button
    navigate_gym_button: Button
    navigate_start_button: Button

    
    def __init__(self, game_manager: GameManager):
        super().__init__()
        
        self.game_manager = game_manager
        
        # Online Manager
        if GameSettings.IS_ONLINE:
            self.online_manager = OnlineManager()
            #self.chat_overlay = ChatOverlay(
            #     send_callback=..., <- send chat method
            #     get_messages=..., <- get chat messages method
            # )
        else:
            self.online_manager = None
        self.sprite_online = Sprite("ingame_ui/options1.png", (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
        self._chat_bubbles: Dict[int, Tuple[str, str]] = {}
        self._last_chat_id_seen = 0

        self.overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)

        self.setting_screen = pg.image.load("assets/images/UI/raw/UI_Flat_Frame01a.png")
        self.setting_screen = pg.transform.scale(self.setting_screen, (800, 600))
        self.backpack_screen = pg.image.load("assets/images/UI/raw/UI_Flat_Frame02a.png")
        self.backpack_screen = pg.transform.scale(self.backpack_screen, (800, 600))
        self.volume_slider_background = pg.image.load("assets/images/UI/raw/UI_Flat_BarFill01f.png")
        self.volume_slider_background = pg.transform.scale(self.volume_slider_background, (720, 36))
        self.shop_screen = pg.image.load("assets/images/UI/raw/UI_Flat_Frame03a.png")
        self.shop_screen = pg.transform.scale(self.shop_screen, (800, 600))
        self.navigate_screen = pg.image.load("assets/images/UI/raw/UI_Flat_Frame03a.png")
        self.navigate_screen = pg.transform.scale(self.navigate_screen, (800, 600))


        self.minimap = MiniMap(self.game_manager.current_map.path_name, scale = 0.06)
        self.navigator = Navigation(self.game_manager, GameSettings.TILE_SIZE)

        self.active_ui = None
        self.sound_mute = True
        self.volume = 0.5

        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT * 3 // 4
        
        self.setting_button = Button(
            "UI/button_setting.png", "UI/button_setting_hover.png",
            10, 10, 100, 100,
            lambda: self.open_ui("setting")
            )
        
        self.backpack_button = Button(
            "UI/button_backpack.png", "UI/button_backpack_hover.png",
            120, 10, 100, 100,
            lambda: self.open_ui("backpack")
            )
        
        self.setting_back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            px - 60, py, 80, 80,
            lambda: self.open_ui(None)
            )
        
        self.backpack_back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            px - 60, py, 80, 80,
            lambda: self.open_ui(None)
            )
        
        self.shop_back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            px - 60, py, 80, 80,
            lambda: self.open_ui(None)
            )
        
        self.save_button = Button(
            "UI/button_save.png", "UI/button_save_hover.png",
            px - 260, py - 20, 100, 100,
            lambda: self.game_manager.save("saves/test.json")
            )
        
        self.load_button = Button(
            "UI/button_load.png", "UI/button_load_hover.png",
            px + 140, py - 20, 100, 100,
            lambda: self.game_load("saves/test.json")
            )
        
        self.mute_button = Button(
            "UI/raw/UI_Flat_IconCross01a.png", "UI/raw/UI_Flat_IconCross01a.png",
            px - 45, py - 150, 90, 60,
            lambda: self.mute()
            )
        
        self.volume_slider = Slider(
            "UI/raw/UI_Flat_ToggleLeftOn01a.png",
            px + 360 - 36, 300, 36, 36,
            lambda: self.sound_change()
            )
        
        self.buy_ui_button = Button(
            "UI/raw/UI_Flat_Button02a_4.png", "UI/raw/UI_Flat_Button02a_1.png",
            px - 200, 100, 150, 60,
            lambda: self.open_ui("shop_buy")
            )
        
        self.sell_ui_button = Button(
            "UI/raw/UI_Flat_Button02a_4.png", "UI/raw/UI_Flat_Button02a_1.png",
            px + 50, 100, 150, 60,
            lambda: self.open_ui("shop_sell")
            )
        
        self.buy_heal_potion_button = Button(
            "UI/button_shop.png", "UI/button_shop_hover.png",
            550, 200, 50, 50,
            lambda: self.buy("Heal_potion")
            )
        
        self.buy_strength_potion_button = Button(
            "UI/button_shop.png", "UI/button_shop_hover.png",
            550, 260, 50, 50,
            lambda: self.buy("Strength_potion")
            )
        
        self.buy_defense_potion_button = Button(
            "UI/button_shop.png", "UI/button_shop_hover.png",
            550, 320, 50, 50,
            lambda: self.buy("Defense_potion")
            )
        
        self.buy_ball_button = Button(
            "UI/button_shop.png", "UI/button_shop_hover.png",
            550, 380, 50, 50,
            lambda: self.buy("Pokeball")
            )
        
        self.sell_heal_potion_button = Button(
            "UI/button_shop.png", "UI/button_shop_hover.png",
            550, 200, 50, 50,
            lambda: self.sell("Heal_potion")
            )
        
        self.sell_strength_potion_button = Button(
            "UI/button_shop.png", "UI/button_shop_hover.png",
            550, 260, 50, 50,
            lambda: self.sell("Strength_potion")
            )
        
        self.sell_defense_potion_button = Button(
            "UI/button_shop.png", "UI/button_shop_hover.png",
            550, 320, 50, 50,
            lambda: self.sell("Defense_potion")
            )
        
        self.sell_ball_button = Button(
            "UI/button_shop.png", "UI/button_shop_hover.png",
            550, 380, 50, 50,
            lambda: self.sell("Pokeball")
            )
        
        self.navigation_button = Button(
            "UI/button_play.png", "UI/button_play_hover.png",
            230, 10, 100, 100,
            lambda: self.open_ui("navigation")
            )
        
        self.navigate_gym_button = Button(
            "UI/button_play.png", "UI/button_play_hover.png",
            360, 200, 80, 80,
            lambda: self.nav_to("gym")
            )
        
        self.navigate_start_button = Button(
            "UI/button_play.png", "UI/button_play_hover.png",
            480, 200, 80, 80,
            lambda: self.nav_to("start")
            )
        
        font = pg.font.Font("assets/fonts/Pokemon Solid.ttf", 36)
        self.text_mute = font.render("Mute", True, (0, 0, 0))
        self.text_volume = font.render("Volume", True, (0, 0, 0))
        self.text_settings = pg.font.Font("assets/fonts/Pokemon Solid.ttf", 48).render("Settings", True, (0, 0, 0))
        self.text_buy = font.render("BUY", True, (0, 0, 0))
        self.text_sell = font.render("SELL", True, (0, 0, 0))
        self.text_heal_potion = pg.font.Font("assets/fonts/Pokemon Solid.ttf", 32).render("Heal", True, (0, 0, 0))
        self.text_str_potion = pg.font.Font("assets/fonts/Pokemon Solid.ttf", 32).render("Strength", True, (0, 0, 0))
        self.text_def_potion = pg.font.Font("assets/fonts/Pokemon Solid.ttf", 32).render("Defense", True, (0, 0, 0))
        self.text_Pokeball = pg.font.Font("assets/fonts/Pokemon Solid.ttf", 32).render("Pokeball", True, (0, 0, 0))
        self.text_buy_stuff = pg.font.Font("assets/fonts/Pokemon Solid.ttf", 28).render("-$10", True, (0, 0, 0))
        self.text_sell_stuff = pg.font.Font("assets/fonts/Pokemon Solid.ttf", 28).render("+$10", True, (0, 0, 0))
        self.text_navigation = font.render("Navigate To :", True, (0, 0, 0))
        self.text_navigate_gym = pg.font.Font("assets/fonts/Pokemon Solid.ttf", 28).render("GYM", True, (0, 0, 0))
        self.text_navigate_start = pg.font.Font("assets/fonts/Pokemon Solid.ttf", 28).render("START", True, (0, 0, 0))


    def buy(self, item: str):
        items = self.game_manager.bag._items_data
        for i, data in enumerate(items):
            if data["name"] == "Coins":
                if data["count"] >= 10:
                    data["count"] -= 10
                else:
                    return
                
        for i, data in enumerate(items):
            if data["name"] == item:
                data["count"] += 1

    def sell(self, item: str):
        items = self.game_manager.bag._items_data
        for i, data in enumerate(items):
            if data["name"] == item:
                if data["count"] > 0:
                    data["count"] -= 1
                else:
                    return
                
        for i, data in enumerate(items):
            if data["name"] == "Coins":
                data["count"] += 10

    def game_load(self, path: str):
        new_manager = GameManager.load(path)
        if new_manager:
            self.game_manager.__dict__.update(new_manager.__dict__)
            self.minimap = MiniMap(self.game_manager.current_map.path_name, scale=0.06)

    def open_ui(self, scene_name: str):
        self.active_ui = scene_name

    def mute(self):
        self.sound_mute = not self.sound_mute

    def sound_change(self):
        mx = self.volume_slider.hitbox.x
        self.volume = (mx - (GameSettings.SCREEN_WIDTH / 2 - 360)) / 720
        sound_manager.set_music_volume(self.volume)

    def nav_to(self, destination: str):
        if destination == "gym":
            self.navigator.navigate_to((24, 24))
        elif destination == "start":
            self.navigator.navigate_to((16, 30))
        self.open_ui(None)


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

        old_map = self.minimap.path_name
        new_map = self.game_manager.current_map.path_name

        if old_map != new_map:
            self.minimap.update(new_map)

        self.navigator.update(dt)

        self.setting_button.update(dt)
        self.backpack_button.update(dt)
        self.setting_back_button.update(dt)
        self.backpack_back_button.update(dt)
        self.save_button.update(dt)
        self.load_button.update(dt)
        self.mute_button.update(dt)
        self.volume_slider.update(dt)
        self.buy_ui_button.update(dt)
        self.sell_ui_button.update(dt)
        self.navigation_button.update(dt)
        
        
        if self.active_ui is not None:
            self.overlay.fill((0, 0, 0, 128))
            if self.active_ui == "shop_buy":
                self.buy_heal_potion_button.update(dt)
                self.buy_strength_potion_button.update(dt)
                self.buy_defense_potion_button.update(dt)
                self.buy_ball_button.update(dt)

            if self.active_ui == "shop_sell":
                self.sell_heal_potion_button.update(dt)
                self.sell_strength_potion_button.update(dt)
                self.sell_defense_potion_button.update(dt)
                self.sell_ball_button.update(dt)

            if self.active_ui == "navigation":
                self.navigate_gym_button.update(dt)
                self.navigate_start_button.update(dt)

        
        if self.sound_mute:
            sound_manager.resume_all()
            self.sound_change()
            self.mute_button.img_button = Sprite("UI/raw/UI_Flat_IconCross01a.png", (90, 60))
        else:
            sound_manager.pause_all()
            sound_manager.set_music_volume(0)
            self.mute_button.img_button = Sprite("UI/raw/UI_Flat_IconCheck01a.png", (90, 60))

        # Update others
        self.game_manager.bag.update(dt)


        """
        TODO: UPDATE CHAT OVERLAY:
        # if self._chat_overlay:
        #     if _____.key_pressed(...):
        #         self._chat_overlay.____
        #     self._chat_overlay.update(____)
        # Update chat bubbles from recent messages
        # This part's for the chatting feature, we've made it for you.
        # if self.online_manager:
        #     try:
        #         msgs = self.online_manager.get_recent_chat(50)
        #         max_id = self._last_chat_id_seen
        #         now = time.monotonic()
        #         for m in msgs:
        #             mid = int(m.get("id", 0))
        #             if mid <= self._last_chat_id_seen:
        #                 continue
        #             sender = int(m.get("from", -1))
        #             text = str(m.get("text", ""))
        #             if sender >= 0 and text:
        #                 self._chat_bubbles[sender] = (text, now + 5.0)
        #             if mid > max_id:
        #                 max_id = mid
        #         self._last_chat_id_seen = max_id
        #     except Exception:
        #         pass
        """
        
        if self.game_manager.player is not None and self.online_manager is not None:
            _ = self.online_manager.update(
                self.game_manager.player.position.x, 
                self.game_manager.player.position.y,
                self.game_manager.current_map.path_name
            )
        
    @override
    def draw(self, screen: pg.Surface):        
        if self.game_manager.player:
            
            camera = self.game_manager.player.camera
            self.game_manager.current_map.draw(screen, camera)
            self.game_manager.player.draw(screen, camera)
            
        else:
            camera = PositionCamera(0, 0)
            self.game_manager.current_map.draw(screen, camera)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)

        # if self._chat_overlay:
        #     self._chat_overlay.draw(screen)

        
        if self.online_manager and self.game_manager.player:
            list_online = self.online_manager.get_list_players()
            for player in list_online:
                if player["map"] == self.game_manager.current_map.path_name:
                    cam = self.game_manager.player.camera
                    pos = cam.transform_position_as_position(Position(player["x"], player["y"]))
                    self.sprite_online.update_pos(pos)
                    self.sprite_online.draw(screen)
                # try:
                #     self._draw_chat_bubbles(...)
                # except Exception:
                #     pass

        self.minimap.draw(screen, self.game_manager.player.position)

        if self.active_ui == "setting":
            screen.blit(self.overlay, (0, 0))
            screen.blit(self.setting_screen, (GameSettings.SCREEN_WIDTH / 2 - 400, GameSettings.SCREEN_HEIGHT / 2 - 300))
            self.setting_back_button.draw(screen)
            self.save_button.draw(screen)
            self.load_button.draw(screen)
            self.mute_button.draw(screen)
            screen.blit(self.volume_slider_background, (GameSettings.SCREEN_WIDTH / 2 - 360, 300))
            self.volume_slider.draw(screen)
            screen.blit(self.text_mute, (GameSettings.SCREEN_WIDTH / 2 - 180, 400))
            screen.blit(self.text_volume, (GameSettings.SCREEN_WIDTH / 2 - 70, 240))
            screen.blit(self.text_settings, (GameSettings.SCREEN_WIDTH / 2 - 100, 100))

        if self.active_ui == "backpack":
            screen.blit(self.overlay, (0, 0))
            screen.blit(self.backpack_screen, (GameSettings.SCREEN_WIDTH / 2 - 400, GameSettings.SCREEN_HEIGHT / 2 - 300))
            self.backpack_back_button.draw(screen)
            self.game_manager.bag.draw_monsters(screen)
            self.game_manager.bag.draw_items(screen)

        if self.active_ui == "shop_buy":
            screen.blit(self.overlay, (0, 0))
            screen.blit(self.shop_screen, (GameSettings.SCREEN_WIDTH / 2 - 400, GameSettings.SCREEN_HEIGHT / 2 - 300))
            self.buy_ui_button.draw(screen)
            self.sell_ui_button.draw(screen)
            self.shop_back_button.draw(screen)
            screen.blit(self.text_buy, (GameSettings.SCREEN_WIDTH / 2 - 170, 110))
            screen.blit(self.text_sell, (GameSettings.SCREEN_WIDTH / 2 + 80, 110))
            screen.blit(self.text_heal_potion, (360, 200))
            screen.blit(pg.image.load(f"assets/images/ingame_UI/potion.png"), (320, 210))
            screen.blit(self.text_str_potion, (360, 260))
            screen.blit(pg.image.load(f"assets/images/ingame_UI/potion.png"), (320, 270))
            screen.blit(self.text_def_potion, (360, 320))
            screen.blit(pg.image.load(f"assets/images/ingame_UI/potion.png"), (320, 330))
            screen.blit(self.text_Pokeball, (360, 380))
            screen.blit(pg.image.load(f"assets/images/ingame_UI/ball.png"), (320, 390))
            self.buy_heal_potion_button.draw(screen)
            self.buy_strength_potion_button.draw(screen)
            self.buy_defense_potion_button.draw(screen)
            self.buy_ball_button.draw(screen)
            screen.blit(self.text_buy_stuff, (650, 200))
            screen.blit(self.text_buy_stuff, (650, 260))
            screen.blit(self.text_buy_stuff, (650, 320))
            screen.blit(self.text_buy_stuff, (650, 380))

        if self.active_ui == "shop_sell":
            screen.blit(self.overlay, (0, 0))
            screen.blit(self.shop_screen, (GameSettings.SCREEN_WIDTH / 2 - 400, GameSettings.SCREEN_HEIGHT / 2 - 300))
            self.buy_ui_button.draw(screen)
            self.sell_ui_button.draw(screen)
            self.shop_back_button.draw(screen)
            screen.blit(self.text_buy, (GameSettings.SCREEN_WIDTH / 2 - 170, 110))
            screen.blit(self.text_sell, (GameSettings.SCREEN_WIDTH / 2 + 80, 110))
            screen.blit(self.text_heal_potion, (360, 200))
            screen.blit(pg.image.load(f"assets/images/ingame_UI/potion.png"), (320, 210))
            screen.blit(self.text_str_potion, (360, 260))
            screen.blit(pg.image.load(f"assets/images/ingame_UI/potion.png"), (320, 270))
            screen.blit(self.text_def_potion, (360, 320))
            screen.blit(pg.image.load(f"assets/images/ingame_UI/potion.png"), (320, 330))
            screen.blit(self.text_Pokeball, (360, 380))
            screen.blit(pg.image.load(f"assets/images/ingame_UI/ball.png"), (320, 390))
            self.sell_heal_potion_button.draw(screen)
            self.sell_strength_potion_button.draw(screen)
            self.sell_defense_potion_button.draw(screen)
            self.sell_ball_button.draw(screen)
            screen.blit(self.text_sell_stuff, (650, 200))
            screen.blit(self.text_sell_stuff, (650, 260))
            screen.blit(self.text_sell_stuff, (650, 320))
            screen.blit(self.text_sell_stuff, (650, 380))

        if self.active_ui == "navigation":
            screen.blit(self.overlay, (0, 0))
            screen.blit(self.navigate_screen, (GameSettings.SCREEN_WIDTH / 2 - 400, GameSettings.SCREEN_HEIGHT / 2 - 300))
            screen.blit(self.text_navigation, (GameSettings.SCREEN_WIDTH / 2 - 100, 100))
            screen.blit(self.text_navigate_gym, (370, 300))
            screen.blit(self.text_navigate_start, (480, 300))
            self.navigate_gym_button.draw(screen)
            self.navigate_start_button.draw(screen)


        path = self.navigator.get_path()
        if path:
            for (tx, ty) in path:    
                px = tx * GameSettings.TILE_SIZE
                py = ty * GameSettings.TILE_SIZE       
                pos = camera.transform_position_as_position(Position(px, py))

                s = pg.Surface((GameSettings.TILE_SIZE, GameSettings.TILE_SIZE), pg.SRCALPHA)
                s.fill((0, 255, 0, 50))
                screen.blit(s, (pos.x, pos.y))
        
            
        self.setting_button.draw(screen)
        self.backpack_button.draw(screen)
        self.navigation_button.draw(screen)


    def _draw_chat_bubbles(self, screen: pg.Surface, camera: PositionCamera) -> None:

        # if not self.online_manager:
        #     return
        # REMOVE EXPIRED BUBBLES
        # now = time.monotonic()
        # expired = [pid for pid, (_, ts) in self._chat_bubbles.items() if ts <= now]
        # for pid in expired:
        #     self._chat_bubbles.____(..., ...)
        # if not self._chat_bubbles:
        #     return

        # DRAW LOCAL PLAYER'S BUBBLE
        # local_pid = self.____
        # if self.game_manager.player and local_pid in self._chat_bubbles:
        #     text, _ = self._chat_bubbles[...]
        #     self._draw_bubble_for_pos(..., ..., ..., ..., ...)

        # DRAW OTHER PLAYERS' BUBBLES
        # for pid, (text, _) in self._chat_bubbles.items():
        #     if pid == local_pid:
        #         continue
        #     pos_xy = self._online_last_pos.____(..., ...)
        #     if not pos_xy:
        #         continue
        #     px, py = pos_xy
        #     self._draw_bubble_for_pos(..., ..., ..., ..., ...)

        pass
        """
        DRAWING CHAT BUBBLES:
        - When a player sends a chat message, the message should briefly appear above
        that player's character in the world, similar to speech bubbles in RPGs.
        - Each bubble should last only a few seconds before fading or disappearing.
        - Only players currently visible on the map should show bubbles.
         What you need to think about:
            ------------------------------
            1. **Which players currently have messages?**
            You will have a small structure mapping player IDs to the text they sent
            and the time the bubble should disappear.
            2. **How do you know where to place the bubble?**
            The bubble belongs above the player's *current position in the world*.
            The game already tracks each player’s world-space location.
            Convert that into screen-space and draw the bubble there.
            3. **How should bubbles look?**
            You decide. The visual style is up to you:
            - A rounded rectangle, or a simple box.
            - Optional border.
            - A small triangle pointing toward the character's head.
            - Enough padding around the text so it looks readable.
            4. **How do bubbles disappear?**
            Compare the current time to the stored expiration timestamp.
            Remove any bubbles that have expired.
            5. **In what order should bubbles be drawn?**
            Draw them *after* world objects but *before* UI overlays.
        Reminder:
        - For the local player, you can use the self.game_manager.player.position to get the player's position
        - For other players, maybe you can find some way to store other player's last position?
        - For each player with a message, maybe you can call a helper to actually draw a single bubble?
        """

def _draw_chat_bubble_for_pos(self, screen: pg.Surface, camera: PositionCamera, world_pos: Position, text: str, font: pg.font.Font):
    pass
    """
    Steps:
        ------------------
        1. Convert a player’s world position into a location on the screen.
        (Use the camera system provided by the game engine.)
        2. Decide where "above the player" is.
        Typically a little above the sprite’s head.
        3. Measure the rendered text to determine bubble size.
        Add padding around the text.
    """
