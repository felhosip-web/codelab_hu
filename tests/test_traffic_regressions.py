"""Regression checks for traffic snapshots, timing and canvas geometry."""
import unittest
from unittest.mock import Mock, patch

from PySide6.QtWidgets import QApplication

from core.engine import Engine
from core.step import VisualizationStep
from plugins.traffic_light.plugin import TrafficLightPlugin, TrafficIntersectionPlugin
from ui.traffic_intersection_widget import IntersectionCanvasWidget, TrafficIntersectionViewerWidget


class TestTrafficRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_restore_parameters_only_for_matching_plugin(self):
        for operation in ('load_state', 'undo', 'redo'):
            for matching in (False, True):
                with self.subTest(operation=operation, matching=matching):
                    engine = Engine()
                    engine.current_plugin = TrafficLightPlugin()
                    state = engine.get_current_state()
                    state.plugin_id = engine.current_plugin.id if matching else 'other'
                    state.params = {'red_duration': 7}
                    with patch.object(engine.state_manager, 'load_from_file', return_value=state), \
                         patch.object(engine.state_manager, 'undo', return_value=state), \
                         patch.object(engine.state_manager, 'redo', return_value=state):
                        result = engine.load_state(None) if operation == 'load_state' else getattr(engine, operation)()
                    self.assertEqual(engine.current_plugin.params.get('red_duration'), 7 if matching else 3)
                    self.assertEqual(result.plugin_mismatch, not matching)

    def test_cycle_markers_do_not_extend_signal_durations(self):
        for plugin in (TrafficLightPlugin(), TrafficIntersectionPlugin()):
            steps = list(plugin.get_steps())
            for step in steps:
                if step.extra['tag'] == 'LOOP_START':
                    self.assertEqual(step.extra['step_duration_ms'], 0)
                elif step.extra['remaining_time']:
                    self.assertEqual(step.extra['step_duration_ms'], 1000)
            phases = {}
            for step in steps:
                extra = step.extra
                if extra['remaining_time']:
                    key = (extra['cycle'], extra.get('phase', extra.get('state')))
                    phases.setdefault(key, []).append(extra['remaining_time'])
            for countdown in phases.values():
                self.assertEqual(countdown, list(range(countdown[0], 0, -1)))

    def test_empty_step_clears_canvas_and_dashboard(self):
        widget = TrafficIntersectionViewerWidget()
        widget.update_state(next(TrafficIntersectionPlugin().get_steps()))
        widget.update_state(VisualizationStep(array=None, explanation='Empty', extra={}))
        self.assertEqual(widget.canvas.lights, {})
        self.assertEqual(widget.canvas.vehicles, {})
        self.assertEqual(widget.canvas.right_of_way, 'NONE')
        self.assertIn('É-D: 0 | K-Ny: 0', widget.queue_info_label.text())
        self.assertIn('0 db', widget.passed_info_label.text())
        self.assertEqual(widget.countdown_label.text(), '-')
        self.assertEqual(widget.cycle_info_label.text(), 'Ciklus: 0 / 0')
        self.assertEqual(widget.status_detail.text(), 'Empty')
        widget.canvas.set_simulation_state(None, None, 'NORTH_SOUTH')
        self.assertEqual(widget.canvas.right_of_way, 'NORTH_SOUTH')
        widget.deleteLater()

    def test_six_car_queues_fit_canvas(self):
        widget = TrafficIntersectionViewerWidget()
        canvas = widget.canvas
        canvas.resize(400, 360)
        plugin = TrafficIntersectionPlugin()
        plugin.set_param('vehicles_per_approach', 6)
        widget.update_state(next(plugin.get_steps()))
        self.assertIn('É-D: 12 | K-Ny: 12', widget.queue_info_label.text())
        with patch.object(canvas, '_draw_car_rect') as draw:
            canvas._draw_vehicles(Mock(), 200, 180, 360 * .38 / 2)
        self.assertEqual(draw.call_count, 24)
        for call in draw.call_args_list:
            _, x, y, width, height, *_ = call.args
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLessEqual(x + width, 400)
            self.assertLessEqual(y + height, 360)
        widget.deleteLater()

    def test_crossing_reaches_far_edge_before_departure(self):
        steps = list(TrafficIntersectionPlugin().get_steps())
        for direction in ('north', 'south', 'east', 'west'):
            frames = [v for step in steps for v in step.extra['vehicles'][direction] if v['id'] == steps[0].extra['vehicles'][direction][0]['id']]
            progress = [v['crossing_progress'] for v in frames if v['status'] == 'crossing']
            self.assertIn(1, progress)
            self.assertIn(2, progress)
            self.assertTrue(any(v['status'] == 'departed' for v in frames))
