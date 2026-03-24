import unittest
from datetime import datetime

from src.config import get_mock_edges, get_mock_route_templates, get_mock_stops
from src.route_optimizer import get_route_options
from src.occupancy import predict_stop_occupancy_percent
from src.gnn_baseline import train_gnn_occupancy_regressor
from src.experiments import run_single_intervention_scenario


class TestFlowSyncSmoke(unittest.TestCase):
    def test_route_options_not_empty(self) -> None:
        stops = get_mock_stops()
        edges = get_mock_edges()
        templates = get_mock_route_templates()
        origin_id = "D1"
        destination_id = "D4"
        routes = get_route_options(
            origin_id=origin_id,
            destination_id=destination_id,
            departure_dt=datetime(2026, 3, 23, 8, 30, 0),
            event_active=False,
            stops=stops,
            edges=edges,
            route_templates=templates,
        )
        self.assertTrue(len(routes) > 0)

    def test_occupancy_range(self) -> None:
        occ = predict_stop_occupancy_percent(
            stop_id="D2",
            dt=datetime(2026, 3, 23, 9, 0, 0),
            event_active=False,
            route_context_factor=1.0,
            method="regression",
            noise_enabled=False,
        )
        self.assertGreaterEqual(occ, 5.0)
        self.assertLessEqual(occ, 98.0)

    def test_gnn_train_outputs(self) -> None:
        stops = get_mock_stops()
        edges = get_mock_edges()
        model, pred_map = train_gnn_occupancy_regressor(
            stops=stops,
            edges=edges,
            event_active=False,
            departure_dt=datetime(2026, 3, 23, 8, 30, 0),
            training_timestamps=3,
        )
        self.assertTrue(len(pred_map) > 0)

    def test_scenario_runs(self) -> None:
        stops = get_mock_stops()
        edges = get_mock_edges()
        scenario = run_single_intervention_scenario(
            departure_dt=datetime(2026, 3, 23, 8, 30, 0),
            event_active=False,
            stops=stops,
            edges=edges,
            overload_threshold_percent=75.0,
        )
        self.assertTrue(hasattr(scenario, "waiting_proxy_before"))


if __name__ == "__main__":
    unittest.main()

