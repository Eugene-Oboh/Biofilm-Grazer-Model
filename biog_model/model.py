import random

import numpy as np
from mesa import Model
from mesa.space import MultiGrid
from .agents import LogisticBiofilmPatch
from .schedule import RandomActivationByBreed


class BiofilmGridModel(Model):

    def __init__(
            self,
            *args,
            height=20,
            width=20,
            growth_rate=0.0031,
            max_biomass=0.5,
            initial_biomass_percent=(0, 5),  # in percentage of max_biomass
            **kwargs
    ):
        """
        Create a new bng model with the given parameters.
        """
        super().__init__(*args, **kwargs)

        # Set parameters
        self.height = height
        self.width = width
        self.growth_rate = growth_rate
        self.max_biomass = max_biomass
        self.initial_biomass_percent = initial_biomass_percent

        self.schedule = RandomActivationByBreed(self)
        self.grid = MultiGrid(height=self.height, width=self.width, torus=False)

    def create_grid_random(self):
        # create biofilm patch
        for agent, x, y in self.grid.coord_iter():
            init_biomass_low, init_biomass_high = [v / 100 * self.max_biomass for v in self.initial_biomass_percent]
            initial_biomass = random.uniform(init_biomass_low, init_biomass_high)

            patch = LogisticBiofilmPatch(
                unique_id=self.next_id(),
                model=self,
                max_biomass=self.max_biomass,
                initial_biomass=initial_biomass,
                growth_rate=self.growth_rate
            )
            self.grid.place_agent(patch, (x, y))
            self.schedule.add(patch)

    def create_grid_from(self, data: np.ndarray):

        grid_shape = (self.grid.height, self.grid.width)
        if grid_shape != data.shape:
            raise ValueError(f'Given {data.shape=} does not match grid shape ({grid_shape=})')

        for agent, x, y in self.grid.coord_iter():
            initial_biomass = data[y, x]
            patch = LogisticBiofilmPatch(
                unique_id=self.next_id(),
                model=self,
                max_biomass=self.max_biomass,
                initial_biomass=initial_biomass,
                 growth_rate=self.growth_rate
            )
            self.grid.place_agent(patch, (x, y))
            self.schedule.add(patch)

    def step(self):
        self.schedule.step()
