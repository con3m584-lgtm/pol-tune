import os
import time
import random
import base64
from datetime import datetime

import gradio as gr
import pandas as pd

# =====================================================
# 1. 파일 설정
# =====================================================
DATA_PATH = "crime_data.csv"
IMAGE_PATH = "astro_podori_posuni.png.png"

# =====================================================
# 2. 유틸
# =====================================================
def load_img_base64(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

def get_today_info():
    now = datetime.now()
    weekday_map = ["월", "화", "수", "목", "금", "토", "일"]
    return now.strftime("%Y.%m.%d"), weekday_map[now.weekday()]

IMG_BASE64 = load_img_base64(IMAGE_PATH)

# =====================================================
# 3. 데이터 로드
# =====================================================
def load_data():
    df = pd.read_csv(DATA_PATH, encoding="utf-8")

    required_cols = ["요일", "성별정리", "연령대", "범죄카테고리"]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"CSV 필수 컬럼 누락: {missing_cols}")

    for col in required_cols:
        df[col] = df[col].fillna("").astype(str).str.strip()

    grouped = (
        df.groupby(["요일", "성별정리", "연령대", "범죄카테고리"])
        .size()
        .reset_index(name="건수")
    )
    return grouped

FREQ_DF = load_data()

# =====================================================
# 4. 기본 설정
# =====================================================
AGE_CHOICES = ["10대", "20대", "30대", "40대", "50대", "60대이상"]
GENDER_CHOICES = ["남", "여"]

CRIME_ICONS = {
    "사기": "💳",
    "절도": "🔒",
    "폭력": "⚠️",
    "가정폭력": "🏠",
    "성범죄": "🚨",
    "주취소란": "🍺",
    "교통": "🚗",
    "실종": "📍",
    "생활소란": "🔊",
    "기타": "🔎"
}

CRIME_COLORS = {
    "성범죄": "#ff73bb",
    "폭력": "#ff9272",
    "가정폭력": "#ffb46e",
    "사기": "#78caff",
    "절도": "#739fff",
    "교통": "#98eb86",
    "주취소란": "#ffd96f",
    "실종": "#b592ff",
    "생활소란": "#cfd8ef",
    "기타": "#a9bde0"
}

CRIME_BADGES = {
    "성범죄": ("위험", "badge-danger"),
    "폭력": ("주의", "badge-warning"),
    "가정폭력": ("주의", "badge-warning"),
    "사기": ("경계", "badge-caution"),
    "절도": ("경계", "badge-caution"),
    "교통": ("주의", "badge-traffic"),
    "주취소란": ("관심", "badge-info"),
    "실종": ("관심", "badge-info"),
    "생활소란": ("참고", "badge-soft"),
    "기타": ("참고", "badge-soft")
}

CRIME_THEME = {
    "사기": "theme-fraud",
    "절도": "theme-theft",
    "폭력": "theme-violence",
    "가정폭력": "theme-home",
    "성범죄": "theme-sex",
    "주취소란": "theme-drink",
    "교통": "theme-traffic",
    "실종": "theme-missing",
    "생활소란": "theme-noise",
    "기타": "theme-etc"
}

# =====================================================
# 5. 상태
# =====================================================
def init_state():
    return {"step": "intro", "age": None, "gender": None}

