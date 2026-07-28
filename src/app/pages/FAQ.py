import html
import re
import textwrap
from pathlib import Path

import pandas as pd
import streamlit as st

# =========================================================
# 기본 설정
# =========================================================
MAX_LINE_LENGTH = 74

CURRENT_DIR = Path(__file__).resolve().parent
CSV_CANDIDATES = [
    CURRENT_DIR / "data" / "faq" / "car_faq.csv",
    CURRENT_DIR.parent / "data" / "faq" / "car_faq.csv",
    Path("data/faq/car_faq.csv"),
    Path("car_faq.csv"),
]

# =========================================================
# CSV 파일 찾기 및 불러오기
# =========================================================
def find_csv_path() -> Path:
    """사용 가능한 car_faq.csv 경로를 찾아 반환합니다."""
    for path in CSV_CANDIDATES:
        if path.exists():
            return path

    searched_paths = "\n".join(f"- {path}" for path in CSV_CANDIDATES)
    raise FileNotFoundError(
        "car_faq.csv 파일을 찾을 수 없습니다.\n"
        "아래 경로 중 한 곳에 파일이 있는지 확인하세요.\n"
        f"{searched_paths}"
    )


@st.cache_data
def load_faq_data() -> pd.DataFrame:
    """FAQ CSV 파일을 읽고 질문·답변의 불필요한 공백을 제거합니다."""
    csv_path = find_csv_path()

    df = pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
    )

    required_columns = {"question", "answer"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "CSV 파일에 필요한 열이 없습니다: "
            + ", ".join(sorted(missing_columns))
        )

    df["question"] = df["question"].astype(str).str.strip()
    df["answer"] = df["answer"].astype(str).str.strip()

    return df


# =========================================================
# 텍스트 정리 및 줄바꿈 함수
# =========================================================
def normalize_spaces(text: str) -> str:
    """줄바꿈과 여러 공백을 한 칸으로 정리합니다."""
    return re.sub(r"\s+", " ", str(text)).strip()


def wrap_lines(
    text: str,
    width: int = MAX_LINE_LENGTH,
) -> list[str]:
    clean_text = normalize_spaces(text)
    if not clean_text:
        return []

    return textwrap.wrap(
        clean_text,
        width=max(width, 10),
        break_long_words=False,
        break_on_hyphens=False,
        replace_whitespace=True,
        drop_whitespace=True,
    )


def convert_links(text: str) -> str:
    safe_text = html.escape(str(text))
    link_html = (
        '<a href="https://www.car.go.kr" target="_blank" '
        'rel="noopener noreferrer">자동차리콜센터</a>'
    )
    safe_text = safe_text.replace("https://www.car.go.kr", link_html)
    safe_text = safe_text.replace("www.car.go.kr", link_html)
    return safe_text


def split_numbered_items(text: str) -> list[str]:
    clean_text = normalize_spaces(text)
    pattern = (
        r"(?="
        r"(?:\d+\.\s+)"
        r"|(?:[①②③④⑤⑥⑦⑧⑨⑩]\s*)"
        r"|(?:ㅇ\s+)"
        r"|(?:[-*]\s+)"
        r")"
    )
    marked_text = re.sub(pattern, "|||", clean_text)
    return [block.strip() for block in marked_text.split("|||") if block.strip()]


def format_normal_block(text: str) -> str:
    lines = wrap_lines(text, MAX_LINE_LENGTH)
    return "<br>".join(convert_links(line) for line in lines)


def format_numbered_block(marker: str, content: str) -> str:
    base_indent = 4
    marker_space = len(marker) + 1
    content_width = MAX_LINE_LENGTH - base_indent - marker_space

    lines = wrap_lines(content, content_width)

    if not lines:
        return (
            f'<div class="faq-numbered-item">'
            f'<span class="faq-marker">{convert_links(marker)}</span>'
            f"</div>"
        )

    line_html = "<br>".join(convert_links(line) for line in lines)

    return (
        '<div class="faq-numbered-item">'
        f'<span class="faq-marker">{convert_links(marker)}</span>'
        f'<span class="faq-item-content">{line_html}</span>'
        "</div>"
    )


def format_bullet_block(content: str) -> str:
    content_width = MAX_LINE_LENGTH - 7
    lines = wrap_lines(content, content_width)

    if not lines:
        return ""

    line_html = "<br>".join(convert_links(line) for line in lines)

    return (
        '<div class="faq-numbered-item">'
        '<span class="faq-marker">•</span>'
        f'<span class="faq-item-content">{line_html}</span>'
        "</div>"
    )


def format_heading_block(content: str) -> str:
    lines = wrap_lines(content, MAX_LINE_LENGTH - 2)
    return (
        '<div class="faq-subheading">'
        + "<br>".join(convert_links(line) for line in lines)
        + "</div>"
    )


def format_answer(text: str) -> str:
    blocks = split_numbered_items(text)
    formatted_blocks = []

    for block in blocks:
        numbered_match = re.match(
            r"^(\d+\.|[①②③④⑤⑥⑦⑧⑨⑩])\s*(.*)$",
            block,
            flags=re.DOTALL,
        )
        heading_match = re.match(
            r"^ㅇ\s*(.+)$",
            block,
            flags=re.DOTALL,
        )
        bullet_match = re.match(
            r"^[-*]\s*(.+)$",
            block,
            flags=re.DOTALL,
        )

        if numbered_match:
            marker, content = numbered_match.groups()
            formatted_blocks.append(
                format_numbered_block(marker, content.strip())
            )
        elif heading_match:
            formatted_blocks.append(
                format_heading_block(heading_match.group(1).strip())
            )
        elif bullet_match:
            formatted_blocks.append(
                format_bullet_block(bullet_match.group(1).strip())
            )
        else:
            sentences = re.split(r"(?<=[다요]\.)\s+", block)
            paragraph_html = []
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    paragraph_html.append(format_normal_block(sentence))

            formatted_blocks.append(
                '<div class="faq-normal-block">'
                + "<br><br>".join(paragraph_html)
                + "</div>"
            )

    return "".join(formatted_blocks)


