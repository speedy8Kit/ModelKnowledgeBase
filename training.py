import model_knowledge_base
import matplotlib.pyplot as plt
from itertools import product
from disease import DiseaseExemple, SignOfDiseaseExemple
from typing import TypedDict
import pandas as pd
import numpy as np

class PosiblePD(TypedDict):
    zdp:         list
    pd_duration: list[tuple[int]]


class InductivelyGeneratedKnowledgeBase(dict[str, list[PosiblePD]]):
    pass


class SignType(str):
    def __init__(self, s) -> None:
        if not (s in ['discrete', 'continuous']):
            raise TypeError('SignType')
        super().__init__(s)
        
        
def createArayDelimiters(original_array_length: int,
                         count_dilimetrs:       int ) -> list[int]:
    if count_dilimetrs == 0:
        return [[]]
    stop = [*range(original_array_length-count_dilimetrs, original_array_length)]
    arr  = []
    
    def create(word, i_let):
        while word[i_let] < stop[i_let]+1:
            if len(word) < count_dilimetrs:
                create([*word, word[-1]+1], i_let+1)
            else:
                arr.append(word.copy())
            word[i_let] += 1
    
    create([1], 0)
    
    return arr


def checkIntersections(a0: tuple[float, float],
                       a1: tuple[float, float] ) -> bool:
    a0 = sorted(a0)
    a1 = sorted(a1)
    ans = not (a0[1] < a1[0] or a1[1] < a0[0]) 
    return ans

