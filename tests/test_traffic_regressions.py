"""Regression checks for traffic snapshots, timing and canvas geometry."""
import os
import unittest
from unittest.mock import Mock, patch

try:
    from PySide6.QtWidgets import QApplication
    from ui.traffic_intersection_widget import IntersectionCanvasWidget, TrafficIntersectionViewerWidget
    HAS_QT = True
except ImportError:
    HAS_QT = False

from core.engine import Engine
from core.step import VisualizationStep
from plugins.traffic_light.plugin import TrafficLightPlugin, TrafficIntersectionPlugin


class TestTrafficRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if HAS_QT:
            os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
            cls.app = QApplication.instance() or QApplication([])
        else:
            cls.app = None

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
                elif step.extra['duration'] and step.extra['step_duration_ms']:
                    self.assertEqual(step.extra['step_duration_ms'], 1000)
            phases = {}
            for step in steps:
                extra = step.extra
                if extra['duration'] and extra['step_duration_ms']:
                    key = (extra['cycle'], extra.get('phase', extra.get('state')))
                    phases.setdefault(key, []).append(extra['remaining_time'])
            for countdown in phases.values():
                self.assertEqual(countdown, list(range(countdown[0], 0, -1)))

    def test_intersection_events_follow_calls_and_snapshot_counts(self):
        plugin = TrafficIntersectionPlugin()
        plugin.set_param('vehicles_per_approach', 1)
        plugin.set_param('ns_green_duration', 5)
        plugin.set_param('ew_green_duration', 5)
        steps = list(plugin.get_steps())
        tick = []
        empty_green_ticks = 0
        for step in steps:
            extra = step.extra
            if not extra['duration']:
                continue
            tick.append(step)
            vehicles = extra['vehicles']
            waiting = lambda dirs: sum(
                v['status'] in ('waiting', 'queued')
                for d in dirs for v in vehicles[d]
            )
            departed = sum(v['status'] == 'departed'
                           for approach in vehicles.values() for v in approach)
            self.assertEqual(step.array, [waiting(('north', 'south')),
                                          waiting(('east', 'west')), departed])
            if not extra['step_duration_ms']:
                continue
            green = any(light['green'] for light in extra['lights'].values())
            expected = ['PROCESS_CROSSING', 'CHECK_CONFLICT']
            expected += ['START_VEHICLES', 'ADVANCE_QUEUE'] if green else ['CLEAR_INTERSECTION']
            tags = [event.extra['tag'] for event in tick]
            if tags[0] == 'SET_SIGNALS':
                tags = tags[1:]
            self.assertEqual(tags, expected)
            self.assertEqual(sum(event.extra['step_duration_ms'] for event in tick), 1000)
            for event in tick:
                self.assertEqual(event.extra['remaining_time'], extra['remaining_time'])
                self.assertEqual(event.metrics['remaining_time'], extra['remaining_time'])
                self.assertGreater(event.extra['remaining_time'], 0)
            crossing = tick[-len(expected)]
            check = tick[-len(expected) + 1]
            self.assertEqual(crossing.extra['vehicles'], check.extra['vehicles'])
            if green and not any(v['status'] in ('waiting', 'queued', 'crossing')
                                 for approach in vehicles.values() for v in approach):
                empty_green_ticks += 1
            if not green:
                self.assertIn('belépés tiltva', check.explanation)
            tick = []
        self.assertEqual(tick, [])
        self.assertGreater(empty_green_ticks, 0)
        # Default green durations leave vehicles crossing during yellow.
        default_steps = list(TrafficIntersectionPlugin().get_steps())
        self.assertTrue(any(step.extra['tag'] == 'CLEAR_INTERSECTION'
                            and any(v['status'] == 'crossing'
                                    for approach in step.extra['vehicles'].values() for v in approach)
                            for step in default_steps))

    @unittest.skipUnless(HAS_QT, "PySide6 required")
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

    @unittest.skipUnless(HAS_QT, "PySide6 required")
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
