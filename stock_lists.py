"""
한국/미국 주요 주식 종목 리스트
자동완성 검색에 사용됩니다.
"""

# ============================================================
# 한국 주식 (KOSPI + KOSDAQ 주요 종목)
# 형식: {"종목명": "종목코드.KS 또는 .KQ"}
# ============================================================
KR_STOCKS = {
    # KOSPI 대형주
    "삼성전자": "005930.KS",
    "삼성전자우": "005935.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "삼성바이오로직스": "207940.KS",
    "현대차": "005380.KS",
    "현대차2우B": "005387.KS",
    "현대차우": "005385.KS",
    "기아": "000270.KS",
    "셀트리온": "068270.KS",
    "KB금융": "105560.KS",
    "POSCO홀딩스": "005490.KS",
    "NAVER": "035420.KS",
    "카카오": "035720.KS",
    "LG화학": "051910.KS",
    "삼성SDI": "006400.KS",
    "현대모비스": "012330.KS",
    "신한지주": "055550.KS",
    "SK이노베이션": "096770.KS",
    "SK텔레콤": "017670.KS",
    "SK": "034730.KS",
    "LG전자": "066570.KS",
    "LG": "003550.KS",
    "삼성물산": "028260.KS",
    "삼성생명": "032830.KS",
    "삼성화재": "000810.KS",
    "삼성전기": "009150.KS",
    "삼성SDS": "018260.KS",
    "삼성에스디에스": "018260.KS",
    "카카오뱅크": "323410.KS",
    "카카오페이": "377300.KS",
    "하나금융지주": "086790.KS",
    "우리금융지주": "316140.KS",
    "KT&G": "033780.KS",
    "KT": "030200.KS",
    "한국전력": "015760.KS",
    "포스코퓨처엠": "003670.KS",
    "HD현대중공업": "329180.KS",
    "HD한국조선해양": "009540.KS",
    "HD현대": "267250.KS",
    "한화에어로스페이스": "012450.KS",
    "한화오션": "042660.KS",
    "한화솔루션": "009830.KS",
    "한화": "000880.KS",
    "두산에너빌리티": "034020.KS",
    "두산밥캣": "241560.KS",
    "두산로보틱스": "454910.KS",
    "현대건설": "000720.KS",
    "현대글로비스": "086280.KS",
    "현대제철": "004020.KS",
    "현대로템": "064350.KS",
    "현대엘리베이": "017800.KS",
    "기업은행": "024110.KS",
    "대한항공": "003490.KS",
    "아시아나항공": "020560.KS",
    "한국항공우주": "047810.KS",
    "LG이노텍": "011070.KS",
    "LG디스플레이": "034220.KS",
    "LG유플러스": "032640.KS",
    "LG생활건강": "051900.KS",
    "아모레퍼시픽": "090430.KS",
    "아모레G": "002790.KS",
    "CJ제일제당": "097950.KS",
    "CJ": "001040.KS",
    "CJ ENM": "035760.KS",
    "넷마블": "251270.KS",
    "엔씨소프트": "036570.KS",
    "크래프톤": "259960.KS",
    "펄어비스": "263750.KS",
    "한미반도체": "042700.KS",
    "SK스퀘어": "402340.KS",
    "고려아연": "010130.KS",
    "롯데케미칼": "011170.KS",
    "롯데지주": "004990.KS",
    "S-Oil": "010950.KS",
    "GS": "078930.KS",
    "GS건설": "006360.KS",
    "미래에셋증권": "006800.KS",
    "한국투자증권": "071050.KS",
    "삼성증권": "016360.KS",
    "NH투자증권": "005940.KS",
    "키움증권": "039490.KS",
    "메리츠금융지주": "138040.KS",
    "DB손해보험": "005830.KS",
    "한화생명": "088350.KS",
    "포스코인터내셔널": "047050.KS",
    "에코프로": "086520.KS",
    "에코프로비엠": "247540.KS",
    "금양": "001570.KS",
    "HLB": "028300.KS",
    "SK바이오팜": "326030.KS",
    "유한양행": "000100.KS",
    "녹십자": "006280.KS",
    "한미약품": "128940.KS",
    "종근당": "185750.KS",
    "일진머티리얼즈": "020150.KS",
    "코스모신소재": "005070.KS",
    "LS ELECTRIC": "010120.KS",
    "LS": "006260.KS",
    "효성중공업": "298040.KS",
    "HD현대일렉트릭": "267260.KS",

    # KOSDAQ 주요 종목
    "에코프로에이치엔": "383310.KQ",
    "알테오젠": "196170.KQ",
    "HLB생명과학": "067630.KQ",
    "레인보우로보틱스": "277810.KQ",
    "리노공업": "058470.KQ",
    "HPSP": "403870.KQ",
    "클래시스": "214150.KQ",
    "파크시스템스": "140860.KQ",
    "주성엔지니어링": "036930.KQ",
    "이오테크닉스": "039030.KQ",
    "솔브레인": "357780.KQ",
    "에스티팜": "237690.KQ",
    "셀트리온제약": "068760.KQ",
    "JYP Ent": "035900.KQ",
    "SM": "041510.KQ",
    "하이브": "352820.KS",
    "와이지엔터테인먼트": "122870.KQ",
    "카카오게임즈": "293490.KQ",
    "위메이드": "112040.KQ",
    "컴투스": "078340.KQ",
    "씨젠": "096530.KQ",
    "셀리버리": "268600.KQ",
    "메디톡스": "086900.KQ",
    "CJ프레시웨이": "051500.KQ",
    "티씨케이": "064760.KQ",
    "원익IPS": "240810.KQ",
    "피에스케이": "319660.KQ",
    "테크윙": "089030.KQ",
    "심텍": "222800.KQ",
    "ISC": "095340.KQ",
    "코미코": "183300.KQ",
    "엘앤에프": "066970.KQ",
    "천보": "278280.KQ",
    "나노신소재": "121600.KQ",
    "포스코DX": "022100.KQ",
    "더블유게임즈": "192080.KQ",
    "케이카": "381970.KQ",
    "루닛": "328130.KQ",
    "뷰노": "338220.KQ",
}