# =====================================================
# 6. 문구 로직
# =====================================================
def tip_by_crime(age_group: str, crime: str) -> str:
    if crime == "교통":
        tips = {
            "10대": [
                "횡단보도에서는 신호를 끝까지 확인하세요.",
                "이어폰 착용 시 차량 접근을 더 주의하세요.",
                "자전거·킥보드 이용 시 교차로를 살피세요."
            ],
            "20대": [
                "보행 중 스마트폰 사용을 줄이세요.",
                "야간 이동 시 우회전 차량을 확인하세요.",
                "신호 위반 차량 접근을 한 번 더 살피세요."
            ],
            "30대": [
                "운전 시 전방 주시와 방어운전을 생활화하세요.",
                "골목길 진출입 시 보행자를 함께 살피세요.",
                "보행 중에도 차량 접근을 확인하세요."
            ],
            "40대": [
                "출퇴근 시간대 교차로 주변을 특히 주의하세요.",
                "운전 시 과속보다 주변 상황 확인을 우선하세요.",
                "야간 보행 시 밝은 길을 이용하세요."
            ],
            "50대": [
                "무리한 진로 변경보다 여유 있게 주행하세요.",
                "비 오는 날과 야간에는 시야 확보를 더 챙기세요.",
                "이면도로에서는 보행자 중심으로 살피세요."
            ],
            "60대이상": [
                "횡단보도에서는 여유 있게 건너세요.",
                "골목길에서는 잠시 멈춰 주변을 살피세요.",
                "야간 외출 시 밝은 옷이 도움이 됩니다."
            ]
        }
        return random.choice(tips.get(age_group, tips["20대"]))

    generic = {
        "사기": [
            "출처 불명 링크는 바로 누르지 마세요.",
            "기관 사칭 연락은 꼭 확인하세요.",
            "선입금 요구 거래는 의심해보세요."
        ],
        "절도": [
            "소지품을 시야에서 벗어나지 않게 하세요.",
            "차량 문단속을 다시 확인하세요.",
            "늦은 시간에는 주변을 함께 살피세요."
        ],
        "폭력": [
            "갈등 상황은 즉시 피하는 것이 좋습니다.",
            "시비에 휘말리지 않도록 주의하세요.",
            "혼자 해결하려 하지 마세요."
        ],
        "가정폭력": [
            "위험 신호를 가볍게 넘기지 마세요.",
            "위험 상황은 바로 도움을 요청하세요.",
            "가까운 사람과 상황을 공유하세요."
        ],
        "성범죄": [
            "늦은 시간에는 밝은 길을 이용하세요.",
            "낯선 접근이 느껴지면 도움을 요청하세요.",
            "귀가 전 이동 경로를 확인하세요."
        ],
        "주취소란": [
            "감정적 대응을 피하세요.",
            "술자리 후 이동 시 주변을 살피세요.",
            "충돌 상황과 거리를 두세요."
        ],
        "실종": [
            "이동 전 위치를 공유해두세요.",
            "낯선 장소에서는 일행과 떨어지지 마세요.",
            "휴대폰 상태를 수시로 확인하세요."
        ],
        "생활소란": [
            "감정적으로 대응하지 마세요.",
            "직접 충돌보다 거리 두기가 안전합니다.",
            "불편 상황이 길어지면 도움을 요청하세요."
        ],
        "기타": [
            "주변 상황을 한 번 더 살피세요.",
            "의심스러운 상황은 혼자 판단하지 마세요.",
            "안전한 이동 경로를 먼저 확인하세요."
        ]
    }
    return random.choice(generic.get(crime, generic["기타"]))

def summary_message(crimes):
    if not crimes:
        return "🔮 오늘은 비교적 차분한 흐름입니다. 기본적인 안전수칙을 한 번 더 확인해보세요."

    opening = random.choice([
        "🔮 오늘의 흐름을 비춰보면,",
        "🌙 오늘의 기운을 살펴보면,",
        "✨ 오늘은 특히,"
    ])

    if "사기" in crimes and "절도" in crimes:
        return f"{opening}<br><b>금전거래와 소지품 관리</b>에 조금 더 주의가 필요한 흐름입니다."
    if "교통" in crimes:
        return f"{opening}<br><b>이동 중 차량 흐름과 보행 안전</b>을 한 번 더 살펴보는 것이 좋겠습니다."
    if "폭력" in crimes or "주취소란" in crimes:
        return f"{opening}<br><b>감정 충돌과 긴장 상황</b>에 거리를 두는 편이 유리합니다."
    if "성범죄" in crimes:
        return f"{opening}<br><b>늦은 시간 이동 경로와 주변 분위기</b>를 더욱 세심하게 확인하는 것이 좋겠습니다."

    joined = " · ".join(crimes[:2])
    return f"{opening}<br><b>{joined}</b> 유형에 조금 더 주의가 필요한 흐름이 보입니다."

# =====================================================
# 7. 공통 HTML
# =====================================================
def topbar():
    return """
    <div class="topbar">
        <div class="topbar-title">🔮 오늘의 치안운세</div>
    </div>
    """

