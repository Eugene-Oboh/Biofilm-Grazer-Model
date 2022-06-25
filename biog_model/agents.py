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

        time = self.model.clock.time
        light_intensity = self.model.illumination.get_intensity(time)
        light_growth_rate = self.growth_rate * (light_intensity/(10 * self.model.max_light_intensity)/100 + light_intensity)

        B = self.biomass
        biomass_change = (light_growth_rate * B * np.clip(1 - B/self.max_biomass, 0, 1))
        self.biomass = np.clip(B + biomass_change, 0, self.max_biomass)
