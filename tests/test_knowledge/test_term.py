import pytest

from doggos.algebras import GodelAlgebra
from doggos.knowledge import Clause
from doggos.knowledge import Term
from doggos.fuzzy_sets import Type1FuzzySet, IntervalType2FuzzySet
from doggos.knowledge.linguistic_variable import LinguisticVariable, Domain
from doggos.utils.membership_functions import triangular


import numpy as np


class TestTermAntecedent:

    def test_exception_typeerror_algebra_init(self):
        domain = Domain(0, 10, 0.5)
        ling_var = LinguisticVariable('Temperature', domain)
        fuzzy_set = Type1FuzzySet(lambda x: 0.5 * x)
        clause = Clause(ling_var, 'Low', fuzzy_set)
        with pytest.raises(TypeError) as e:
            _ = Term([], clause)
            assert 'algebra must be an Algebra type' in str(e.value)

    def test_and_type1fuzzy_set(self):
        algebra = GodelAlgebra()
        domain = Domain(0, 10, 0.5)
        ling_var = LinguisticVariable('Temperature', domain)
        fuzzy_set1 = Type1FuzzySet(lambda x: 0.5 * x)
        clause1 = Clause(ling_var, 'Low', fuzzy_set1)
        fuzzy_set2 = Type1FuzzySet(lambda x: 2 * x)
        clause2 = Clause(ling_var, 'High', fuzzy_set2)
        clause_dict = {
            clause1: clause1.get_value(2),
            clause2: clause2.get_value(2)
        }
        antecedent1 = Term(algebra, clause1)
        antecedent2 = Term(algebra, clause2)
        antecedent = antecedent1 & antecedent2
        assert antecedent.fire(clause_dict) == algebra.t_norm(clause_dict[clause1], clause_dict[clause2])
        
    def test_and_interval_type2fuzzy_set(self):
        algebra = GodelAlgebra()
        domain = Domain(0, 10, 0.5)
        ling_var = LinguisticVariable('Temperature', domain)
        clause1 = Clause(ling_var, 'high',
                         IntervalType2FuzzySet(lambda x: triangular(106., 112., 112.1)(x)/2,
                                               lambda x: triangular(106., 112., 112.1)(x)))
        clause2 = Clause(ling_var, 'medium',
                         IntervalType2FuzzySet(lambda x: triangular(100, 106., 112)(x)/2,
                                               lambda x: triangular(100, 106., 112)(x)))
        clause_dict = {
            clause1: clause1.get_value(2),
            clause2: clause2.get_value(2)
        }
        antecedent1 = Term(algebra, clause1)
        antecedent2 = Term(algebra, clause2)
        antecedent = antecedent1 & antecedent2
        assert np.array_equal(antecedent.fire(clause_dict), algebra.t_norm(clause_dict[clause1], clause_dict[clause2]))

    def test_or_type1fuzzy_set(self):
        algebra = GodelAlgebra()
        domain = Domain(0, 10, 0.5)
        ling_var = LinguisticVariable('Temperature', domain)
        fuzzy_set1 = Type1FuzzySet(lambda x: 0.5 * x)
        clause1 = Clause(ling_var, 'Low', fuzzy_set1)
        fuzzy_set2 = Type1FuzzySet(lambda x: 2 * x)
        clause2 = Clause(ling_var, 'High', fuzzy_set2)
        clause_dict = {
            clause1: clause1.get_value(2),
            clause2: clause2.get_value(2)
        }
        antecedent1 = Term(algebra, clause1)
        antecedent2 = Term(algebra, clause2)
        antecedent = antecedent1 | antecedent2
        assert antecedent.fire(clause_dict) == algebra.s_norm(clause_dict[clause1], clause_dict[clause2])
        
    def test_or_type2fuzzy_set(self):
        algebra = GodelAlgebra()
        domain = Domain(0, 10, 0.5)
        ling_var = LinguisticVariable('Temperature', domain)
        clause1 = Clause(ling_var, 'high',
                         IntervalType2FuzzySet(lambda x: triangular(106., 112., 112.1)(x)/2,
                                               lambda x: triangular(106., 112., 112.1)(x)))
        clause2 = Clause(ling_var, 'medium',
                         IntervalType2FuzzySet(lambda x: triangular(100, 106., 112)(x)/2,
                                               lambda x: triangular(100, 106., 112)(x)))
        clause_dict = {
            clause1: clause1.get_value(2),
            clause2: clause2.get_value(2)
        }
        antecedent1 = Term(algebra, clause1)
        antecedent2 = Term(algebra, clause2)
        antecedent = antecedent1 | antecedent2
        assert np.array_equal(antecedent.fire(clause_dict), algebra.s_norm(clause_dict[clause1], clause_dict[clause2]))

    def test_complex_type1fuzzy_set(self):
        algebra = GodelAlgebra()
        domain = Domain(0, 10, 0.5)
        ling_var = LinguisticVariable('Temperature', domain)
        fuzzy_set1 = Type1FuzzySet(lambda x: 0.5 * x)
        clause1 = Clause(ling_var, 'Low', fuzzy_set1)
        fuzzy_set2 = Type1FuzzySet(lambda x: 2 * x)
        clause2 = Clause(ling_var, 'High', fuzzy_set2)
        fuzzy_set3 = Type1FuzzySet(lambda x: 4 * x)
        clause3 = Clause(ling_var, 'Giga High', fuzzy_set2)
        fuzzy_set4 = Type1FuzzySet(lambda x: 3 * x)
        clause4 = Clause(ling_var, 'Very High', fuzzy_set2)
        clause_dict = {
            clause1: clause1.get_value(2),
            clause2: clause2.get_value(2),
            clause3: clause2.get_value(2),
            clause4: clause2.get_value(2)
        }
        antecedent1 = Term(algebra, clause1)
        antecedent2 = Term(algebra, clause2)
        antecedent3 = Term(algebra, clause3)
        antecedent4 = Term(algebra, clause4)
        antecedent = (antecedent1 | antecedent2) & (antecedent3 & antecedent4)
        assert antecedent.fire(clause_dict) == algebra.t_norm(
            algebra.s_norm(clause_dict[clause1], clause_dict[clause2]),
            algebra.t_norm(clause_dict[clause3], clause_dict[clause4]))

    def test_complex_interval_type2fuzzy_set(self):
        algebra = GodelAlgebra()
        domain = Domain(0, 10, 0.5)
        ling_var = LinguisticVariable('Temperature', domain)
        clause1 = Clause(ling_var, 'high',
                         IntervalType2FuzzySet(lambda x: triangular(106., 112., 112.1)(x)/2,
                                               lambda x: triangular(106., 112., 112.1)(x)))
        clause2 = Clause(ling_var, 'medium',
                         IntervalType2FuzzySet(lambda x: triangular(100, 106., 112)(x)/2,
                                               lambda x: triangular(100, 106., 112)(x)))
        clause3 = Clause(ling_var, 'low',
                         IntervalType2FuzzySet(lambda x: triangular(99.9, 100., 106.)(x)/2,
                                               lambda x: triangular(99.9, 100., 106.)(x)))
        clause4 = Clause(ling_var, 'high',
                         IntervalType2FuzzySet(lambda x: triangular(2.5, 4, 4.1)(x)/2,
                                               lambda x: triangular(2.5, 4, 4.1)(x)))
        clause_dict = {
            clause1: clause1.get_value(2),
            clause2: clause2.get_value(2),
            clause3: clause2.get_value(2),
            clause4: clause2.get_value(2)
        }
        antecedent1 = Term(algebra, clause1)
        antecedent2 = Term(algebra, clause2)
        antecedent3 = Term(algebra, clause3)
        antecedent4 = Term(algebra, clause4)
        antecedent = (antecedent1 | antecedent2) & (antecedent3 & antecedent4)
        assert np.array_equal(antecedent.fire(clause_dict), algebra.t_norm(
            algebra.s_norm(clause_dict[clause1], clause_dict[clause2]),
            algebra.t_norm(clause_dict[clause3], clause_dict[clause4])))
