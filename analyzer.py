"""
단타(스캘핑) 분석 엔진 모듈
기술적 지표를 종합하여 단타 점수를 산출합니다.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Optional
from config import (
    MA_SHORT, MA_LONG,
    RSI_PERIOD,
    BB_PERIOD, BB_STD,
    VOLUME_LOOKBACK, VOLUME_SURGE_MULTIPLIER,
    WEIGHT_TREND, WEIGHT_MOMENTUM, WEIGHT_VOLUME, WEIGHT_VOLATILITY,
    SCORE_STRONG_BUY, SCORE_BUY, SCORE_HOLD,
    STOP_LOSS_PCT, TARGET_PROFIT_PCT,
)


# ============================================================
# 분석 결과 데이터 클래스
# ============================================================

@dataclass
class IndicatorDetail:
    """개별 지표 분석 결과"""
    name: str
    value: float           # 원시 값
    score: float           # 0-100 점수 (가중치 적용 전)
    weighted_score: float  # 가중치 적용 후 최종 기여 점수
    signal: str            # 시그널 (매수/매도/중립)
    description: str       # 한줄 설명


@dataclass
class AnalysisResult:
    """종합 분석 결과"""
    ticker: str
    current_price: float
    total_score: float                        # 종합 점수 (0-100)
    signal: str                               # 판단 결과
    signal_emoji: str                         # 이모지
    signal_color: str                         # 색상 코드
    entry_price: float                        # 진입가
    stop_loss: float                          # 손절가
    target_price: float                       # 목표가
    expected_profit_pct: float                # 예상 수익률
    risk_reward_ratio: float                  # 위험보상비
    indicators: list                          # IndicatorDetail 리스트
    summary: str                              # 종합 요약
    ma_short: Optional[pd.Series] = None      # 단기 이동평균
    ma_long: Optional[pd.Series] = None       # 장기 이동평균
    rsi: Optional[pd.Series] = None           # RSI 시리즈
    bb_upper: Optional[pd.Series] = None      # 볼린저 상단
    bb_middle: Optional[pd.Series] = None     # 볼린저 중간
    bb_lower: Optional[pd.Series] = None      # 볼린저 하단
    volume_ma: Optional[pd.Series] = None     # 거래량 이동평균


# ============================================================
# 분석 엔진
# ============================================================

class Analyzer:
    """단타 분석 엔진 — 기술적 지표를 종합하여 단타 수익성을 평가합니다."""

    def __init__(self):
        pass

    # ----------------------------------------------------------------
    # 메인 분석 함수
    # ----------------------------------------------------------------
    def analyze(self, df: pd.DataFrame, ticker: str) -> AnalysisResult:
        """
        데이터프레임을 받아 종합 단타 분석을 수행합니다.

        Args:
            df: OHLCV 데이터프레임 (columns: open, high, low, close, volume)
            ticker: 종목 코드

        Returns:
            AnalysisResult: 종합 분석 결과
        """
        if df.empty or len(df) < max(MA_LONG, BB_PERIOD, RSI_PERIOD) + 5:
            raise ValueError(
                f"분석에 필요한 데이터가 부족합니다. (현재 {len(df)}개 봉, "
                f"최소 {max(MA_LONG, BB_PERIOD, RSI_PERIOD) + 5}개 필요)"
            )

        # 지표 계산
        self._compute_indicators(df)

        current_price = float(df["close"].iloc[-1])

        # 개별 지표 분석
        trend_detail = self._analyze_trend(df)
        momentum_detail = self._analyze_momentum(df)
        volume_detail = self._analyze_volume(df)
        volatility_detail = self._analyze_volatility(df)

        indicators = [trend_detail, momentum_detail, volume_detail, volatility_detail]

        # 종합 점수
        total_score = sum(ind.weighted_score for ind in indicators)
        total_score = max(0, min(100, total_score))

        # 판단 결과
        signal, emoji, color = self._determine_signal(total_score)

        # 진입가/손절가/목표가
        entry_price = current_price
        if signal in ["적극 매수", "매수 검토"]:
            stop_loss = round(current_price * (1 - STOP_LOSS_PCT), 2)
            target_price = round(current_price * (1 + TARGET_PROFIT_PCT), 2)
        else:
            stop_loss = round(current_price * (1 - STOP_LOSS_PCT), 2)
            target_price = round(current_price * (1 + TARGET_PROFIT_PCT * 0.5), 2)

        expected_profit_pct = round(((target_price - entry_price) / entry_price) * 100, 2)
        risk = abs(entry_price - stop_loss)
        reward = abs(target_price - entry_price)
        risk_reward_ratio = round(reward / risk, 2) if risk > 0 else 0

        # 종합 요약
        summary = self._generate_summary(signal, total_score, indicators)

        return AnalysisResult(
            ticker=ticker,
            current_price=current_price,
            total_score=total_score,
            signal=signal,
            signal_emoji=emoji,
            signal_color=color,
            entry_price=entry_price,
            stop_loss=stop_loss,
            target_price=target_price,
            expected_profit_pct=expected_profit_pct,
            risk_reward_ratio=risk_reward_ratio,
            indicators=indicators,
            summary=summary,
            ma_short=df.get("ma_short"),
            ma_long=df.get("ma_long"),
            rsi=df.get("rsi"),
            bb_upper=df.get("bb_upper"),
            bb_middle=df.get("bb_middle"),
            bb_lower=df.get("bb_lower"),
            volume_ma=df.get("volume_ma"),
        )

    # ----------------------------------------------------------------
    # 기술적 지표 계산
    # ----------------------------------------------------------------
    def _compute_indicators(self, df: pd.DataFrame) -> None:
        """데이터프레임에 기술적 지표 컬럼을 추가합니다."""
        # 이동평균선 (SMA)
        df["ma_short"] = df["close"].rolling(window=MA_SHORT).mean()
        df["ma_long"] = df["close"].rolling(window=MA_LONG).mean()

        # RSI (Wilder 방식)
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.rolling(window=RSI_PERIOD, min_periods=RSI_PERIOD).mean()
        avg_loss = loss.rolling(window=RSI_PERIOD, min_periods=RSI_PERIOD).mean()
        # EMA 스무딩
        for i in range(RSI_PERIOD, len(df)):
            avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * (RSI_PERIOD - 1) + gain.iloc[i]) / RSI_PERIOD
            avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * (RSI_PERIOD - 1) + loss.iloc[i]) / RSI_PERIOD
        rs = avg_gain / avg_loss
        df["rsi"] = 100 - (100 / (1 + rs))

        # 볼린저 밴드
        df["bb_middle"] = df["close"].rolling(window=BB_PERIOD).mean()
        rolling_std = df["close"].rolling(window=BB_PERIOD).std()
        df["bb_upper"] = df["bb_middle"] + (BB_STD * rolling_std)
        df["bb_lower"] = df["bb_middle"] - (BB_STD * rolling_std)

        # 거래량 이동평균
        df["volume_ma"] = df["volume"].rolling(window=VOLUME_LOOKBACK).mean()

    # ----------------------------------------------------------------
    # 추세 분석 (이동평균선)
    # ----------------------------------------------------------------
    def _analyze_trend(self, df: pd.DataFrame) -> IndicatorDetail:
        """이동평균선 정배열/역배열 분석"""
        ma_short_val = df["ma_short"].iloc[-1]
        ma_long_val = df["ma_long"].iloc[-1]
        close = df["close"].iloc[-1]

        # NaN 처리
        if pd.isna(ma_short_val) or pd.isna(ma_long_val):
            return IndicatorDetail(
                name="추세 (이동평균선)",
                value=0,
                score=50,
                weighted_score=50 * WEIGHT_TREND / 100,
                signal="데이터 부족",
                description="이동평균선 계산에 필요한 데이터가 부족합니다."
            )

        # 정배열: 현재가 > 단기MA > 장기MA
        if close > ma_short_val > ma_long_val:
            raw_score = 90
            # 정배열 강도: 단기-장기 MA 격차
            gap_pct = (ma_short_val - ma_long_val) / ma_long_val * 100
            if gap_pct > 2:
                raw_score = 100
            signal = "강한 상승 추세"
            desc = f"정배열 확인 (가격 > MA{MA_SHORT} > MA{MA_LONG}). 단기 이동평균이 장기 이동평균 위에 위치하여 상승 추세입니다."
        elif close > ma_short_val:
            raw_score = 65
            signal = "약한 상승"
            desc = f"가격이 단기 MA{MA_SHORT} 위에 있으나 장기 MA{MA_LONG}와는 혼조세입니다."
        elif close < ma_short_val < ma_long_val:
            raw_score = 15
            signal = "하락 추세"
            desc = f"역배열 (가격 < MA{MA_SHORT} < MA{MA_LONG}). 하락 추세로 단타 진입에 부적합합니다."
        else:
            raw_score = 45
            signal = "횡보"
            desc = "이동평균선이 수렴 중으로 방향성이 불분명합니다."

        weighted = round(raw_score * WEIGHT_TREND / 100, 2)
        return IndicatorDetail(
            name="추세 (이동평균선)",
            value=round(float(close - ma_short_val), 4),
            score=raw_score,
            weighted_score=weighted,
            signal=signal,
            description=desc,
        )

    # ----------------------------------------------------------------
    # 모멘텀 분석 (RSI)
    # ----------------------------------------------------------------
    def _analyze_momentum(self, df: pd.DataFrame) -> IndicatorDetail:
        """RSI 기반 모멘텀 분석"""
        rsi_val = df["rsi"].iloc[-1]

        if pd.isna(rsi_val):
            return IndicatorDetail(
                name="모멘텀 (RSI)",
                value=0,
                score=50,
                weighted_score=50 * WEIGHT_MOMENTUM / 100,
                signal="데이터 부족",
                description="RSI 계산에 필요한 데이터가 부족합니다."
            )

        rsi_val = float(rsi_val)

        # RSI 이전 값 확인 (과매도 탈출 감지)
        rsi_prev = df["rsi"].iloc[-2] if len(df) > 1 and not pd.isna(df["rsi"].iloc[-2]) else rsi_val

        if rsi_val <= 30:
            if rsi_val > rsi_prev:
                # 과매도 탈출 중 → 강한 매수 시그널
                raw_score = 85
                signal = "과매도 탈출 🔥"
                desc = f"RSI({rsi_val:.1f})가 30 이하에서 반등 중. 과매도 영역 탈출은 강한 반등 시그널입니다."
            else:
                raw_score = 30
                signal = "과매도 지속"
                desc = f"RSI({rsi_val:.1f})가 30 이하로 과매도 상태. 추가 하락 가능성에 주의하세요."
        elif rsi_val >= 70:
            if rsi_val > 80:
                raw_score = 55
                signal = "극한 과매수"
                desc = f"RSI({rsi_val:.1f})가 80 이상으로 극한 과매수. 조정 가능성이 높습니다."
            else:
                raw_score = 70
                signal = "강한 모멘텀 🚀"
                desc = f"RSI({rsi_val:.1f})가 70 이상으로 강한 상승 모멘텀. 추세 매매(돌파) 시그널입니다."
        elif 40 <= rsi_val <= 60:
            raw_score = 50
            signal = "중립"
            desc = f"RSI({rsi_val:.1f})가 중립 구간. 뚜렷한 방향성이 없습니다."
        elif rsi_val < 40:
            raw_score = 40
            signal = "약세"
            desc = f"RSI({rsi_val:.1f})가 약세 구간. 모멘텀이 둔화되고 있습니다."
        else:
            raw_score = 60
            signal = "강세"
            desc = f"RSI({rsi_val:.1f})가 강세 구간. 상승 모멘텀이 유지되고 있습니다."

        weighted = round(raw_score * WEIGHT_MOMENTUM / 100, 2)
        return IndicatorDetail(
            name="모멘텀 (RSI)",
            value=round(rsi_val, 2),
            score=raw_score,
            weighted_score=weighted,
            signal=signal,
            description=desc,
        )

    # ----------------------------------------------------------------
    # 거래량 분석
    # ----------------------------------------------------------------
    def _analyze_volume(self, df: pd.DataFrame) -> IndicatorDetail:
        """거래량 급증 여부 분석"""
        current_vol = float(df["volume"].iloc[-1])
        vol_ma = df["volume_ma"].iloc[-1]

        if pd.isna(vol_ma) or vol_ma == 0:
            return IndicatorDetail(
                name="거래량",
                value=current_vol,
                score=50,
                weighted_score=50 * WEIGHT_VOLUME / 100,
                signal="데이터 부족",
                description="거래량 평균 계산에 필요한 데이터가 부족합니다."
            )

        vol_ma = float(vol_ma)
        vol_ratio = current_vol / vol_ma

        if vol_ratio >= 3.0:
            raw_score = 100
            signal = "폭발적 거래량 💥"
            desc = f"현재 거래량이 평균 대비 {vol_ratio:.1f}배. 강력한 매매 세력 유입 감지."
        elif vol_ratio >= VOLUME_SURGE_MULTIPLIER:
            raw_score = 80
            signal = "거래량 급증 📈"
            desc = f"현재 거래량이 평균 대비 {vol_ratio:.1f}배. 수급이 활발합니다."
        elif vol_ratio >= 1.0:
            raw_score = 55
            signal = "보통"
            desc = f"거래량이 평균 수준({vol_ratio:.1f}배). 특별한 수급 변화 없음."
        elif vol_ratio >= 0.5:
            raw_score = 35
            signal = "거래 부진"
            desc = f"거래량이 평균 대비 {vol_ratio:.1f}배로 저조. 관심도가 낮습니다."
        else:
            raw_score = 15
            signal = "극히 저조"
            desc = f"거래량이 평균의 절반 이하({vol_ratio:.1f}배). 유동성 부족 주의."

        weighted = round(raw_score * WEIGHT_VOLUME / 100, 2)
        return IndicatorDetail(
            name="거래량",
            value=round(vol_ratio, 2),
            score=raw_score,
            weighted_score=weighted,
            signal=signal,
            description=desc,
        )

    # ----------------------------------------------------------------
    # 변동성 분석 (볼린저 밴드)
    # ----------------------------------------------------------------
    def _analyze_volatility(self, df: pd.DataFrame) -> IndicatorDetail:
        """볼린저 밴드 기반 변동성 분석"""
        close = float(df["close"].iloc[-1])
        bb_upper = df["bb_upper"].iloc[-1]
        bb_lower = df["bb_lower"].iloc[-1]
        bb_middle = df["bb_middle"].iloc[-1]

        if pd.isna(bb_upper) or pd.isna(bb_lower) or pd.isna(bb_middle):
            return IndicatorDetail(
                name="변동성 (볼린저밴드)",
                value=0,
                score=50,
                weighted_score=50 * WEIGHT_VOLATILITY / 100,
                signal="데이터 부족",
                description="볼린저 밴드 계산에 필요한 데이터가 부족합니다."
            )

        bb_upper = float(bb_upper)
        bb_lower = float(bb_lower)
        bb_middle = float(bb_middle)

        # 밴드 폭 (변동성)
        band_width = (bb_upper - bb_lower) / bb_middle * 100 if bb_middle > 0 else 0

        # 가격 위치: BB 내에서의 상대 위치 (%b)
        bb_range = bb_upper - bb_lower
        pct_b = (close - bb_lower) / bb_range if bb_range > 0 else 0.5

        if close >= bb_upper:
            raw_score = 75
            signal = "상단 돌파 시도 🔺"
            desc = f"가격이 볼린저 상단({bb_upper:.2f})을 돌파 중. 강한 상승 모멘텀이나 과열 주의."
        elif pct_b >= 0.8:
            raw_score = 70
            signal = "상단 접근"
            desc = f"가격이 볼린저 상단에 근접(%B={pct_b:.2f}). 돌파 기대감."
        elif close <= bb_lower:
            raw_score = 60
            signal = "하단 이탈 → 반등 기대"
            desc = f"가격이 볼린저 하단({bb_lower:.2f}) 이하. 과매도 반등 가능성."
        elif pct_b <= 0.2:
            raw_score = 55
            signal = "하단 접근"
            desc = f"가격이 볼린저 하단에 근접(%B={pct_b:.2f}). 지지선 확인 필요."
        else:
            raw_score = 45
            signal = "밴드 내부"
            desc = f"가격이 볼린저 밴드 중앙부(%B={pct_b:.2f}). 변동성이 제한적입니다."

        # 밴드 폭이 좁으면 → 스퀴즈 (곧 큰 변동 예고)
        if band_width < 3:
            raw_score = min(raw_score + 10, 100)
            desc += " ⚡ 볼린저 스퀴즈 감지 — 큰 변동이 임박할 수 있습니다."

        weighted = round(raw_score * WEIGHT_VOLATILITY / 100, 2)
        return IndicatorDetail(
            name="변동성 (볼린저밴드)",
            value=round(pct_b, 4),
            score=raw_score,
            weighted_score=weighted,
            signal=signal,
            description=desc,
        )

    # ----------------------------------------------------------------
    # 판단 결정
    # ----------------------------------------------------------------
    def _determine_signal(self, score: float) -> tuple:
        """점수를 기반으로 매매 판단을 결정합니다."""
        if score >= SCORE_STRONG_BUY:
            return ("적극 매수", "🟢", "#00C851")
        elif score >= SCORE_BUY:
            return ("매수 검토", "🔵", "#33b5e5")
        elif score >= SCORE_HOLD:
            return ("관망", "🟡", "#ffbb33")
        else:
            return ("매도", "🔴", "#ff4444")

    # ----------------------------------------------------------------
    # 종합 요약 생성
    # ----------------------------------------------------------------
    def _generate_summary(self, signal: str, score: float, indicators: list) -> str:
        """분석 결과 종합 요약을 생성합니다."""
        strong_points = [ind for ind in indicators if ind.score >= 70]
        weak_points = [ind for ind in indicators if ind.score < 40]

        parts = [f"종합 단타 점수: **{score:.0f}/100** — **{signal}**\n"]

        if strong_points:
            parts.append("**✅ 긍정적 요소:**")
            for sp in strong_points:
                parts.append(f"  - {sp.name}: {sp.signal}")

        if weak_points:
            parts.append("**⚠️ 주의 요소:**")
            for wp in weak_points:
                parts.append(f"  - {wp.name}: {wp.signal}")

        if signal == "적극 매수":
            parts.append("\n💡 **전략 제안:** 단기 돌파 매매 진입 유리. 목표가 도달 시 분할 매도를 권장합니다.")
        elif signal == "매수 검토":
            parts.append("\n💡 **전략 제안:** 조건부 진입 가능. 거래량 확인 후 진입하고, 손절 라인을 엄수하세요.")
        elif signal == "관망":
            parts.append("\n💡 **전략 제안:** 현재 구간은 매매 시그널이 불분명합니다. 추세 확인 후 재진입을 권장합니다.")
        else:
            parts.append("\n💡 **전략 제안:** 손실 최소화를 위해 익절 또는 손절을 고려하세요.")

        return "\n".join(parts)
