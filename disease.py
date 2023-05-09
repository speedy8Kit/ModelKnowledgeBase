import pandas as pd
import numpy as np
import random

import sign as sig


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
                 period_time_boundaries: list[tuple[int, int]] | None = None) -> None:
        if period_time_boundaries is None:
            pd_count_min = 1
            pd_count_max = 5
            pd_len_range = range(1, 25)
            rng = np.random.default_rng()
            
            pd_count = rng.integers(pd_count_min, pd_count_max+1)
            period_time_boundaries = [sorted(rng.choice(a = pd_len_range,
                                                     size = 2,
                                                  replace = False)) for _ in range(pd_count)]

        if not (1 <=  len(period_time_boundaries)): 
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
    def __init__(self, sign: sig.Sign, periods_dynamic: PeriodsDynamic, exemple_count_boundaries= None) -> None:
        self._rng = np.random.default_rng()
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
        if type(self.sign) == sig.SignContinuous:
            dec = self.sign.decimal
            min = np.around(self.sign.val_min, dec)
            delta = np.around(self.sign.val_max - self.sign.val_min, dec)
            s += f'ВЗ: min = {min:.{dec}f}\t delta = '
            s += f'{delta:.{dec}f}\n'
            # s += f'\t {self.sign.val_min} {self.sign.val_max}'
            cel = len(f'{delta}') + 3
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
            l_max = 3
            for sign in self.sign_for_pd:
                l = len(f'{sign}')
                l_max = l_max if l_max > l else l
            
            for sign, boundaries in zip(self.sign_for_pd, self.periods_dynamic.period_time_boundaries):
                s3 += f'\t|{boundaries[0]:^4d}|'
                s3 += f'{boundaries[1]:^4d}|'
                temp = f'{sign}'
                s3 += f'{temp:<{l_max}} |\n'
                
            temp = 'ЗДП'
            s1 += f'{temp:^{l_max+1}}' + '|\n'
            s2 += '-'*(l_max+1) + '|\n'
        s += s1 + s2 + s3
        return s
    
    @property
    def data_frame(self):
        if type(self.sign) == sig.SignContinuous:
            sfpd = np.around(self.sign_for_pd, self.sign.decimal)
            # sfpd = self.sign_for_pd
            
        else:
            sfpd = self.sign_for_pd

        temp_1 = pd.DataFrame({'ЧПД': [self.periods_dynamic.pd_count]})
        temp_2 = pd.DataFrame({'ЗДП': list(sfpd)})
        return self.sign.data_frame.join(temp_1), self.periods_dynamic.data_frame.join(temp_2)
    
    def createExample(self) -> list[tuple[int]]:
        
        moments_verification = self.periods_dynamic.createMeasurementTimes()
        l = (sum([len(m) for m in moments_verification]))
        exemples_arr = [None for _ in range(l)]
        moments_arr  = [None for _ in range(l)]
        i = 0
        for mv, s_pd in zip(moments_verification, self.sign_for_pd):
            if type(self.sign) == sig.SignContinuous:
                a = self._rng.uniform(s_pd[0], s_pd[1], len(mv))
            elif type(self.sign) == sig.SignDiscrete:
                a = self._rng.choice(s_pd, len(mv))
            for j, val in enumerate(zip(mv, a)):
                moments_arr[i+j] = val[0]
                exemples_arr[i+j] = val[1]
            i += j + 1

        return (moments_arr, exemples_arr)

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
    
    @property
    def data_frame(self):
        data_disease = pd.DataFrame()
        data_pd      = pd.DataFrame()
        for sign in self.signs:
            data_disease_temp = (sign.data_frame[0])
            data_disease = pd.concat([data_disease, data_disease_temp], ignore_index=True)
            
            data_pd_temp = sign.data_frame[1]
            data_pd_temp.insert(1, 'признак', [sign.sign.name for i in range(len(data_pd_temp.index))])
            
            data_pd      = pd.concat([data_pd, data_pd_temp])
        
        data_disease = data_disease.set_index('признак')
        # mult_ind = data_pd.index.values 
        data_pd.index.name = 'номер ПД'
        data_pd = data_pd.set_index(['признак', data_pd.index])

        return data_disease, data_pd
    
    def createExample(self):
        
        example_disease = [sign.createExample() for sign in self.signs]

        return example_disease

