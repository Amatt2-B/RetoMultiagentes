from typing import Tuple, List, Set, Dict, Optional
import numpy as np
from constants import *
import heapq

class PathFinder:
    def __init__(self, road_map: np.ndarray, directions: np.ndarray):
        self.road_map = road_map
        self.directions = directions
        self.rows, self.cols = road_map.shape

    def get_valid_neighbors(self, pos: Tuple[int, int], is_pedestrian: bool) -> List[Tuple[int, int]]:
        x, y = pos
        neighbors = []
        
        # Para peatones, pueden moverse en sidewalks y cruces
        if is_pedestrian:
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < self.rows and 0 <= new_y < self.cols and 
                    ((self.road_map[new_x, new_y] & SI) == SI or 
                     (self.road_map[new_x, new_y] & RC) == RC)):
                    neighbors.append((new_x, new_y))
        # Para vehículos, seguir las direcciones permitidas
        else:
            dir = self.directions[x, y]
            if dir & ND and x > 0 and (self.road_map[x-1, y] & RO) == RO:
                neighbors.append((x-1, y))
            if dir & SD and x < self.rows-1 and (self.road_map[x+1, y] & RO) == RO:
                neighbors.append((x+1, y))
            if dir & ED and y < self.cols-1 and (self.road_map[x, y+1] & RO) == RO:
                neighbors.append((x, y+1))
            if dir & WD and y > 0 and (self.road_map[x, y-1] & RO) == RO:
                neighbors.append((x, y-1))
                
        return neighbors

    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], is_pedestrian: bool) -> List[Tuple[int, int]]:
        """
        Implementa A* pathfinding
        """
        if start == goal:
            return []

        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            current = heapq.heappop(frontier)[1]

            if current == goal:
                break

            for next_pos in self.get_valid_neighbors(current, is_pedestrian):
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.heuristic(goal, next_pos)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current

        # Reconstruir el camino
        if goal not in came_from:
            return []
            
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    def find_random_valid_goal(self, start: Tuple[int, int], is_pedestrian: bool) -> Tuple[int, int]:
        """
        Encuentra un destino válido aleatorio basado en el tipo de agente
        """
        valid_positions = []
        for x in range(self.rows):
            for y in range(self.cols):
                if is_pedestrian and (self.road_map[x, y] & SI) == SI:
                    valid_positions.append((x, y))
                elif not is_pedestrian and (self.road_map[x, y] & RO) == RO:
                    valid_positions.append((x, y))
        
        # Filtrar posiciones muy cercanas al inicio
        valid_positions = [pos for pos in valid_positions 
                         if self.heuristic(start, pos) > 5]  # Distancia mínima
        
        if not valid_positions:
            return start
            
        return valid_positions[np.random.randint(len(valid_positions))]
