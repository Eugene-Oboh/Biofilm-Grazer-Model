from mesa import Agent
import numpy as np


class LogisticBiofilmPatch(Agent):

    def __init__(self, unique_id, model, max_biomass, initial_biomass, growth_rate):

        super().__init__(unique_id, model)

        self.max_biomass = max_biomass
        self.growth_rate = growth_rate
        self.biomass = initial_biomass
        self.initial_biomass = initial_biomass

    def step(self):
        B = self.biomass
        biomass_change = (self.growth_rate * B * np.clip(1 - B/self.max_biomass, 0, 1))
        self.biomass = np.clip(B + biomass_change, 0, self.max_biomass)


