import numpy as np
import agentpy as ap
from utils import Encodable
from modelmap import *

class Agent(ap.Agent, Encodable):
    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        self.model: CityModel # Just for typings
        self.env: CityEnv = model.env
        # self.agentType = 'agent' if self.agentType is None else self.agentType

    def toObject(self):
        return {
            'id': self.id,
            'pos': self.getPos(),
            'type': self.agentType,
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

class CarAgent(Agent):
    def setup(self):
        self.agentType = 'car'
        self.is_waiting = False  # Track if the car is waiting at a red light

    def update(self):
        moves = self.getRoads()

        if len(moves) != 0:
            # Check if the car is waiting at a red light
            if self.is_waiting:
                # If the light is still red, do nothing
                if not self.canCross(self.getPos()):
                    return
                else:
                    self.is_waiting = False  # Light turned green, start moving

            # Filter available moves
            available_moves = [move for move in moves if not self.isOccupied(move)]
            if available_moves:
                choice = self.model.random.choice(available_moves)
                # Check if the chosen move is allowed (light is green)
                if self.canCross(choice):
                    self.env.move_to(self, choice)
                else:
                    self.is_waiting = True  # Light is red, stop and wait

    def canCross(self, move):
        tile = self.env.road[move]
        return not (((tile & RC) == RC) and self.env.lights.getState(tile) == 'red')

    def getRoads(self):
        dir = self.env.getDir(self)
        moves = []
        x, y = self.getPos()

        if dir & ND:
            move = (x-1, y)
            if self.canCross(move):
                moves.append(move) # North
            
        if dir & SD:
            move = (x+1, y)
            if self.canCross(move):
                moves.append(move) # South

        if dir & ED:
            move = (x, y+1)
            if self.canCross(move):
                moves.append(move) # East
            
        if dir & WD:
            move = (x, y-1)
            if self.canCross(move):
                moves.append(move) # West

        return moves

class PedestrianAgent(Agent):
    def setup(self):
        self.agentType = 'pedestrian'

    def update(self):
        moves = self.getSidewalks()

        if len(moves) != 0:
            # Filtra los movimientos ocupados
            available_moves = [move for move in moves if not self.isOccupied(move)]
            if available_moves:
                choice = self.model.random.choice(available_moves)
                self.env.move_to(self, choice)

    def canCross(self, move):
        tile = self.env.road[move]
        return (((tile & RC) == RC) and self.env.lights.getState(tile) == 'red')

    def getSidewalks(self):
        pos = self.getPos()

        x1 = max(pos[0] - 1, 0)
        x2 = min(pos[0] + 2, self.env.road.shape[0])

        y1 = max(pos[1] - 1, 0)
        y2 = min(pos[1] + 2, self.env.road.shape[1])

        kernel = self.env.road[x1:x2, y1:y2]

        rows, cols = np.where((kernel & SI) == SI)
        rows += x1
        cols += y1
        coords = list(zip(rows, cols))

        cr, cc = np.where((kernel & RC) == RC)
        cr += x1
        cc += y1

        cross = list(filter( lambda x: self.canCross(x), list(zip(cr, cc))))
        
        return coords + cross


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