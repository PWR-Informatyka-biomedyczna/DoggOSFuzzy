from typing import Dict, List

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.feature_selection import SelectKBest, SelectFpr, SelectFdr, SelectFwe, GenericUnivariateSelect, RFE, \
    SelectFromModel, RFECV, SequentialFeatureSelector
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier, NeighborhoodComponentsAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.decomposition import KernelPCA, FactorAnalysis, FastICA, NMF, PCA

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC

from doggos.fuzzy_sets import Type1FuzzySet
from doggos.fuzzy_sets.fuzzy_set import FuzzySet
from doggos.induction.information_system import InformationSystem
from doggos.inference import MamdaniInferenceSystem
from doggos.inference.defuzzification_algorithms import center_of_gravity, karnik_mendel
from doggos.inference.inference_system import InferenceSystem
from doggos.knowledge import Rule, Clause, fuzzify, LinguisticVariable, Domain
from doggos.knowledge.consequents import MamdaniConsequent
from doggos.knowledge.consequents.consequent import Consequent
from doggos.utils.grouping_functions import create_set_of_variables
from doggos.utils.membership_functions.membership_functions import generate_equal_gausses, sigmoid, gaussian


def classify(data):
    preds = []
    for elem in data:
        if elem >= 0.5:
            preds.append(0.0)
        else:
            preds.append(1.0)
    return preds


def normalize(data):
    scaler = MinMaxScaler()
    return scaler.fit_transform(data)


class DataLoader:
    def __init__(self, X: np.ndarray, y: np.ndarray, feature_labels: List[str], target_label: str):
        self.X = X
        self.X_transformed = None
        self.X_train = None
        self.X_train_frame = None
        self.X_test = None
        self.X_test_frame = None
        self.y = y
        self.y_train = None
        self.y_train_frame = None
        self.y_test = None
        self.y_test_frame = None
        self.feature_labels = feature_labels
        self.target_label = target_label

    def prepare_data(self, transforms, test_size):
        self.X_transformed = self.X.copy()
        for transform in transforms:
            self.X_transformed = transform(self.X_transformed)
        self.X_train, self.X_test, self.y_train, self.y_test = \
            train_test_split(self.X_transformed, self.y, test_size=test_size, stratify=self.y)
        self.X_train_frame = pd.DataFrame(data=self.X_train, columns=self.feature_labels)
        self.X_test_frame = pd.DataFrame(data=self.X_test, columns=self.feature_labels)
        self.y_train_frame = pd.Series(self.y_train)
        self.y_test_frame = pd.Series(self.y_test)


class FeatureSelector:
    def __init__(self, selector, **kwargs):
        self.__selector_class = selector
        self.__selector = selector(kwargs)

    def fit_transform(self, X, y=None):
        return self.__selector.fit_transform(X, y)

    def set_params(self, **kwargs):
        self.__selector = self.__selector_class(**kwargs)

    def search(self, linear_params, linear_params_count, X, y=None):
        transformations = []
        for i in range(linear_params_count):
            params = {}
            for key in linear_params.keys():
                params[key] = linear_params[key][i]
            self.set_params(**params)
            transformations.append(self.fit_transform(X, y))
        return transformations


class Evaluator:
    def __init__(self, model, feature_labels: List[str], fuzzy_sets: Dict[str, Dict[str, FuzzySet]],
                 consequents: List[Consequent], inference_system, defuzz_method,
                 domain: Domain = Domain(0, 1.001, 0.001)):
        self.model = model
        self.feature_labels = feature_labels
        self.fuzzy_sets = fuzzy_sets
        self.consequents = consequents
        self.inference_system = inference_system
        self.defuzz_method = defuzz_method
        self.domain = domain
        self.rules = []
        self.clauses = []
        self.antecedents = None

    def get_params(self, deep=True):
        return self.__dict__

    def fit(self, X: pd.DataFrame, y):
        information_system = InformationSystem(X, y, self.feature_labels)
        self.antecedents, str_antecedents = information_system.induce_rules(self.fuzzy_sets, self.domain)
        self.clauses = information_system.rule_builder.clauses

    def construct_rules(self):
        self.rules = [Rule(self.antecedents[decision], self.consequents[str(decision)])
                      for decision in self.antecedents.keys()]

    def predict(self, X: pd.DataFrame):
        fuzzified_dataset = fuzzify(X, self.clauses)
        inference_system = self.inference_system(self.rules)
        return inference_system.infer(self.defuzz_method, fuzzified_dataset)


full_dataset = pd.read_csv("../data/diabetes.csv")
target_label = 'Outcome'
feature_labels = list(full_dataset.columns)
feature_labels.remove(target_label)
X = full_dataset.values[:, :-1]
y = full_dataset.values[:, -1]
transforms = [normalize]
dataloader = DataLoader(X, y, feature_labels, target_label)
dataloader.prepare_data(transforms, test_size=0.2)

