"""
📈 실시간 단타(스캘핑) 수익성 분석 대시보드
Streamlit 기반 메인 애플리케이션
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

from config import (
    DISCLAIMER,
    POPULAR_KR_STOCKS,
    POPULAR_US_STOCKS,
    STOP_LOSS_PCT,
    TARGET_PROFIT_PCT,
)
from data_fetcher import DataFetcher
from analyzer import Analyzer


# ============================================================
# 페이지 설정
# ============================================================
st.set_page_config(
    page_title="📈 단타 수익성 분석기",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 커스텀 CSS
# ============================================================
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 40%, #24243e 100%);
    }

    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #161638 0%, #1e1e4a 100%);
        border-right: 1px solid rgba(100, 100, 255, 0.15);
    }

    /* 메트릭 카드 */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30, 30, 80, 0.7), rgba(40, 40, 100, 0.5));
        border: 1px solid rgba(100, 120, 255, 0.2);
        border-radius: 16px;
        padding: 20px 24px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(80, 80, 200, 0.25);
    }

    /* 메트릭 라벨 */
    div[data-testid="stMetric"] label {
        color: #aab0d0 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        background: linear-gradient(90deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* 구분선 */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(120, 120, 255, 0.3), transparent);
    }

    /* 스코어 보드 */
    .score-board {
        background: linear-gradient(135deg, rgba(30, 30, 80, 0.8), rgba(50, 50, 120, 0.5));
        border: 1px solid rgba(100, 120, 255, 0.25);
        border-radius: 20px;
        padding: 28px;
        margin: 16px 0;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }

    .score-title {
        font-size: 1rem;
        color: #9ca0c0;
        margin-bottom: 8px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .score-value {
        font-size: 3.5rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 4px;
    }

    .score-signal {
        font-size: 1.3rem;
        font-weight: 600;
        margin-top: 8px;
    }

    /* 지표 카드 */
    .indicator-card {
        background: rgba(25, 25, 60, 0.6);
        border: 1px solid rgba(100, 120, 255, 0.15);
        border-radius: 14px;
        padding: 18px 20px;
        margin: 8px 0;
        transition: all 0.2s ease;
    }
    .indicator-card:hover {
        border-color: rgba(100, 120, 255, 0.35);
        background: rgba(30, 30, 70, 0.7);
    }

    .indicator-name {
        font-size: 0.9rem;
        color: #8890b0;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .indicator-signal {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .indicator-desc {
        font-size: 0.82rem;
        color: #7a7fa0;
        line-height: 1.5;
    }

    .indicator-bar-bg {
        height: 6px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 3px;
        margin-top: 10px;
        overflow: hidden;
    }

    .indicator-bar {
        height: 100%;
        border-radius: 3px;
        transition: width 0.6s ease;
    }

    /* 트레이딩 박스 */
    .trade-box {
        background: linear-gradient(135deg, rgba(25, 25, 65, 0.7), rgba(50, 50, 120, 0.4));
        border: 1px solid rgba(100, 120, 255, 0.2);
        border-radius: 16px;
        padding: 22px;
        text-align: center;
    }

    .trade-label {
        font-size: 0.8rem;
        color: #8890b0;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }

    .trade-value {
        font-size: 1.6rem;
        font-weight: 700;
    }

    /* 면책 조항 */
    .disclaimer {
        background: rgba(255, 180, 50, 0.08);
        border: 1px solid rgba(255, 180, 50, 0.2);
        border-radius: 12px;
        padding: 16px 20px;
        font-size: 0.8rem;
        color: #b0a580;
        line-height: 1.6;
    }

    /* 히든 스트림릿 기본 요소 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(30, 30, 80, 0.5);
        border-radius: 10px;
        border: 1px solid rgba(100, 120, 255, 0.15);
        color: #aab0d0;
        padding: 10px 24px;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(80, 80, 200, 0.25) !important;
        border-color: rgba(120, 120, 255, 0.4) !important;
        color: white !important;
    }

    /* 스크롤바 */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(15, 15, 40, 0.5);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(100, 100, 200, 0.3);
        border-radius: 3px;
    }

    /* 앱 헤더 */
    .app-header {
        text-align: center;
        padding: 20px 0 10px 0;
    }
    .app-header h1 {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .app-header p {
        color: #7a7fa0;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 세션 상태 초기화
# ============================================================
if "fetcher" not in st.session_state:
    st.session_state.fetcher = DataFetcher()
if "analyzer" not in st.session_state:
    st.session_state.analyzer = Analyzer()


# ============================================================
# 사이드바
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 15px 0;">
        <div style="font-size: 2.5rem;">📈</div>
        <div style="font-size: 1.2rem; font-weight: 700; 
             background: linear-gradient(135deg, #a78bfa, #60a5fa);
             -webkit-background-clip: text; -webkit-text-fill-color: transparent;
             margin-top: 4px;">
            ScalpX Pro
        </div>
        <div style="color: #6b70a0; font-size: 0.75rem; margin-top: 2px;">
            실시간 단타 수익성 분석기
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 종목 입력
    st.markdown("##### 🔍 종목 검색")
    ticker_input = st.text_input(
        "종목명 또는 코드 입력",
        placeholder="예: 삼성전자, NVDA, 005930",
        help="한국 종목명, 미국 티커, 또는 6자리 종목코드를 입력하세요.",
        label_visibility="collapsed",
    )

    # 인기 종목 바로가기
    st.markdown("##### 🔥 인기 종목")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🇰🇷 한국**")
        for name in list(POPULAR_KR_STOCKS.keys())[:5]:
            if st.button(name, key=f"kr_{name}", use_container_width=True):
                ticker_input = name
                st.session_state["_ticker_override"] = name
    with col2:
        st.markdown("**🇺🇸 미국**")
        for name in list(POPULAR_US_STOCKS.keys())[:5]:
            if st.button(name, key=f"us_{name}", use_container_width=True):
                ticker_input = name
                st.session_state["_ticker_override"] = name

    # 오버라이드 적용
    if "_ticker_override" in st.session_state:
        ticker_input = st.session_state.pop("_ticker_override")

    st.markdown("---")

    # 분석 설정
    st.markdown("##### ⚙️ 분석 설정")
    interval = st.selectbox(
        "봉 간격",
        options=["1m", "2m", "5m", "15m", "30m"],
        index=0,
        format_func=lambda x: {
            "1m": "1분봉", "2m": "2분봉", "5m": "5분봉",
            "15m": "15분봉", "30m": "30분봉"
        }.get(x, x),
    )

    period = st.selectbox(
        "조회 기간",
        options=["1d", "5d"],
        index=0,
        format_func=lambda x: {"1d": "오늘", "5d": "5일"}.get(x, x),
    )

    auto_refresh = st.toggle("🔄 자동 새로고침 (30초)", value=False)

    st.markdown("---")
    st.markdown(f'<div class="disclaimer">{DISCLAIMER}</div>', unsafe_allow_html=True)


# ============================================================
# 메인 영역
# ============================================================

# 헤더
st.markdown("""
<div class="app-header">
    <h1>ScalpX Pro</h1>
    <p>실시간 단타(스캘핑) 수익성 분석 대시보드</p>
