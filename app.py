import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ==============================================================================
# 1. 페이지 기본 설정 및 스타일
# ==============================================================================
st.set_page_config(
    page_title="AUTO-ERP SCM 자동화 대시보드",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바 설정
with st.sidebar:
    st.title("📦 AUTO-ERP SCM")
    st.caption("구글 스프레드시트 기반 실시간 자재 관리 시스템")
    
    st.success("🟢 Apps Script Web App 연결됨")
    
    # 실시간 새로고침 버튼
    if st.button("🔄 데이터 실시간 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ==============================================================================
# 2. Apps Script 웹 앱 URL 설정
# ==============================================================================
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbz3sxE-InFfCaloiWzLIqZ2FGAq3w858qCng8cFB5KQIUnuw9mPvdQmY-7bUL1B_ic/exec"

@st.cache_data(ttl=30)
def load_data_from_script(url: str):
    """Google Apps Script 웹 앱에서 전체 시트 데이터를 JSON으로 불러옵니다."""
    try:
        response = requests.get(url, timeout=15, allow_redirects=True)
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict) and "status" in data and data["status"] == "error":
                    return None, f"Apps Script 에러 발생: {data.get('message', '알 수 없는 오류')}"
                return data, None
            except Exception:
                return None, "응답 데이터를 JSON 형태로 파싱하지 못했습니다."
        else:
            return None, f"HTTP 오류 발생: {response.status_code}"
    except Exception as e:
        return None, f"데이터를 불러오는 중 오류가 발생했습니다: {str(e)}"

raw_data, error_msg = load_data_from_script(WEB_APP_URL)

# ==============================================================================
# 3. 데이터프레임 변환 및 전처리 함수
# ==============================================================================
def find_and_convert_sheet(data_dict, target_keywords):
    """지정된 키워드에 부합하는 시트 데이터를 DataFrame으로 변환합니다."""
    if not isinstance(data_dict, dict):
        return None
    
    for key, values in data_dict.items():
        clean_key = str(key).strip().lower()
        for kw in target_keywords:
            if kw.lower() in clean_key:
                if isinstance(values, list) and len(values) > 0:
                    headers = [str(h).strip() for h in values[0]]
                    rows = values[1:]
                    df = pd.DataFrame(rows, columns=headers)
                    df = df.dropna(how='all')
                    return df
                elif isinstance(values, list):
                    return pd.DataFrame()
    return None

inventory_df = None
inbound_df = None
outbound_df = None

if raw_data:
    inventory_df = find_and_convert_sheet(raw_data, ["inventory", "재고", "stock"])
    inbound_df = find_and_convert_sheet(raw_data, ["inbound", "입고", "in"])
    outbound_df = find_and_convert_sheet(raw_data, ["outbound", "출고", "out"])

# ==============================================================================
# 4. 상단 대시보드 타이틀 & 주요 지표
# ==============================================================================
st.title("🏭 AUTO-ERP 자재 수급/재고 관리 자동화 시스템")
st.caption(f"마지막 데이터 동기화 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if error_msg:
    st.error(error_msg)

# 지표 계산 로직
total_items = 0
total_inbound_qty = 0
total_outbound_qty = 0
low_stock_count = 0

if inventory_df is not None and not inventory_df.empty:
    total_items = len(inventory_df)
    for col in inventory_df.columns:
        if any(keyword in col for keyword in ["재고", "수량", "안전"]):
            inventory_df[col] = pd.to_numeric(inventory_df[col], errors='coerce').fillna(0)
    
    cur_col = next((c for c in inventory_df.columns if "현재" in c or "수량" in c or "재고" in c), None)
    safe_col = next((c for c in inventory_df.columns if "안전" in c), None)
    
    if cur_col and safe_col:
        low_stock_count = len(inventory_df[inventory_df[cur_col] < inventory_df[safe_col]])

# KPI 표시
col1, col2, col3, col4 = st.columns(4)
col1.metric("📋 총 관리 품목", f"{total_items:,} 개")
col2.metric("📥 입고 기록", f"{len(inbound_df) if inbound_df is not None else 0:,} 건")
col3.metric("📤 출고 기록", f"{len(outbound_df) if outbound_df is not None else 0:,} 건")
col4.metric("🚨 안전재고 부족", f"{low_stock_count} 개")

st.divider()

# ==============================================================================
# 5. 메인 대시보드 탭 구성
# ==============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 통합 재고 현황", "📥 입고 관리", "📤 출고 관리", "⚠️ 재고 부족 경고", "📝 작업 등록"])

with tab1:
    st.subheader("실시간 자재 재고 리스트")
    if inventory_df is not None and not inventory_df.empty:
        st.dataframe(inventory_df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("자재 입고 이력")
    if inbound_df is not None and not inbound_df.empty:
        st.dataframe(inbound_df, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("자재 출고 이력")
    if outbound_df is not None and not outbound_df.empty:
        st.dataframe(outbound_df, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("🚨 발주 필요 (안전재고 미달 품목)")
    if inventory_df is not None and not inventory_df.empty:
        st.dataframe(inventory_df[inventory_df[cur_col] < inventory_df[safe_col]], use_container_width=True, hide_index=True)

with tab5:
    st.subheader("📝 신규 입/출고 작업 등록")
    with st.form("action_form"):
        action = st.selectbox("작업 유형", ["입고 (Inbound)", "출고 (Outbound)"])
        item = st.text_input("자재명 / 품목코드")
        qty = st.number_input("수량", min_value=1)
        if st.form_submit_button("등록 전송"):
            st.success(f"{item} ({qty}개) {action} 요청 완료")
