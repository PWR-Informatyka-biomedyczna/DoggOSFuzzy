from typing import Callable, Tuple, NoReturn


from doggos.fuzzy_sets.fuzzy_set import FuzzySet


class Type2FuzzySet(FuzzySet):

    __umf: Callable[[float], float]
    __lmf: Callable[[float], float]
    __proba_distribution: Callable

    def __init__(self):
        raise NotImplementedError


    def __call__(self, x: float) -> Tuple[float, float, float]:
        pass

    @property
    def umf(self) -> Callable:
        pass

    @umf.setter
    def umf(self, x: Callable) -> NoReturn:
        pass

    @property
    def lmf(self) -> Callable:
        pass

    @lmf.setter
    def lmf(self, x: Callable) -> NoReturn:
        pass

    @property
    def proba_distribution(self) -> Callable:
        pass

    @proba_distribution.setter
    def proba_distribution(self, x: Callable) -> NoReturn:
        pass
