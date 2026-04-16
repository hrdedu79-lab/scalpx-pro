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

    # ----------------------------------------------------------------
    # 한국 주식 거래량 상위 종목
    # ----------------------------------------------------------------
    def get_kr_top_volume(self, top_n: int = 15) -> pd.DataFrame:
        """
        한국 주요 종목 중 거래량 상위 종목을 반환합니다.

        Returns:
            pd.DataFrame: columns=['종목명', '종목코드', '현재가', '등락률', '거래량']
        """
        # 캐시 확인 (60초)
        cache_key = "kr_top_volume"
        now = datetime.now()
        if cache_key in self._cache:
            elapsed = (now - self._cache_time[cache_key]).total_seconds()
            if elapsed < 60:
                return self._cache[cache_key].copy()

        # 주요 한국 종목 50개 (속도를 위해 대형주 위주)
        top_kr_tickers = {
            "삼성전자": "005930.KS", "SK하이닉스": "000660.KS",
            "LG에너지솔루션": "373220.KS", "삼성바이오로직스": "207940.KS",
            "현대차": "005380.KS", "기아": "000270.KS",
            "셀트리온": "068270.KS", "KB금융": "105560.KS",
            "POSCO홀딩스": "005490.KS", "NAVER": "035420.KS",
            "카카오": "035720.KS", "LG화학": "051910.KS",
            "삼성SDI": "006400.KS", "현대모비스": "012330.KS",
            "신한지주": "055550.KS", "SK텔레콤": "017670.KS",
            "LG전자": "066570.KS", "삼성물산": "028260.KS",
            "삼성전기": "009150.KS", "카카오뱅크": "323410.KS",
            "한국전력": "015760.KS", "포스코퓨처엠": "003670.KS",
            "HD현대중공업": "329180.KS", "한화에어로스페이스": "012450.KS",
            "한화오션": "042660.KS", "두산에너빌리티": "034020.KS",
            "현대건설": "000720.KS", "대한항공": "003490.KS",
            "한국항공우주": "047810.KS", "LG이노텍": "011070.KS",
            "에코프로": "086520.KS", "에코프로비엠": "247540.KS",
            "HLB": "028300.KS", "삼성생명": "032830.KS",
            "삼성화재": "000810.KS", "하나금융지주": "086790.KS",
            "크래프톤": "259960.KS", "하이브": "352820.KS",
            "HD현대일렉트릭": "267260.KS", "HD한국조선해양": "009540.KS",
            "두산로보틱스": "454910.KS", "현대로템": "064350.KS",
            "한미반도체": "042700.KS", "SK이노베이션": "096770.KS",
            "SK바이오팜": "326030.KS", "메리츠금융지주": "138040.KS",
            "SK스퀘어": "402340.KS", "효성중공업": "298040.KS",
            "LS ELECTRIC": "010120.KS", "한화솔루션": "009830.KS",
        }

        ticker_list = list(top_kr_tickers.values())
        name_map = {v: k for k, v in top_kr_tickers.items()}  # 코드→이름 역매핑

        try:
            # 일괄 다운로드 (1일 데이터)
            df = yf.download(
                ticker_list,
                period="1d",
                interval="1d",
                group_by="ticker",
                progress=False,
                threads=True,
            )

            results = []
            for ticker_code in ticker_list:
                try:
                    if len(ticker_list) == 1:
                        row = df
                    else:
                        row = df[ticker_code] if ticker_code in df.columns.get_level_values(0) else None

                    if row is None or row.empty:
                        continue

                    close_val = float(row["Close"].iloc[-1])
                    open_val = float(row["Open"].iloc[-1])
                    volume_val = int(row["Volume"].iloc[-1])

                    if volume_val == 0:
                        continue

                    change_pct = ((close_val - open_val) / open_val * 100) if open_val > 0 else 0

                    results.append({
                        "종목명": name_map.get(ticker_code, ticker_code),
                        "종목코드": ticker_code,
                        "현재가": close_val,
                        "등락률": round(change_pct, 2),
                        "거래량": volume_val,
                    })
                except Exception:
                    continue

            if not results:
                return pd.DataFrame()

            result_df = pd.DataFrame(results)
            result_df = result_df.sort_values("거래량", ascending=False).head(top_n).reset_index(drop=True)
            result_df.index = result_df.index + 1  # 1부터 시작

            # 캐시 저장
            self._cache[cache_key] = result_df.copy()
            self._cache_time[cache_key] = now

            return result_df

        except Exception as e:
            return pd.DataFrame()

