import numpy as np
from scipy.stats import cosine

class Illumination:
    def __init__(self, day_fraction=0.65, diel_length=1440): #1440 is total minutes in a day
        self.day_fraction = day_fraction
        self.diel_length = diel_length

        day_fraction = float(day_fraction)
        if not (0 < day_fraction < 1):
            raise ValueError("Day fraction should be between 0 and 1")

        #: fraction of diel period that is illuminated
        self.day_fraction = day_fraction
        #: numer of minutes in the illuminated fraction
        self.hours_day = day_fraction * self.diel_length

        C = 1.0 / np.sqrt(2 * np.pi)
        # to scale the cosine distribution from 0 to 1 (at zenith)

        self._profile = cosine(loc=self.hours_day / 2, scale=C ** 2 * self.hours_day)

    def get_intensity(self, time):
        """
        Get light intensity based on `time` in hours
        """
        daytime = time % self.diel_length
        # normalize to by max value of distrib
        return self._profile.pdf(daytime) / self._profile.pdf(self.hours_day / 2)