class InductiveShapingModel():
    def __init__(self,
                 mkb:                       model_knowledge_base.ModelKnowledgeBase,
                 pd_count_max:              int,
                 count_mesurment_in_pd_max: int                                     ) -> None:
        self._rng                       = np.random.default_rng() 
        self.count_pd_max               = pd_count_max
        self.mkb                        = mkb
        self.count_mesurment_in_pd_max  = count_mesurment_in_pd_max

        self.posible_pd                 = {}
        first_example = self.mkb.createExample(count_mesurment_in_pd_max=self.count_mesurment_in_pd_max)
        for d in self.mkb.disease:
            self.posible_pd[f'{d.name}'] = {}
            for s in self.mkb.signs:
                self.posible_pd[f'{d.name}'][f'{s.name}'] = {}
        for disease_name in first_example:
            disease_exemple = first_example[disease_name]['signs_discrete']
            for sign_name in disease_exemple:
                self.posible_pd[disease_name][sign_name] = self.findePosiblePD(disease_exemple[sign_name], 'discrete')

            disease_exemple = first_example[disease_name]['signs_continuous']
            for sign_name in disease_exemple:
                self.posible_pd[disease_name][sign_name] = self.findePosiblePD(disease_exemple[sign_name], 'continuous')

    def findePosiblePD(self, 
                       exemple:   SignOfDiseaseExemple, 
                       sign_type: SignType             ) -> InductivelyGeneratedKnowledgeBase:
        arr_val         = exemple['value']
        arr_time        = exemple['time']
        igkb = {f'{pd_count+1}':[] for pd_count in range(self.count_pd_max)}
        
        for count_dilimetrs_pd in range(self.count_pd_max):
        
            delimiters_arr = createArayDelimiters(len(arr_val), count_dilimetrs_pd)

            for delimiters in delimiters_arr:
                
                delimiters.append(None)
                delimiter_prev = 0
                v = []
                
                for delimiter in delimiters:
                    
                    if sign_type == 'discrete':
                        v.append(set(arr_val[delimiter_prev:delimiter]))
                        delimiter_prev = delimiter
                        if len(v)<2:
                            continue
                        union_pd = v[-1] & v[-2]
                        if len(union_pd) != 0:
                            break
                    
                    elif sign_type == 'continuous':
                        sample = (arr_val[delimiter_prev:delimiter])
                        v.append((min(sample), max(sample)))
                        delimiter_prev = delimiter
                        if len(v)<2:
                            continue
                        
                        if checkIntersections(v[-2], v[-1]):
                            break
                        
                    else:
                        raise TypeError(f'{sign_type} not SignType')

                else:
                    delimiter_prev = 0
                    time = []
                    for delimiter in delimiters:
                        times = arr_time[delimiter_prev:delimiter]
                        delimiter_prev = delimiter
                        time.append((times[0], times[-1]))
                        
                    igkb[f'{count_dilimetrs_pd+1}'].append({'zdp': v, 'pd_duration': time})
        return igkb


    def unionPD(self,
                igkb_1: InductivelyGeneratedKnowledgeBase,
                igkb_2: InductivelyGeneratedKnowledgeBase,
                sign_type: SignType):

        def unionVal(arr1: list, arr2: list, sign_type: SignType):
            ans = []
            if sign_type == 'discrete':
                for a, b in zip(arr1, arr2):
                    ans.append(a | b)
                    if len(ans)<2:
                        continue
                    
                    union_pd = ans[-1] & ans[-2]
                    if len(union_pd) != 0:
                        return None
            elif sign_type == 'continuous':
                for a, b in zip(arr1, arr2):
                    temp = [*a, *b]
                    ans.append((min(temp), max(temp)))
                    if len(ans)<2:
                        continue
                    if checkIntersections(ans[-2], ans[-1]):
                        return None
            else:
                raise TypeError(f'{sign_type} not SignType')
                
            return ans
        
        
        def unionTime(arr1, arr2):
            ans = []
            for a, b in zip(arr1, arr2):
                all_val = [*a, *b]
                ans.append((min(all_val), max(all_val)))
            return ans
        
        
        ans = {}
        for count_pd in range(1, self.count_pd_max+1):
            ans[f'{count_pd}'] = []
            for combinations in product(igkb_1[f'{count_pd}'], igkb_2[f'{count_pd}']):
                union_val = unionVal(combinations[0]['zdp'], combinations[1]['zdp'], sign_type)
                if union_val is not None:
                    union_time = unionTime(combinations[0]['pd_duration'], combinations[1]['pd_duration'])
                    ans[f'{count_pd}'].append({'zdp': union_val, 'pd_duration': union_time})
        return ans

    
    def interpretPDTime(self,
                          arr: list[tuple[int, int]]):
        # [(1, 23), (3, 44), (20, 57), (24, 77)]
        ans = []
        for i in range(len(arr)):
            if i != 0:
                max = arr[i][1] - arr[i-1][1]
            else:
                max = arr[i][1]
                
            if i != len(arr)-1:
                min = arr[i+1][0] - arr[i][0]
            else:
                min = int(max / 2)
                
                
            ans.append((min, max))
        return ans

    def trainModel(self):
        example = self.mkb.createExample(count_mesurment_in_pd_max=self.count_mesurment_in_pd_max)
        for disease_name in example:
            
            disease_exemple = example[disease_name]['signs_discrete']
            for sign_name in disease_exemple:
                posible = self.findePosiblePD(disease_exemple[sign_name], 'discrete')
                self.posible_pd[disease_name][sign_name] = self.unionPD(self.posible_pd[disease_name][sign_name], posible, 'discrete')
                
            disease_exemple = example[disease_name]['signs_continuous']
            for sign_name in disease_exemple:
                posible = self.findePosiblePD(disease_exemple[sign_name], 'continuous')
                self.posible_pd[disease_name][sign_name] = self.unionPD(self.posible_pd[disease_name][sign_name], posible, 'continuous')

    def printIGKB(self):
        for desease_name in self.posible_pd:
            print(desease_name)
            for sign_name in self.posible_pd[desease_name]:
                print('\t', sign_name)
                for count_pd in self.posible_pd[desease_name][sign_name]:
                    print('\t\t', count_pd, ' периодов:')
                    for pd in self.posible_pd[desease_name][sign_name][count_pd]:
                        
                        print('\t\t\t', pd['zdp'], '  //  ' , self.interpretPDTime(pd['pd_duration']))
                 
                 
                 
    # !!!!!! Костыли, долго, некрасиво !!!!!!!
    def comparisonCountPD_IGKB_MKB(self):
        dta_1, data_2, data_3 = self.mkb.data_frame
        d = [x.name for x in self.mkb.disease for _ in self.mkb.signs]
        s = [x.name for _ in self.mkb.disease for x in self.mkb.signs]
        count_pd = [[data_2.loc[d_i, s_i] for d_i, s_i in zip(d, s)],
                    []]
        for d_i, s_i in zip(d, s):
            for i in range(self.count_pd_max, 0, -1):
                if len(self.posible_pd[d_i][s_i][f'{i}']) > 0:
                    break
            count_pd[1].append(i)
            
        a = pd.DataFrame(zip(count_pd[0], count_pd[1]), index=[d, s])
        a.columns     = ['ЧПД МБЗ', 'ИФБЗ']
        a.index.names = ['болезнь', 'признак']
        data_count_pd_match = a['ЧПД МБЗ'] == a['ИФБЗ']
        data_count_pd_match = \
            np.around(
                data_count_pd_match
                    .groupby(level=0)
                    .sum() / len(self.mkb.signs) * 100,
                1)

        return a, data_count_pd_match, np.around(np.mean(data_count_pd_match), 1)

    def comparisonZDP_IGKB_MKB(self):
        dta_1, data_2, data_3 = self.mkb.data_frame
        a = self.comparisonCountPD_IGKB_MKB()[0]
        data_check  = data_3.loc[a['ЧПД МБЗ'] == a['ИФБЗ']]
        mult_ind    = data_check.index
        tuples      = []
        zdp_igkb    = []
        zdp_mkb     = []
        for disease, sign, pd_num in mult_ind:
            pd_count = data_2.loc[disease, sign]
            for i, posible_answer in enumerate(self.posible_pd[disease][sign][f'{pd_count}']):
                zdp_igkb.append((np.array([*posible_answer['zdp'][pd_num-1]])))
                zdp_mkb.append(data_3.loc[(disease, sign, pd_num), 'ЗДП'])
                tuples.append((disease, sign, i+1, pd_num))
        
        mult_ind_2 = pd.MultiIndex.from_tuples(tuples, names=["заболевание", "признак","вариант решения", "номер ПД"])
        temp = pd.DataFrame(zip(zdp_igkb, zdp_mkb), index=mult_ind_2)
        temp = temp.sort_index(level=[0,1,2,3])
        
        temp.columns = ['ЗДП для ИФБЗ', 'ЗДП для МБЗ']
        
        mult_ind_disease_sign = temp.groupby(level=[0, 1]).count().index
        ans = []
        for disease, sign in mult_ind_disease_sign:
            sign_of_illness         = temp.loc[(disease, sign)]
            count_identica_matc     = 0
            count_igkb_subset_mkb   = 0
            count_mkb_subset_igkb   = 0
            count_else              = 0
            count_all               = 0
            for a in sign_of_illness.values:
                count_all += 1
                
                if sign.split()[0] == 'дискретный':
                    set_1, set_2 = set(a[0]), set(a[1])
                    if len(set_1) == len(set_2) == len(set_1 | set_2):
                        count_identica_matc   += 1
                    elif len(set_1 | set_2) == len(set_2):
                        count_igkb_subset_mkb += 1
                    elif len(set_1 | set_2) == len(set_1):
                        count_mkb_subset_igkb += 1
                    else:
                        count_else            += 1
                elif sign.split()[0] == 'непрерывный':
                    min_1, max_1 = a[0]
                    min_2, max_2 = a[1]
                    if min_1 == min_2 and max_1 == max_2:
                        count_identica_matc   += 1
                    elif min_2 <= min_1 <= max_1 <= max_2:
                        count_igkb_subset_mkb += 1
                    elif min_1 <= min_2 <= max_2 <= max_1:
                        count_mkb_subset_igkb += 1
                    else:
                        count_else            += 1
                    
                else:
                    raise TypeError("Я не знаю тип признака")
                
                
            ans.append(np.around(
                np.array([count_identica_matc, count_igkb_subset_mkb, count_mkb_subset_igkb, count_else]) / count_all * 100,
                1
                ))
        data_ans = pd.DataFrame(ans, index= mult_ind_disease_sign)
        data_ans.columns = ['совпадает', 'ИФБЗ подмножество МБЗ', 'МБЗ подмножество ИФБЗ', 'другое']
        return temp, data_ans
        
if __name__ == '__main__':
    mkb = model_knowledge_base.ModelKnowledgeBase(signs_count   = 3,
                                                  disease_count = 3 )
    mkb.generateSings(boundaries_value_exponent_cont = [2, 3],
                      part_discr_cont                = 0.5,
                      count_value_max_discr          = 10     )
    mkb.generateDisease(pd_count_max=3)
    
    model = InductiveShapingModel(mkb                          = mkb,
                                  pd_count_max                 = 3,
                                  count_mesurment_in_pd_max    = 2)
    
    for _ in range(0):
        model.trainModel()
    # model.printIGKB()
    # model.comparisonZDP_IGKB_MKB()
    print(*model.comparisonZDP_IGKB_MKB(), sep='\n\n')