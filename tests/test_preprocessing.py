import pytest
import pandas as pd
import numpy as np

from core.preprocessing import PreprocessingPipeline


def test_remove_duplicates():
    df = pd.DataFrame({
        "a": [1, 1, 2, 3],
        "b": [10, 10, 20, 30]
    })
    pipeline = PreprocessingPipeline(df)
    pipeline.remove_duplicates()
    res_df = pipeline.get_df()
    assert len(res_df) == 3
    assert len(pipeline.get_operations()) == 1


def test_missing_value_imputation():
    df = pd.DataFrame({
        "num": [10.0, 20.0, np.nan, 40.0],
        "cat": ["apple", "banana", "apple", np.nan]
    })
    pipeline = PreprocessingPipeline(df)
    pipeline.impute_missing("num", strategy="mean")
    pipeline.impute_missing("cat", strategy="mode")

    res_df = pipeline.get_df()
    assert res_df["num"].isna().sum() == 0
    assert res_df["num"].iloc[2] == pytest.approx(70.0 / 3.0)
    assert res_df["cat"].isna().sum() == 0
    assert res_df["cat"].iloc[3] == "apple"


def test_label_and_one_hot_encoding():
    df = pd.DataFrame({
        "color": ["red", "blue", "green", "blue"],
        "size": ["S", "M", "L", "S"]
    })
    pipeline = PreprocessingPipeline(df)
    pipeline.label_encode(["size"])
    pipeline.one_hot_encode(["color"])

    res_df = pipeline.get_df()
    assert pd.api.types.is_numeric_dtype(res_df["size"])
    assert "color_blue" in res_df.columns
    assert "color_green" in res_df.columns
    assert "color_red" in res_df.columns


def test_feature_scaling():
    df = pd.DataFrame({
        "val": [10.0, 20.0, 30.0, 40.0, 50.0]
    })
    pipeline = PreprocessingPipeline(df)
    pipeline.scale_features(["val"], method="standard")
    res_df = pipeline.get_df()

    assert pytest.approx(res_df["val"].mean(), abs=1e-5) == 0.0
    assert pytest.approx(res_df["val"].std(ddof=0), abs=1e-5) == 1.0


def test_train_test_split_isolation():
    df = pd.DataFrame({
        "feat1": np.random.rand(50),
        "feat2": np.random.rand(50),
        "target": [0, 1] * 25
    })
    X_train, X_test, y_train, y_test = PreprocessingPipeline.prepare_train_test_split(
        df, target_col="target", test_size=0.2, random_state=42, is_classification=True
    )
    assert len(X_train) == 40
    assert len(X_test) == 10
    assert len(y_train) == 40
    assert len(y_test) == 10
    # No index overlap
    assert set(X_train.index).isdisjoint(set(X_test.index))
