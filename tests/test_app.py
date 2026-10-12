"""Regression checks for appearance changes and interacting cohort filters."""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(Path.cwd() / "app.py"), default_timeout=30).run()
        self.assertEqual(list(self.app.exception), [])

    def test_ranges_render_inside_their_expander_with_readable_bounds(self):
        self.assertEqual(len(self.app.expander[0].slider), 3)
        accuracy = self.app.slider[0]
        self.assertIn("(%)", accuracy.label)
        self.assertLessEqual(accuracy.max, 100)
        self.assertEqual(self.app.slider[2].max % 100, 0)

    def test_theme_changes_preserve_search_and_always_have_one_selection(self):
        self.app.text_input[0].set_value("Gemini").run()
        for mode in ["Light", "Dark", "Light"]:
            self.app.radio[0].set_value(mode).run()
            self.assertEqual(list(self.app.exception), [])
            self.assertEqual(self.app.text_input[0].value, "Gemini")
            self.assertEqual(self.app.radio[0].value, mode)
            self.assertTrue(any(f"color-scheme: {mode.lower()}" in item.value for item in self.app.markdown))

    def test_narrowing_accuracy_does_not_reset_cost_range(self):
        cost = self.app.slider[1]
        selected_cost = (cost.min, min(cost.max, 2.0))
        self.app.slider[1].set_value(selected_cost).run()
        accuracy = self.app.slider[0]
        self.app.slider[0].set_value((max(accuracy.min, 90.0), accuracy.max)).run()
        self.assertEqual(list(self.app.exception), [])
        self.assertEqual(self.app.slider[1].value, selected_cost)

    def test_explorer_sort_selection_survives_a_theme_change(self):
        sort_control = next(control for control in self.app.selectbox if control.label == "Sort results by")
        sort_control.set_value("Cost / 1k docs (USD)").run()
        self.app.radio[0].set_value("Light").run()
        self.assertEqual(list(self.app.exception), [])
        sort_control = next(control for control in self.app.selectbox if control.label == "Sort results by")
        self.assertEqual(sort_control.value, "Cost / 1k docs (USD)")

    def test_clearing_and_restoring_providers_recovers_from_empty_results(self):
        provider = self.app.sidebar.multiselect[0].options[0]
        self.app.sidebar.multiselect[0].set_value([]).run()
        self.assertEqual(list(self.app.exception), [])
        self.assertTrue(any("No models match" in message.value for message in self.app.info))
        self.app.sidebar.multiselect[0].set_value([provider]).run()
        self.assertEqual(list(self.app.exception), [])
        self.assertEqual(len(self.app.tabs), 5)


if __name__ == "__main__":
    unittest.main()