</div>
""", unsafe_allow_html=True)

# 분석 실행
if ticker_input:
    fetcher = st.session_state.fetcher
    analyzer = st.session_state.analyzer

    try:
        # 티커 해석
        ticker = fetcher.resolve_ticker(ticker_input)

        # 장 상태 확인
        market_status = fetcher.is_market_open(ticker)
        st.info(market_status["message"])

        # 데이터 로드 (스피너)
        with st.spinner(f"📊 {ticker_input} 데이터 로딩 중..."):
            # 종목 정보
            stock_info = fetcher.get_stock_info(ticker)

            # 분봉 데이터
            try:
                df_intraday = fetcher.fetch_intraday_data(ticker, interval=interval, period=period)
            except Exception:
                # 1분봉 실패 시 5분봉으로 폴백
                df_intraday = fetcher.fetch_intraday_data(ticker, interval="5m", period="5d")

            # 일봉 데이터 (이동평균 참고용)
            df_daily = fetcher.fetch_daily_data(ticker)

        # 분석 수행
        # 분봉 데이터가 충분하면 분봉으로, 아니면 일봉으로 분석
        if len(df_intraday) >= 25:
            result = analyzer.analyze(df_intraday.copy(), ticker)
            analysis_data = df_intraday
            data_label = f"{interval} 분봉"
        else:
            result = analyzer.analyze(df_daily.copy(), ticker)
            analysis_data = df_daily
            data_label = "일봉"

        # ============================================================
        # 상단: 종목 정보 + 현재가
        # ============================================================
        st.markdown("---")

        top_col1, top_col2, top_col3, top_col4 = st.columns([2, 1, 1, 1])
        with top_col1:
            currency = stock_info["currency"]
            currency_symbol = "₩" if currency == "KRW" else "$"
            st.markdown(f"""
            <div style="padding: 8px 0;">
                <span style="font-size: 1.6rem; font-weight: 800; color: #e0e0ff;">
                    {stock_info['name']}
                </span>
                <span style="font-size: 0.9rem; color: #6b70a0; margin-left: 10px;">
                    {ticker}
                </span>
            </div>
            """, unsafe_allow_html=True)
        with top_col2:
            st.metric("현재가", f"{currency_symbol}{result.current_price:,.2f}")
        with top_col3:
            prev_close = stock_info.get("previous_close", 0)
            if prev_close > 0:
                change = result.current_price - prev_close
                change_pct = (change / prev_close) * 100
                st.metric("전일 대비", f"{change_pct:+.2f}%", delta=f"{change:+,.2f}")
            else:
                st.metric("전일 대비", "N/A")
        with top_col4:
            kst = pytz.timezone("Asia/Seoul")
            st.metric("분석 시간", datetime.now(kst).strftime("%H:%M:%S"))

        # ============================================================
        # 스코어보드 + 트레이딩 정보
        # ============================================================
        score_col, trade_col = st.columns([1, 1])

        with score_col:
            # 점수 색상
            if result.total_score >= 75:
                score_gradient = "linear-gradient(135deg, #00C851, #33ff99)"
            elif result.total_score >= 55:
                score_gradient = "linear-gradient(135deg, #33b5e5, #66ccff)"
            elif result.total_score >= 35:
                score_gradient = "linear-gradient(135deg, #ffbb33, #ffdd77)"
            else:
                score_gradient = "linear-gradient(135deg, #ff4444, #ff7777)"

            st.markdown(f"""
            <div class="score-board" style="text-align: center;">
                <div class="score-title">단타 수익성 점수</div>
                <div class="score-value" style="background: {score_gradient};
                     -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    {result.total_score:.0f}
                </div>
                <div style="color: #6b70a0; font-size: 0.85rem;">/ 100</div>
                <div class="score-signal" style="color: {result.signal_color};">
                    {result.signal_emoji} {result.signal}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with trade_col:
            st.markdown('<div class="score-board">', unsafe_allow_html=True)
            st.markdown(f'<div class="score-title">💰 매매 전략</div>', unsafe_allow_html=True)

            tc1, tc2, tc3 = st.columns(3)
            with tc1:
                st.markdown(f"""
                <div class="trade-box">
                    <div class="trade-label">진입가</div>
                    <div class="trade-value" style="color: #60a5fa;">
                        {currency_symbol}{result.entry_price:,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with tc2:
                st.markdown(f"""
                <div class="trade-box">
                    <div class="trade-label">손절가 (-{STOP_LOSS_PCT*100:.0f}%)</div>
                    <div class="trade-value" style="color: #ff6b6b;">
                        {currency_symbol}{result.stop_loss:,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with tc3:
                st.markdown(f"""
                <div class="trade-box">
                    <div class="trade-label">목표가 (+{TARGET_PROFIT_PCT*100:.0f}%)</div>
                    <div class="trade-value" style="color: #51cf66;">
                        {currency_symbol}{result.target_price:,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            rr_col1, rr_col2 = st.columns(2)
            with rr_col1:
                st.markdown(f"""
                <div style="text-align: center; margin-top: 14px;">
                    <span style="color: #8890b0; font-size: 0.8rem;">예상 수익률</span><br/>
                    <span style="font-size: 1.2rem; font-weight: 700; color: #51cf66;">
                        {result.expected_profit_pct:+.2f}%
                    </span>
                </div>
                """, unsafe_allow_html=True)
            with rr_col2:
                st.markdown(f"""
                <div style="text-align: center; margin-top: 14px;">
                    <span style="color: #8890b0; font-size: 0.8rem;">위험보상비 (R:R)</span><br/>
                    <span style="font-size: 1.2rem; font-weight: 700; color: #a78bfa;">
                        1 : {result.risk_reward_ratio}
                    </span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # ============================================================
        # 탭: 차트 / 지표 상세 / 분석 요약
        # ============================================================
        tab_chart, tab_indicators, tab_summary = st.tabs([
            "📊 실시간 차트", "📋 지표 상세", "📝 분석 요약"
        ])

        # --- 차트 탭 ---
        with tab_chart:
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.04,
                row_heights=[0.55, 0.25, 0.20],
                subplot_titles=[
                    f"{stock_info['name']} — {data_label} 캔들차트",
                    "거래량",
                    f"RSI ({result.indicators[1].value})",
                ],
            )

            # 캔들스틱
            fig.add_trace(
                go.Candlestick(
                    x=analysis_data.index,
                    open=analysis_data["open"],
                    high=analysis_data["high"],
                    low=analysis_data["low"],
                    close=analysis_data["close"],
                    increasing_line_color="#00C851",
                    decreasing_line_color="#ff4444",
                    increasing_fillcolor="#00C851",
                    decreasing_fillcolor="#ff4444",
                    name="가격",
                ),
                row=1, col=1,
            )

            # 이동평균선
            if result.ma_short is not None:
                fig.add_trace(
                    go.Scatter(
                        x=analysis_data.index, y=result.ma_short,
                        name=f"MA5", line=dict(color="#ffa726", width=1.2),
                        opacity=0.8,
                    ),
                    row=1, col=1,
                )
            if result.ma_long is not None:
                fig.add_trace(
                    go.Scatter(
                        x=analysis_data.index, y=result.ma_long,
                        name=f"MA20", line=dict(color="#42a5f5", width=1.2),
                        opacity=0.8,
                    ),
                    row=1, col=1,
                )

            # 볼린저 밴드
            if result.bb_upper is not None:
                fig.add_trace(
                    go.Scatter(
                        x=analysis_data.index, y=result.bb_upper,
                        name="BB 상단", line=dict(color="#ab47bc", width=1, dash="dot"),
                        opacity=0.5,
                    ),
                    row=1, col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        x=analysis_data.index, y=result.bb_lower,
                        name="BB 하단", line=dict(color="#ab47bc", width=1, dash="dot"),
                        fill="tonexty", fillcolor="rgba(171, 71, 188, 0.06)",
                        opacity=0.5,
                    ),
                    row=1, col=1,
                )

            # 진입가/손절가/목표가 라인
            fig.add_hline(
                y=result.entry_price, line_dash="dash",
                line_color="#60a5fa", line_width=1,
                annotation_text="진입가", annotation_position="right",
                row=1, col=1,
            )
            fig.add_hline(
                y=result.stop_loss, line_dash="dash",
                line_color="#ff6b6b", line_width=1,
                annotation_text="손절가", annotation_position="right",
                row=1, col=1,
            )
            fig.add_hline(
                y=result.target_price, line_dash="dash",
                line_color="#51cf66", line_width=1,
                annotation_text="목표가", annotation_position="right",
                row=1, col=1,
            )

            # 거래량 바 차트
            colors = [
                "#00C851" if c >= o else "#ff4444"
                for c, o in zip(analysis_data["close"], analysis_data["open"])
            ]
            fig.add_trace(
                go.Bar(
                    x=analysis_data.index,
                    y=analysis_data["volume"],
                    marker_color=colors,
                    name="거래량",
                    opacity=0.7,
                ),
                row=2, col=1,
            )
            # 거래량 평균선
            if result.volume_ma is not None:
                fig.add_trace(
                    go.Scatter(
                        x=analysis_data.index, y=result.volume_ma,
                        name="거래량 MA", line=dict(color="#ffa726", width=1),
                    ),
                    row=2, col=1,
                )

            # RSI
            if result.rsi is not None:
                fig.add_trace(
                    go.Scatter(
                        x=analysis_data.index, y=result.rsi,
                        name="RSI", line=dict(color="#ab47bc", width=1.5),
                    ),
                    row=3, col=1,
                )
                # RSI 과매수/과매도 라인
                fig.add_hline(y=70, line_dash="dot", line_color="rgba(255,100,100,0.4)", row=3, col=1)
                fig.add_hline(y=30, line_dash="dot", line_color="rgba(100,255,100,0.4)", row=3, col=1)
                fig.add_hrect(
                    y0=70, y1=100, fillcolor="rgba(255,100,100,0.05)",
                    line_width=0, row=3, col=1,
                )
                fig.add_hrect(
                    y0=0, y1=30, fillcolor="rgba(100,255,100,0.05)",
                    line_width=0, row=3, col=1,
                )

            # 차트 레이아웃
            fig.update_layout(
                height=700,
                template="plotly_dark",
                paper_bgcolor="rgba(15, 12, 41, 0)",
                plot_bgcolor="rgba(20, 20, 50, 0.6)",
                font=dict(family="Inter, sans-serif", color="#c0c5e0"),
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, font=dict(size=11),
                    bgcolor="rgba(0,0,0,0)",
                ),
                xaxis_rangeslider_visible=False,
                margin=dict(l=10, r=10, t=40, b=10),
                hovermode="x unified",
            )

            fig.update_xaxes(
                gridcolor="rgba(100, 100, 200, 0.08)",
                showgrid=True,
            )
            fig.update_yaxes(
                gridcolor="rgba(100, 100, 200, 0.08)",
                showgrid=True,
            )

            st.plotly_chart(fig, use_container_width=True, key="main_chart")

        # --- 지표 상세 탭 ---
        with tab_indicators:
            for ind in result.indicators:
                # 바 색상
                if ind.score >= 70:
                    bar_color = "#00C851"
                elif ind.score >= 50:
                    bar_color = "#33b5e5"
                elif ind.score >= 35:
                    bar_color = "#ffbb33"
                else:
                    bar_color = "#ff4444"

                # 시그널 색상
                if "매수" in ind.signal or "상승" in ind.signal or "급증" in ind.signal or "돌파" in ind.signal or "탈출" in ind.signal or "폭발" in ind.signal or "모멘텀" in ind.signal:
                    sig_color = "#51cf66"
                elif "매도" in ind.signal or "하락" in ind.signal or "저조" in ind.signal or "부진" in ind.signal or "과매수" in ind.signal:
                    sig_color = "#ff6b6b"
                else:
                    sig_color = "#ffd43b"

                st.markdown(f"""
                <div class="indicator-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="indicator-name">{ind.name}</div>
                        <div style="font-size: 1rem; font-weight: 700; color: {bar_color};">
                            {ind.score:.0f}/100 (기여: {ind.weighted_score:.1f}점)
                        </div>
                    </div>
                    <div class="indicator-signal" style="color: {sig_color};">
                        {ind.signal}
                    </div>
                    <div class="indicator-desc">{ind.description}</div>
                    <div class="indicator-bar-bg">
                        <div class="indicator-bar" style="width: {ind.score}%; background: {bar_color};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # --- 분석 요약 탭 ---
        with tab_summary:
            st.markdown(f"""
            <div class="score-board">
                <div style="font-size: 1.1rem; line-height: 1.8; color: #c0c5e0;">
                    {result.summary.replace(chr(10), '<br/>')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 부가 정보
            st.markdown("##### 📊 종목 부가 정보")
            info_col1, info_col2, info_col3 = st.columns(3)
            with info_col1:
                mc = stock_info.get("market_cap", 0)
                if mc > 0:
                    if mc >= 1_000_000_000_000:
                        mc_str = f"{mc / 1_000_000_000_000:.1f}조"
                    elif mc >= 100_000_000:
                        mc_str = f"{mc / 100_000_000:.0f}억"
                    elif mc >= 1_000_000_000:
                        mc_str = f"${mc / 1_000_000_000:.1f}B"
                    else:
                        mc_str = f"{mc:,.0f}"
                    st.metric("시가총액", mc_str)
                else:
                    st.metric("시가총액", "N/A")
            with info_col2:
                st.metric("업종", stock_info.get("sector", "N/A"))
            with info_col3:
                h52 = stock_info.get("fifty_two_week_high", 0)
                l52 = stock_info.get("fifty_two_week_low", 0)
                if h52 > 0:
                    st.metric("52주 고점", f"{currency_symbol}{h52:,.2f}")
                else:
                    st.metric("52주 고점", "N/A")

            # 데이터 프리뷰
            with st.expander("📄 원시 데이터 보기"):
                st.dataframe(
                    analysis_data.tail(50).style.format({
                        "open": "{:.2f}", "high": "{:.2f}",
                        "low": "{:.2f}", "close": "{:.2f}",
                        "volume": "{:,.0f}",
                    }),
                    use_container_width=True,
                )

    except Exception as e:
        st.error(f"❌ 오류 발생: {str(e)}")
        st.markdown("""
        <div style="background: rgba(255, 60, 60, 0.08); border: 1px solid rgba(255, 60, 60, 0.2); 
             border-radius: 12px; padding: 20px; margin-top: 10px;">
            <h4 style="color: #ff6b6b;">🔧 문제 해결 가이드</h4>
            <ul style="color: #b0b5d0; line-height: 2;">
                <li>종목명/코드를 다시 확인해주세요. (예: 삼성전자, NVDA, 005930)</li>
                <li>네트워크 연결 상태를 확인해주세요.</li>
                <li>API 요청 한도 초과 시 잠시 후 다시 시도해주세요.</li>
                <li>한국 종목은 6자리 숫자 코드도 사용 가능합니다.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

else:
    # 랜딩 화면
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
        <div style="font-size: 5rem; margin-bottom: 20px;">📊</div>
        <h2 style="color: #c0c5e0; font-weight: 700; margin-bottom: 10px;">
            종목을 검색하여 분석을 시작하세요
        </h2>
        <p style="color: #6b70a0; font-size: 1rem; max-width: 500px; margin: 0 auto; line-height: 1.8;">
            왼쪽 사이드바에서 종목명이나 코드를 입력하거나,<br/>
            인기 종목 버튼을 클릭하여 바로 분석할 수 있습니다.
        </p>
        <div style="margin-top: 40px; display: flex; justify-content: center; gap: 30px; flex-wrap: wrap;">
            <div style="background: rgba(30, 30, 80, 0.5); border: 1px solid rgba(100, 120, 255, 0.15); 
                 border-radius: 14px; padding: 24px 30px; min-width: 160px;">
                <div style="font-size: 1.8rem;">🎯</div>
                <div style="color: #aab0d0; font-weight: 600; margin-top: 8px;">스캘핑 점수</div>
                <div style="color: #6b70a0; font-size: 0.8rem; margin-top: 4px;">0-100점 종합 평가</div>
            </div>
            <div style="background: rgba(30, 30, 80, 0.5); border: 1px solid rgba(100, 120, 255, 0.15); 
                 border-radius: 14px; padding: 24px 30px; min-width: 160px;">
                <div style="font-size: 1.8rem;">📈</div>
                <div style="color: #aab0d0; font-weight: 600; margin-top: 8px;">실시간 차트</div>
                <div style="color: #6b70a0; font-size: 0.8rem; margin-top: 4px;">캔들 + 보조지표</div>
            </div>
            <div style="background: rgba(30, 30, 80, 0.5); border: 1px solid rgba(100, 120, 255, 0.15); 
                 border-radius: 14px; padding: 24px 30px; min-width: 160px;">
                <div style="font-size: 1.8rem;">💰</div>
                <div style="color: #aab0d0; font-weight: 600; margin-top: 8px;">매매 전략</div>
                <div style="color: #6b70a0; font-size: 0.8rem; margin-top: 4px;">진입/손절/목표가</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 자동 새로고침
# ============================================================
if auto_refresh and ticker_input:
    import time
    time.sleep(30)
    st.rerun()
