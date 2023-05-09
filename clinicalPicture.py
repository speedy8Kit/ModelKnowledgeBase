
from faker import Faker
fake = Faker()
import numpy as np
import pandas as pd
import disease as dis
import sign as sig

class ClinicalPicture():
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
        self.disease                = None
    
    @property
    def signs(self):
        return self._sings_discrete + self._signs_continous

    @property
    def data_frame(self):
        data_signs : pd.DataFrame = self.disease[0].data_frame[0]
        data_signs  = data_signs.loc[:, data_signs.columns != 'ЧПД']
        
        data_disease    = pd.DataFrame()
        data_pd         = pd.DataFrame()
        for d in self.disease:
            data_disease_temp = d.data_frame[0].loc[:, ['ЧПД']]
            data_disease_temp = data_disease_temp.T
            data_disease_temp.index = [f'{d.name}']
            data_disease = pd.concat([data_disease, data_disease_temp])
            
            data_pd_temp = d.data_frame[1]
            data_pd_temp.insert(0, 'заболевание', [d.name for i in range(len(data_pd_temp.index))])
            data_pd = pd.concat([data_pd, data_pd_temp])
        
        data_pd      = data_pd.set_index(['заболевание', data_pd.index])
        data_disease.index.name = 'заболевание'
        index = pd.MultiIndex.from_tuples(zip(['ЧПД для признака' for _ in range(len(data_disease.columns))],
                                          data_disease.columns))
        data_disease.columns = index
        
        return data_signs, data_disease, data_pd
    
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
        
        
        self._sings_discrete = [sig.SignDiscrete(name = f'дискретный {i+1}',
                                            possible_value = list(range(rng.integers(2,  value_count_max+1))),
                                              normal_value = 0) 
                               for i in range(sings_discrete_count)]

        val_mean = rng.random(size=signs_continous_count) * (value_mean_boundaries[1] - value_mean_boundaries[0]) \
            + value_mean_boundaries[0]
        
        # rand*10^rand_exponent
        val_delt = rng.random(size=signs_continous_count) * \
                   np.power(10, rng.integers(low = value_exponent_boundaries[0],
                                            high = value_exponent_boundaries[1]+1,
                                            size = signs_continous_count), dtype = np.float64) 
        val_min = val_mean - val_delt / 2
        val_max = val_mean + val_delt / 2

        self._signs_continous = [sig.SignContinuous(name = f'непрерывный {i+1}',
                                             val_min = val_bound[0],
                                             val_max = val_bound[1],
                                        normal_value = (val_bound[0] + val_bound[1])/2) 
                               for i, val_bound in enumerate(zip(val_min, val_max))]
        
    def generateDisease(self):
        if len(self.signs) < self._signs_count:
            self.generateSings()
        periods_dynamics = np.array(list([dis.PeriodsDynamic() for _ in range(self._signs_count)] 
                                              for _ in range(self._disease_count)))
        
        sign_of_disease = np.array([[dis.SignOfDisease(sign=sign, periods_dynamic=per_d) 
                for sign, per_d in zip(self.signs, periods_dynamic)] 
                    for periods_dynamic in periods_dynamics])
        
        self.disease = [dis.Disease(f'болезнь {i}', signs=sings) for i, sings in enumerate(sign_of_disease)]

    def createExample(self):
        if self.disease is None:
            self.generateDisease
        exemple_disease_arr = [dis.createExample() for dis in self.disease]
        
        return exemple_disease_arr            


if __name__ == '__main__':
    def checClinicalPicture(is_print: bool):
            
        g = ClinicalPicture(signs_count=6, disease_count=3)

        g.generateSings()
        g.generateDisease()
        
        if is_print:
            print('Заболевание:')
            print(*g.createExample(), sep='\n\nЗаболевание:\n')
            a, b, c = g.data_frame
            
            print(c['болезнь 0'])

    checClinicalPicture(True)
    