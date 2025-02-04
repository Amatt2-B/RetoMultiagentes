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
    
    # FIXME: cambiar el nombre xd
    def isEdging(self):
        x, y = self.getPos()
        r, c = self.env.shape

        return x <= 0 or y <= 0 or x+1 >= r or y+1 >= c

class CarAgent(Agent):
    def setup(self):
        self.agentType = 'car'

    def update(self):
        moves = self.getRoads()

        if len(moves) != 0:
            choice = self.model.random.choice(moves)
            self.env.move_to(self, choice)

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
            choice = self.model.random.choice(moves)
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
    def __init__(self, lights):
        self.groups = [[group, -1] for group in lights]
        self.crossings = { }
        self.step()

    def step(self):
        # TODO: There has to be a better way to do this idk
        for idx, (group, greenIdx) in enumerate(self.groups):
            greenIdx = (greenIdx + 1) % len(group)
            self.groups[idx][1] = greenIdx

            for i, lightID in enumerate(group):
                self.crossings[lightID] = 'green' if greenIdx == i else 'red'

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

            if agent.isEdging():
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