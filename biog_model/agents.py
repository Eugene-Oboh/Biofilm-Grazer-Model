import matplotlib.pyplot as plt
from mesa import Agent
import numpy as np
from biog_model.random_walk import RandomWalker


class Gastropods(RandomWalker):
    """
    A snail that walk around and eat biofilm.
    """

    def __init__(self, unique_id, pos, model, moore, grazing_rate, grazing_rate_percent_of_biomass, init_grazer_biomass, percent_of_food_to_weight, max_grazer_biomass):
        super().__init__(unique_id, pos, model, moore=moore)

        self.grazing_rate = grazing_rate
        self.grazing_rate_percent_of_biomass = grazing_rate_percent_of_biomass
        self.init_grazer_biomass = init_grazer_biomass
        self.max_grazer_biomass = max_grazer_biomass
        self.biomass = init_grazer_biomass
        self.percent_of_food_to_weight = percent_of_food_to_weight


    def step(self):
        """
        during the night, grazers rest.
        during the day time the following happens
        Grazers will have an initial biomass eg. 1g
        grazers will have a grazing rate eg 1% of their biomass
        grazers will move and eat biofilm biomass according to current grazing rate
        a % of biofilm biomass grazed will be added to the grazers biomass
        """

        time = self.model.clock.time
        light_intensity = self.model.illumination.get_intensity(time)
        if light_intensity <= 0.01:
            return
        self.random_move()
        #if self.model.biofilm:

        # If there is biofilm define grazing efficiency
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        biofilm_patch = [obj for obj in this_cell if isinstance(obj, LogisticBiofilmPatch)][0]

        self.biomass += (self.percent_of_food_to_weight * self.grazing_rate) / 100
        self.biomass = np.clip(self.biomass, 0, self.max_grazer_biomass)
        #self.biomass = np.clip(self.init_grazer_biomass, self.max_grazer_biomass)
        if self.model.phosphorus_conc <=5:
            self.grazing_rate = (self.grazing_rate_percent_of_biomass * self.biomass)/100 * 1.4
        else:
            self.grazing_rate = (self.grazing_rate_percent_of_biomass * self.biomass) / 100
        biofilm_patch.biomass -= (self.grazing_rate)
        biofilm_patch.biomass = np.clip(biofilm_patch.biomass, 0, biofilm_patch.max_biomass)
        #print(self.biomass)

        print(f'this is grazer biomass {self.biomass=} at {self.grazing_rate=}')


    """
        if biofilm_patch.biomass:
            self.grazing_rate = self.init_grazing_rate
            for i in range(time):
                if i % 1440 ==0:
                    self.grazing_rate = self.grazing_rate + 0.001

                biofilm_patch.biomass_grazed = self.grazing_rate
     """


class LogisticBiofilmPatch(Agent):

    def __init__(self, unique_id, model, max_biomass, initial_biomass, growth_rate):

        super().__init__(unique_id, model)
        self.max_biomass = max_biomass
        self.growth_rate = growth_rate
        self.biomass = initial_biomass
        self.initial_biomass = initial_biomass
        #self.biomass_grazed = 0
        self.all_growth_rate = None
        self.neighborhood_effect = None



    def step(self):
        # Nutrient and light effect
        time = self.model.clock.time
        light_intensity = np.clip(self.model.illumination.get_intensity(time), 0.00001, 1)

        light = light_intensity / (self.model.light_kl + light_intensity)
        nutrient = self.model.phosphorus_conc / (self.model.phosphorus_kp + self.model.phosphorus_conc)

        light_nutrient_growth_rate = self.growth_rate * (light * nutrient)
        #print(light_nutrient_growth_rate)


        #light_growth_rate = self.growth_rate * (light_intensity/(self.model.light_kl + light_intensity))
        #nutrient_growth_rate = self.growth_rate * (self.model.phosphorus_conc / (self.model.phosphorus_kp + self.model.phosphorus_conc))

        # Neighborhood effect
        neighborhood_biomass = []
        for neighbor_pos in self.model.grid.get_neighborhood(self.pos, moore=False, radius=1):
            neighbor_cell = self.model.grid.get_cell_list_contents([neighbor_pos])
            neighbor_patch = [obj for obj in neighbor_cell if isinstance(obj, LogisticBiofilmPatch)][0]
            neighbor_biomass = neighbor_patch.biomass
            neighborhood_biomass.append(neighbor_biomass)
        neighborhood_effect = sum(neighborhood_biomass) / len(neighborhood_biomass) * (0.001 / 100)
        if self.model.neighborhood_effect == False:
            neighbor_effect = 0
        else:
            neighbor_effect = neighborhood_effect


        #print(light_nutrient_growth_rate)
        B = self.biomass
        biomass_change = (light_nutrient_growth_rate * B * np.clip(1 - B/self.max_biomass, 0, 1)) + neighbor_effect
        self.biomass = np.clip(B + biomass_change, 0, self.max_biomass)
        #self.biomass_grazed = 0