def progress(step: int):
    dots = []
    for i in range(1, 5):
        cls = "progress-dot active" if i <= step else "progress-dot"
        dots.append(f"<div class='{cls}'></div>")
    return f"<div class='progress-wrap'>{''.join(dots)}</div>"

# =====================================================
# 8. 화면 HTML
# =====================================================
def intro_screen():
    image_html = ""
    if IMG_BASE64:
        image_html = f"""
        <div class="hero-image-wrap">
            <div class="hero-aura hero-aura-1"></div>
            <div class="hero-aura hero-aura-2"></div>

            <div class="magic-stars star-a">✨</div>
            <div class="magic-stars star-b">⭐</div>
            <div class="magic-stars star-c">🌙</div>
            <div class="magic-stars star-d">✦</div>

            <div class="hero-ring hero-ring-1"></div>
            <div class="hero-ring hero-ring-2"></div>

            <div class="hero-image-crop">
                <img src="data:image/png;base64,{IMG_BASE64}" class="hero-image">
            </div>

            <div class="hero-bottom-light"></div>
        </div>
        """

    return f"""
    {topbar()}
    <div class="card">
        <div class="step-chip">1 / 4</div>
        {progress(1)}
        <div class="title">오늘의 치안운세</div>
        <div class="subtitle">
            포돌이와 포순이가<br>
            최근 신고 데이터를 바탕으로<br>
            오늘 조심해야 할 흐름을 알려드립니다
        </div>
        {image_html}
        <div class="hero-quote">신비로운 화면 속에서 오늘의 안전 포인트를 확인해보세요</div>
    </div>
    """

def age_screen():
    return f"""
    {topbar()}
    <div class="card">
        <div class="step-chip">2 / 4</div>
        {progress(2)}
        <div class="title">연령대 선택</div>
        <div class="subtitle">
            오늘의 흐름을 더 정확히 보기 위해<br>
            먼저 연령대를 선택해주세요
        </div>
        <div class="mini-orb-wrap">
            <div class="mini-aura"></div>
            <div class="mini-orb"></div>
            <div class="mini-ring"></div>
        </div>
    </div>
    """

def gender_screen(age):
    return f"""
    {topbar()}
    <div class="card">
        <div class="step-chip">3 / 4</div>
        {progress(3)}
        <div class="title">성별 선택</div>
        <div class="subtitle">
            <b>{age}</b> 기준으로 이어집니다.<br>
            마지막으로 성별을 선택해주세요
        </div>
        <div class="mini-orb-wrap">
            <div class="mini-aura"></div>
            <div class="mini-orb"></div>
            <div class="mini-ring"></div>
        </div>
    </div>
    """

def loading_screen(age, gender):
    return f"""
    {topbar()}
    <div class="card loading-card">
        <div class="step-chip">4 / 4</div>
        {progress(4)}
        <div class="loading-orb-wrap">
            <div class="loading-aura"></div>
            <div class="loading-ring loading-ring-1"></div>
            <div class="loading-ring loading-ring-2"></div>
            <div class="loading-orb"></div>
            <div class="loading-star s1">✨</div>
            <div class="loading-star s2">⭐</div>
            <div class="loading-star s3">🌙</div>
        </div>
        <div class="loading-title">운세를 읽는 중...</div>
        <div class="loading-sub">{age} / {gender} 조건의 흐름을 분석하고 있습니다</div>
    </div>
    """

