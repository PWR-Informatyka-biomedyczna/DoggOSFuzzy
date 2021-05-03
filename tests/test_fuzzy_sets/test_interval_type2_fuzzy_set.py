import pytest
import numpy as np

from tests.test_tools import approx, _random_sample

from doggos.fuzzy_sets import IntervalType2FuzzySet
from doggos.utils.membership_functions import linear, sigmoid


class TestIntervalType2FuzzySet:

    @pytest.mark.parametrize('x', _random_sample(-10, 10, 5))
    def test_base_fuzzy_set_call(self, x):
        lmf = linear(2, 3, 1)
        umf = linear(1, 3, 1)
        fuzzy_set = IntervalType2FuzzySet(lmf, umf)
        assert fuzzy_set(x) == approx((lmf(x), umf(x)))

    @pytest.mark.parametrize('x', np.random.randn(10, 15))
    def test_vectorized_one_dimension_set_call(self, x):
        lmf = lambda a: np.where(a > 0, 0.9, 0.1)
        umf = lambda b: np.where(b > 0, 1.0, 0.11)
        fuzzy_set = IntervalType2FuzzySet(lmf, umf)
        assert all(res == approx(exp) for res, exp in zip(
            fuzzy_set(x),
            (lmf(x), umf(x))
        ))

    @pytest.mark.parametrize('x', np.random.randn(10, 15, 10))
    def test_vectorized_multi_dimension_set_call(self, x):
        lmf = lambda a: np.where(a > 0, 0.88, 0.17)
        umf = lambda b: np.where(b > 0, 0.92, 0.18)
        fuzzy_set = IntervalType2FuzzySet(lmf, umf)
        assert all(res == approx(exp) for res, exp in zip(
            fuzzy_set(x),
            (lmf(x), umf(x))
        ))

    def test_uncallable_functions_fuzzy_set(self):
        lmf = linear(2, 3, 1)
        umf = "str"
        with pytest.raises(ValueError) as e:
            _ = IntervalType2FuzzySet(lmf, umf)
            assert 'Membership functions must be callable' in str(e.value)
        with pytest.raises(ValueError) as e:
            _ = IntervalType2FuzzySet(umf, lmf)
            assert 'Membership functions must be callable' in str(e.value)

    @pytest.mark.parametrize('x', _random_sample(-10, 10, 5))
    def test_lower_mf_higher_than_upper_mf_exception(self, x):
        lmf = sigmoid(1, 3)
        umf = sigmoid(2, 3)
        fuzzy_set = IntervalType2FuzzySet(lmf, umf)
        with pytest.raises(ValueError) as e:
            _ = fuzzy_set(x)
            assert 'Lower membership function returned higher value than upper membership function' in str(e.value)

    @pytest.mark.parametrize('x', _random_sample(-10, 10, 5))
    def test_upper_mf_equal_to_lower_mf_true(self, x):
        lmf = sigmoid(1, 3)
        umf = sigmoid(1, 3)
        fuzzy_set = IntervalType2FuzzySet(lmf, umf)
        assert fuzzy_set(x) == approx((lmf(x), umf(x)))

    @pytest.mark.parametrize('x', _random_sample(-10, 10, 5))
    def test_upper_mf_setter_correct(self, x):
        lmf = sigmoid(2, 2)
        umf1 = sigmoid(1, 2)
        umf2 = sigmoid(0, 2)
        fuzzy_set = IntervalType2FuzzySet(lmf, umf1)
        fuzzy_set.upper_membership_function = umf2
        assert fuzzy_set(2) == approx((lmf(2), umf2(2)))

    def test_upper_mf_setter_exception(self):
        lmf = sigmoid(2, 2)
        umf = sigmoid(1, 2)
        fuzzy_set = IntervalType2FuzzySet(lmf, umf)
        with pytest.raises(ValueError) as e:
            fuzzy_set.upper_membership_function = 'str'
            assert 'Membership function should be callable' in str(e.value)

    @pytest.mark.parametrize('x', _random_sample(-10, 10, 5))
    def test_lower_mf_setter_correct(self, x):
        lmf1 = linear(2, 3, 1)
        lmf2 = linear(3, 3, 1)
        umf = linear(1, 3, 1)
        fuzzy_set = IntervalType2FuzzySet(lmf1, umf)
        fuzzy_set.lower_membership_function = lmf2
        assert fuzzy_set(x) == approx((lmf2(x), umf(x)))

    def test_lower_mf_setter_exception(self):
        lmf = sigmoid(2, 2)
        umf = sigmoid(1, 2)
        fuzzy_set = IntervalType2FuzzySet(lmf, umf)
        with pytest.raises(ValueError) as e:
            fuzzy_set.lower_membership_function = []
            assert 'Membership function should be callable' in str(e.value)
