import pygame as pg
import pytmx

from src.utils import load_tmx, Position, GameSettings, PositionCamera, Teleport

class Map:
    # Map Properties
    path_name: str
    tmxdata: pytmx.TiledMap
    # Position Argument
    spawn: Position
    teleporters: list[Teleport]
    # Rendering Properties
    _surface: pg.Surface
    _collision_map: list[pg.Rect]

    def __init__(self, path: str, tp: list[Teleport], spawn: Position):
        self.path_name = path
        self.tmxdata = load_tmx(path)
        self.spawn = spawn
        self.teleporters = tp

        pixel_w = self.tmxdata.width * GameSettings.TILE_SIZE
        pixel_h = self.tmxdata.height * GameSettings.TILE_SIZE

        # Prebake the map
        self._surface = pg.Surface((pixel_w, pixel_h), pg.SRCALPHA)
        self._render_all_layers(self._surface)
        # Prebake the collision map
        self._collision_map = self._create_collision_map()
        self._bush_map = self._create_bush_map()

    def update(self, dt: float):
        return

    def draw(self, screen: pg.Surface, camera: PositionCamera):
        screen.blit(self._surface, camera.transform_position(Position(0, 0)))
        
        # Draw the hitboxes collision map
        if GameSettings.DRAW_HITBOXES:
            for rect in self._collision_map:
                pg.draw.rect(screen, (255, 0, 0), camera.transform_rect(rect), 1)
            for bush in self._bush_map:
                pg.draw.rect(screen, (0, 255, 0), camera.transform_rect(bush), 1)
        
        
    def check_collision(self, rect: pg.Rect) -> bool:
        for collision_rect in self._collision_map:
            if rect.colliderect(collision_rect):
                return True
        return False
    
    def check_bush_collision(self, rect: pg.Rect) -> bool:
        for bush in self._bush_map:
            if rect.colliderect(bush):
                return True
        return False

        
    def check_teleport(self, pos: Position) -> Teleport | None:
        for tp in self.teleporters:
            
            if(
                tp.pos.x - GameSettings.TILE_SIZE <= pos.x <= tp.pos.x + GameSettings.TILE_SIZE
                and tp.pos.y - GameSettings.TILE_SIZE <= pos.y <= tp.pos.y + GameSettings.TILE_SIZE
            ):
                return tp
        return None

    def _render_all_layers(self, target: pg.Surface) -> None:
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                self._render_tile_layer(target, layer)
            # elif isinstance(layer, pytmx.TiledImageLayer) and layer.image:
            #     target.blit(layer.image, (layer.x or 0, layer.y or 0))
 
    def _render_tile_layer(self, target: pg.Surface, layer: pytmx.TiledTileLayer) -> None:
        for x, y, gid in layer:
            if gid == 0:
                continue
            image = self.tmxdata.get_tile_image_by_gid(gid)
            if image is None:
                continue

            image = pg.transform.scale(image, (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
            target.blit(image, (x * GameSettings.TILE_SIZE, y * GameSettings.TILE_SIZE))
    
    def _create_collision_map(self) -> list[pg.Rect]:
        rects = []
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and ("collision" in layer.name.lower() or "house" in layer.name.lower()):
                for x, y, gid in layer:
                    if gid != 0:
                        rects.append(pg.Rect(x * GameSettings.TILE_SIZE, y * GameSettings.TILE_SIZE, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
        return rects

    def _create_bush_map(self) -> list[pg.Rect]:
        rects = []
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and (layer.name == "PokemonBush"):
                for x, y, gid in layer:
                    if gid != 0:
                        rects.append(pg.Rect(x * GameSettings.TILE_SIZE, y * GameSettings.TILE_SIZE, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
        return rects

    @classmethod
    def from_dict(cls, data: dict) -> "Map":
        tp = [Teleport.from_dict(t) for t in data["teleport"]]
        pos = Position(data["player"]["x"] * GameSettings.TILE_SIZE, data["player"]["y"] * GameSettings.TILE_SIZE)
        return cls(data["path"], tp, pos)

    def to_dict(self):
        return {
            "path": self.path_name,
            "teleport": [t.to_dict() for t in self.teleporters],
            "player": {
                "x": self.spawn.x // GameSettings.TILE_SIZE,
                "y": self.spawn.y // GameSettings.TILE_SIZE,
            }
        }

class MiniMap:
    
    # Map Properties
    path_name: str
    tmxdata: pytmx.TiledMap
    _surface: pg.Surface

    def __init__(self, path: str, scale: float):
        
        self.path_name = path
        self.tmxdata = load_tmx(path)
        self.scale = scale

        # 完整地圖像素大小（原圖）
        pixel_w = self.tmxdata.width * GameSettings.TILE_SIZE
        pixel_h = self.tmxdata.height * GameSettings.TILE_SIZE

        full_surface = pg.Surface((pixel_w, pixel_h), pg.SRCALPHA)
        self._render_all_layers(full_surface)

        scaled_w = int(pixel_w * self.scale)
        scaled_h = int(pixel_h * self.scale)
        self._surface = pg.transform.scale(full_surface, (scaled_w, scaled_h))

    def update(self, path: str):
 
        self.path_name = path
        self.tmxdata = load_tmx(path)

        pixel_w = self.tmxdata.width * GameSettings.TILE_SIZE
        pixel_h = self.tmxdata.height * GameSettings.TILE_SIZE

        full_surface = pg.Surface((pixel_w, pixel_h), pg.SRCALPHA)
        self._render_all_layers(full_surface)

        scaled_w = int(pixel_w * self.scale)
        scaled_h = int(pixel_h * self.scale)
        self._surface = pg.transform.scale(full_surface, (scaled_w, scaled_h))


    def draw(self, screen: pg.Surface, player_pos: Position):

        x = GameSettings.SCREEN_WIDTH - self._surface.get_width() - 10
        y = 10

        screen.blit(self._surface, (x, y))

        px = int(player_pos.x * self.scale)
        py = int(player_pos.y * self.scale)
        px = x + px
        py = y + py

        pg.draw.circle(screen, (255, 50, 50), (px, py), 3)

    def _render_all_layers(self, target: pg.Surface) -> None:
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                self._render_tile_layer(target, layer)
            
 
    def _render_tile_layer(self, target: pg.Surface, layer: pytmx.TiledTileLayer) -> None:
        for x, y, gid in layer:
            if gid == 0:
                continue
            image = self.tmxdata.get_tile_image_by_gid(gid)
            if image is None:
                continue

            image = pg.transform.scale(image, (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
            target.blit(image, (x * GameSettings.TILE_SIZE, y * GameSettings.TILE_SIZE))
