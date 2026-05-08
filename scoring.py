import pandas as pd
import numpy as np

def calculate_rsi(closes, period=14):
    delta = closes.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_bollinger(closes, period=20):
    ma = closes.rolling(window=period).mean()
    std = closes.rolling(window=period).std()
    upper = ma + (2 * std)
    lower = ma - (2 * std)
    current = closes.iloc[-1]
    band_range = upper.iloc[-1] - lower.iloc[-1]
    if band_range == 0:
        return 0.5
    position = (current - lower.iloc[-1]) / band_range
    return position, upper.iloc[-1], lower.iloc[-1]

def calculate_macd(closes):
    ema12 = closes.ewm(span=12, adjust=False).mean()
    ema26 = closes.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def calculate_ema(closes, span):
    return closes.ewm(span=span, adjust=False).mean()

def score_rsi(rsi):
    if rsi < 25:    return 25
    elif rsi < 30:  return 22
    elif rsi < 40:  return 18
    elif rsi < 50:  return 12
    elif rsi < 60:  return 8
    elif rsi < 70:  return 4
    elif rsi < 80:  return 2
    else:           return 0

def score_bollinger(position):
    if position <= 0:       return 20
    elif position < 0.10:   return 17
    elif position < 0.25:   return 13
    elif position < 0.50:   return 10
    elif position < 0.75:   return 6
    elif position < 0.90:   return 3
    else:                   return 0

def score_macd(macd, signal):
    macd_now = macd.iloc[-1]
    macd_prev = macd.iloc[-2]
    signal_now = signal.iloc[-1]
    signal_prev = signal.iloc[-2]

    gap = macd_now - signal_now
    prev_gap = macd_prev - signal_prev

    just_crossed_above = macd_prev < signal_prev and macd_now > signal_now
    just_crossed_below = macd_prev > signal_prev and macd_now < signal_now

    if just_crossed_above:                          return 20
    elif gap > 0 and gap > prev_gap:                return 16
    elif gap > 0 and gap <= prev_gap:               return 11
    elif just_crossed_below:                        return 4
    elif gap < 0 and abs(gap) < abs(prev_gap):      return 7
    elif gap < 0 and abs(gap) > abs(prev_gap) * 1.5: return 0
    else:                                           return 2

def score_ema(closes, ema9, ema21):
    current = closes.iloc[-1]
    ema9_now = ema9.iloc[-1]
    ema9_prev = ema9.iloc[-2]
    ema21_now = ema21.iloc[-1]
    ema21_prev = ema21.iloc[-2]

    gap = ema9_now - ema21_now
    prev_gap = ema9_prev - ema21_prev
    gap_widening = abs(gap) > abs(prev_gap)

    crossing_up = ema9_prev < ema21_prev and ema9_now > ema21_now
    crossing_down = ema9_prev > ema21_prev and ema9_now < ema21_now

    if current > ema9_now > ema21_now and gap_widening:    return 15
    elif current > ema9_now > ema21_now and not gap_widening: return 11
    elif crossing_up:                                       return 13
    elif ema9_now < ema21_now < current:                   return 7
    elif current < ema9_now and ema9_now > ema21_now:      return 5
    elif crossing_down:                                     return 2
    else:                                                   return 0

def score_volume(hist):
    avg_volume = hist["Volume"].tail(20).mean()
    current_volume = hist["Volume"].iloc[-1]
    if avg_volume == 0:
        return 0
    ratio = current_volume / avg_volume
    if ratio >= 3.0:    return 10
    elif ratio >= 2.0:  return 8
    elif ratio >= 1.5:  return 6
    elif ratio >= 1.0:  return 4
    elif ratio >= 0.75: return 2
    else:               return 0

def score_52_week(current_price, week_high, week_low):
    if week_high == week_low or week_high == 0:
        return 5
    position = (current_price - week_low) / (week_high - week_low)
    if position <= 0.10:    return 10
    elif position <= 0.20:  return 8
    elif position <= 0.35:  return 6
    elif position <= 0.50:  return 5
    elif position <= 0.65:  return 4
    elif position <= 0.80:  return 3
    elif position <= 0.90:  return 2
    else:                   return 1

def get_verdict(score):
    if score >= 66:     return "🟢 BUY"
    elif score >= 36:   return "🟡 HOLD"
    else:               return "🔴 SELL"

def calculate_score(stock_data, hist):
    closes = hist["Close"]

    rsi = calculate_rsi(closes)
    bb_position, bb_upper, bb_lower = calculate_bollinger(closes)
    macd, signal = calculate_macd(closes)
    ema9 = calculate_ema(closes, 9)
    ema21 = calculate_ema(closes, 21)

    s_rsi = score_rsi(rsi)
    s_bb = score_bollinger(bb_position)
    s_macd = score_macd(macd, signal)
    s_ema = score_ema(closes, ema9, ema21)
    s_vol = score_volume(hist)
    s_52w = score_52_week(
        stock_data["current_price"],
        stock_data["52w_high"],
        stock_data["52w_low"]
    )

    total = s_rsi + s_bb + s_macd + s_ema + s_vol + s_52w

    return {
        "score": total,
        "verdict": get_verdict(total),
        "breakdown": {
            "RSI":              (s_rsi, 25, round(rsi, 1)),
            "Bollinger Bands":  (s_bb, 20, round(bb_position * 100, 1)),
            "MACD":             (s_macd, 20, None),
            "EMA 9/21":         (s_ema, 15, None),
            "Volume":           (s_vol, 10, None),
            "52 Week":          (s_52w, 10, None),
        }
    }