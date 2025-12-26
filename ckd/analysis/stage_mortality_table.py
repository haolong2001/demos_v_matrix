"""
Utility helpers to read the stage-specific mortality CSV into a dense
multi-dimensional array for fast lookup during simulation.

Once loaded, the array can be indexed by
  (sim_year, agent_gender, agent_race, albumin_scenario, eGFR_stage, age_group)
to fetch the corresponding mortality rate in O(1) time.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

DEFAULT_MORTALITY_PATH = Path("../../data/stage_specific_mortality.csv")
GENDER_ORDER = ["male", "female"]
RACE_ORDER = ["chinese", "malay", "indian", "others"]
ALBUMIN_SCENARIOS = list(range(5))
STAGE_LABELS = ["1", "2", "3.1", "3.2", "4", "5"]


def _build_age_groups() -> List[str]:
    buckets = ["0", "1-4"]
    for lower in range(5, 85, 5):
        upper = lower + 4
        buckets.append(f"{lower}-{upper}")
    buckets.append("85+")
    return buckets


AGE_GROUP_LABELS = _build_age_groups()


@dataclass
class StageMortalityTable:
    """
    Holds a dense mortality tensor and the categorical index mappings needed to query it.
    """

    rates: np.ndarray
    year_index: Dict[int, int]
    gender_index: Dict[str, int]
    race_index: Dict[str, int]
    stage_index: Dict[str, int]
    age_index: Dict[str, int]

    @classmethod
    def from_csv(cls, path: Path | str = DEFAULT_MORTALITY_PATH) -> "StageMortalityTable":
        """
        Load the CSV output (e.g., data/stage_specific_mortality.csv) into memory.
        """
        df = pd.read_csv(path)
        df["agent_gender"] = df["agent_gender"].str.lower()
        df["agent_race"] = df["agent_race"].str.lower()
        df["eGFR_stage"] = (
            df["eGFR_stage"]
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
        )
        df["age_group"] = df["age_group"].astype(str)

        years = sorted(df["sim_year"].unique().tolist())
        year_index = {year: idx for idx, year in enumerate(years)}
        gender_index = {gender: idx for idx, gender in enumerate(GENDER_ORDER)}
        race_index = {race: idx for idx, race in enumerate(RACE_ORDER)}
        stage_index = {stage: idx for idx, stage in enumerate(STAGE_LABELS)}
        age_index = {age: idx for idx, age in enumerate(AGE_GROUP_LABELS)}

        shape = (
            len(years),
            len(GENDER_ORDER),
            len(RACE_ORDER),
            len(ALBUMIN_SCENARIOS),
            len(STAGE_LABELS),
            len(AGE_GROUP_LABELS),
        )
        rates = np.full(shape, np.nan, dtype=float)

        for _, row in df.iterrows():
            y = year_index[row["sim_year"]]
            g = gender_index[row["agent_gender"]]
            r = race_index[row["agent_race"]]
            alb = int(row["albumin_scenario"])
            stage = stage_index[row["eGFR_stage"]]
            age = age_index[row["age_group"]]
            rates[y, g, r, alb, stage, age] = row["mortality_rate"]

        return cls(rates, year_index, gender_index, race_index, stage_index, age_index)

    def get_rate(
        self,
        sim_year: int,
        agent_gender: str,
        agent_race: str,
        albumin_scenario: int,
        eGFR_stage: str,
        age_group: str,
    ) -> float:
        """
        Retrieve the mortality rate for the requested coordinates.
        Returns NaN if any axis value is unknown.
        """
        try:
            y = self.year_index[sim_year]
            g = self.gender_index[agent_gender.lower()]
            r = self.race_index[agent_race.lower()]
            alb = int(albumin_scenario)
            stage = self.stage_index[str(eGFR_stage)]
            age = self.age_index[age_group]
        except KeyError:
            return float("nan")
        if not (0 <= alb < len(ALBUMIN_SCENARIOS)):
            return float("nan")
        return float(self.rates[y, g, r, alb, stage, age])


def load_stage_mortality_table(path: Path | str = DEFAULT_MORTALITY_PATH) -> StageMortalityTable:
    """
    Convenience wrapper: StageMortalityTable.from_csv shortcut.
    """
    return StageMortalityTable.from_csv(path)
