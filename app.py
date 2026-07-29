import streamlit as st
import pandas as pd

# ==========================================
# 1. 페이지 설정 및 구글 시트 정보 입력
# ==========================================
st.set_page_config(
    page_title="ERP 자재 관리 대시보드",
    page_icon="📦",
    layout="wide"
)

# 🔑 보내주신 API 키 및 스프레드시트 ID
GOOGLE_API_KEY = "AQ.Ab8RN6LzTl0bU9beCAzCpdkAMa1S4VutdqaVYm7utbR9Mk8d5Q"
SPREADSHEET_ID = "1hOVkgPdg36bGo7ng97JaJ_pIbRILdo-bLHD_P4quKvE"

# ==========================================
# 2. 구글 스프레드시트 데이터 불러오기 함수
# ==========================================
@st.cache_data(ttl=60)
def load_sheet_data(sheet_name):
    # Google Sheets API v4 URL 구조
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{sheet_name}?key={GOOGLE_API_KEY}"
    try:
        res = pd.read_json(url)
        values = res.get("values", [])
        if values and len(values) > 1:
            headers = values[0]  # 첫 번째 행: 컬럼 이름
            data = values[1:]    # 두 번째 행부터: 실제 데이터
            return pd.DataFrame(data, columns=headers)
        elif values and len(values) == 1:
            return pd.DataFrame(columns=values[0])
        return pd.DataFrame()
    except Exception as e:
        st.error(f"'{sheet_name}' 시트를 불러오지 못했습니다. 스프레드시트 공유 설정이나 시트 이름을 확인해 주세요.")
        return pd.DataFrame()

# ==========================================
# 3. 사이드바 (동기화 버튼)
# ==========================================
with st.sidebar:
    st.title("📦 AUTO-ERP SCM")
    st.caption("Google Sheets API 연동 대시보드")
    st.success("🟢 API Key 연결 완료")
    
    if st.button("🔄 데이터 실시간 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ==========================================
# 4. 데이터 로드 및 수치형 데이터 변환
# ==========================================
df_inventory = load_sheet_data("inventory")
df_inbound = load_sheet_data("inbound")
df_outbound = load_sheet_data("outbound")

# 수량 및 단가 데이터를 숫자 타입으로 변환
if not df_inventory.empty:
    for col in ["stock", "safety", "unitPrice"]:
        if col in df_inventory.columns:
            df_inventory[col] = pd.to_numeric(df_inventory[col], errors="coerce").fillna(0)

# ==========================================
# 5. 메인 대시보드 UI
# ==========================================
st.title("ERP 자재 관리 대시보드")
st.caption("구글 스프레드시트 기반 실시간 수급 현황")

# 상단 KPI 메트릭 카운트 계산
total_items = len(df_inventory)
low_stock_count = 0
low_stock_df = pd.DataFrame()

if not df_inventory.empty and "stock" in df_inventory.columns and "safety" in df_inventory.columns:
    low_stock_df = df_inventory[df_inventory["stock"] < df_inventory["safety"]]
    low_stock_count = len(low_stock_df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("전체 관리 자재", f"{total_items} 품목")
col2.metric("입고 기록 수", f"{len(df_inbound)} 건")
col3.metric("출고 기록 수", f"{len(df_outbound)} 건")
col4.metric("안전재고 부족 경고", f"{low_stock_count} 품목", delta_color="inverse")

st.divider()

# ==========================================
# 6. 메인 탭 구성
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 재고 현황", "📥 입고 내역", "📤 출고 내역", "🚨 안전재고 부족"])

with tab1:
    st.subheader("통합 자재 재고 현황")
    if not df_inventory.empty:
        # 카테고리 필터 기능
        if "category" in df_inventory.columns:
            categories = ["전체"] + list(df_inventory["category"].unique())
            selected_cat = st.selectbox("카테고리 필터", categories)
            if selected_cat != "전체":
                display_df = df_inventory[df_inventory["category"] == selected_cat]
            else:
                display_df = df_inventory
        else:
            display_df = df_inventory

        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("재고 데이터가 비어 있거나 시트를 불러올 수 없습니다.")

with tab2:
    st.subheader("최근 입고 기록")
    if not df_inbound.empty:
        st.dataframe(df_inbound, use_container_width=True, hide_index=True)
    else:
        st.info("입고 기록이 없습니다.")

with tab3:
    st.subheader("최근 출고 기록")
    if not df_outbound.empty:
        st.dataframe(df_outbound, use_container_width=True, hide_index=True)
    else:
        st.info("출고 기록이 없습니다.")

with tab4:
    st.subheader("⚠️ 안전재고 미달 품목")
    if not low_stock_df.empty:
        st.warning(f"현재 {len(low_stock_df)}개 품목의 재고가 안전재고보다 부족합니다.")
        st.dataframe(low_stock_df, use_container_width=True, hide_index=True)
    else:
        st.success("모든 자재의 재고가 안전재고 이상으로 충분합니다.")
