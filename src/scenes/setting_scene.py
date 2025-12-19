import pygame as pg

from src.utils import GameSettings
from src.sprites import BackgroundSprite
from src.scenes.scene import Scene
from src.interface.components import Button, Slider
from src.core.services import scene_manager, sound_manager, input_manager
from typing import override
from src.sprites import Sprite

class SettingScene(Scene):
    
    background: BackgroundSprite
    play_back_button: Button
    mute_button: Button
    volume_slider: Slider
    
    
    
    def __init__(self):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")

        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT * 3 // 4
        
        self.play_back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            px - 60, py - 20, 100, 100,
            lambda: scene_manager.change_scene("menu")
        )

        self.setting_screen = pg.image.load("assets/images/UI/raw/UI_Flat_Frame01a.png")
        self.setting_screen = pg.transform.scale(self.setting_screen, (800, 600))
        self.volume_slider_background = pg.image.load("assets/images/UI/raw/UI_Flat_BarFill01f.png")
        self.volume_slider_background = pg.transform.scale(self.volume_slider_background, (720, 36))

        self.sound_mute = True
        self.volume = 0.5

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
        
        font = pg.font.Font("assets/fonts/Pokemon Solid.ttf", 36)
        self.text_mute = font.render("Mute", True, (0, 0, 0))
        self.text_volume = font.render("Volume", True, (0, 0, 0))
        self.text_settings = pg.font.Font("assets/fonts/Pokemon Solid.ttf", 48).render("Settings", True, (0, 0, 0))

    def mute(self):
        self.sound_mute = not self.sound_mute

    def sound_change(self):
        mx = self.volume_slider.hitbox.x
        self.volume = (mx - (GameSettings.SCREEN_WIDTH / 2 - 360)) / 720
        sound_manager.set_music_volume(self.volume)

    
    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 101 Opening (Part 1).ogg")
        pass

    @override
    def exit(self) -> None:
        pass

    @override
    def update(self, dt: float) -> None:
        if input_manager.key_pressed(pg.K_SPACE):
            scene_manager.change_scene("menu")
            return
        self.play_back_button.update(dt)
        self.mute_button.update(dt)
        self.volume_slider.update(dt)

        if self.sound_mute:
            sound_manager.resume_all()
            self.sound_change()
            self.mute_button.img_button = Sprite("UI/raw/UI_Flat_IconCross01a.png", (90, 60))
        else:
            sound_manager.pause_all()
            sound_manager.set_music_volume(0)
            self.mute_button.img_button = Sprite("UI/raw/UI_Flat_IconCheck01a.png", (90, 60))


    @override
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        screen.blit(self.setting_screen, (GameSettings.SCREEN_WIDTH / 2 - 400, GameSettings.SCREEN_HEIGHT / 2 - 300))
        self.play_back_button.draw(screen)
        self.mute_button.draw(screen)
        screen.blit(self.volume_slider_background, (GameSettings.SCREEN_WIDTH / 2 - 360, 300))
        self.volume_slider.draw(screen)
        screen.blit(self.text_mute, (GameSettings.SCREEN_WIDTH / 2 - 180, 400))
        screen.blit(self.text_volume, (GameSettings.SCREEN_WIDTH / 2 - 70, 240))
        screen.blit(self.text_settings, (GameSettings.SCREEN_WIDTH / 2 - 100, 100))
    