def result_screen(age, gender):
    date_str, weekday = get_today_info()

    sub = FREQ_DF[
        (FREQ_DF["요일"] == weekday) &
        (FREQ_DF["성별정리"] == gender) &
        (FREQ_DF["연령대"] == age)
    ]

    if len(sub) == 0:
        sub = FREQ_DF[
            (FREQ_DF["성별정리"] == gender) &
            (FREQ_DF["연령대"] == age)
        ]

    if len(sub) == 0:
        sub = FREQ_DF[FREQ_DF["연령대"] == age]

    if len(sub) == 0:
        return f"""
        {topbar()}
        <div class="card">
            <div class="step-chip">4 / 4</div>
            {progress(4)}
            <div class="title">오늘의 치안운세</div>
            <div class="meta">{date_str} · {weekday}<br>{age} / {gender}</div>
            <div class="summary-box">
                <div class="summary-label">오늘의 한줄운세</div>
                <div class="summary-text">🔮 아직 이 조건의 데이터 흐름은 충분히 모이지 않았습니다.<br>다른 조건으로 다시 확인해보세요.</div>
            </div>
        </div>
        """

    top3 = (
        sub.groupby("범죄카테고리")["건수"]
        .sum()
        .sort_values(ascending=False)
        .head(3)
        .index.tolist()
    )

    cards = ""
    for i, crime in enumerate(top3, 1):
        icon = CRIME_ICONS.get(crime, "🔎")
        badge_text, badge_class = CRIME_BADGES.get(crime, ("참고", "badge-soft"))
        color = CRIME_COLORS.get(crime, "#a8bce0")
        theme = CRIME_THEME.get(crime, "theme-etc")

        cards += f"""
        <div class="crime-card {theme}" style="border-left-color:{color}; animation-delay:{(i-1)*0.12:.2f}s;">
            <div class="crime-header">
                <div class="crime-rank">{i}</div>
                <div class="crime-title-wrap">
                    <div class="crime-title">{icon} {crime}</div>
                    <div class="crime-mini-row">
                        <span class="crime-badge {badge_class}">{badge_text}</span>
                    </div>
                </div>
            </div>
            <div class="crime-desc">{tip_by_crime(age, crime)}</div>
        </div>
        """

    return f"""
    {topbar()}
    <div class="card">
        <div class="step-chip">4 / 4</div>
        {progress(4)}
        <div class="title">오늘의 치안운세</div>
        <div class="meta">{date_str} · {weekday}<br>{age} / {gender}</div>

        <div class="summary-box">
            <div class="summary-label">오늘의 한줄운세</div>
            <div class="summary-text">{summary_message(top3)}</div>
        </div>

        <div class="section-title">오늘 주의 범죄</div>
        <div class="crime-card-wrap">{cards}</div>
    </div>
    """

# =====================================================
# 9. 이벤트 함수
# =====================================================
def next_step(state, value):
    step = state["step"]

    if step == "intro":
        state["step"] = "age"
        return (
            age_screen(),
            gr.update(choices=AGE_CHOICES, value=None, visible=True, label="연령대 선택"),
            gr.update(value="✨ 다음", interactive=True),
            state
        )

    if step == "age":
        if value not in AGE_CHOICES:
            return (
                age_screen(),
                gr.update(visible=True),
                gr.update(value="✨ 다음", interactive=True),
                state
            )

        state["age"] = value
        state["step"] = "gender"
        return (
            gender_screen(value),
            gr.update(choices=GENDER_CHOICES, value=None, visible=True, label="성별 선택"),
            gr.update(value="🌙 결과 보기", interactive=True),
            state
        )

    if step == "gender":
        if value not in GENDER_CHOICES:
            return (
                gender_screen(state["age"]),
                gr.update(visible=True),
                gr.update(value="🌙 결과 보기", interactive=True),
                state
            )

        state["gender"] = value
        state["step"] = "loading"
        return (
            loading_screen(state["age"], state["gender"]),
            gr.update(visible=False, value=None),
            gr.update(value="🔮 다시 보기", interactive=False),
            state
        )

    state = init_state()
    return (
        intro_screen(),
        gr.update(visible=False, value=None),
        gr.update(value="🔮 시작하기", interactive=True),
        state
    )

def after_loading(state, current_screen):
    if state["step"] == "loading":
        time.sleep(0.9)
        state["step"] = "result"
        return (
            result_screen(state["age"], state["gender"]),
            gr.update(value="🔮 다시 보기", interactive=True),
            state
        )

    return (
        current_screen,
        gr.update(),
        state
    )

# =====================================================
# 10. CSS
# =====================================================
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Noto+Sans+KR:wght@400;500;700;800&display=swap');