mf_types = ['gaussian', 'triangular', 'trapezoidal']
n_mfs = [3, 5, 7, 9, 11]
fuzzy_set_types = ['t1']
con_labels = np.unique(dataloader.y)
con_labels = [str(label) for label in con_labels]
con_n_mfs = [2]
con_mf_types = ['gaussian', 'triangular', 'trapezoidal']

models = [LinearDiscriminantAnalysis, PCA, KernelPCA, NeighborhoodComponentsAnalysis, SelectKBest, SelectFpr, SelectFdr,
          SelectFwe, GenericUnivariateSelect, RFECV, RFE, SelectFromModel, SequentialFeatureSelector, FactorAnalysis,
          FastICA, NMF, SequentialFeatureSelector]

models_demo = [LinearDiscriminantAnalysis, PCA, KernelPCA]

linear_params = [
    {}
]

feature_selector = FeatureSelector()

model = RandomForestClassifier()
consequents = None
inference_system = MamdaniInferenceSystem
defuzz_method = center_of_gravity
kernels = ['linear', 'poly', 'rbf', 'cosine']
algorithms = ['parallel', 'deflation']
funcs = ['logcosh', 'exp', 'cube']
inits = ['random', 'nndsvda', 'nndsvdar']
losses = ['frobenius', 'kullback-leibler', 'itakura-saito']
n_jobs = -1
decomposer = NMF
pcs = []
for i, feature in enumerate(feature_labels):
    pcs.append(str(i))

# plt.scatter(dataloader.X_transformed[:, 0], dataloader.X_transformed[:, 1], c=dataloader.y)
# plt.show()

print(feature_labels)
dataloader.X_transformed += 1e-07
# for kernel in kernels:
# for algorithm in algorithms:
for init in inits:
    for loss in losses:
        #    for func in funcs:
        # model = decomposer(n_components=2, kernel=kernel, n_jobs=n_jobs)
        # model = decomposer(n_components=2, algorithm=algorithm, fun=func)
        # model = decomposer(n_components=2)
        model = decomposer(n_components=2, solver='mu', init=init, beta_loss=loss, max_iter=1000)
        # print(kernel)

        transformed = model.fit_transform(dataloader.X_transformed, dataloader.y)
        # print(normalize(model.lambdas_.reshape(-1, 1)))
        # print('Covariance', model.get_covariance())
        # print('Components', model.components_)
        # print('Noise', model.noise_variance_)
        # plt.bar(pcs, model.lambdas_)
        # plt.show()
        plt.scatter(transformed[:, 0], transformed[:, 1], c=dataloader.y)
        plt.show()

"""
for fuzzy_set_type in fuzzy_set_types:
    for n_mf in n_mfs:
        for mf_type in mf_types:
            features, fuzzy_sets, clauses = create_set_of_variables(feature_labels,
                                                                    mf_type=mf_type,
                                                                    n_mfs=n_mf,
                                                                    fuzzy_set_type=fuzzy_set_type)
            defuzz_func = None
            if fuzzy_set_type == 't1':
                defuzz_func = center_of_gravity
            elif fuzzy_set_type == 'it2':
                defuzz_func = karnik_mendel

            evaluator = Evaluator(model, feature_labels, fuzzy_sets, consequents, inference_system, defuzz_method)
            evaluator.fit(dataloader.X_train_frame, dataloader.y_train_frame)

            for con_mf_type in con_mf_types:
                for con_n_mf in con_n_mfs:
                    con_features, con_fuzzy_sets, con_clauses = create_set_of_variables(con_labels,
                                                                                        mf_type=con_mf_type,
                                                                                        n_mfs=con_n_mf,
                                                                                        fuzzy_set_type=fuzzy_set_type)

                    consequents = {}
                    for clause in con_clauses:
                        target = clause.linguistic_variable.name
                        consequents[target] = MamdaniConsequent(clause)
                    evaluator.consequents = consequents
                    evaluator.construct_rules()
                    values_train = evaluator.predict(dataloader.X_train_frame)
                    values_test = evaluator.predict(dataloader.X_test_frame)
                    plt.scatter(values_train, values_train, c=dataloader.y_train)
                    plt.show()

                    plt.scatter(values_test, values_test, c=dataloader.y_test)
                    plt.show()

                    values_train = values_train.reshape(-1, 1)
                    values_test = values_test.reshape(-1, 1)

                    evaluator.model.fit(values_train, dataloader.y_train)
                    y_pred = evaluator.model.predict(values_test)

                    acc = accuracy_score(dataloader.y_test, y_pred)
                    f1 = f1_score(dataloader.y_test, y_pred)

                    print('\n', mf_type, n_mf, fuzzy_set_type, con_mf_type)
                    print('Accuracy: ', acc)
                    print('F1 Score: ', f1)

                    preds = classify(values_test)
                    acc = accuracy_score(dataloader.y_test, preds)
                    f1 = f1_score(dataloader.y_test, preds)

                    print('\nAccuracy: ', acc)
                    print('F1 Score: ', f1)
"""
