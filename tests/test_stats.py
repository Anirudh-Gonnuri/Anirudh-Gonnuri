"""Tests for the statistics logic. Run with: python -m unittest discover tests"""

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from github_data import summarise  # noqa: E402
from stats import heat_level, heat_levels  # noqa: E402


def viewer(weeks: list[list[tuple[str, int]]], total: int = 0, repositories: int = 0) -> dict:
    return {
        "contributionsCollection": {
            "contributionCalendar": {
                "totalContributions": total,
                "weeks": [
                    {"contributionDays": [{"date": d, "contributionCount": c} for d, c in week]}
                    for week in weeks
                ],
            }
        },
        "repositories": {"totalCount": repositories},
    }


def repository(**sizes: int) -> dict:
    return {"languages": {"edges": [{"size": s, "node": {"name": n, "color": "#123456"}} for n, s in sizes.items()]}}


class SummariseTests(unittest.TestCase):
    def test_days_are_sorted_whatever_order_the_api_returns(self) -> None:
        stats = summarise(viewer([[("2026-02-02", 1)], [("2026-01-01", 5)]]), [])
        self.assertEqual(stats.days, ((date(2026, 1, 1), 5), (date(2026, 2, 2), 1)))
        self.assertEqual(stats.busiest_day, 5)

    def test_excluded_languages_do_not_affect_shares(self) -> None:
        stats = summarise(viewer([]), [repository(Go=75, HTML=9000), repository(Dart=25)])
        self.assertEqual([(l.name, l.share) for l in stats.languages], [("Go", 0.75), ("Dart", 0.25)])

    def test_sizes_are_combined_across_repositories(self) -> None:
        stats = summarise(viewer([]), [repository(Go=30), repository(Go=30, Dart=40)])
        self.assertEqual(stats.languages[0].name, "Go")
        self.assertAlmostEqual(stats.languages[0].share, 0.6)

    def test_languages_under_the_minimum_share_are_dropped(self) -> None:
        stats = summarise(viewer([]), [repository(Go=995, C=5)])
        self.assertEqual([l.name for l in stats.languages], ["Go"])

    def test_each_language_keeps_its_github_colour(self) -> None:
        stats = summarise(viewer([]), [repository(Go=1)])
        self.assertEqual(stats.languages[0].colour, "#123456")

    def test_tied_languages_have_a_stable_order(self) -> None:
        stats = summarise(viewer([]), [repository(Zig=50, Ada=50)])
        self.assertEqual([l.name for l in stats.languages], ["Ada", "Zig"])


class HeatLevelTests(unittest.TestCase):
    def test_no_activity_is_always_level_zero(self) -> None:
        self.assertIsNone(heat_levels([0, 0]))
        self.assertEqual(heat_level(0, None), 0)

    def test_a_single_active_day_does_not_crash(self) -> None:
        self.assertEqual(heat_level(7, heat_levels([0, 7, 0])), 1)

    def test_outlier_does_not_flatten_the_scale(self) -> None:
        cuts = heat_levels([1, 2, 3, 4, 5, 6, 7, 95])
        self.assertEqual(heat_level(1, cuts), 1)
        self.assertEqual(heat_level(5, cuts), 3)
        self.assertEqual(heat_level(95, cuts), 4)


if __name__ == "__main__":
    unittest.main()