# ============================================================
# 미국 주식 (S&P 500 + 주요 나스닥 종목)
# 형식: {"티커 (회사명)": "티커"}
# ============================================================
US_STOCKS = {
    # 빅테크 / 매그니피센트 7
    "AAPL (Apple)": "AAPL",
    "MSFT (Microsoft)": "MSFT",
    "GOOGL (Alphabet/Google)": "GOOGL",
    "GOOG (Alphabet Class C)": "GOOG",
    "AMZN (Amazon)": "AMZN",
    "NVDA (NVIDIA)": "NVDA",
    "META (Meta/Facebook)": "META",
    "TSLA (Tesla)": "TSLA",

    # 반도체
    "AMD (Advanced Micro Devices)": "AMD",
    "INTC (Intel)": "INTC",
    "AVGO (Broadcom)": "AVGO",
    "QCOM (Qualcomm)": "QCOM",
    "TXN (Texas Instruments)": "TXN",
    "MU (Micron)": "MU",
    "MRVL (Marvell)": "MRVL",
    "LRCX (Lam Research)": "LRCX",
    "AMAT (Applied Materials)": "AMAT",
    "KLAC (KLA Corp)": "KLAC",
    "ASML (ASML Holdings)": "ASML",
    "TSM (TSMC)": "TSM",
    "ARM (Arm Holdings)": "ARM",
    "SMCI (Super Micro Computer)": "SMCI",
    "ON (ON Semiconductor)": "ON",

    # 소프트웨어 / 클라우드
    "CRM (Salesforce)": "CRM",
    "ORCL (Oracle)": "ORCL",
    "ADBE (Adobe)": "ADBE",
    "NOW (ServiceNow)": "NOW",
    "SNOW (Snowflake)": "SNOW",
    "PLTR (Palantir)": "PLTR",
    "PANW (Palo Alto Networks)": "PANW",
    "CRWD (CrowdStrike)": "CRWD",
    "ZS (Zscaler)": "ZS",
    "DDOG (Datadog)": "DDOG",
    "NET (Cloudflare)": "NET",
    "MDB (MongoDB)": "MDB",
    "SHOP (Shopify)": "SHOP",
    "SQ (Block/Square)": "SQ",
    "UBER (Uber)": "UBER",
    "DASH (DoorDash)": "DASH",
    "ABNB (Airbnb)": "ABNB",
    "COIN (Coinbase)": "COIN",
    "HOOD (Robinhood)": "HOOD",
    "U (Unity)": "U",
    "RBLX (Roblox)": "RBLX",
    "TWLO (Twilio)": "TWLO",

    # AI / 로봇
    "AI (C3.ai)": "AI",
    "BBAI (BigBear.ai)": "BBAI",
    "SOUN (SoundHound AI)": "SOUN",
    "UPST (Upstart)": "UPST",
    "PATH (UiPath)": "PATH",
    "IONQ (IonQ)": "IONQ",
    "RGTI (Rigetti)": "RGTI",

    # 스트리밍 / 미디어
    "NFLX (Netflix)": "NFLX",
    "DIS (Disney)": "DIS",
    "SPOT (Spotify)": "SPOT",
    "ROKU (Roku)": "ROKU",
    "WBD (Warner Bros)": "WBD",
    "PARA (Paramount)": "PARA",

    # 게임
    "RBLX (Roblox)": "RBLX",
    "EA (Electronic Arts)": "EA",
    "TTWO (Take-Two)": "TTWO",
    "ATVI (Activision)": "ATVI",

    # 전자상거래 / 소비재
    "WMT (Walmart)": "WMT",
    "COST (Costco)": "COST",
    "TGT (Target)": "TGT",
    "HD (Home Depot)": "HD",
    "LOW (Lowe's)": "LOW",
    "NKE (Nike)": "NKE",
    "SBUX (Starbucks)": "SBUX",
    "MCD (McDonald's)": "MCD",
    "PEP (PepsiCo)": "PEP",
    "KO (Coca-Cola)": "KO",
    "PG (Procter & Gamble)": "PG",

    # 금융
    "JPM (JPMorgan Chase)": "JPM",
    "BAC (Bank of America)": "BAC",
    "WFC (Wells Fargo)": "WFC",
    "GS (Goldman Sachs)": "GS",
    "MS (Morgan Stanley)": "MS",
    "C (Citigroup)": "C",
    "BRK-B (Berkshire Hathaway)": "BRK-B",
    "V (Visa)": "V",
    "MA (Mastercard)": "MA",
    "PYPL (PayPal)": "PYPL",
    "AXP (American Express)": "AXP",
    "SCHW (Charles Schwab)": "SCHW",

    # 헬스케어 / 바이오
    "JNJ (Johnson & Johnson)": "JNJ",
    "UNH (UnitedHealth)": "UNH",
    "LLY (Eli Lilly)": "LLY",
    "NVO (Novo Nordisk)": "NVO",
    "PFE (Pfizer)": "PFE",
    "ABBV (AbbVie)": "ABBV",
    "MRK (Merck)": "MRK",
    "TMO (Thermo Fisher)": "TMO",
    "ABT (Abbott)": "ABT",
    "BMY (Bristol-Myers)": "BMY",
    "GILD (Gilead)": "GILD",
    "AMGN (Amgen)": "AMGN",
    "MRNA (Moderna)": "MRNA",
    "ISRG (Intuitive Surgical)": "ISRG",

    # 에너지
    "XOM (ExxonMobil)": "XOM",
    "CVX (Chevron)": "CVX",
    "COP (ConocoPhillips)": "COP",
    "SLB (Schlumberger)": "SLB",
    "EOG (EOG Resources)": "EOG",

    # EV / 에너지
    "RIVN (Rivian)": "RIVN",
    "LCID (Lucid)": "LCID",
    "NIO (NIO)": "NIO",
    "LI (Li Auto)": "LI",
    "XPEV (XPeng)": "XPEV",
    "ENPH (Enphase Energy)": "ENPH",
    "FSLR (First Solar)": "FSLR",
    "PLUG (Plug Power)": "PLUG",

    # 항공우주 / 방산
    "BA (Boeing)": "BA",
    "LMT (Lockheed Martin)": "LMT",
    "RTX (RTX/Raytheon)": "RTX",
    "NOC (Northrop Grumman)": "NOC",
    "GD (General Dynamics)": "GD",

    # 통신
    "T (AT&T)": "T",
    "VZ (Verizon)": "VZ",
    "TMUS (T-Mobile)": "TMUS",

    # 산업재
    "CAT (Caterpillar)": "CAT",
    "DE (John Deere)": "DE",
    "UPS (UPS)": "UPS",
    "FDX (FedEx)": "FDX",
    "GE (GE Aerospace)": "GE",
    "HON (Honeywell)": "HON",
    "MMM (3M)": "MMM",
    "UNP (Union Pacific)": "UNP",

    # 기타 인기
    "SOFI (SoFi)": "SOFI",
    "MARA (Marathon Digital)": "MARA",
    "RIOT (Riot Platforms)": "RIOT",
    "GME (GameStop)": "GME",
    "AMC (AMC Entertainment)": "AMC",
    "BABA (Alibaba)": "BABA",
    "JD (JD.com)": "JD",
    "PDD (PDD Holdings)": "PDD",
}


def search_kr_stocks(query: str) -> list:
    """한국 주식 종목 검색 (초성/이름 매칭)"""
    if not query:
        return list(KR_STOCKS.keys())

    query = query.strip().lower()
    results = []
    for name in KR_STOCKS:
        if query in name.lower():
            results.append(name)
    # 종목 코드로도 검색
    for name, code in KR_STOCKS.items():
        code_num = code.split(".")[0]
        if query in code_num:
            if name not in results:
                results.append(name)
    return results


def search_us_stocks(query: str) -> list:
    """미국 주식 종목 검색 (티커/회사명 매칭)"""
    if not query:
        return list(US_STOCKS.keys())

    query = query.strip().lower()
    results = []
    for name in US_STOCKS:
        if query in name.lower():
            results.append(name)
    return results
