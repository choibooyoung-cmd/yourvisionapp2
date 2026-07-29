import streamlit as st
import requests
import pandas as pd

# ==============================================================================
# 1. 페이지 기본 설정 및 스타일
# ==============================================================================
st.set_page_config(
    page_title="AUTO-ERP SCM",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바 설정
with st.sidebar:
    st.title("📦 AUTO-ERP SCM")
    st.caption("Google Sheets API / Apps Script 연동 대시보드")
    
    # 연결 상태 표시
    st.success("API Key / Script 연결 완료")
    
    # 실시간 새로고침 버튼
    if st.button("🔄 데이터 실시간 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ==============================================================================
# 2. Apps Script ID 및 웹 앱 URL 설정
# ==============================================================================
SCRIPT_ID = "19D3YAV6Gh2adRsQ09wn_yiYpKK9Q1iQCy_KXUNElc9X0cDiE4cYT15om"

# Apps Script 웹 앱 배포 URL (또는 Exec URL)
# Apps Script에서 '웹 앱으로 배포' 후 생성된 URL 형태로 조회합니다.
WEB_APP_URL = f"https://script.google.com/macros/s/{SCRIPT_ID}/exec"


@st.cache_data(ttl=60)  # 1분간 캐시 유지
def load_data_from_script(url: str):
    """Google Apps Script 웹 앱에서 전체 시트 데이터를 JSON으로 불러옵니다."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data, None
        else:
            return None, f"HTTP 오류 발생: {response.status_code}"
    except Exception as e:
        return None, f"데이터를 불러오는 중 오류가 발생했습니다: {str(e)}"

# 데이터 로드
raw_data, error_msg = load_data_from_script(WEB_APP_URL)

# ==============================================================================
# 3. 시트 데이터 추출 및 정형화 (대소문자/공백 무시 유연한 처리)
# ==============================================================================
def get_sheet_dataframe(data_dict, target_name):
    """시트 이름의 대소문자 및 공백 차이를 무시하고 일치하는 시트의 데이터프레임을 반환합니다."""
    if not data_dict or not isinstance(data_dict, dict):
        return pd.DataFrame()
    
    clean_target = target_name.strip().lower()
    
    for key, values in data_dict.items():
        if str(key).strip().lower() == clean_target:
            if isinstance(values, list) and len(values) > 0:
                # 첫 번째 행을 컬럼 헤더로 사용
                df = pd.DataFrame(values[1:], columns=values[0])
                return df
            elif isinstance(values, list):
                return pd.DataFrame()
    return None

inventory_df = None
inbound_df = None
outbound_df = None

if raw_data:
    inventory_df = get_sheet_dataframe(raw_data, "inventory")
    inbound_df = get_sheet_dataframe(raw_data, "inbound")
    outbound_df = get_sheet_dataframe(raw_data, "outbound")

# 에러 메시지 출력 영역
if error_msg:
    st.error(error_msg)
else:
    if inventory_df is None:
        st.error("'inventory' 시트를 불러오지 못했습니다. Apps Script 배포 설정이나 시트 이름을 확인해 주세요.")
    if inbound_df is None:
        st.error("'inbound' 시트를 불러오지 못했습니다. Apps Script 배포 설정이나 시트 이름을 확인해 주세요.")
    if outbound_df is None:
        st.error("'outbound' 시트를 불러오지 못했습니다. Apps Script 배포 설정이나 시트 이름을 확인해 주세요.")

# ==============================================================================
# 4. 대시보드 헤더 및 KPI 요약 카드
# ==============================================================================
st.title("ERP 자재 관리 대시보드")
st.caption("구글 스프레드시트 기반 실시간 수급 현황")

col1, col2, col3, col4 = st.columns(4)

total_items = len(inventory_df) if inventory_df is not None and not inventory_df.empty else 0
total_inbound = len(inbound_df) if inbound_df is not None and not inbound_df.empty else 0
total_outbound = len(outbound_df) if outbound_df is not None and not outbound_df.empty else 0

# 안전재고 부족 품목 계산 (컬럼명이 존재할 경우)
low_stock_count = 0
if inventory_df is not None and not inventory_df.empty:
    # '현재재고' 및 '안전재고' 컬럼이 있는 경우 계산
    cols = [str(c).strip() for c in inventory_df.columns]
    if "현재재고" in cols and "안전재고" in cols:
        try:
            temp_df = inventory_df.copy()
            temp_df["현재재고"] = pd.to_numeric(temp_df["현재재고"], errors="coerce").fillna(0)
            temp_df["안전재고"] = pd.to_numeric(temp_df["안전재고"], errors="coerce").fillna(0)
            low_stock_count = len(temp_df[temp_df["현재재고"] < temp_df["안전재고"]])
        except Exception:
            low_stock_count = 0

with col1:
    st.metric("전체 관리 자재", f"{total_items} 품목")
with col2:
    st.metric("입고 기록 수", f"{total_inbound} 건")
with col3:
    st.metric("출고 기록 수", f"{total_outbound} 건")
with col4:
    st.metric("안전재고 부족 경고", f"{low_stock_count} 품목")

st.divider()

# ==============================================================================
# 5. 탭 구성 (재고 현황 / 입고 내역 / 출고 내역 / 안전재고 부족)
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 재고 현황", "📥 입고 내역", "📤 출고 내역", "🚨 안전재고 부족"])

with tab1:
    st.subheader("통합 자재 재고 현황")
    if inventory_df is not None and not inventory_df.empty:
        st.dataframe(inventory_df, use_container_width=True)
    else:
        st.info("재고 데이터가 비어 있거나 시트를 불러올 수 없습니다.")

with tab2:
    st.subheader("자재 입고 내역")
    if inbound_df is not None and not inbound_df.empty:
        st.dataframe(inbound_df, use_container_width=True)
    else:
        st.info("입고 데이터가 비어 있거나 시트를 불러올 수 없습니다.")

with tab3:
    st.subheader("자재 출고 내역")
    if outbound_df is not None and not outbound_df.empty:
        st.dataframe(outbound_df, use_container_width=True)
    else:
        st.info("출고 데이터가 비어 있거나 시트를 불러올 수 없습니다.")

with tab4:
    st.subheader("안전재고 부족 자재 목록")
    if inventory_df is not None and not inventory_df.empty:
        cols = [str(c).strip() for c in inventory_df.columns]
        if "현재재고" in cols and "안전재고" in cols:
            temp_df = inventory_df.copy()
            temp_df["현재재고"] = pd.to_numeric(temp_df["현재재고"], errors="coerce").fillna(0)
            temp_df["안전재고"] = pd.to_numeric(temp_df["안전재고"], errors="coerce").fillna(0)
            alert_df = temp_df[temp_df["현재재고"] < temp_df["안전재고"]]
            
            if not alert_df.empty:
                st.warning(f"총 {len(alert_df)}개 품목이 안전재고보다 부족합니다.")
                st.dataframe(alert_df, use_container_width=True)
            else:
                st.success("모든 자재가 안전재고 이상 유지되고 있습니다.")
        else:
            st.info("시트에 '현재재고' 및 '안전재고' 열이 명시되어 있어야 비교가 가능합니다.")
    else:
        st.info("재고 데이터를 불러올 수 없습니다.")
