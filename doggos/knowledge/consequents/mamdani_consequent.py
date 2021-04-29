from typing import Tuple, List
import numpy as np

from doggos.knowledge.consequents.consequent import Consequent
from doggos.knowledge.clause import Clause
from doggos.fuzzy_sets.membership.membership_degree import MembershipDegree


class MamdaniConsequent(Consequent):
    """
    Class used to represent a fuzzy rule consequent:
    https://en.wikipedia.org/wiki/Fuzzy_rule

    Attributes
    --------------------------------------------
    __clause : Clause
        supplies Consequent with universe and a fuzzy set. Provided fuzzy set type must match fuzzy sets used in Fuzzy
        Rule Antecedent, otherwise an exception will be raised during computations.

    __cut_mf : Tuple[List[float], ...] or List[float]
        fuzzy set provided by clause cut to the rule firing level

    Methods
    --------------------------------------------
    calculate_cut(rule_firing: Tuple[float, ...] or float) -> Tuple[List[float]] or List[float]
        cut fuzzy set provided by Clause to rule firing level

    Examples:
    --------------------------------------------

    """

    def __init__(self, clause: Clause):
        """
        Create Rules Consequent used in Mamdani Inference System. Provided Clause holds fuzzy set describing Consequent
        and Linguistic Variable which value user wants to compute.
        :param clause: Clause holding fuzzy set and linguistic variable
        """
        self.__clause = clause
        self.__cut_mf = None

    def output(self, rule_firing: MembershipDegree) -> List[MembershipDegree]:
        """
        Cuts membership function to the level of rule firing. It is a minimum of membership function values
        and respecting rule firing. Rule firing should hold values from range [0, 1].
        IMPORTANT:
        Make sure type of fuzzy set used in Clause matches type of fuzzy sets used in Antecedent of Rule and therefore
        its firing type.
        :param rule_firing: firing value of a Rule in which Consequent is used
        :return: fuzzy set membership function or tuple of those, cut to the level of firing value
        """
        if isinstance(rule_firing, float):
            return self.__t1_cut(rule_firing)
        elif isinstance(rule_firing, tuple):
            if len(rule_firing) == 2:
                return self.__it2_cut(rule_firing)
        else:
            raise Exception

    def __t1_cut(self, rule_firing: float):
        """
        Makes a cut for type one fuzzy sets. If Clause fuzzy set type mismatches rule_firing type, exception is raised.
        :param rule_firing: crisp value of rule firing
        :return: fuzzy set membership function, cut to the level of firing value
        """
        self.__cut_mf = np.minimum(self.__clause.fuzzy_set, rule_firing)
        return self.__cut_mf

    def __it2_cut(self, rule_firing: Tuple[float, float]):
        """
        Makes a cut for interval type two fuzzy sets. If Clause fuzzy set type mismatches rule_firing type, exception is
        raised. Lower membership function is cut to level of first element of tuple, upper membership function is cut to
        level of second element of tuple.
        :param rule_firing: tuple of crisp values of rule firing
        :return: tuple of fuzzy set membership functions, cut to the level of firing value
        """
        self.__cut_mf = (np.minimum(self.__clause.fuzzy_set[0], rule_firing[0]),
                         np.minimum(self.__clause.fuzzy_set[1], rule_firing[1]))
        return self.__cut_mf