body {
    background:
      radial-gradient(circle at 12% 14%, rgba(255,255,255,0.15) 1px, transparent 2px),
      radial-gradient(circle at 28% 32%, rgba(255,255,255,0.10) 1px, transparent 2px),
      radial-gradient(circle at 82% 18%, rgba(255,255,255,0.12) 1px, transparent 2px),
      radial-gradient(circle at 74% 42%, rgba(255,255,255,0.08) 1px, transparent 2px),
      radial-gradient(circle at 18% 78%, rgba(255,255,255,0.08) 1px, transparent 2px),
      linear-gradient(180deg, #10051f 0%, #1b1038 20%, #2c185b 42%, #1a2756 70%, #0f172d 100%);
    font-family: 'Noto Sans KR', sans-serif;
}

.gradio-container {
    max-width: 520px !important;
    margin: 0 auto !important;
    background: transparent !important;
    min-height: 100vh;
    padding-bottom: 96px !important;
}

.topbar {
    position: sticky;
    top: 0;
    z-index: 20;
    padding: 10px 6px 8px 6px;
    margin-bottom: 8px;
    backdrop-filter: blur(8px);
    background: linear-gradient(180deg, rgba(14,10,28,0.74), rgba(14,10,28,0.18));
}

.topbar-title {
    text-align: center;
    color: #f2f6ff;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.2px;
}

.card {
    width: 100%;
    background:
      radial-gradient(circle at 20% 20%, rgba(255,255,255,0.04) 1px, transparent 2px),
      radial-gradient(circle at 70% 30%, rgba(255,255,255,0.05) 1px, transparent 2px),
      linear-gradient(180deg, rgba(20,14,44,0.97) 0%, rgba(34,22,69,0.97) 45%, rgba(19,29,66,0.97) 100%);
    border-radius: 28px;
    padding: 20px 14px 18px 14px;
    box-shadow:
      0 20px 48px rgba(4,5,18,0.50),
      0 0 0 1px rgba(255,255,255,0.05) inset,
      0 0 30px rgba(108,124,255,0.08);
    border: 1px solid rgba(255,255,255,0.08);
    margin-top: 10px;
    position: relative;
    overflow: hidden;
}

.card:before {
    content: "";
    position: absolute;
    inset: 0;
    background:
      radial-gradient(circle at 50% -10%, rgba(162,126,255,0.10), transparent 40%),
      radial-gradient(circle at 90% 10%, rgba(92,197,255,0.08), transparent 28%);
    pointer-events: none;
}

.title, .section-title, .loading-title {
    font-family: 'Jua', 'Noto Sans KR', sans-serif;
    color: #fff;
}

.step-chip {
    width: fit-content;
    margin: 0 auto 10px auto;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    color: #edf4ff;
    background: linear-gradient(180deg, rgba(255,255,255,0.14), rgba(255,255,255,0.06));
    border: 1px solid rgba(255,255,255,0.10);
    position: relative;
    z-index: 2;
}

.progress-wrap {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-bottom: 12px;
    position: relative;
    z-index: 2;
}

.progress-dot {
    width: 38px;
    height: 6px;
    border-radius: 999px;
    background: rgba(255,255,255,0.10);
}

.progress-dot.active {
    background: linear-gradient(90deg, #ae8dff, #6db8ff);
    box-shadow: 0 0 12px rgba(126,166,255,0.30);
}

.title {
    text-align: center;
    font-size: 34px;
    margin-bottom: 10px;
    text-shadow: 0 0 18px rgba(151,125,255,0.18);
    position: relative;
    z-index: 2;
}

.subtitle {
    text-align: center;
    color: #edf1ff;
    font-size: 15px;
    line-height: 1.9;
    margin-bottom: 18px;
    font-weight: 500;
    position: relative;
    z-index: 2;
}

.meta {
    font-size: 14px;
    line-height: 1.8;
    color: #dce7ff;
    margin-bottom: 14px;
    font-weight: 500;
    text-align: center;
    position: relative;
    z-index: 2;
}

.hero-image-wrap {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 255px;
    margin: 0 auto 16px auto;
    overflow: visible;
    z-index: 2;
}

.hero-aura {
    position: absolute;
    border-radius: 50%;
    filter: blur(18px);
    animation: glowPulse 3.8s ease-in-out infinite;
}

.hero-aura-1 {
    width: 290px;
    height: 290px;
    background: radial-gradient(circle, rgba(167,129,255,0.28) 0%, rgba(87,141,255,0.16) 38%, rgba(255,255,255,0) 78%);
}

.hero-aura-2 {
    width: 205px;
    height: 205px;
    background: radial-gradient(circle, rgba(255,224,167,0.14) 0%, rgba(255,255,255,0) 74%);
    animation-delay: 1.2s;
}

.hero-ring {
    position: absolute;
    border-radius: 50%;
    border: 1.5px dashed rgba(195,186,255,0.22);
    animation: ringRotate 12s linear infinite;
}

.hero-ring-1 { width: 254px; height: 254px; }
.hero-ring-2 {
    width: 208px;
    height: 208px;
    border-color: rgba(255,219,132,0.14);
    animation-direction: reverse;
    animation-duration: 8s;
}

.hero-image-crop {
    position: relative;
    z-index: 3;
    width: min(100%, 420px);
    height: 250px;
    overflow: hidden;
    border-radius: 28px;
    background: transparent;
    box-shadow:
      0 12px 24px rgba(0,0,0,0.22),
      0 0 22px rgba(132,120,255,0.16);
}

.hero-image {
    display: block;
    width: 112%;
    height: 112%;
    object-fit: cover;
    object-position: center center;
    transform: translate(-6%, -6%);
    animation: heroFloat 3.1s ease-in-out infinite;
    filter:
      drop-shadow(0 10px 18px rgba(0,0,0,0.18))
      drop-shadow(0 0 18px rgba(137,119,255,0.14))
      brightness(1.02)
      contrast(1.03);
}

.hero-bottom-light {
    position: absolute;
    bottom: 10px;
    width: 185px;
    height: 26px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(176,188,255,0.22), rgba(255,255,255,0));
    filter: blur(8px);
    z-index: 1;
}

.magic-stars {
    position: absolute;
    font-size: 21px;
    opacity: 0.95;
    z-index: 4;
    animation: sparkle 2.7s ease-in-out infinite;
}

.star-a { top: 10px; left: 14px; }
.star-b { top: 14px; right: 14px; animation-delay: 0.5s; }
.star-c { bottom: 18px; left: 24px; animation-delay: 1s; }
.star-d { bottom: 16px; right: 22px; animation-delay: 1.5s; }

.hero-quote {
    margin-top: 8px;
    text-align: center;
    font-size: 14px;
    color: #e6eaff;
    font-weight: 700;
    line-height: 1.7;
    position: relative;
    z-index: 2;
}

.mini-orb-wrap {
    position: relative;
    width: 116px;
    height: 116px;
    margin: 14px auto 4px auto;
    z-index: 2;
}

.mini-aura {
    position: absolute;
    width: 116px;
    height: 116px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(158,132,255,0.18), rgba(255,255,255,0));
    filter: blur(8px);
}

