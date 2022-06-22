import random
import typing as T
from dataclasses import dataclass

import numpy as np
from mesa import Model
from mesa.space import MultiGrid
from .agents import LogisticBiofilmPatch
from .schedule import RandomActivationByBreed


@dataclass
class BIOFILM_PARAMS:
    growth_rate:float = 0.0031  # TODO: units?
    max_biomass: float = 0.5,    # TODO: units
    initial_biomass_percent: T.Tuple[float, float] = (0, 5)  # in percentage of max_biomass



class Clock:
    """
    This is the model's simulation clock

    It tracks minutes elapsed in simulation time, and increments it in some step size.
    """

    def __init__(self, initial_time=0, step_size=1):
        self.time = initial_time  # minutes elapsed
        self.step_size = step_size

    def increment(self):
        self.time += self.step_size

    def reset(self):
        self.time = 0

    @property
    def hours(self):
        return self.time / 60

    @property
    def minutes(self):
        return self.time


class BiofilmGridModel(Model):

    def __init__(
            self,
            *args,
            height=20,
            width=20,
            clock_params=None,
            biofilm_params=None,
            **kwargs
    ):
        """
        Create a new bng model with the given parameters.
        """
        super().__init__(*args, **kwargs)

        # Set parameters
        self.height = height
        self.width = width

        clock_params = clock_params or {}
        self.clock = Clock(**clock_params)

        biofilm_params = biofilm_params or {}
        self.biofilm_params = BIOFILM_PARAMS(**biofilm_params)

        self.agent_scheduler = RandomActivationByBreed(self)
        self.grid = MultiGrid(height=self.height, width=self.width, torus=False)


    def create_grid_random(self):
        bparams = self.biofilm_params
        # create biofilm patch
        for agent, x, y in self.grid.coord_iter():
            init_biomass_low, init_biomass_high = [v / 100 * bparams.max_biomass for v in bparams.initial_biomass_percent]
            initial_biomass = random.uniform(init_biomass_low, init_biomass_high)

            patch = LogisticBiofilmPatch(
                unique_id=self.next_id(),
                model=self,
                max_biomass=bparams.max_biomass,
                initial_biomass=initial_biomass,
                growth_rate=bparams.growth_rate
            )
            self.grid.place_agent(patch, (x, y))
            self.agent_scheduler.add(patch)


    def create_grid_from(self, data: np.ndarray):
        bparams = self.biofilm_params

        grid_shape = (self.grid.height, self.grid.width)
        if grid_shape != data.shape:
            raise ValueError(f'Given {data.shape=} does not match grid shape ({grid_shape=})')

        for agent, x, y in self.grid.coord_iter():
            initial_biomass = data[y, x]
            patch = LogisticBiofilmPatch(
                unique_id=self.next_id(),
                model=self,
                max_biomass=bparams.max_biomass,
                initial_biomass=initial_biomass,
                growth_rate=bparams.growth_rate
            )
            self.grid.place_agent(patch, (x, y))
            self.agent_scheduler.add(patch)


    def step(self):
        """
        Each step of the model should do the following:

        - increment the clock
        - step all the agents (using self.agent_schedule.step())
        """
        self.clock.increment()
        self.agent_scheduler.step()  # this updates all agents in order of agent class(?)
