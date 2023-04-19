
from faker import Faker
fake = Faker()
import numpy as np

import disease as d


class GeneratorDisease():
    '''
    A class for creating an intellectual knowledge base allows
    you to separately form signs and diseases with created signs
    
    Attributes
    ----------
    disease_count: int
    signs_count: int
    sings_discrete_part: float

    ----------
    createValue()
        requires redefinition is used to create an arbitrary attribute value
    '''
    
    def __init__(self,  disease_count: int = 2, signs_count: int = 6) -> None:
        self._disease_count         = disease_count
        self._signs_count           = signs_count
        self._sings_discrete        = []
        self._signs_continous       = []
    
    @property
    def signs(self):
        return self._sings_discrete + self._signs_continous


    def generateSings(self,
                      sings_discrete_part:          float                           = 0.5,
                      value_count_max:              int                             = 20,
                      value_mean_boundaries:        tuple[float, float]             = [-10, 10],
                      value_exponent_boundaries:    tuple[float, float]             = [-4, 2]):
        rng                     = np.random.default_rng()
        sings_discrete_count    = int(self._signs_count * sings_discrete_part)
        signs_continous_count   = self._signs_count - sings_discrete_count
        
        if not (value_mean_boundaries[0] <= value_mean_boundaries[1]):
            raise KeyError('ваш value_start_boundaries - полный бред')
        if not (-5 <= value_exponent_boundaries[0] <= value_exponent_boundaries[1] < 4):
            raise KeyError('ваш value_exponent_boundaries - полный бред')
        
        
        self._sings_discrete = [d.SignDiscrete(name = f'дискретный {i+1}',
                                   possible_value = list(range(rng.integers(2,  value_count_max+1))),
                                     normal_value = 0) 
                               for i in range(sings_discrete_count)]

        val_mean = rng.random(size=signs_continous_count) * (value_mean_boundaries[1] - value_mean_boundaries[0]) + value_mean_boundaries[0]
        
        # rand*10^rand_exponent
        val_delt = rng.random(size=signs_continous_count) * \
                   np.power(10, rng.integers(low = value_exponent_boundaries[0],
                                            high = value_exponent_boundaries[1]+1,
                                            size = signs_continous_count), dtype = np.float64) 
        val_min = val_mean - val_delt / 2
        val_max = val_mean + val_delt / 2

        self._signs_continous = [d.SignContinuous(name = f'непрерывный {i+1}',
                                             val_min = val_bound[0],
                                             val_max = val_bound[1],
                                        normal_value = (val_bound[0] + val_bound[1])/2) 
                               for i, val_bound in enumerate(zip(val_min, val_max))]
        
    def generateDisease(self):
        if len(self.signs) < self._signs_count:
            self.generateSings()
        self.periods_dynamics = np.array(list([d.PeriodsDynamic() for _ in range(self._signs_count)] 
                                              for _ in range(self._disease_count)))
        
        # print(self.periods_dynamics.shape)
        signs = [d.SignOfDisease(sign=sign, periods_dynamic=pd) 
             for sign, pd in zip(self.signs, self.periods_dynamics[0])]
        
        d = d.Disease('болезнь 1', signs=signs)
        
        print(self.periods_dynamics[0,0])
        print(self.periods_dynamics[0,0].data_frame)
        


if __name__ == '__main__':
    g = GeneratorDisease(signs_count=10)

    g.generateSings()
    g.generateDisease()
    print(g._signs_continous[0].data_frame)