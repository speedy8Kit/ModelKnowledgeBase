import pandas as pd
import numpy as np
import random

class Sign():
    '''measurable characteristic for a person
    
    Attributes
    ----------
    name: str
        parameter name must be unique
    normal_value
        the most common trait value for a normal person
    
    Methods
    ----------
    createValue()
        requires redefinition is used to create an arbitrary attribute value
    '''
    def __init__(self, name: str, normal_value, possible_value) -> None:
        self.name           = name
        self.possible_value = possible_value
        self.normal_value   = normal_value
    
    @property
    def data_frame(self) -> pd.DataFrame:
        values = [' '.join(map(str, self.possible_value))]
        return pd.DataFrame({'признак': self.name,
                             'ВЗ': values,
                             })

    def createExamples(self, exeption:list = None, exemple_count_boundaries: int = None):
        pass
    

class SignDiscrete(Sign):
    '''measurable characteristic for a person
    
    Attributes
    ----------
    name: str
        parameter name must be unique
    possible_value: list
    normal_value: possible_value[i]
        the most common trait value for a normal person
    '''
    def __init__(self, name, possible_value: list, normal_value) -> None:
        super().__init__(name, normal_value, possible_value)
        self._rng = np.random.default_rng()
    
    def __str__(self) -> str:
        s = f'признак: "{self.name}" \n\t Возможные значения (ВЗ):\
            {self.possible_value} \n\t Нормалное значение (НЗ): {self.normal_value}'
        return s
    
    def __dataframe__(self) -> pd.DataFrame:
        return super().__dataframe__()
    
    def createExamples(self, exeption: list = None, exemple_count_boundaries: tuple[int, int] = None):
        rng = self._rng
        exeptions_count = len(exeption) if exeption else 0
        posible_count_max = len(self.possible_value) - exeptions_count
        
        if not exemple_count_boundaries:
            count_min = np.ceil(len(self.possible_value) * 0.1)
            count_max = len(self.possible_value) - count_min 
            count_max = posible_count_max if posible_count_max < count_max else count_max
            exemple_count_boundaries = [count_min, count_max]
            
        elif not (0 < exemple_count_boundaries[0] <= posible_count_max):
            raise TypeError(f'вообщето y признака "{self.name}" нет "{exemple_count_boundaries}" значений ...')
        
        exemple_count = random.randint(exemple_count_boundaries[0], exemple_count_boundaries[1])
        if not exeption:
            return random.sample(self.possible_value, exemple_count)
        for val in exeption:
            if val not in self.possible_value:
                raise TypeError(f'вообщето y признака "{self.name}" значения "{val}"  нет...')

            
        possible = [val for val in self.possible_value if val not in exeption]

        return random.sample(possible, exemple_count)
    
        
class SignContinuous(Sign):
    '''measurable characteristic for a person
    
    Attributes
    ----------
    name: str
        parameter name must be unique
    min\max_val: float?
    normal_value
        the most common trait value for a normal person
    '''
    def __init__(self, name: str, val_min: float, val_max: float, normal_value) -> None:
        
        # self.val_min = val_min
        # self.val_max = val_max
        d = val_max - val_min
        self.decimal = -int(f'{d:e}'.split('e')[1])+3
        super().__init__(name, normal_value, [val_min, val_max])
        
        self._rng = np.random.default_rng()
    
    @property
    def val_min(self):
        return self.possible_value[0]
        
    @property
    def val_max(self):
        return self.possible_value[1]
    
    def __str__(self) -> str:
        s = f'признак "{self.name}" \n\t Возможные значения (ВЗ): [{self.val_min}, {self.val_max}] \n\t Нормалное значение (НЗ): {self.normal_value}'
        return s
        
    def createExamples(self, exeption: tuple[float, float] = None, exemple_count_boundaries: tuple[float, float] = None):
        if exemple_count_boundaries is None:
            min_val = 0.1 * (self.val_max - self.val_min)
            max_val = self.val_max - self.val_min - min_val * 2
            exemple_count_boundaries = [min_val, max_val]
        # print(exeption, exemple_count_boundaries, [self.val_min, self.val_max])
        if exeption is None:
            gap = [self.val_min, self.val_max]
        elif not (self.val_min <= exeption[0] <= exeption[1] <= self.val_max):
            str_err = f'вообщето призак "{self.name}" не включает промежуток {exeption}, так как его границы' + \
                              f'[{self.val_min}, {self.val_max}]'
            raise TypeError(str_err)
        else:
            gaps  = [[self.val_min, exeption[0]], [exeption[1], self.val_max]]
            delta = [exeption[0] - self.val_min, self.val_max - exeption[1]]
            # print(delta)
            ind = self._rng.choice([0, 1], p = delta/np.sum(delta))
            gap   = gaps[ind] \
                    if      np.min(delta) > exemple_count_boundaries[0] \
                    else    gaps[np.argmax(delta)]

        # print(f'{gap=}')
        # print(f'{exemple_count_boundaries=}')
        if exemple_count_boundaries[0] > (gap[1] - gap[0]):
            str_err = f'вообщето призак "{self.name}" с границами [{self.val_min}, {self.val_max}] не имеет неприрывного' + \
                        f'промежутка длиной "{exemple_count_boundaries[0]}", так чтобы он не пересекался с {exeption}'
            raise TypeError(str_err)
        if exemple_count_boundaries[1] > (gap[1] - gap[0]):
            exemple_count_boundaries[1] = gap[1] - gap[0]
            
        exemple_count = exemple_count_boundaries[0] + random.random() * (exemple_count_boundaries[1] - exemple_count_boundaries[0])

        posible_max_count = gap[1] - gap[0] - exemple_count
        
        
        posible = gap[0] + (random.random() * posible_max_count)
        # if posible - self.val_min < exemple_count_boundaries[0] or \
        #    self.val_max  - (posible + exemple_count) < exemple_count_boundaries[0]:
        #     return self.createExample(exeption, exemple_count_boundaries)
        # print(f'{[posible, posible + exemple_count]}')

        return [posible, posible + exemple_count]

