from pathlib import Path

from health_classification import build_health_classification_outputs


def test_build_health_classification_outputs_generates_metrics_and_figures(tmp_path):
    metrics, figure_paths, csv_paths = build_health_classification_outputs(output_root=tmp_path)

    assert isinstance(metrics, dict)
    for metric in ("accuracy", "precision", "recall", "f1"):
        assert metric in metrics
        assert 0.0 <= float(metrics[metric]) <= 1.0

    assert figure_paths
    assert csv_paths

    for path in figure_paths + csv_paths:
        assert Path(path).exists(), f"Expected output missing: {path}"
