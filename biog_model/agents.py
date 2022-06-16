from mesa import Agent
import numpy as np




class LogisticBiofilmPatch(Agent):

    def __init__(self, unique_id, model, max_biomass, initial_biomass, growth_rate):

        super().__init__(unique_id, model)

        self.max_biomass = max_biomass
        self.growth_rate = growth_rate
        self.biomass = initial_biomass
        self.initial_biomass = initial_biomass
        #self.neighbor_effect = neighbor_effect


    def step(self):
        B = self.biomass
        neighborhood_biomass = []

        for neighbor_pos in self.model.grid.get_neighborhood(self.pos, moore=False):
            neighbor_cell = self.model.grid.get_cell_list_contents([neighbor_pos])
            neighbor_patch=[obj for obj in neighbor_cell if isinstance(obj, LogisticBiofilmPatch)][0]
            neighbor_biomass = neighbor_patch.biomass
            neighborhood_biomass.append(neighbor_biomass)
        neighborhood_effect = sum(neighborhood_biomass) / 4 * (0.5 / 100)
        biomass_change = (self.growth_rate * B * np.clip(1 - B/self.max_biomass, 0, 1))
        self.biomass = np.clip(B + biomass_change, 0, self.max_biomass) + neighborhood_effect





