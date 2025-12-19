import pygame as pg

from src.core import GameManager, OnlineManager
from collections import deque

class Navigation:

    def __init__(self, game_manager: GameManager, tile_size):  
        self.gm = game_manager
        self.tile = tile_size
        self.speed = 4
        self.active_path: list[tuple[int, int]] = []
    
    def navigate_to(self, target_tile: tuple[int, int]):
        player = self.gm.player
        px = player.position.x // self.tile
        py = player.position.y // self.tile
        path = self.bfs((px, py), target_tile)

        if path:
            self.active_path = path[1:]  # 第一格是玩家的點

    def update(self, dt: float):

        if not self.active_path:
            return
        
        player = self.gm.player
        tx, ty = self.active_path[0]
        target_px = tx * self.tile
        target_py = ty * self.tile

        if abs(player.position.x - target_px) > self.speed:
            if player.position.x > target_px:
                player.position.x -= self.speed
            else:
                player.position.x += self.speed
            player.animation.update_pos(player.position)
            return
        
        if abs(player.position.y - target_py) > self.speed:
            if player.position.y > target_py:
                player.position.y -= self.speed
            else:
                player.position.y += self.speed
            player.animation.update_pos(player.position)
            return

        self.active_path.pop(0)

    def bfs(self, start, goal):

        queue = deque([start])
        visited = {start: None}
        dirs = [(1,0), (-1,0), (0,1), (0,-1)]

        def is_blocked(x, y):
            rect = pg.Rect(x * self.tile, y * self.tile, self.tile, self.tile)
            return self.gm.check_collision(rect)
        
        while queue:
            x, y = queue.popleft()
            if (x, y) == goal:
                break
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in visited and not is_blocked(nx, ny):
                    visited[(nx, ny)] = (x, y)
                    queue.append((nx, ny))

        if goal not in visited:
            return []

        path = []
        cur = goal
        while cur:
            path.append(cur)
            cur = visited[cur]

        return list(reversed(path))

    def get_path(self):
        return self.active_path