import pytest
from core.evaluation_engine import EvaluationEngine


def test_compute_roc_curve_data_multiclass():
    test_data = {
        "y_true": ["0", "1", "2", "0", "1", "2"],
        "probabilities": [
            [0.8, 0.1, 0.1],
            [0.1, 0.8, 0.1],
            [0.1, 0.1, 0.8],
            [0.7, 0.2, 0.1],
            [0.2, 0.7, 0.1],
            [0.1, 0.2, 0.7]
        ]
    }
    roc_res = EvaluationEngine.compute_roc_curve_data(test_data)
    assert len(roc_res["curves"]) == 3
    for curve in roc_res["curves"]:
        assert curve["auc"] >= 0.5
        assert len(curve["fpr"]) > 0


def test_compute_residuals_data():
    test_data = {
        "y_true": [10.0, 20.0, 30.0],
        "y_pred": [11.0, 19.0, 32.0],
        "residuals": [-1.0, 1.0, -2.0]
    }
    res = EvaluationEngine.compute_residuals_data(test_data)
    assert res["max_error"] == 2.0
    assert len(res["residuals"]) == 3
