import streamlit as st
import requests
import pandas as pd
from datetime import datetime

#st.set_page_config(
    page_title="AUTO-ERP SCM 자동화 대시보드",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a professional dashboard look
st.markdown("""
    <style>
    .metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    .stApp { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

#with st.sidebar:
    st.title("📦 AUTO-ERP SCM")
    st.markdown("---")
    st.success("🟢 연결 상태: Google Apps Script")
    if st.button("🔄 데이터 실시간 갱신", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbz3sxE-InFfCaloiWzLIqZ2FGAq3w858qCng8cFB5KQIUnuw9mPvdQmY-7bUL1B_ic/exec"

@st.cache_data(ttl=60)
def load_data_from_script(url: str):
    try:
        response = requests.get(url, timeout=10)
        return response.json() if response.status_code == 200 else None
    except:
        return None

raw_data = load_data_from_script(WEB_APP_URL)

#def get_df_by_keyword(data, keywords):
    if not data: return pd.DataFrame()
    for key, values in data.items():
        if any(kw in str(key).lower() for kw in keywords):
            return pd.DataFrame(values[1:], columns=values[0]).dropna(how='all')
    return pd.DataFrame()

inventory_df = get_df_by_keyword(raw_data, ["inventory", "재고", "stock"])
inbound_df = get_df_by_keyword(raw_data, ["inbound", "입고", "in"])
outbound_df = get_df_by_keyword(raw_data, ["outbound", "출고", "out"])

#st.title("🏭 ERP 자재 수급 관리 시스템")
st.write(f"최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("총 관리 품목", f"{len(inventory_df):,}")
col2.metric("입고 건수", f"{len(inbound_df):,}")
col3.metric("출고 건수", f"{len(outbound_df):,}")
col4.metric("재고 부족", f"{len(inventory_df[inventory_df.iloc[:, 1] < 10]):,}") # Example threshold

#tab1, tab2, tab3, tab4 = st.tabs(["📊 재고 현황", "📥 입고 현황", "📤 출고 현황", "📝 작업 등록"])

with tab1:
    st.subheader("재고 통합 관리")
    st.dataframe(inventory_df, use_container_width=True)

with tab2:
    st.subheader("최근 입고 내역")
    st.dataframe(inbound_df, use_container_width=True)

with tab3:
    st.subheader("최근 출고 내역")
    st.dataframe(outbound_df, use_container_width=True)

with tab4:
    st.subheader("입/출고 작업 등록")
    with st.form("action_form"):
        c1, c2 = st.columns(2)
        item = c1.text_input("품목 코드/명")
        qty = c2.number_input("수량", min_value=1)
        type = st.radio("작업 유형", ["입고", "출고"], horizontal=True)
        if st.form_submit_button("등록 요청"):
            st.info(f"요청됨: {item} ({type}) {qty}개")