.mini-orb {
    width: 72px;
    height: 72px;
    border-radius: 50%;
    position: absolute;
    left: 22px;
    top: 22px;
    background: radial-gradient(circle, rgba(255,255,255,0.98), rgba(201,212,255,0.74), rgba(121,103,255,0.38));
    box-shadow:
      0 0 26px rgba(150,120,255,0.28),
      0 0 12px rgba(109,184,255,0.18);
    animation: orbPulse 2.5s ease-in-out infinite;
}

.mini-ring {
    width: 116px;
    height: 116px;
    border-radius: 50%;
    border: 1.5px dashed rgba(203,190,255,0.24);
    animation: ringRotate 8s linear infinite;
}

.loading-card {
    text-align: center;
}

.loading-orb-wrap {
    position: relative;
    width: 150px;
    height: 150px;
    margin: 8px auto 18px auto;
    z-index: 2;
}

.loading-aura {
    position: absolute;
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(152,126,255,0.24), rgba(255,255,255,0));
    filter: blur(10px);
}

.loading-orb {
    position: absolute;
    left: 35px;
    top: 35px;
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,0.96), rgba(183,210,255,0.70), rgba(100,87,255,0.36));
    box-shadow:
      0 0 30px rgba(132,120,255,0.30),
      0 0 16px rgba(93,184,255,0.20);
    animation: orbPulse 2s ease-in-out infinite;
}

.loading-ring {
    position: absolute;
    border-radius: 50%;
    border: 2px dashed rgba(195,186,255,0.24);
    animation: ringRotate 7s linear infinite;
}

.loading-ring-1 {
    width: 150px;
    height: 150px;
    top: 0;
    left: 0;
}

.loading-ring-2 {
    width: 120px;
    height: 120px;
    top: 15px;
    left: 15px;
    border-color: rgba(255,219,132,0.14);
    animation-direction: reverse;
}

