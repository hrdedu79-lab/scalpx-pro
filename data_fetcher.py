"""
데이터 수집 모듈 (Data Fetcher)
yfinance를 활용하여 주식 시세 데이터를 가져옵니다.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
from config import (
    POPULAR_KR_STOCKS,
    POPULAR_US_STOCKS,
    KR_MARKET_OPEN_HOUR, KR_MARKET_OPEN_MINUTE,
    KR_MARKET_CLOSE_HOUR, KR_MARKET_CLOSE_MINUTE,
    US_MARKET_OPEN_HOUR, US_MARKET_OPEN_MINUTE,
    US_MARKET_CLOSE_HOUR, US_MARKET_CLOSE_MINUTE,
)
from stock_lists import KR_STOCKS, US_STOCKS


class DataFetcher:
    """주식 시세 데이터 수집 클래스"""

    def __init__(self):
        self._cache = {}
        self._cache_time = {}
        self._cache_ttl = 30  # 캐시 유효 시간 (초)

    # ----------------------------------------------------------------
    # 종목 코드 해석
    # ----------------------------------------------------------------
    def resolve_ticker(self, user_input: str) -> str:
        """사용자 입력을 yfinance 티커 심볼로 변환합니다."""
        user_input = user_input.strip()

        # 1. 전체 한국 종목 리스트에서 매칭 (stock_lists.py)
        if user_input in KR_STOCKS:
            return KR_STOCKS[user_input]

        # 2. config.py 인기 종목 매칭 (하위 호환)
        if user_input in POPULAR_KR_STOCKS:
            return POPULAR_KR_STOCKS[user_input]

        # 3. 미국 종목 — 티커 직접 매칭
        upper = user_input.upper()
        if upper in POPULAR_US_STOCKS:
            return POPULAR_US_STOCKS[upper]

        # 4. 미국 종목 — US_STOCKS 값(티커)으로 매칭
        us_tickers = set(US_STOCKS.values())
        if upper in us_tickers:
            return upper

        # 5. 미국 종목 — "NVDA (NVIDIA)" 형태의 키로 매칭
        for key, val in US_STOCKS.items():
            if upper == val or upper in key.upper():
                return val

        # 6. 숫자 6자리 → 한국 종목 코드로 간주
        if user_input.isdigit() and len(user_input) == 6:
            return f"{user_input}.KS"

        # 7. 그 외 영문 → 미국 종목으로 간주
        if user_input.isalpha():
            return user_input.upper()

        return user_input.upper()

    # ----------------------------------------------------------------
    # 시장 구분
    # ----------------------------------------------------------------
    def is_korean_stock(self, ticker: str) -> bool:
        """한국 주식 여부를 판별합니다."""
        return ticker.endswith(".KS") or ticker.endswith(".KQ")

    # ----------------------------------------------------------------
    # 장 시간 확인
    # ----------------------------------------------------------------
    def is_market_open(self, ticker: str) -> dict:
        """
        현재 장이 열려있는지 확인합니다.
        Returns:
            dict: {"is_open": bool, "message": str, "market": str}
        """
        now = datetime.now()

        if self.is_korean_stock(ticker):
            tz = pytz.timezone("Asia/Seoul")
            now_local = datetime.now(tz)
            market_name = "한국 (KRX)"
            open_time = now_local.replace(
                hour=KR_MARKET_OPEN_HOUR, minute=KR_MARKET_OPEN_MINUTE,
                second=0, microsecond=0
            )
            close_time = now_local.replace(
                hour=KR_MARKET_CLOSE_HOUR, minute=KR_MARKET_CLOSE_MINUTE,
                second=0, microsecond=0
            )
        else:
            tz = pytz.timezone("US/Eastern")
            now_local = datetime.now(tz)
            market_name = "미국 (NYSE/NASDAQ)"
            open_time = now_local.replace(
                hour=US_MARKET_OPEN_HOUR, minute=US_MARKET_OPEN_MINUTE,
                second=0, microsecond=0
            )
            close_time = now_local.replace(
                hour=US_MARKET_CLOSE_HOUR, minute=US_MARKET_CLOSE_MINUTE,
                second=0, microsecond=0
            )

        weekday = now_local.weekday()
        is_weekday = weekday < 5
        is_trading_hours = open_time <= now_local <= close_time

        if not is_weekday:
            return {
                "is_open": False,
                "message": f"🔴 {market_name} 장외 시간 (주말). 마지막 거래일 종가 기준으로 분석합니다.",
                "market": market_name,
            }
        elif not is_trading_hours:
            return {
                "is_open": False,
                "message": f"🔴 {market_name} 장외 시간 ({open_time.strftime('%H:%M')}~{close_time.strftime('%H:%M')}). 마지막 거래일 종가 기준으로 분석합니다.",
                "market": market_name,
            }
        else:
            return {
                "is_open": True,
                "message": f"🟢 {market_name} 장중 — 실시간 데이터 분석 중",
                "market": market_name,
            }

    # ----------------------------------------------------------------
    # 종목 정보
    # ----------------------------------------------------------------
    def get_stock_info(self, ticker: str) -> dict:
        """종목 기본 정보를 가져옵니다."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return {
                "name": info.get("shortName") or info.get("longName", ticker),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "currency": info.get("currency", "KRW" if self.is_korean_stock(ticker) else "USD"),
                "market_cap": info.get("marketCap", 0),
                "previous_close": info.get("previousClose", 0),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh", 0),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow", 0),
            }
        except Exception as e:
            return {
                "name": ticker,
                "sector": "N/A",
                "industry": "N/A",
                "currency": "KRW" if self.is_korean_stock(ticker) else "USD",
                "market_cap": 0,
                "previous_close": 0,
                "fifty_two_week_high": 0,
                "fifty_two_week_low": 0,
                "error": str(e),
            }

    # ----------------------------------------------------------------
    # 시세 데이터 (분봉)
    # ----------------------------------------------------------------
    def fetch_intraday_data(self, ticker: str, interval: str = "1m", period: str = "1d") -> pd.DataFrame:
        """
        분봉 데이터를 가져옵니다.

        Args:
            ticker: 티커 심볼
            interval: 봉 간격 (1m, 2m, 5m, 15m, 30m, 60m)
            period: 조회 기간 (1d, 5d, 1mo)

        Returns:
            pd.DataFrame: OHLCV 데이터
        """
        cache_key = f"{ticker}_{interval}_{period}"
        now = datetime.now()

        # 캐시 확인
        if cache_key in self._cache:
            elapsed = (now - self._cache_time[cache_key]).total_seconds()
            if elapsed < self._cache_ttl:
                return self._cache[cache_key].copy()

        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)

            if df.empty:
                raise ValueError(f"'{ticker}' 데이터를 가져올 수 없습니다. 종목 코드를 확인해주세요.")

            # 컬럼 정리
            df = df.rename(columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            })

            # 필요한 컬럼만 유지
            cols = ["open", "high", "low", "close", "volume"]
            df = df[[c for c in cols if c in df.columns]]

            # 캐시 저장
            self._cache[cache_key] = df.copy()
            self._cache_time[cache_key] = now

            return df

        except Exception as e:
            raise RuntimeError(f"데이터 수집 오류: {str(e)}")

    # ----------------------------------------------------------------
    # 일봉 데이터 (보조)
    # ----------------------------------------------------------------
    def fetch_daily_data(self, ticker: str, period: str = "3mo") -> pd.DataFrame:
        """일봉 데이터를 가져옵니다 (이동평균선 계산용)."""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval="1d")

            if df.empty:
                raise ValueError(f"'{ticker}' 일봉 데이터를 가져올 수 없습니다.")

            df = df.rename(columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            })
            cols = ["open", "high", "low", "close", "volume"]
            df = df[[c for c in cols if c in df.columns]]
            return df

        except Exception as e:
            raise RuntimeError(f"일봉 데이터 수집 오류: {str(e)}")

    # ----------------------------------------------------------------
    # 현재가 빠른 조회
    # ----------------------------------------------------------------
    def get_current_price(self, ticker: str) -> float:
        """현재가를 빠르게 조회합니다."""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d", interval="1m")
            if not data.empty:
                return float(data["Close"].iloc[-1])
            # fallback
            info = stock.info
            return float(info.get("regularMarketPrice", info.get("previousClose", 0)))
        except Exception:
            return 0.0
