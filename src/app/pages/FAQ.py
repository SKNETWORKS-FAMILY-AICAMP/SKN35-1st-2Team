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

# FAQ.py가 어느 폴더에 있든 프로젝트의 data/car_faq.csv를 찾도록 설정
CURRENT_DIR = Path(__file__).resolve().parent
CSV_CANDIDATES = [
    CURRENT_DIR / "data" / "car_faq.csv",
    CURRENT_DIR.parent / "data" / "car_faq.csv",
    Path("data/car_faq.csv"),
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
    """
    공백을 포함하여 한 줄이 지정한 글자 수를 넘지 않도록 나눕니다.

    한 단어가 74자를 넘는 특수한 경우에는 단어 자체를 강제로 자르지 않습니다.
    """
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
    """문자열을 HTML 안전 문자로 바꾸고 자동차리콜센터 주소를 링크로 변환합니다."""
    safe_text = html.escape(str(text))

    link_html = (
        '<a href="https://www.car.go.kr" target="_blank" '
        'rel="noopener noreferrer">자동차리콜센터</a>'
    )

    safe_text = safe_text.replace(
        "https://www.car.go.kr",
        link_html,
    )

    safe_text = safe_text.replace(
        "www.car.go.kr",
        link_html,
    )

    return safe_text


def split_numbered_items(text: str) -> list[str]:
    """
    답변을 일반 문장과 번호 항목으로 분리합니다.

    분리 대상:
    - 1. 2. 3.
    - ① ② ③
    - ㅇ 제목
    - -, * 글머리표
    """
    clean_text = normalize_spaces(text)

    # 번호와 글머리표 앞에 내부 구분자를 삽입합니다.
    pattern = (
        r"(?="
        r"(?:\d+\.\s+)"
        r"|(?:[①②③④⑤⑥⑦⑧⑨⑩]\s*)"
        r"|(?:ㅇ\s+)"
        r"|(?:[-*]\s+)"
        r")"
    )

    marked_text = re.sub(pattern, "|||", clean_text)

    return [
        block.strip()
        for block in marked_text.split("|||")
        if block.strip()
    ]


def format_normal_block(text: str) -> str:
    """일반 답변 내용을 최대 74자로 줄바꿈합니다."""
    lines = wrap_lines(text, MAX_LINE_LENGTH)

    return "<br>".join(
        convert_links(line)
        for line in lines
    )


def format_numbered_block(
    marker: str,
    content: str,
) -> str:
    """
    번호 항목을 새 줄에서 시작하고, 다음 줄부터 내용 위치에 맞춰 들여씁니다.

    출력 예시:
        2. 「부가가치세법」에 따른 세금계산서 또는 영수증
           (신용카드매출전표 포함)
    """
    base_indent = 4
    marker_space = len(marker) + 1

    # 들여쓰기와 번호 길이까지 포함하여 최대 74자가 되도록 계산
    content_width = (
        MAX_LINE_LENGTH
        - base_indent
        - marker_space
    )

    lines = wrap_lines(content, content_width)

    if not lines:
        return (
            f'<div class="faq-numbered-item">'
            f'<span class="faq-marker">{convert_links(marker)}</span>'
            f"</div>"
        )

    line_html = "<br>".join(
        convert_links(line)
        for line in lines
    )

    return (
        '<div class="faq-numbered-item">'
        f'<span class="faq-marker">{convert_links(marker)}</span>'
        f'<span class="faq-item-content">{line_html}</span>'
        "</div>"
    )


def format_bullet_block(content: str) -> str:
    """글머리표 항목을 줄바꿈하고 다음 줄을 들여씁니다."""
    content_width = MAX_LINE_LENGTH - 7
    lines = wrap_lines(content, content_width)

    if not lines:
        return ""

    line_html = "<br>".join(
        convert_links(line)
        for line in lines
    )

    return (
        '<div class="faq-numbered-item">'
        '<span class="faq-marker">•</span>'
        f'<span class="faq-item-content">{line_html}</span>'
        "</div>"
    )


def format_heading_block(content: str) -> str:
    """'ㅇ 내용' 형태의 중간 제목을 굵게 표시합니다."""
    lines = wrap_lines(content, MAX_LINE_LENGTH - 2)

    return (
        '<div class="faq-subheading">'
        + "<br>".join(convert_links(line) for line in lines)
        + "</div>"
    )


def format_answer(text: str) -> str:
    """
    FAQ 답변 전체를 HTML로 변환합니다.

    적용 규칙:
    1. 일반 A 내용은 공백 포함 최대 74자
    2. 1., 2., 3. 항목은 각각 새 줄에서 시작
    3. ①, ②, ③ 항목도 각각 새 줄에서 시작
    4. 번호 항목의 다음 줄은 내용 시작 위치에 맞춰 들여쓰기
    5. 항목 사이에 간격을 넣어 가독성 개선
    """
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
                format_numbered_block(
                    marker,
                    content.strip(),
                )
            )

        elif heading_match:
            formatted_blocks.append(
                format_heading_block(
                    heading_match.group(1).strip()
                )
            )

        elif bullet_match:
            formatted_blocks.append(
                format_bullet_block(
                    bullet_match.group(1).strip()
                )
            )

        else:
            # 일반 문장은 '다.' 또는 '요.' 뒤에서 문단을 한 번 더 분리
            sentences = re.split(
                r"(?<=[다요]\.)\s+",
                block,
            )

            paragraph_html = []

            for sentence in sentences:
                sentence = sentence.strip()

                if sentence:
                    paragraph_html.append(
                        format_normal_block(sentence)
                    )

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

    /* TOP 버튼 이동 위치가 Streamlit 상단 메뉴에 가려지지 않도록 설정 */
    #faq-top {
        scroll-margin-top: 80px;
    }

    /* Streamlit에서 실제로 스크롤되는 영역 */
    [data-testid="stAppViewContainer"] {
        scroll-behavior: smooth;
    }

    [data-testid="stExpander"] summary {
        display: flex;
        align-items: center;
    }

    [data-testid="stExpander"] summary p {
        margin: 0;
        font-size: 1rem;
        font-weight: 600;
    }

    [data-testid="stExpander"] summary p::before {
        content: "Q. ";
        font-weight: 700;
    }

    [data-testid="stExpanderDetails"] {
        padding: 0.8rem 1.5rem 1.3rem 1.5rem;
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

    /* HTML 텍스트 출력 오류가 없는 단순 앵커 방식 TOP 버튼 */
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

# TOP 버튼을 클릭했을 때 이동할 위치
st.markdown(
    '<div id="faq-top"></div>',
    unsafe_allow_html=True,
)

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

st.write(
    "자동차 리콜 및 제작결함과 관련하여 "
    "자주 묻는 질문을 확인해 보세요."
)

st.divider()


try:
    faq_df = load_faq_data()

except (FileNotFoundError, ValueError, UnicodeDecodeError) as error:
    st.error(str(error))
    st.stop()


for _, row in faq_df.iterrows():
    question = str(row["question"]).strip()
    answer = str(row["answer"]).strip()

    # 질문 원문에 Q.가 있으면 제거
    toggle_title = re.sub(
        r"^Q[.,]\s*",
        "",
        question,
    )

    formatted_answer = format_answer(answer)

    with st.expander(toggle_title):
        st.markdown(
            f"""
            <div class="faq-answer-box">
                <div class="faq-answer-label">A.</div>
                <div class="faq-answer-content">
                    {formatted_answer}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# 페이지 전체의 최상단으로 이동
st.markdown(
    """
    <a
        class="faq-top-button"
        href="#faq-top"
        aria-label="맨 위로 이동">
        TOP
    </a>
    """,
    unsafe_allow_html=True,
)
