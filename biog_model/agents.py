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
        light_growth_rate = self.growth_rate * (light_intensity/(self.model.light_kL + light_intensity))
        nutrient_growth_rate = self.growth_rate * (self.model.phosphorus_conc / (self.model.phosphorus_kp + self.model.phosphorus_conc))

        light = light_intensity / (self.model.light_kL + light_intensity)
        nutrient = self.model.phosphorus_conc / (self.model.phosphorus_kp + self.model.phosphorus_conc)

        if light == 0:
            light_nutrient_growth_rate = self.growth_rate * nutrient
        elif nutrient ==0:
            light_nutrient_growth_rate = self.growth_rate * light
        else:
            light_nutrient_growth_rate = self.growth_rate * (light * nutrient)


        print(light_nutrient_growth_rate)
        B = self.biomass
        biomass_change = (light_nutrient_growth_rate * B * np.clip(1 - B/self.max_biomass, 0, 1))
        self.biomass = np.clip(B + biomass_change, 0, self.max_biomass)