.loading-star {
    position: absolute;
    font-size: 20px;
    animation: sparkle 2s ease-in-out infinite;
}

.s1 { top: 10px; left: 18px; }
.s2 { top: 22px; right: 12px; animation-delay: 0.5s; }
.s3 { bottom: 14px; left: 18px; animation-delay: 1s; }

.loading-title {
    font-size: 30px;
    margin-bottom: 8px;
    text-shadow: 0 0 18px rgba(151,125,255,0.18);
    position: relative;
    z-index: 2;
}

.loading-sub {
    color: #e6eaff;
    font-size: 15px;
    line-height: 1.8;
    font-weight: 600;
    position: relative;
    z-index: 2;
}

.summary-box {
    background: linear-gradient(135deg, rgba(131,96,255,0.24), rgba(87,170,255,0.14));
    border-radius: 18px;
    padding: 15px;
    margin-bottom: 16px;
    border: 1px solid rgba(177,185,255,0.14);
    box-shadow: 0 10px 22px rgba(0,0,0,0.14);
    position: relative;
    z-index: 2;
}

.summary-label {
    font-size: 13px;
    color: #cfe0ff !important;
    font-weight: 700;
    margin-bottom: 6px;
}

.summary-text {
    font-size: 17px;
    font-weight: 700;
    line-height: 1.8;
    text-align: center;
    color: #ffffff;
    animation: summaryFade 0.7s ease-out;
}

.section-title {
    font-size: 24px;
    margin-bottom: 10px;
    position: relative;
    z-index: 2;
}

.crime-card-wrap {
    display: flex;
    flex-direction: column;
    gap: 16px;
    position: relative;
    z-index: 2;
}

