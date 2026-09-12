import itertools
import math
import unittest

from src.risk_engine import (LEVEL_RANK, analyse_contract, find_min_upfront, level_for_score,
                             suggest_structure)

P = 0.756  # Demo Logistics Group mock probability
BASE = dict(payment_probability=P, contract_value=120_000, cash_reserve=45_000,
            monthly_cost=25_000, upfront_pct=0.0, payment_terms_days=60)


def run(**overrides):
    args = {**BASE, **overrides}
    return analyse_contract(**args)


class ScoreBounds(unittest.TestCase):
    def test_score_always_between_0_and_100(self):
        grid = itertools.product(
            [0, 0.3, 0.756, 1.0],                  # p
            [0, 1, 5_000, 120_000, 1e9, 1e12],     # contract
            [0, 1, 45_000, 1e7],                   # cash
            [0, 1, 25_000, 1e7],                   # monthly cost
            [0, 0.3, 1.0],                         # upfront
            [0, 30, 60, 90, 365],                  # terms
        )
        for p, cv, cash, mc, up, t in grid:
            r = analyse_contract(p, cv, cash, mc, up, t)
            self.assertTrue(0 <= r["score"] <= 100, (p, cv, cash, mc, up, t, r["score"]))
            self.assertIn(r["level"], LEVEL_RANK)
            self.assertLessEqual(len(r["reasons"]), 3)
            self.assertGreaterEqual(len(r["reasons"]), 1)

    def test_garbage_inputs_do_not_crash(self):
        for bad in (None, "abc", float("nan"), float("inf"), -500):
            r = analyse_contract(bad, bad, bad, bad, bad, bad)
            self.assertTrue(0 <= r["score"] <= 100)


class LevelBoundaries(unittest.TestCase):
    def test_band_edges(self):
        cases = {0: "LOW", 30: "LOW", 31: "MODERATE", 55: "MODERATE", 56: "HIGH",
                 75: "HIGH", 76: "CRITICAL", 100: "CRITICAL"}
        for score, level in cases.items():
            self.assertEqual(level_for_score(score), level, score)

    def test_rounding_at_edge(self):
        self.assertEqual(level_for_score(30.4), "LOW")
        self.assertEqual(level_for_score(30.6), "MODERATE")

    def test_result_level_matches_score(self):
        r = run()
        self.assertEqual(r["level"], level_for_score(r["score"]))


class EdgeCases(unittest.TestCase):
    def test_cash_zero_does_not_crash(self):
        r = run(cash_reserve=0)
        self.assertIsNone(r["contract_to_cash_ratio"])
        self.assertEqual(r["cash_runway_months"], 0)
        self.assertTrue(r["flags"]["no_cash"])
        self.assertEqual(r["level"], "CRITICAL")

    def test_monthly_cost_zero_does_not_crash(self):
        r = run(monthly_cost=0)
        self.assertIsNone(r["cash_runway_months"])
        self.assertTrue(r["flags"]["no_costs"])
        self.assertLess(r["score"], run()["score"])

    def test_contract_zero(self):
        r = run(contract_value=0)
        self.assertEqual(r["score"], 0)
        self.assertEqual(r["level"], "LOW")
        self.assertEqual(r["net_exposure"], 0)

    def test_everything_zero(self):
        r = analyse_contract(0, 0, 0, 0, 0, 0)
        self.assertEqual(r["score"], 0)

    def test_full_upfront_removes_net_exposure(self):
        r = run(upfront_pct=1.0)
        self.assertEqual(r["net_exposure"], 0)
        self.assertTrue(r["flags"]["fully_prepaid"])
        self.assertEqual(r["level"], "LOW")
        self.assertLess(r["score"], run()["score"] - 50)

    def test_upfront_as_percentage_is_tolerated(self):
        self.assertEqual(run(upfront_pct=30)["score"], run(upfront_pct=0.30)["score"])

    def test_ninety_day_terms(self):
        self.assertGreater(run(payment_terms_days=90)["score"], run(payment_terms_days=60)["score"])

    def test_extremely_large_contract(self):
        r = run(contract_value=1e12)
        self.assertEqual(r["level"], "CRITICAL")
        self.assertIn("more than 100×", r["reasons"][0]["text"])

    def test_very_small_contract_is_low(self):
        r = run(contract_value=1_000)
        self.assertEqual(r["level"], "LOW")

    def test_spec_derivations(self):
        r = run(upfront_pct=0.25)
        self.assertAlmostEqual(r["net_exposure"], 90_000)
        self.assertAlmostEqual(r["contract_to_cash_ratio"], 2.0)
        self.assertAlmostEqual(r["cash_runway_months"], 1.8)
        self.assertAlmostEqual(r["term_months"], 2.0)