# #######################################################################################



if __name__ == '__main__':
    def checkPeriodsDynamic(is_print: bool):
        p_d = PeriodsDynamic()
        p_d = PeriodsDynamic([(1, 10), (1,10)])
        max = 0
        min = 22
        
        test_1 = True
        test_2 = True
        for _ in range(10000):
            val = p_d.createMeasurementTimes()
            max = max if max > val[0][-1] else val[0][-1]
            min = min if min < val[1][0] else val[1][0]
            
            test_1 = test_1 and np.array_equal(val[0], np.sort(val[0]))
            test_1 = test_1 and np.array_equal(val[1], np.sort(val[1]))
            test_2 = test_2 and (val[0][-1] < val[1][0])
            

        test_3 = min-1==1 and max==10
        test = (test_1 and test_2 and test_3)
        if not is_print:
            return test
        
        for _ in range(10):
            s = ''
            for ar in p_d.createMeasurementTimes():
                temp = f'{ar}'
                s += f'{temp:>15}'
                print(s)

        return test
    

    def checkSignOfDisease(is_print: bool):
        sign_interval_1     = sig.SignContinuous(name = 'температура', 
                                            val_min = 27,
                                            val_max = 42,
                                        normal_value = [35.5, 37.2])
        sign_enumerable_1   = sig.SignDiscrete(name = 'цвет лица',
                                    possible_value = ['1', '2', '3', '4', '5',
                                                    '11', '22', '33', '44', '55', '66'])
        pdi = [PeriodsDynamic() for _ in range(2)]
        
        sod = [SignOfDisease(sign, pdi_i) for pdi_i, sign in zip(pdi, [sign_interval_1, sign_enumerable_1])]
        test = True

        def test_in(val, index_pd):

            if type(sod[i].sign) == sig.SignContinuous:
                boundaries = sod[i].sign_for_pd[index_pd]
                is_in = boundaries[0] <= val <= boundaries[1]
            else: 
                is_in =  val in sod[i].sign_for_pd[index_pd]
            return is_in
        
        for i in range(2):
            for _ in range(100):
                ex = sod[i].createExample()
                index_pd = 0
                for measurement in ex[1]:
                    if test_in(measurement, index_pd):
                        continue

                    index_pd += 1
                    if index_pd > len(sod[i].sign_for_pd):
                        test = False
                    else:
                        test = test and test_in(measurement, index_pd)
        
        
        if is_print:
            for i in range(2):
                for _ in range(1):
                    # print(*sod[i].data_frame, sep='\n\n')
                    print(*sod[i].createExample(), sep='\n')
                    print()
                print(*sod[i].data_frame, sep='\n\n')
                print('='*30)
                
        return test
    
    def checkDisease(is_print: bool):
        sign_interval_1     = sig.SignContinuous(name = 'температура', 
                                              val_min = 27,
                                              val_max = 42,
                                         normal_value = [35.5, 37.2])
        sign_enumerable_1   = sig.SignDiscrete(name = 'цвет лица',
                                     possible_value = ['1', '2', '3', '4', '5',
                                                       '11', '22', '33', '44', '55', '66'],
                                       normal_value = 'нормальный')
        pdi = [PeriodsDynamic() for _ in range(2)]

        sod_1 = SignOfDisease(sign_interval_1, pdi[0])
        sod_2 = SignOfDisease(sign_enumerable_1, pdi[1])
        
        dis = Disease('боль', [sod_1, sod_2])
        
        if is_print:
            print(dis.createExample())
            print(*dis.data_frame, sep='\n')
        return True
        
        
    if not checkPeriodsDynamic(False):
        print('error checkPeriodsDynamic')
    if not checkSignOfDisease(True):
        print('error checkSignOfDisease')
    if not checkDisease(False):
        print('error checkDisease')


# del pd, np, random, sign
