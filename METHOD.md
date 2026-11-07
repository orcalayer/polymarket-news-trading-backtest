# Method

All four tests use on-chain Polymarket trades from our database. Tests 1 to 3 enter at a price observed after the signal;
test 4 enters at the K-th wallet's own average price plus 1 cent, which is optimistic for a copier. Every test pays
Polymarket's taker fee.

## Markets

- **Tests 1 to 3.** Non-sports event markets: politics and elections, geopolitics, economics and central banks, technology
  and AI, culture, crypto events and other events.
  - Test 1 removed sports and esports (by slug and by question, including season-long sports questions), short Up or Down
    markets, price-target markets (crypto, oil, gold, indices), daily weather markets, and markets that count mentions or
    posts.
  - Tests 2 and 3 removed sports, dated, price-target and weather markets by slug, and test 2 also markets that count
    mentions or posts.
- **Test 4.** All markets, reported separately for short Up or Down markets, sports and the rest.

## 1. A 5-second news bot, honest and with a look-ahead bug

Period: September 14 to October 14, 2026; markets ending from September 14 to December 12, 2026 with at least $20,000 of
lifetime volume as of October 14 (this includes volume after the shocks).

- **Honest shock** (`shocks_5s.csv`): the level before is the median trade price over the 5 minutes before the shock (at
  least 3 trades, in a window that ends 5 seconds before it). A shock is the first trade at least 5 cents away from that
  level. The next shock in the same market can come no sooner than 15 minutes later. This uses only what is known at the
  shock.
- **Look-ahead jump** (`lookahead_jumps.csv`): the same level before, plus the level after, the median of other trades 2 to 15
  minutes later; a jump counts only if the level after is at least 10 cents away from the level before, and it starts at the
  first trade at least 3 cents away from the level before in the same direction. Choosing events by the level after is the
  bug: it needs the future.
- **Trade**: buy $10 of the side the move favors at the first trade 5 seconds after the shock (`price_after_5s`), with no
  spread added, fee 0.05 × p × (1 - p). Value it at the level 2 to 15 minutes later (no exit cost), or at resolution (YES
  payout 1 or 0) for resolved markets.

## 2. Following a news move (real-time detector)

Period: May 1 to October 21, 2026, on markets with at least $50,000 of lifetime volume. Minute bars of the YES side
(count, dollars, volume-weighted price).

- **Trigger at minute t**: reference = volume-weighted price over minutes [t - 60, t - 10) (at least $200 and 3 trades); now =
  volume-weighted price over [t - 2, t] (at least $100); trigger when |now - reference| is 10 cents or more. One trigger per
  market per 24 hours.
- **Follow**: buy the rising side at the volume-weighted price of [t + 1, t + 4) plus 2 cents, with the fee; entries at
  extreme prices are skipped. Exit at the volume-weighted price of [t + 60, t + 120), [t + 240, t + 300) or
  [t + 1440, t + 1500) minus 2 cents and the fee, or at resolution.
- **Fade**: the same on the falling side.
- **Periods**: selection (before August 16) and check (August 16 onward), reported separately. Returns are per $1 staked,
  with a floor of -100%: an exit at a price under 2 cents goes below zero after slippage; the floor touched 291 exits in all,
  up to 8% of the exits in one cell, and moves the averages by less than 1 point.

## 3. Copying wallets that bought before the news

- **News jumps**: a jump at minute t: the volume-weighted price 10 to 30 minutes after t is at least 15 cents away from that of
  the 60 minutes before t, and the price 1 to 4 hours later still keeps two thirds of that move. 1,047 jumps after the market
  filter; jumps before August 16 select the wallets, the later jumps form the check period.
- **Early buyers**: wallets that bought the rising side (net at least $100) in one of three windows: 24 hours to 2 minutes
  before the move, 2 hours to 2 minutes before, or from 2 minutes before to 5 minutes after. An event counts once.
- **Groups**: early wallets bought early on at least 3 different events before August 16 and were on the rising side at least
  75% of the time. The control group met the same minimum activity (3 or more events) without that record (at most 300
  wallets, chosen in a fixed order).
- **Copy**: each group's buys from August 16 to October 21 that reached $100 on one side of a market within 24 hours, one
  signal per market and side, copied at a later price another trader actually paid shortly after, a few cents worse at
  most, with the fee. A copy was possible for 14% to 20% of the signals; the rest had no such later trade or were at extreme prices. Valued at the
  payout if resolved, otherwise at the last trade.
- **Right side on later jumps**: the share of the group's net buys on the check-period jumps that were on the rising side.

## 4. Copying new wallets that agree

- **New wallets**: 86,228 wallets whose first trade was from September 1 to October 20, 2026, dated by their first trade. A
  wallet is new in its first 72 hours (also reported for 168 hours).
- **Signal**: the K-th different new wallet that buys at least $10 of the same side of a market within 24 hours (and more of
  that side than of the other). One signal per market.
- **Copy**: at the K-th wallet's volume-weighted price plus 1 cent (its average price includes its earlier buys of that side),
  entries from 0.15 to 0.85, held to resolution, minus each market's own taker fee rate. Also reported before fees and
  without the 3 largest events.

## Statistics and limits

- Means per trade with plain t-statistics. Trades on the same event or day are not independent; treat t near 2 with care.
- **Rules and later choices.** The detection, entry and exit rules of tests 2 and 3 were fixed before the results. The market
  cleaning of test 1, the removal of mention and post-count markets from test 2 and the -100% floor in test 2 were added
  when preparing this release.
- **Bots.** Test 3 dropped wallets with more than 40,000 fills on one side during the check period from the copy; test 4
  dropped 1,174 wallets with more than 5,000 trades by late October. Both filters use later activity.
- **Fee rate.** 0.05 is at or above Polymarket's taker rate on politics, economics and geopolitics markets; crypto event
  markets pay up to 0.07 and are a small share of tests 1 to 3.
- **Trades with an empty market id.** Some trades in our table carry no market id (5% to 18% of dollar volume outside the sports and Up or Down
  categories in some months of 2026, mostly in uncategorized sports and Up or Down markets, in an earlier check). Tests 1 to 3 joined trades on the market id and missed them, so their counts may
  be low; the signs of the results do not depend on it. Test 4 matched markets by asset id and is not affected.
- One market universe and one half-year; reacting faster than 5 seconds was not tested.
