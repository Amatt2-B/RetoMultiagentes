import numpy as np
import agentpy as ap
from utils import Encodable
from modelmap import *
from pathfinding import PathFinder

class Agent(ap.Agent, Encodable):
    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        self.model: CityModel
        self.env: CityEnv = model.env
        self.current_path: List[Tuple[int, int]] = []
        self.goal: Optional[Tuple[int, int]] = None

    def toObject(self):
        return {
            'id': self.id,
            'pos': self.getPos(),
            'type': self.agentType,
            'goal': self.goal
        }
    
    def getPos(self) -> tuple[int, int]:
        return self.model.env.positions[self]
    
    def isAtBoundary(self):
        x, y = self.getPos()
        r, c = self.env.shape
        return x <= 0 or y <= 0 or x+1 >= r or y+1 >= c

    def isOccupied(self, move):
        """Verifica si una celda está ocupada por otro agente."""
        for agent in self.model.agents:
            if agent.getPos() == move:
                return True
        return False
    
    def set_new_goal(self):
        """Establece un nuevo objetivo aleatorio válido"""
        start = self.getPos()
        self.goal = self.model.pathfinder.find_random_valid_goal(
            start, 
            isinstance(self, PedestrianAgent)
        )
        self.current_path = self.model.pathfinder.find_path(
            start,
            self.goal,
            isinstance(self, PedestrianAgent)
        )
        if not self.current_path:
            self.current_path = []
            self.goal = None

class CarAgent(Agent):
    def setup(self):
        self.agentType = 'car'
        self.is_waiting = False
        self.set_new_goal()

    def update(self):
        if not self.current_path or not self.goal:
            self.set_new_goal()
            return
        
        if len(self.current_path) <= 1:
            self.set_new_goal()
            return

        next_pos = self.current_path[1]  # Tomamos el siguiente punto en el camino
        
        # Verificar si podemos movernos a la siguiente posición
        if not self.isOccupied(next_pos) and self.canCross(next_pos):
            self.env.move_to(self, next_pos)
            self.current_path.pop(0)  # Removemos la posición actual
            self.is_waiting = False
        else:
            self.is_waiting = True

    def canCross(self, move):
        tile = self.env.road[move]
        return not (((tile & RC) == RC) and self.env.lights.getState(tile) == 'red')

class PedestrianAgent(Agent):
    def setup(self):
        self.agentType = 'pedestrian'
        self.set_new_goal()

    def update(self):
        if not self.current_path or not self.goal:
            self.set_new_goal()
            return
            
        if len(self.current_path) <= 1:
            self.set_new_goal()
            return

        next_pos = self.current_path[1]  # Tomamos el siguiente punto en el camino
        
        # Verificar si podemos movernos a la siguiente posición
        if not self.isOccupied(next_pos) and (
            ((self.env.road[next_pos] & RC) != RC) or 
            self.canCross(next_pos)
        ):
            self.env.move_to(self, next_pos)
            self.current_path.pop(0)  # Removemos la posición actual

    def canCross(self, move):
        tile = self.env.road[move]
        return (((tile & RC) == RC) and self.env.lights.getState(tile) == 'red')

class LightSystem():
    def __init__(self, lights, green_duration=10, red_duration=10):
        self.groups = [[group, -1] for group in lights]
        self.crossings = { }
        self.green_duration = green_duration
        self.red_duration = red_duration
        self.timers = {lightID: 0 for group in lights for lightID in group}
        self.step()

    def step(self):
        for idx, (group, greenIdx) in enumerate(self.groups):
            greenIdx = (greenIdx + 1) % len(group)
            self.groups[idx][1] = greenIdx

            for i, lightID in enumerate(group):
                state = 'green' if greenIdx == i else 'red'
                self.crossings[lightID] = state
                self.timers[lightID] = self.green_duration if state == 'green' else self.red_duration

    def getState(self, ID):
        ID = ID & 0xffff0000
        return self.crossings.get(ID, 'green')

class CityEnv(ap.Grid):
    def setup(self):
        self.road: np.ndarray = self.p.road
        self.dir: np.ndarray = self.p.dir
        self.lights = LightSystem(self.p.lights)

    def getDir(self, agent: Agent):
        return self.dir[agent.getPos()]

class CityModel(ap.Model):
    def setup(self):
        self.p.road = np.pad(self.p.road, 1, 'edge')
        self.p.dir = np.pad(self.p.dir, 1)

        self.env = CityEnv(self, self.p.road.shape)
        self.pathfinder = PathFinder(self.p.road, self.p.dir)
        
        self.agents: list[Agent]
        self.agents, agentPos = self.GenAgents(
            numCars=self.p.numCars, 
            numPed=self.p.numPedestrians
        )
        self.env.add_agents(self.agents, positions=agentPos)
        self.deleted = []

    def GenAgents(self, numCars, numPed):
        roads = list(zip(*np.where((self.env.road & RO) == RO)))
        sidewalks = list(zip(*np.where((self.env.road & SI) == SI)))

        self.random.shuffle(roads)
        self.random.shuffle(sidewalks)

        carPos = roads[:numCars]
        pedPos = sidewalks[:numPed]

        agents = []

        for _ in carPos:
            agents.append(CarAgent(self))

        for _ in pedPos:
            agents.append(PedestrianAgent(self))

        return agents, (carPos + pedPos)

    def step(self):
        # Step traffic ligths every 8 steps
        if self.t % 8 == 0:
            self.env.lights.step()
        alive = []
        deleted: list[Agent] = []
        for agent in self.agents:
            agent.update()

            if agent.isAtBoundary():
                deleted.append(agent)
            else:
                alive.append(agent)

        self.env.remove_agents(deleted)
        self.agents = alive
        self.deleted = [x.id for x in deleted]

params = {
    'steps': 40,
    'road': roadType,
    'dir': directions,
    'numPedestrians': 15,
    'numCars': 10,
    'lights': INTERSECTIONS,
}
