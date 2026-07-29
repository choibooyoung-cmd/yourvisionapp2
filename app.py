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
    
    st.success("API / Web App 연결 완료")
    
    if st.button("🔄 데이터 실시간 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ==============================================================================
# 2. Apps Script 웹 앱 URL 설정
# ==============================================================================
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbx_I_E2tuyBPp8KZm7J5J9xhVYMXdusaCwlYFuop1z9dmz3wNAHDLZ7IfGDy-qvWYXe/exec"


@st.cache_data(ttl=60)
def load_data_from_script(url: str):
    """Google Apps Script 웹 앱에서 전체 시트 데이터를 JSON으로 불러옵니다."""
    try:
        response = requests.get(url, timeout=15, allow_redirects=True)
        if response.status_code == 200:
            try:
                data = response.json()
                return data, None
            except Exception:
                return None, "응답 데이터를 JSON 형태로 파싱하지 못했습니다."
        else:
            return None, f"HTTP 오류 발생: {response.status_code}"
    except Exception as e:
        return None, f"데이터를 불러오는 중 오류가 발생했습니다: {str(e)}"

raw_data, error_msg = load_data_from_script(WEB_APP_URL)

# ==============================================================================
# 3. 유연한 시트 매칭 및 데이터프레임 변환
# ==============================================================================
def find_and_convert_sheet(data_dict, target_keywords):
    """
    여러 키워드(예: ['inventory', '재고', '재고현황']) 중 하나라도 일치하는 시트를 찾아 Dataframe으로 변환합니다.
    """
    if not isinstance(data_dict, dict):
        return None
    
    for key, values in data_dict.items():
        clean_key = str(key).strip().lower()
        for kw in target_keywords:
            if kw.lower() in clean_key:
                if isinstance(values, list) and len(values) > 0:
                    # 첫 행을 헤더(열 이름)로 사용
                    headers = values[0]
                    rows = values[1:]
                    return pd.DataFrame(rows, columns=headers)
                elif isinstance(values, list):
                    return pd.DataFrame()
    return None

inventory_df = None
inbound_df = None
outbound_df = None

if raw_data:
    # 한글/영어 키워드 모두 대응
    inventory_df = find_and_convert_sheet(raw_data, ["inventory", "재고", "stock"])
    inbound_df = find_and_convert_sheet(raw_data, ["inbound", "입고", "in"])
    outbound_df = find_and_convert_sheet(raw_data, ["outbound", "출고", "out"])

# 에러 및 안내 메시지
if error_msg:
    st.error(error_msg)
elif raw_data:
    missing_sheets = []
    if inventory_df is None: missing_sheets.append("'inventory' (또는 '재고')")
    if inbound_df is None: missing_sheets.append("'inbound' (또는 '입고')")
    if outbound_df is None: missing_sheets.append("'outbound' (또는 '출고')")
    
    if missing_sheets:
        st.warning(f"다음 시트를 찾지 못했습니다: {', '.join(missing_sheets)}")
        # 디버깅용: 실제 인식된 시트 이름 보여주기
        with st.expander("🔍 현재 수신된 구글 시트 탭 목록 확인하기"):
            st.write("구글 시트에서 받아온 실제 탭 이름들:", list(raw_data.keys()))

# ==============================================================================
# 4. 대시보드 헤더 및 KPI 요약 카드
# ==============================================================================
st.title("ERP 자재 관리 대시보드")
st.caption("구글 스프레드시트 기반 실시간 수급 현황")

col1, col2, col3, col4 = st.columns(4)

total_items = len(inventory_df) if inventory_df is not None and not inventory_df.empty else 0
total_inbound = len(inbound_df) if inbound_df is not None and not inbound_df.empty else 0
total_outbound = len(outbound_df) if outbound_df is not None and not outbound_df.empty else 0

low_stock_count = 0
if inventory_df is not None and not inventory_df.empty:
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
# 5. 탭 구성
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
            st.info("시트에 '현재재고' 및 '안전재고' 열이 명시되어 있어야 합니다.")
    else:
        st.info("재고 데이터를 불러올 수 없습니다.")
