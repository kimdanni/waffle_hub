import time
from pathlib import Path

import optuna
import optuna.visualization as oplt
import plotly.io as pio
from optuna.pruners import HyperbandPruner
from optuna.samplers import GridSampler, RandomSampler, TPESampler

from waffle_hub.schema.configs import OptunaHpoMethodConfig

# TODO [Exception]: scheduler 및 pruner 관련 none 일 경우 (config 에서도 error 가 발생할 수 있음) 하위 계층에서도 error 발생
#      class HPOMethodError(Exception) 정의 필요


class OptunaHPO:
    def __init__(self, hub_root, hpo_method):
        self._study_name = None
        self._hub_root = hub_root
        self._config = OptunaHpoMethodConfig()
        self._hpo_method = hpo_method
        self._study = None

    def set_study_name(self, study_name):
        if study_name is None:
            raise ValueError("Study name cannot be None.")
        self._study_name = study_name

    # TODO : user can customize sheduler / pruner After update config add property and setter
    # TODO : study name must be property and setter

    def _initialize_sampler(self, hpo_method):
        self._sampler, self._pruner = self._config.initialize_method(hpo_method)

    def create_study(
        self,
        direction: str = "maximize",
    ):
        self._initialize_sampler(self._hpo_method)
        if self._study_name is None:
            raise ValueError("Study name cannot be None.")

        self._study = optuna.create_study(
            study_name=self._study_name,
            storage=f"sqlite:///{self._hub_root}/{self._study_name}/{self._study_name}.db",
            direction=direction,
            sampler=self._sampler,
            pruner=self._pruner,
        )

    def load_study(
        self,
        study_name: str,
    ):
        self.set_study_name(study_name)
        # load studies using db
        self._study = optuna.load_study(
            study_name,
            storage=f"sqlite:///{self._hub_root}/{self._study_name}/{self._study_name}.db",
        )
        # db must be located in study hub

    def visualize_hpo_results(self):
        # 시각화 생성
        param_importance = oplt.plot_param_importances(self._study)
        contour = oplt.plot_contour(self._study)
        coordinates = oplt.plot_parallel_coordinate(self._study)
        slice_plot = oplt.plot_slice(self._study)
        optimization_history = oplt.plot_optimization_history(self._study)

        # 생성한 시각화를 이미지 파일로 저장
        pio.write_image(param_importance, self._hub_root / self._study_name / "param_importance.png")
        pio.write_image(contour, self._hub_root / self._study_name / "contour.png")
        pio.write_image(coordinates, self._hub_root / self._study_name / "coordinates.png")
        pio.write_image(slice_plot, self._hub_root / self._study_name / "slice_plot.png")
        pio.write_image(
            optimization_history, self._hub_root / self._study_name / "optimization_history.png"
        )

    def optimize(self, objective, dataset, n_trials, search_space, **kwargs):
        def objective_wrapper(trial):
            def _get_search_space(trial, search_space):
                params = {
                    k: trial.suggest_categorical(k, v)
                    if isinstance(v, tuple)
                    else trial.suggest_float(k, v[0], v[1])
                    for k, v in search_space.items()
                }
                return params

            params = _get_search_space(trial, search_space)
            return objective(trial=trial, dataset=dataset, params=params, **kwargs)

        self._study.optimize(objective_wrapper, n_trials=n_trials)

    def hpo(self, study_name, objective, dataset, n_trials, direction, search_space, **kwargs):
        self.set_study_name(study_name)  # Set the study name using the property setter
        self.create_study(direction=direction)
        self.optimize(objective, dataset, n_trials, search_space, **kwargs)
        best_value = self._study.best_value
        best_trial = self._study.best_trial.number
        best_params = self._study.best_params
        total_time = str(self._study.trials_dataframe()["duration"].sum())
        return {
            "best_trial": best_trial,
            "best_params": best_params,
            "best_score": best_value,
            "total_time": total_time,
        }
