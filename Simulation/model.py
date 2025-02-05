import numpy as np
import agentpy as ap
from utils import Encodable
from typing import List, Tuple, Optional
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
    
    def isOutOfBounds(self):
        '''
        Check if the agent is in the borders of its environment
        '''
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

    def update(self):
        moves = self.getRoads()

        if len(moves) != 0:
            choice = self.model.random.choice(moves)
            self.env.move_to(self, choice)

    def canCross(self, move):
        tile = self.env.road[move]
        # Checks if the tile is accessible
        return self.env.lights.getState(tile) == 'green'

    def getRoads(self):
        dir = self.env.getDir(self)
        moves = []
        x, y = self.getPos()

        # Check for the available moves for the current road direction
        # FIXME: this brings the problem that an agent can do weird
        #        if the tile has many available directions
        #        keeping state of a previous direction and checking to avoid 
        #        things like a 180 degree turn could be a good solution
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
        #self.set_new_goal()
    def initialize_goal(self):
        """Call this method after the agent's position is set."""
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
    def __init__(self, lights):
        # Each light group will have the light ids and the current index for the
        # green light
        self.groups = [[group, -1] for group in lights]
        self.crossings = { }
        self.step()

    def step(self):
        # TODO: There has to be a better way to do this idk
        for idx, (group, greenIdx) in enumerate(self.groups):
            # Increment the green index and wrap around
            greenIdx = (greenIdx + 1) % len(group)
            # Update the green index
            self.groups[idx][1] = greenIdx

            # Update the lights dictionary
            for i, lightID in enumerate(group):
                self.crossings[lightID] = 'green' if greenIdx == i else 'red'

    def getState(self, ID):
        # Ignore the first 16 most significant bits
        ID = ID & 0xffff0000
        # If there is no ID associated with the tile just return green
        return self.crossings.get(ID, 'green')

class CityEnv(ap.Grid):
    def setup(self):
        self.road: np.ndarray = self.p.road
        self.dir: np.ndarray = self.p.dir
        self.lights = LightSystem(self.p.lights)
        self.positions = {}  # Initialize the positions dictionary

    def getDir(self, agent: Agent):
        return self.dir[agent.getPos()]

class CityModel(ap.Model):
    def setup(self):
        # Pad the environment for despawn purposes
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

        # Add a counter for spawning new cars
        self.car_spawn_counter = 0

    def GenAgents(self, numCars, numPed):
        '''
        Initialize the agents and place them on random tiles they can walk on
        '''
        # Get all possible positions on the roads
        roads = list(zip(*np.where((self.env.road & RO) == RO)))  # Road tiles
 
    # Exclude positions that are directly on the edge of the grid
        roads = [(x, y) for x, y in roads if 1 <= x < self.env.road.shape[0] - 1 and 1 <= y < self.env.road.shape[1] - 1]
 
    # Shuffle the roads for random distribution
        self.random.shuffle(roads)

    # Limit the number of cars to numCars
        carPos = roads[:numCars]

    # Use the existing logic for pedestrians (sidewalks)
        sidewalks = list(zip(*np.where((self.env.road & SI) == SI)))  # Sidewalk tiles
        self.random.shuffle(sidewalks)
        pedPos = sidewalks[:numPed]

    # Create agents
        agents = []
        agentPositions = []

    # Create car agents at selected positions
        for pos in carPos:
            car = CarAgent(self)
            agents.append(car)
            agentPositions.append(pos)
            # Add the agent and its position to the environment's positions dictionary
            self.env.positions[car] = pos
            print(f"Added car agent {car.id} at position {pos}")

    # Create pedestrian agents at selected positions
        for pos in pedPos:
            pedestrian = PedestrianAgent(self)
            agents.append(pedestrian)
            agentPositions.append(pos)
            # Add the agent and its position to the environment's positions dictionary
            self.env.positions[pedestrian] = pos
            print(f"Added pedestrian agent {pedestrian.id} at position {pos}")
            pedestrian.initialize_goal()

        return agents, agentPositions




    def step(self):
        # Step traffic lights every 8 steps
        if self.t % 8 == 0:
            self.env.lights.step()

        # Spawn a new car every 5 steps
        self.car_spawn_counter += 1
        if self.car_spawn_counter % 10 == 0:
            self.spawn_new_car()

        alive = []
        deleted: list[Agent] = []
        for agent in self.agents:
            agent.update()

            # Despawn agents on the edges
            if agent.isOutOfBounds():
                deleted.append(agent)
            else:
                alive.append(agent)

        self.env.remove_agents(deleted)
        self.agents = alive
        # Save the deleted agents IDs to send later to the simulation
        self.deleted = [x.id for x in deleted]

    def spawn_new_car(self):
        '''
        Spawns a new car agent at a valid road position.
        '''
        # Get all valid road positions (excluding edges)
        roads = list(zip(*np.where((self.env.road & RO) == RO)))
        roads = [(x, y) for x, y in roads if 1 <= x < self.env.road.shape[0] - 1 and 1 <= y < self.env.road.shape[1] - 1]

        if roads:  # Ensure there are valid positions available
            # Choose a random position for the new car
            new_pos = self.random.choice(roads)

            # Create the new car agent
            new_car = CarAgent(self)

            # Add the new car to the list of agents and the environment
            self.agents.append(new_car)
            self.env.add_agents([new_car], positions=[new_pos])

            print(f"Spawned new car at position: {new_pos}")
        else:
            print("No valid road positions available to spawn a new car.")

params = {
    'steps': 40,
    'road': roadType,
    'dir': directions,
    'numPedestrians': 15,
    'numCars': 10,
    'lights': INTERSECTIONS,
}
