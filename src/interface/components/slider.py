from __future__ import annotations
import pygame as pg

from src.sprites import Sprite
from src.core.services import input_manager
from src.utils import Logger, GameSettings, Position
from typing import Callable, override
from .component import UIComponent


class Slider(UIComponent):
    img_slider: Sprite
    img_slider_default: Sprite
    hitbox: pg.Rect
    on_click: Callable[[], None] | None

    def __init__(
        self,
        img_path: str,
        x: int, y: int, width: int, height: int,
        on_click: Callable[[], None] | None = None
    ):
        self.img_slider_default = Sprite(img_path, (width, height))
        self.hitbox = pg.Rect(x, y, width, height)
       
        self.img_slider = Sprite(img_path, (width, height))
        self.on_click = on_click
        self.dragging = False

    
    
    @override
    def update(self, dt: float) -> None:
        
        if self.on_click is not None:
            if input_manager.mouse_pressed(1):
                if self.hitbox.collidepoint(input_manager.mouse_pos):
                    self.dragging = True
                    self.on_click()
                    mx = pg.mouse.get_pos()[0]
                    self.hitbox.x = min(max(mx, GameSettings.SCREEN_WIDTH / 2 - 360), GameSettings.SCREEN_WIDTH / 2 + 360 - 36)
                
            elif input_manager.mouse_released(1):
                self.dragging = False
            
            elif pg.MOUSEMOTION:
                if self.dragging:
                    self.on_click()
                    mx = pg.mouse.get_pos()[0]
                    self.hitbox.x = min(max(mx, GameSettings.SCREEN_WIDTH / 2 - 360), GameSettings.SCREEN_WIDTH / 2 + 360 - 36)
           


    
    @override
    def draw(self, screen: pg.Surface) -> None:
        
        _ = screen.blit(self.img_slider.image, self.hitbox)






