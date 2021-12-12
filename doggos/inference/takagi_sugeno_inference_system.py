from typing import Dict, List, Callable, Iterable

import numpy as np
import pandas as pd

from doggos.fuzzy_sets.fuzzy_set import MembershipDegree
from doggos.inference.inference_system import InferenceSystem
from doggos.knowledge import Rule
from doggos.knowledge.linguistic_variable import LinguisticVariable
from doggos.knowledge.clause import Clause


class TakagiSugenoInferenceSystem(InferenceSystem):
    """
    Class used to represent a takagi-sugeno inference system:
    https://www.mathworks.com/help/fuzzy/types-of-fuzzy-inference-systems.html

    Attributes
    --------------------------------------------
    _rule_base: Iterable[Rule]
        fuzzy rule base used for inference

    Methods
    --------------------------------------------
    infer(self, defuzzification_method: Callable,
          features: Dict[Clause, List[MembershipDegree]],
          measures: Dict[LinguisticVariable, List[float]]) -> dict[LinguisticVariable, list]:
        infer decision from rule base

    Examples:
    --------------------------------------------
    Creating simple mamdani inference system and infering decision
    >>> consequent_1 = TakagiSugenoInferenceSystem(parameters_1, 0, consequent_linguistic_variable_1)
    >>> first_rule = Rule(antecedent_1, consequent_1)
    ^repeat for all rules
    >>> rule_base = [first_rule, second_rule, third_rule]
    >>> features: Dict[Clause, MembershipDegree] = fuzzifier.fuzzify(dataset)
    >>> data = df_X.reset_index().to_dict(orient='list')
    >>> data.pop('index', None)
    >>> measures = {linguistic_variable_1: data['linguistic-variable-1'],
    >>>     linguistic_variable_2: data['linguistic-variable-2'],
    >>>     linguistic_variable_3: data['linguistic-variable-3'],
    >>>     linguistic_variable_4: data['linguistic_variable_4']}
    >>> takagi_sugeno = TakagiSugenoInferenceSystem(rule_base)
    >>> defuzzifiaction_method = takagi_sugeno_karnik_mendel
    >>> print(takagi_sugeno.infer(defuzzifiaction_method, features, measures))
    {consequent_linguistic_variable_1: [0.5],
    consequent_linguistic_variable_2: [0.25],
    consequent_linguistic_variable_1: [0.3],
    consequent_linguistic_variable_1: [0.71]}
    """

    __cache = {}

    def infer(self,
              defuzzification_method: Callable,
              features: Dict[Clause, List[MembershipDegree]],
              measures: Dict[LinguisticVariable, List[float]]) -> List[float]:
        """
        Inferences output based on features of given object and measured values of them, using chosen method.

        :param defuzzification_method: method of calculating inference system output.
            Must match to the type of fuzzy sets used in rules and be callable, and takes two ndarrays as parameters.
            Those arrays represent firing values of antecedents of all rules in _rule_base and outputs of their
            consequents
        :param features: a dictionary of clauses and membership values of measures
        :param measures: a dictionary of linguistic variables and values measured for them
        :return: dictionary of linguistic variables and corresponding outputs of inference system
        """
        if not isinstance(features, Dict):
            raise ValueError("Features must be dictionary")
        if not isinstance(measures, Dict):
            raise ValueError("Measures must be dictionary")
        if not isinstance(defuzzification_method, Callable):
            raise ValueError("Defuzzification_method must be Callable")

        conclusions = []
        for i in range(len(list(measures.values())[0])):
            single_features = {}
            single_measures = {}
            for key, value in features.items():
                single_features[key] = np.take(value, i, axis=-1)
            for key, value in measures.items():
                single_measures[key] = value[i]
            input_tuple = self.__get_input_tuple(single_measures.values())
            if self.__is_cached(input_tuple):
                conclusions.append(self.__cache[input_tuple])
            else:
                outputs = []
                firings = []
                for rule in self._rule_base:
                    outputs.append(rule.consequent.output(single_measures))
                    firings.append(rule.antecedent.fire(single_features))
                outputs = np.array(outputs)
                firings = np.array(firings)
                ind = np.argsort(outputs)
                outputs = outputs[ind]
                firings = firings[ind]
                conclusion = defuzzification_method(np.array(firings),
                                                      np.array(outputs))
                conclusions.append(conclusion)
                self.__cache[input_tuple] = conclusion

        return conclusions

    def __is_cached(self, _input):
        try:
            self.__cache[_input]
            return True
        except KeyError:
            return False

    def __get_input_tuple(self, _input):
        in_values = list(_input)
        for rule in self._rule_base:
            for param in rule.consequent.function_parameters.values():
                in_values.append(param)
        return tuple(in_values)
