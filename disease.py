import pandas as pd
import numpy as np
import random

import sign as sign


class PeriodsDynamic():
    '''Unique value for each symptom and disease
    
    Attributes
    ----------
    
    1 <= periods_dynamics_count <= 5: int
        the number of intervals where each has a length of
        at least period_time_min and no more than period_time_max
    time_period_boundaries: tuple[int, int]
        gap list [[period_0_time_min, period_0_time_max], [period_1_time_min, period_1_time_max], ...]
        1 <= period <= 24
    '''
    def __init__(self,
                 period_time_boundaries: tuple[int, int] | None = None) -> None:
        if period_time_boundaries is None:
            pd_count_min = 1
            pd_count_max = 5
            pd_len_range = range(1, 25)
            rng = np.random.default_rng()
            
            pd_count = rng.integers(pd_count_min, pd_count_max+1)
            period_time_boundaries = [sorted(rng.choice(a = pd_len_range,
                                                     size = 2,
                                                  replace = False)) for _ in range(pd_count)]
        
        if not (1 <=  len(period_time_boundaries) <= 5): 
            raise TypeError("что за фигня c количеством periods_dynamics?!?")

        for period in period_time_boundaries:
            if not (1 <= period[0] < period[1] <= 24):
                raise TypeError("что за фигню в ограничения period_time напихали?!?")

        self.period_time_boundaries = np.array(period_time_boundaries)
        
        
    def __str__(self) -> str:
        s = ''
        for v in self.period_time_boundaries:
            s += f'НГ: {v[0]:<4}, ВГ: {v[1]:<4}'
            s += ';\n'
        s = s[:-2]
        s += '.'
        return s
    
    @property
    def data_frame(self):
        print(self.period_time_boundaries[:][0])
        data = pd.DataFrame({'НГ': self.period_time_boundaries[:, 0],
                             'ВГ': self.period_time_boundaries[:, 1]})
    
        return data
    
    @property
    def pd_count(self):
        return len(self.period_time_boundaries)
        
    def createMeasurementTimes(self):
        period_count = len(self.period_time_boundaries)
        
        pd_times = np.array([random.randint(period_time[0], period_time[1]) 
                             for period_time in self.period_time_boundaries])
        
        # it may turn out that for the selected duration of the dynamic period it is impossible to perform 3 measurements
        measurements_in_pd_count_max = np.where(pd_times > 3, 3, pd_times)
        # select the number of measurements for the period, taking into account the maximum possible
        measurements_in_pd_count = [random.randint(1, max) for max in measurements_in_pd_count_max]
        
        # select the time for each measurement on the entire time axis grouped by periods of dynamics
        measurement_times = [np.sort(random.sample(range(1, pd_times[i]+1), measurements_in_pd_count[i])) 
                             for i in range(period_count)]
        time_summary = 0
        for i, el in enumerate(measurement_times):
            measurement_times[i], time_summary = el + time_summary, time_summary + pd_times[i]
            
        return measurement_times

class SignOfDisease():
    def __init__(self, sign: sign.Sign, periods_dynamic: PeriodsDynamic, exemple_count_boundaries= None) -> None:
        self.sign                       = sign
        self.periods_dynamic            = periods_dynamic
        sign_for_pd_prev = None
        self.sign_for_pd = []
        for i in range(len(self.periods_dynamic.period_time_boundaries)):
            self.sign_for_pd.append(self.sign.createExamples(sign_for_pd_prev, exemple_count_boundaries))
            sign_for_pd_prev = self.sign_for_pd[i]
            # print(sign_for_pd_prev)
            
    
    def __str__(self) -> str:
            
        s = f'Признак: {self.sign.name:14s}\n'
        s1 = f'\t| НГ | ВГ |'
        s2 = '\t' + '|' + '-'*4 + '+' + '-'*4 + '+'
        s3 = ''
        
        s += f'ЧПД: {self.periods_dynamic.pd_count}\n'
        if type(self.sign) == sign.SignContinuous:
            dec = self.sign.decimal
            min = np.around(self.sign.val_min, dec)
            delta = np.around(self.sign.val_max - self.sign.val_min, dec)
            s += f'ВЗ: min = {min:.{dec}f}\t delta = '
            s += f'{delta:.{dec}f}\n'
            # s += f'\t {self.sign.val_min} {self.sign.val_max}'
            cel = len(f'{delta}')
            temp = 'ЗДП - min'
            s1 += f'{temp:^{cel*2+6}}' + '|\n'
            s2 += '-' *(cel*2+6) + '|' + '\n'
            
            for sign, boundaries in zip(self.sign_for_pd, self.periods_dynamic.period_time_boundaries):
                s3 += f'\t|{boundaries[0]:^4d}|'
                s3 += f'{boundaries[1]:^4d}|'
                s3 += f' [{np.around(sign[0] - self.sign.val_min, dec):>{cel}.{dec}f}, '
                s3 += f'{np.around(sign[1] - self.sign.val_min, dec):>{cel}.{dec}f}] |\n'


                # for s in sign:
                #     s += f'{s:3e}'
                # s += f']'
        else:
            s += f'ВЗ: {self.sign.possible_value}\n'
            l = len(f'{self.sign.possible_value}')
            s2 += '-'*20 + '\n'
            for sign, boundaries in zip(self.sign_for_pd, self.periods_dynamic.period_time_boundaries):
                s3 += f'\t|{boundaries[0]:^4d}|'
                s3 += f'{boundaries[1]:^4d}|'
                s3 += f'\t{sign} |\n'
            temp = 'ЗДП'
            s1 += f'{temp:^{l}}' + '|\n'
        s += s1 + s2 + s3
        return s
       
    def createExample(self):
        moments_verification = self.periods_dynamic.createMeasurementTimes()
        return moments_verification

class Disease():
    def __init__(self, name, signs: tuple[SignOfDisease]) -> None:
        self.name = name
        self.signs = signs
        
    def __str__(self) -> str:
        s = f'Боезнь: {self.name} \n'
        for sign in self.signs:
            for line in sign.__str__().splitlines():
                s += '\t' + line + '\n'
            s += '\n'
        return s

del pd, np, random, sign
