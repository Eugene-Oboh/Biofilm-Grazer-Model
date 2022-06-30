import matplotlib.pyplot as plt
from mesa import Agent
import numpy as np
from biog_model.random_walk import RandomWalker


class Gastropods(RandomWalker):
    """
    A snail that walk around and eat biofilm.
    """

    def __init__(self, unique_id, pos, model, moore, grazing_eff, init_grazing_eff):
        super().__init__(unique_id, pos, model, moore=moore)

        self.grazing_eff = grazing_eff
        self.init_grazing_eff = init_grazing_eff

    def step(self):
        """
        A model step. Move, then eat biofilm.
        """
        time = self.model.clock.time
        light_intensity = self.model.illumination.get_intensity(time)
        if light_intensity ==0:
            self.random_move()
            #if self.model.biofilm:

            # If there is biofilm define grazing efficiency
            this_cell = self.model.grid.get_cell_list_contents([self.pos])
            biofilm_patch = [obj for obj in this_cell if isinstance(obj, LogisticBiofilmPatch)][0]
            if biofilm_patch.biomass:
                self.grazing_eff = self.init_grazing_eff
                for i in range(time):
                    if i % 1440 ==0:
                        self.grazing_eff = self.grazing_eff + 0.001

                    biofilm_patch.biomass_grazed = self.grazing_eff



class LogisticBiofilmPatch(Agent):

    def __init__(self, unique_id, model, max_biomass, initial_biomass, growth_rate):

        super().__init__(unique_id, model)

        self.max_biomass = max_biomass
        self.growth_rate = growth_rate
        self.biomass = initial_biomass
        self.initial_biomass = initial_biomass
        self.biomass_grazed = 0


    def step(self):
        # Implement light & nutrient effects
        time = self.model.clock.time
        light_intensity = self.model.illumination.get_intensity(time)
        #light_growth_rate = self.growth_rate * (light_intensity/(self.model.light_kl + light_intensity))
        #nutrient_growth_rate = self.growth_rate * (self.model.phosphorus_conc / (self.model.phosphorus_kp + self.model.phosphorus_conc))

        light = light_intensity / (self.model.light_kl + light_intensity)
        nutrient = self.model.phosphorus_conc / (self.model.phosphorus_kp + self.model.phosphorus_conc)

        if light == 0:
            light_nutrient_growth_rate = self.growth_rate * nutrient
        elif not self.model.light:
            light_nutrient_growth_rate = self.growth_rate * nutrient
        elif nutrient == 0:
            light_nutrient_growth_rate = self.growth_rate * light
        elif not self.model.nutrient:
            light_nutrient_growth_rate = self.growth_rate * light
        else:
            light_nutrient_growth_rate = self.growth_rate * (light * nutrient)

        # Neighborhood effect
        neighborhood_biomass = []
        for neighbor_pos in self.model.grid.get_neighborhood(self.pos, moore=False, radius=1):
            neighbor_cell = self.model.grid.get_cell_list_contents([neighbor_pos])
            neighbor_patch = [obj for obj in neighbor_cell if isinstance(obj, LogisticBiofilmPatch)][0]
            neighbor_biomass = neighbor_patch.biomass
            neighborhood_biomass.append(neighbor_biomass)
        neighborhood_effect = sum(neighborhood_biomass) / len(neighborhood_biomass) * (0.01 / 100)
        if self.model.neighborhood_effect == False:
            neighbor_effect = 0
        else:
            neighbor_effect = neighborhood_effect

        #print(light_nutrient_growth_rate)
        B = self.biomass
        biomass_change = (light_nutrient_growth_rate * B * np.clip(1 - B/self.max_biomass, 0, 1)) + neighbor_effect
        self.biomass = np.clip(B + biomass_change - self.biomass_grazed, 0, self.max_biomass)
        self.biomass_grazed = 0







