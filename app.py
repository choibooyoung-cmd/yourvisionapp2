import streamlit as st
import pandas as pd

# 페이지 기본 설정
st.set_page_config(page_title="My Vision App", layout="wide")

st.title("데이터 요약 및 피벗 테이블")

# 예시 데이터 생성 (실제 데이터 로드 코드로 대체 가능)
data = {
    "카테고리": ["A", "A", "B", "B", "C"],
    "항목": ["X", "Y", "X", "Y", "X"],
    "금액": [10000, 25000, 15000, 30000, 50000]
}
df = pd.DataFrame(data)

# 피벗 테이블 생성
pivot_df = df.pivot_table(index="카테고리", columns="항목", values="금액", aggfunc="sum")

# ------------------------------------------------------------------
# [오류 수정 위치] 들여쓰기 수정 및 안전한 원화 포맷팅 적용
# ------------------------------------------------------------------
formatted_pivot = pivot_df.map(
    lambda x: f"{int(x):,}원" if pd.notnull(x) and isinstance(x, (int, float)) else ""
)

# 화면 출력
st.subheader("원본 피벗 테이블")
st.dataframe(pivot_df)

st.subheader("포맷팅 적용 피벗 테이블")
st.dataframe(formatted_pivot)
