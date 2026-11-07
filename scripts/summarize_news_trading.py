#!/usr/bin/env python3
"""Recompute the results in "Polymarket News Trading: Why Following the Move Loses" from the CSV files in data/
(Python 3.9+, standard library only).

    python3 scripts/summarize_news_trading.py

1. Look-ahead trap: buy $10 in the direction of a price move at the first trade 5 seconds after it, pay the fee
   0.05 x p x (1 - p), and value the position at the price level 2 to 15 minutes later (median of other trades) or at
   resolution. lookahead_jumps.csv picks moves by that later level (it needs the future); shocks_5s.csv picks them only by
   what is known at the move (the first trade at least 5 cents away from the 5-minute level).
2. Following a news move: news_moves.csv has every trigger of a real-time detector on minute bars; returns per $1 staked,
   entry and exit at the minute VWAP plus 2 cents of slippage and the fee, capped at -100%.
3. and 4. Aggregates for copying early buyers and new-wallet consensus (early_buyers_copy.csv, newcomer_consensus.csv).
t-statistics are plain (not clustered)."""
import csv
import math
import os

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def rows(name):
    with open(os.path.join(D, name), newline="") as f:
        return list(csv.DictReader(f))


def fee(p):
    return 0.05 * p * (1 - p)


def copy10(price, value):
    """$10 bought at price (fee added), worth value per share at the end."""
    if not 0.01 < price < 0.99:
        return None
    return 10.0 / (price + fee(price)) * value - 10.0


def stat(xs):
    xs = [x for x in xs if x is not None]
    n = len(xs)
    if n < 2:
        return n, float("nan"), float("nan")
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / n)
    return n, m, m / (sd / math.sqrt(n)) if sd else float("nan")


def trap_value(r, horizon):
    p = r["price_after_5s"]
    target = r["level_after_2_15min"] if horizon == "level" else r["yes_payout"]
    if p == "" or target == "":
        return None
    p, target, up = float(p), float(target), float(r["move"]) > 0
    return copy10(p, target) if up else copy10(1 - p, 1 - target)


print("1. LOOK-AHEAD TRAP (buy 5 s after the move, $ per $10)")
for label, name in (("chosen by the level 2-15 min LATER (look-ahead)", "lookahead_jumps.csv"),
                    ("chosen only by what is known at the move (honest)", "shocks_5s.csv")):
    R = rows(name)
    n1, m1, t1 = stat([trap_value(r, "level") for r in R])
    n2, m2, t2 = stat([trap_value(r, "resolution") for r in R])
    with_level = [r for r in R if r["level_after_2_15min"] != ""]
    further = sum(1 for r in with_level if (float(r["level_after_2_15min"]) - float(r["first_trade"])) * float(r["move"]) > 0)
    print("  %-50s moves %5d | to the later level n %4d %+5.2f (t %+5.1f) | to resolution n %4d %+5.2f (t %+5.1f) | "
          "moved further %3.0f%%" % (label, len(R), n1, m1, t1, n2, m2, t2, 100.0 * further / len(with_level)))

print("\n2. FOLLOWING A NEWS MOVE (real-time detector; return per $1 staked)")
R = rows("news_moves.csv")
for period in ("selection", "check"):
    X = [r for r in R if r["period"] == period]
    print("  %s period: %d triggers" % (period, len(X)))
    for side in ("follow", "fade"):
        cells = []
        for h in ("1h", "4h", "24h", "resolution"):
            n, m, t = stat([float(r["%s_%s" % (side, h)]) for r in X if r["%s_%s" % (side, h)] != ""])
            cells.append("%-10s n %4d %+6.1f%% (t %+5.1f)" % (h, n, 100 * m, t))
        print("    %-6s " % side + " | ".join(cells))

print("\n3. COPYING EARLY BUYERS OF EARLIER NEWS JUMPS (check period, per $ staked)")
for r in rows("early_buyers_copy.csv"):
    print("  %-20s %-28s wallets %4s | copied %4s | ROI %+5.1f%% (t %+4.1f) | without top-3 events %+5.1f%% | right side on check jumps %s%%"
          % (r["window"], r["group"], r["wallets"], r["copied_signals_check_period"], float(r["copy_roi_pct"]), float(r["t"]),
             float(r["copy_roi_without_top3_events_pct"]), r["right_side_share_pct"]))

print("\n4. COPYING NEW-WALLET CONSENSUS (net of fees, per $ staked)")
for r in rows("newcomer_consensus.csv"):
    if r["segment"] == "all":
        print("  new = first %3s h | K%s | signals %6s | net %+5.1f%% (t %+5.1f) | before fees %+5.1f%%"
              % (r["new_window_hours"], r["k_wallets"], r["signals"], float(r["net_roi_pct"]), float(r["t"]), float(r["gross_roi_pct"])))
    else:
        print("      %-14s K%s | signals %6s | net %+5.1f%% (t %+5.1f) | without top-3 events %+5.1f%%"
              % (r["segment"], r["k_wallets"], r["signals"], float(r["net_roi_pct"]), float(r["t"]), float(r["net_roi_without_top3_events_pct"])))
