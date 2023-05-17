import pandas as pd
import numpy as np


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
        self._rng = np.random.default_rng()
        self.name           = name
        self.possible_value = possible_value
        self.normal_value   = normal_value
    
    @property
    def data_frame(self) -> pd.DataFrame:
        if type(self) == SignDiscrete:
            values = [' '.join(map(str, self.possible_value))]
        elif type(self) == SignContinuous:
            values = f'[{np.around(self.val_min, self.decimal)}, {np.around(self.val_max, self.decimal)}]'
            
        t = ['Дискретный'] if type(self) == SignDiscrete \
                                     else ['Непрерывный']
        return pd.DataFrame({'признак'  : self.name,
                             'тип'      : t,
                             'ВЗ'       : values,
                             })

    def createSample(self, exeptions:list = [], boundaries_len_sample_in_percent: tuple[float, float] = [0.1, 0.5]):
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
    def __init__(self, name, possible_value: list, normal_value=None) -> None:
        if normal_value is None:
            normal_value = possible_value[0]
        super().__init__(name, normal_value, possible_value)
    
    def __str__(self) -> str:
        s = f'признак: "{self.name}" \n\t Возможные значения (ВЗ):' +\
            f'{self.possible_value} \n\t Нормалное значение (НЗ): {self.normal_value}'
        return s
    
    def createSample(self,
                     exeptions: list = [],
                     boundaries_len_sample_in_percent: tuple[float, float] = [0.1, 0.5]):
        
        
        for val in exeptions:
            if val not in self.possible_value:
                raise TypeError(f'вообщето y признака "{self.name}" значения "{val}"  нет...')
        possible_val_sample = [val for val in self.possible_value if val not in exeptions]
        
        count_possible_value = len(self.possible_value)
        
        len_samle_max = count_possible_value - len(exeptions)
        if len_samle_max < 1:
            raise TypeError(f'невозможно сгенерировать выборку из 0 экземпляров')

        count_min = np.ceil(boundaries_len_sample_in_percent[0] * count_possible_value)
        count_max = np.ceil(boundaries_len_sample_in_percent[1] * count_possible_value)
        if count_max > len_samle_max:
            count_max = len_samle_max
        if not (0 < count_min <= count_max <= len_samle_max):
            str_err = f'вообщето y признака "{self.name}" без {exeptions} нет ' +\
                      f'от {count_min} до {count_max} ' +\
                       'значений ...'
            raise TypeError(str_err)

        sample_len = self._rng.integers(count_min, count_max + 1)
        
        return self._rng.choice(possible_val_sample, sample_len, False)
 
  
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
    def __init__(self, name: str, val_min: float, val_max: float, normal_value = None) -> None:
        d = val_max - val_min
        self.decimal = -int(f'{d:e}'.split('e')[1]) + 2
        val_min = np.around(val_min, self.decimal)
        val_max = np.around(val_max, self.decimal)
        if normal_value is None:
            normal_value = np.mean([val_min, val_max])
        super().__init__(name, normal_value, [val_min, val_max])

    
    @property
    def val_min(self):
        return self.possible_value[0]
        
    @property
    def val_max(self):
        return self.possible_value[1]

    def __str__(self) -> str:
        s = f'признак "{self.name}" \n\t Возможные значения (ВЗ): [{self.val_min}, {self.val_max}] \n\t Нормалное значение (НЗ): {self.normal_value}'
        return s
        
    def createSample(self, 
                     exeption: tuple[float, float] = [], 
                     boundaries_len_sample_in_percent: tuple[float, float] = [0.1, 0.5]):
        
        boundaries_len_sample = [i * (self.val_max - self.val_min) for i in boundaries_len_sample_in_percent]

        if len(exeption) != 2:
            gap = [self.val_min, self.val_max]
        else:
            if not (self.val_min <= exeption[0] <= exeption[1] <= self.val_max):
                str_err = f'вообще-то призак "{self.name}" не включает промежуток {exeption},' + \
                          f'так как его границы [{self.val_min}, {self.val_max}]'
                raise TypeError(str_err)

            gaps  = [[self.val_min, exeption[0]], [exeption[1], self.val_max]]
            delta = [exeption[0] - self.val_min, self.val_max - exeption[1]]
            ind = self._rng.choice([0, 1], p = delta/np.sum(delta))
            gap   = gaps[ind] \
                    if      np.min(delta) > boundaries_len_sample[0] \
                    else    gaps[np.argmax(delta)]

        if boundaries_len_sample[0] > (gap[1] - gap[0]):
            str_err = f'вообщето призак "{self.name}" с границами [{self.val_min}, {self.val_max}] не имеет неприрывного' +\
                      f'промежутка длиной хотябы"{boundaries_len_sample[0]}", так чтобы он не пересекался с {exeption}'
            raise TypeError(str_err)
        
        if boundaries_len_sample[1] > (gap[1] - gap[0]):
            boundaries_len_sample[1] = gap[1] - gap[0]
            
        sample_len = np.around(self._rng.uniform(boundaries_len_sample[0], boundaries_len_sample[1]), self.decimal)
        sample_start = np.around(self._rng.uniform(gap[0] , gap[1] - sample_len), self.decimal)
        return [sample_start, sample_start + sample_len]
    
    
if __name__ == '__main__':
    def checkSignDiscrete(is_print):
        sign_enumerable = SignDiscrete(name = 'цвет лица',
                             possible_value = ['1', '2', '3', '4', '5',
                                            '11', '22', '33', '44', '55', '66'],
                               normal_value = 'нормальный')
        if is_print: 
            print(sign_enumerable)
            v = []
            for _ in range(3):
                v = sign_enumerable.createSample(v, [0.1, 0.3])
                print(v)
        is_correct = sign_enumerable.name = 'цвет лица'
        return is_correct
    
    def checkSignContinuous(is_print):
        sign_interval = SignContinuous(name = 'температура', 
                                    val_min = 27,
                                    val_max = 42,
                               normal_value = [35.5, 37.2])
        if is_print:
            v = []
            for _ in range(3):
                v = sign_interval.createSample(v, [0.1, 0.3])
                print(v[1]-v[0])
        
        return True
    
    if not checkSignDiscrete(False):
        print('error checkSignDiscrete')
    if not checkSignContinuous(False):
        print('error checkSignContinuous')