# =========================================================
# 페이지 스타일
# =========================================================
st.markdown(
    """
    <style>
    html {
        scroll-behavior: smooth;
    }

    #faq-top {
        scroll-margin-top: 80px;
    }

    [data-testid="stAppViewContainer"] {
        scroll-behavior: smooth;
    }

    /* -------------------------------------------------- */
    /* 질문 버튼 강제 왼쪽 정렬 스타일 */
    /* -------------------------------------------------- */
    button[data-testid="stBaseButton-secondary"] {
        justify-content: flex-start !important;
        text-align: left !important;
        padding: 0.6rem 1rem !important;
    }

    button[data-testid="stBaseButton-secondary"] > div {
        justify-content: flex-start !important;
        width: 100% !important;
    }

    button[data-testid="stBaseButton-secondary"] p {
        text-align: left !important;
        font-weight: 600 !important;
        font-size: 1.15rem !important;     # Q. 글자 폰트 크기 설정
    }

    /* 답변 상자 스타일 */
    .faq-answer-container {
        padding: 1.2rem 1.5rem;
        background-color: #f8f9fa;
        border-radius: 8px;
        border-left: 4px solid #ff4b4b;
        margin-top: -0.2rem;
        margin-bottom: 0.8rem;
    }

    .faq-answer-box {
        display: grid;
        grid-template-columns: 2rem minmax(0, 1fr);
        column-gap: 0.35rem;
        font-size: 1rem;
        line-height: 1.85;
        word-break: keep-all;
        overflow-wrap: break-word;
    }

    .faq-answer-label {
        font-weight: 700;
        color: #ff4b4b;
    }

    .faq-answer-content {
        min-width: 0;
    }

    .faq-normal-block {
        margin-bottom: 1rem;
    }

    .faq-subheading {
        margin: 0.9rem 0 0.5rem 0;
        font-weight: 700;
    }

    .faq-numbered-item {
        display: grid;
        grid-template-columns: max-content minmax(0, 1fr);
        column-gap: 0.55rem;
        margin: 0.7rem 0;
        padding-left: 1rem;
    }

    .faq-marker {
        font-weight: 600;
        white-space: nowrap;
    }

    .faq-item-content {
        min-width: 0;
    }

    .faq-answer-content a {
        font-weight: 600;
        text-decoration: none;
    }

    .faq-answer-content a:hover {
        text-decoration: underline;
    }

    /* TOP 버튼 */
    .faq-top-button {
        position: fixed;
        right: 30px;
        bottom: 30px;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 52px;
        height: 52px;
        border-radius: 50%;
        background: #ff4b4b;
        color: white !important;
        font-size: 13px;
        font-weight: 700;
        text-decoration: none !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.28);
        transition: transform 0.15s ease, background 0.15s ease;
    }

    .faq-top-button:hover {
        background: #e03b3b;
        transform: translateY(-2px);
    }

    @media (max-width: 700px) {
        .faq-top-button {
            right: 18px;
            bottom: 18px;
            width: 48px;
            height: 48px;
        }
        .faq-numbered-item {
            padding-left: 0.3rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 화면 출력
# =========================================================

# TOP 버튼 앵커
st.markdown('<div id="faq-top"></div>', unsafe_allow_html=True)

title_col, spacer_col, link_col = st.columns(
    [3, 6, 3],
    vertical_alignment="center",
)

with title_col:
    st.title("FAQ")

with link_col:
    st.link_button(
        "🚗 자동차 리콜센터 바로가기",
        "https://www.car.go.kr",
        use_container_width=True,
    )

st.write("자동차 리콜 및 제작결함과 관련하여 자주 묻는 질문을 확인해 보세요.")
st.divider()


try:
    faq_df = load_faq_data()
except (FileNotFoundError, ValueError, UnicodeDecodeError) as error:
    st.error(str(error))
    st.stop()

# 세션 상태 초기화 (열린 FAQ의 index 저장)
if "opened_faq_index" not in st.session_state:
    st.session_state.opened_faq_index = None

# FAQ 목록 출력 (단 하나만 열리는 아코디언)
for index, row in faq_df.reset_index(drop=True).iterrows():
    question = str(row["question"]).strip()
    answer = str(row["answer"]).strip()

    toggle_title = re.sub(r"^Q[.,]\s*", "", question)
    formatted_answer = format_answer(answer)

    is_open = st.session_state.opened_faq_index == index
    icon = "▼" if is_open else "▶"

    # 질문 클릭 버튼
    if st.button(
        f"{icon} Q. {toggle_title}",
        key=f"faq_btn_{index}",
        use_container_width=True,
    ):
        if is_open:
            st.session_state.opened_faq_index = None
        else:
            st.session_state.opened_faq_index = index
        st.rerun()

    # 열린 항목 답변 출력
    if is_open:
        st.markdown(
            f"""
            <div class="faq-answer-container">
                <div class="faq-answer-box">
                    <div class="faq-answer-label">A.</div>
                    <div class="faq-answer-content">
                        {formatted_answer}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# TOP 버튼
st.markdown(
    """
    <a class="faq-top-button" href="#faq-top" aria-label="맨 위로 이동">
        TOP
    </a>
    """,
    unsafe_allow_html=True,
)