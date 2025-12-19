import pygame as pg
import json
from src.utils import GameSettings
from src.utils.definition import Monster, Item


class Bag:
    _monsters_data: list[Monster]
    _items_data: list[Item]

    def __init__(self, monsters_data: list[Monster] | None = None, items_data: list[Item] | None = None):
        self._monsters_data = monsters_data if monsters_data else []
        self._items_data = items_data if items_data else []

    def update(self, dt: float):
        pass


    def draw_monsters(self, screen: pg.Surface):
        font = pg.font.Font("assets/fonts/Pokemon Solid.ttf", 32)
        start_x = GameSettings.SCREEN_WIDTH / 2 - 300
        start_y = GameSettings.SCREEN_HEIGHT / 2 - 250
        line_space = 50

        monsters = self._monsters_data

        screen.blit(font.render("Monsters:", True, (0, 0, 0)), (start_x, start_y))
        for i, monster in enumerate(monsters):
            screen.blit(font.render(f"{monster['name']}", True, (0, 0, 0)), (start_x + 20, start_y + (i + 1) * line_space))
            screen.blit(pg.image.load(f"assets/images/{monster["sprite_path"]}"), (start_x - 30, start_y + (i + 1) * line_space))

    def draw_items(self, screen: pg.Surface):
        font = pg.font.Font("assets/fonts/Pokemon Solid.ttf", 32)
        start_x = GameSettings.SCREEN_WIDTH / 2
        start_y = GameSettings.SCREEN_HEIGHT / 2 - 250
        line_space = 50
        
        items = self._items_data
        
        screen.blit(font.render("Items:", True, (0, 0, 0)), (start_x, start_y))
        for j, item in enumerate(items):
            screen.blit(font.render(f"{item['name']} x {item['count']}", True, (0, 0, 0)), (start_x + 20, start_y + (j + 1) * line_space))
            screen.blit(pg.image.load(f"assets/images/{item['sprite_path']}"), (start_x - 20, start_y + (j + 1) * line_space + 10))


    def to_dict(self) -> dict[str, object]:
        return {
            "monsters": list(self._monsters_data),
            "items": list(self._items_data)
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Bag":
        monsters = data.get("monsters") or []
        items = data.get("items") or []
        bag = cls(monsters, items)
        return bag