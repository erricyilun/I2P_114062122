from __future__ import annotations
import pygame as pg
from .entity import Entity
from src.core.services import input_manager, scene_manager
from src.utils import Position, PositionCamera, GameSettings, Logger, Direction
from src.core import GameManager
import math
from typing import override

class Player(Entity):
    speed: float = 4.0 * GameSettings.TILE_SIZE
    game_manager: GameManager

    def __init__(self, x: float, y: float, game_manager: GameManager) -> None:
        super().__init__(x, y, game_manager)

    @override
    def update(self, dt: float) -> None:
        dis = Position(0, 0)

        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            dis.x -= self.speed * dt
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            dis.x += self.speed * dt
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            dis.y -= self.speed * dt
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            dis.y += self.speed * dt
        
        
        dis_x = dis.x
        dis_y = dis.y

        if dis.x != 0 and dis.y != 0:
            dis_x /= math.sqrt(2)
            dis_y /= math.sqrt(2)

        self.rect = self.animation.rect.copy()

        self.rect.x += dis_x        
        if self.game_manager.check_collision(self.rect):
            self.rect.x -= dis_x
            self.position.x = Entity._snap_to_grid(self.rect.x)
        
        self.rect.y += dis_y
        if self.game_manager.check_collision(self.rect):
            self.rect.y -= dis_y
            self.rect.y = Entity._snap_to_grid(self.rect.y)

        if self.game_manager.check_bush_collision(self.rect):
            if input_manager.key_pressed(pg.K_SPACE):
                scene_manager.change_scene("bush")

        self.position.x = self.rect.x
        self.position.y = self.rect.y
        self._set_direction()

        # Check teleportation
        tp = self.game_manager.current_map.check_teleport(self.position)
        if tp:
            dest = tp.destination
            self.game_manager.switch_map(dest)
                
        super().update(dt)

    def _set_direction(self) -> None:
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            self.animation.switch("right")
        elif input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            self.animation.switch("left")
        elif input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            self.animation.switch("down")
        elif input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            self.animation.switch("up")

    @override
    def draw(self, screen: pg.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        
    @override
    def to_dict(self) -> dict[str, object]:
        return super().to_dict()
    
    @classmethod
    @override
    def from_dict(cls, data: dict[str, object], game_manager: GameManager) -> Player:
        return cls(data["x"] * GameSettings.TILE_SIZE, data["y"] * GameSettings.TILE_SIZE, game_manager)

    