.crime-card {
    border-radius: 20px;
    padding: 18px;
    border-left: 6px solid #6ab0ff;
    box-shadow:
      0 12px 24px rgba(0,0,0,0.22),
      0 0 12px rgba(115,159,255,0.08);
    opacity: 0;
    transform: translateY(18px) scale(0.98);
    animation: cardReveal 0.55s ease-out forwards;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.crime-card:active {
    transform: scale(0.98);
}

.theme-fraud { background: linear-gradient(180deg, rgba(62,84,158,0.92), rgba(29,38,83,0.95)); }
.theme-theft { background: linear-gradient(180deg, rgba(28,72,124,0.92), rgba(14,32,63,0.95)); }
.theme-violence { background: linear-gradient(180deg, rgba(110,44,58,0.92), rgba(56,20,30,0.95)); }
.theme-home { background: linear-gradient(180deg, rgba(96,64,38,0.92), rgba(48,28,16,0.95)); }
.theme-sex { background: linear-gradient(180deg, rgba(113,34,73,0.92), rgba(54,12,34,0.95)); }
.theme-drink { background: linear-gradient(180deg, rgba(92,72,24,0.92), rgba(48,34,12,0.95)); }
.theme-traffic { background: linear-gradient(180deg, rgba(48,88,32,0.92), rgba(18,42,12,0.95)); }
.theme-missing { background: linear-gradient(180deg, rgba(53,61,122,0.92), rgba(26,30,70,0.95)); }
.theme-noise { background: linear-gradient(180deg, rgba(78,82,110,0.92), rgba(34,36,56,0.95)); }
.theme-etc { background: linear-gradient(180deg, rgba(54,62,90,0.92), rgba(22,28,48,0.95)); }

.crime-header {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 8px;
}

.crime-rank {
    width: 36px;
    height: 36px;
    min-width: 36px;
    border-radius: 999px;
    background: linear-gradient(180deg, #b293ff, #6698ff);
    color: white !important;
    font-size: 15px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 14px rgba(126,166,255,0.20);
}

.crime-title-wrap {
    flex: 1;
}

.crime-title {
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 7px;
    color: #ffffff;
}

.crime-mini-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.crime-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    line-height: 1;
}

.badge-danger { background: rgba(255,102,138,0.20); border: 1px solid rgba(255,128,160,0.35); color: #ffe5ec !important; }
.badge-warning { background: rgba(255,168,106,0.20); border: 1px solid rgba(255,190,130,0.35); color: #fff1dc !important; }
.badge-caution { background: rgba(255,220,116,0.18); border: 1px solid rgba(255,225,140,0.30); color: #fff6dc !important; }
.badge-traffic { background: rgba(141,217,255,0.20); border: 1px solid rgba(160,226,255,0.35); color: #e6f8ff !important; }
.badge-info { background: rgba(160,180,255,0.18); border: 1px solid rgba(182,199,255,0.30); color: #eef2ff !important; }
.badge-soft { background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.18); color: #f0f5ff !important; }

.crime-desc {
    font-size: 16px;
    line-height: 1.9;
    font-weight: 500;
    color: #eef3ff;
}

button.primary {
    position: sticky !important;
    bottom: 10px !important;
    z-index: 30 !important;
    background: linear-gradient(180deg, #9a7dff 0%, #6c8cff 35%, #5db8ff 100%) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 18px !important;
    box-shadow:
      0 14px 28px rgba(31,49,131,0.35),
      0 0 16px rgba(111,130,255,0.12) !important;
    font-weight: 800 !important;
    font-size: 17px !important;
    padding: 14px 18px !important;
    min-height: 54px !important;
}

button.primary:hover {
    filter: brightness(1.06);
    transform: translateY(-1px);
}

.gradio-container .form,
.gradio-container .gr-form,
.gradio-container fieldset,
.gradio-container .block,
.gradio-container .gr-block {
    background: transparent !important;
}

.gradio-container .gradio-radio,
.gradio-container .radio-group {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.gradio-container .block-label,
.gradio-container .label-wrap,
.gradio-container .gr-label {
    color: #f3f7ff !important;
    font-weight: 800 !important;
    background: transparent !important;
    margin-bottom: 8px !important;
    font-size: 15px !important;
}

.gradio-container .wrap {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 10px !important;
    background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03)) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 18px !important;
    padding: 12px !important;
}

.gradio-container .wrap label {
    background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.05)) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 16px !important;
    padding: 12px 14px !important;
    min-width: 78px;
    text-align: center;
    font-size: 16px !important;
    font-weight: 700 !important;
    color: #eaf2ff !important;
    box-shadow: 0 8px 16px rgba(0,0,0,0.10);
}

@keyframes heroFloat {
    0% { transform: translate(-6%, -6%) translateY(0) scale(1); }
    50% { transform: translate(-6%, -6%) translateY(-8px) scale(1.02); }
    100% { transform: translate(-6%, -6%) translateY(0) scale(1); }
}

@keyframes sparkle {
    0%,100% { opacity: 0.42; transform: scale(0.92); }
    50% { opacity: 1; transform: scale(1.2); }
}

@keyframes glowPulse {
    0%,100% { transform: scale(0.96); opacity: 0.72; }
    50% { transform: scale(1.06); opacity: 1; }
}

@keyframes ringRotate {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes orbPulse {
    0%,100% { transform: scale(0.98); }
    50% { transform: scale(1.04); }
}

@keyframes cardReveal {
    0% { opacity: 0; transform: translateY(18px) scale(0.98); }
    100% { opacity: 1; transform: translateY(0) scale(1); }
}

@keyframes summaryFade {
    0% { opacity: 0; transform: translateY(8px); }
    100% { opacity: 1; transform: translateY(0); }
}

@media (max-width: 640px) {
    .title { font-size: 29px; }
    .hero-image-crop { width: min(100%, 365px); height: 220px; }
    .crime-card { padding: 16px; border-radius: 18px; }
    .crime-title { font-size: 17px; }
    .crime-desc { font-size: 15px; line-height: 1.8; }
    .summary-text { font-size: 15px; }
}
"""

# =====================================================
# 11. UI
# =====================================================
with gr.Blocks(css=CSS, theme=gr.themes.Soft()) as demo:
    state = gr.State(init_state())

    screen = gr.HTML(intro_screen())
    select = gr.Radio([], visible=False, label="")
    btn = gr.Button("🔮 시작하기", variant="primary")

    event = btn.click(
        next_step,
        inputs=[state, select],
        outputs=[screen, select, btn, state],
        queue=False
    )

    event.then(
        after_loading,
        inputs=[state, screen],
        outputs=[screen, btn, state],
        queue=False
    )

demo.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", 7860)),
    show_error=True
)
