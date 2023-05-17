
from faker import Faker
fake = Faker()
import numpy as np
import pandas as pd
import disease as dis
import sign as sig
from typing import TypedDict


class ModelKnowledgeBase():
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
        self._disease_count   = disease_count
        self._signs_count     = signs_count
        self._sings_discrete  = []
        self._signs_continous = []
        self.disease          = None
        self._rng             = np.random.default_rng()
    
    @property
    def signs(self):
        return self._sings_discrete + self._signs_continous

    @property
    def data_frame(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: 
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
            data_pd_temp.insert(0, 'заболевание', [d.name for _ in range(len(data_pd_temp.index))])
            data_pd = pd.concat([data_pd, data_pd_temp])
        
        data_pd      = data_pd.set_index(['заболевание', data_pd.index])
        data_disease.index.name = 'заболевание'
        
        # index = pd.MultiIndex.from_tuples((['ЧПД для признака' for _ in range(len(data_disease.columns))],
        #                                   data_disease.columns))
        # data_disease.columns = index
        
        return data_signs, data_disease, data_pd
    
    def generateSings(self,
                      part_discr_cont:                float               = 0.5,
                      count_value_max_discr:          int                 = 20,
                      boundaries_value_mean_cont:     tuple[float, float] = [-10, 10],
                      boundaries_value_exponent_cont: tuple[float, float] = [-4, 2]):
        
        sings_discrete_count    = int(self._signs_count * part_discr_cont)
        signs_continous_count   = self._signs_count - sings_discrete_count
        
        if not (boundaries_value_mean_cont[0] <= boundaries_value_mean_cont[1]):
            raise KeyError('ваш boundaries_value_mean_cont - полный бред')
        if not (-5 <= boundaries_value_exponent_cont[0] <= boundaries_value_exponent_cont[1] < 6):
            raise KeyError('ваш boundaries_value_mean_cont - полный бред')
        
        
        self._sings_discrete = [sig.SignDiscrete(name = f'дискретный {i+1}',
                                       possible_value = list(range(self._rng.integers(2,  count_value_max_discr+1))),
                                         normal_value = 0) 
                               for i in range(sings_discrete_count)]

        val_mean = self._rng.random(size=signs_continous_count) * (boundaries_value_mean_cont[1] - boundaries_value_mean_cont[0]) \
            + boundaries_value_mean_cont[0]
        
        # rand*10^rand_exponent
        val_delt = self._rng.random(size=signs_continous_count) * \
                   np.power(10, self._rng.integers(low = boundaries_value_exponent_cont[0],
                                                  high = boundaries_value_exponent_cont[1]+1,
                                                  size = signs_continous_count), dtype = np.float64) 
        val_min = val_mean - val_delt / 2
        val_max = val_mean + val_delt / 2

        self._signs_continous = [sig.SignContinuous(name = f'непрерывный {i+1}',
                                                 val_min = val_bound[0],
                                                 val_max = val_bound[1],
                                            normal_value = (val_bound[0] + val_bound[1])/2) 
                               for i, val_bound in enumerate(zip(val_min, val_max))]
        
    def generateDisease(self, *, pd_count_max = 5, pd_len_max = 25) -> dict:
        if len(self.signs) < self._signs_count:
            self.generateSings()
        periods_dynamics = np.array([[dis.PeriodsDynamic(pd_count_max = pd_count_max,
                                                           pd_len_max = pd_len_max) 
                                        for _ in range(self._signs_count)] 
                                            for _ in range(self._disease_count)])
        
        sign_of_disease = np.array([[dis.SignOfDisease(sign=sign, periods_dynamic=per_d) 
                                        for sign, per_d in zip(self.signs, periods_dynamic)] 
                                            for periods_dynamic in periods_dynamics])
        
        self.disease = [dis.Disease(f'болезнь {i}', signs=sings) for i, sings in enumerate(sign_of_disease)]

    def createExample(self, *, count_mesurment_in_pd_max = 3) -> dict[str, dis.DiseaseExemple]:
        if self.disease is None:
            self.generateDisease()
        exemple_disease_arr = {}
        for dis in self.disease:
            
            exemple_disease_arr[f'{dis.name}'] = dis.createExample(count_mesurment_in_pd_max=count_mesurment_in_pd_max)
        
        return exemple_disease_arr            


if __name__ == '__main__':
    def checClinicalPicture(is_print: bool):

        g = ModelKnowledgeBase(signs_count=6, disease_count=3)

        g.generateSings()
        g.generateDisease()
        
        if is_print:
            print('Заболевание:')
            a = g.createExample()
            print(*a.values(), sep = '\n')
            a, b, c = g.data_frame
            print(c)

    checClinicalPicture(True)
    
    print(dis.DiseaseExemple.__required_keys__)





    