class Monotonicity(unittest.TestCase):
    def test_higher_upfront_never_increases_exposure(self):
        for terms in (30, 45, 60, 90):
            scores = [run(upfront_pct=u / 100, payment_terms_days=terms)["score_raw"] for u in range(0, 101, 5)]
            self.assertEqual(scores, sorted(scores, reverse=True), terms)
            nets = [run(upfront_pct=u / 100)["net_exposure"] for u in range(0, 101, 5)]
            self.assertEqual(nets, sorted(nets, reverse=True))

    def test_shorter_terms_never_increase_term_risk(self):
        for up in (0, 0.2, 0.5):
            timing = [next(c["points"] for c in run(payment_terms_days=t, upfront_pct=up)["components"]
                           if c["key"] == "timing") for t in (30, 45, 60, 90)]
            self.assertEqual(timing, sorted(timing), up)
            totals = [run(payment_terms_days=t, upfront_pct=up)["score_raw"] for t in (30, 45, 60, 90)]
            self.assertEqual(totals, sorted(totals))

    def test_riskier_customer_never_lowers_score(self):
        scores = [run(payment_probability=p / 10)["score_raw"] for p in range(11)]
        self.assertEqual(scores, sorted(scores))

    def test_more_cash_never_raises_score(self):
        scores = [run(cash_reserve=c)["score_raw"] for c in (1, 10_000, 45_000, 100_000, 1e6)]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_customer_risk_is_not_contract_risk(self):
        """Same customer, different businesses -> very different exposure."""
        stretched = run()
        comfortable = run(cash_reserve=500_000)
        self.assertEqual(stretched["level"], "CRITICAL")
        self.assertEqual(comfortable["level"], "LOW")


class DemoStory(unittest.TestCase):
    def test_default_demo_deal_is_critical_and_restructure_helps(self):
        current = run()
        revised = run(upfront_pct=0.30, payment_terms_days=30)
        self.assertEqual(current["level"], "CRITICAL")
        self.assertLessEqual(LEVEL_RANK[revised["level"]], LEVEL_RANK["MODERATE"])
        self.assertLess(revised["score"], current["score"])

    def test_min_upfront_finder(self):
        s = find_min_upfront(P, 120_000, 45_000, 25_000, 60)
        self.assertIsNotNone(s)
        self.assertEqual(s["upfront_pct"] % 5, 0)
        self.assertLessEqual(LEVEL_RANK[s["level"]], LEVEL_RANK["MODERATE"])
        if s["upfront_pct"] > 0:
            below = run(upfront_pct=(s["upfront_pct"] - 5) / 100)
            self.assertGreater(LEVEL_RANK[below["level"]], LEVEL_RANK["MODERATE"])

    def test_suggest_structure_statuses(self):
        self.assertEqual(suggest_structure(P, 120_000, 45_000, 25_000, 60)["status"], "upfront")
        self.assertEqual(suggest_structure(P, 1_000, 45_000, 25_000, 60)["status"], "already")
        self.assertEqual(suggest_structure(0.9, 5e6, 1_000, 5e6, 90)["status"], "not_reachable")


if __name__ == "__main__":
    unittest.main()
