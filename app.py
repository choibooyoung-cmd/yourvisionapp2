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

@st.cache_data(ttl=30)  # 30초 간격 자동 갱신
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
# 4. 상단 대시보드 타이틀 & 주요 지표 (KPI Cards)
# ==============================================================================
st.title("🏭 AUTO-ERP 자재 수급/재고 관리 자동화 시스템")
st.caption(f"마지막 데이터 동기화 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if error_msg:
    st.error(error_msg)

# 컬럼 매핑 설정 (KeyError 방지용 안전 장치)
cur_col = None
safe_col = None

if inventory_df is not None and not inventory_df.empty:
    columns_list = list(inventory_df.columns)
    
    # 사이드바나 상단에서 컬럼을 수동으로 매핑할 수 있도록 예외처리
    try:
        cur_col = next(c for c in columns_list if "현재" in c or "수량" in c or "재고" in c)
    except StopIteration:
        cur_col = columns_list[0] if columns_list else None
        
    try:
        safe_col = next(c for c in columns_list if "안전" in c)
    except StopIteration:
        safe_col = columns_list[1] if len(columns_list) > 1 else None

# 지표 계산 로직
total_items = 0
total_inbound_qty = 0
total_outbound_qty = 0
low_stock_count = 0

if inventory_df is not None and not inventory_df.empty:
    total_items = len(inventory_df)
    
    # 숫자형 변환
    if cur_col and cur_col in inventory_df.columns:
        inventory_df[cur_col] = pd.to_numeric(inventory_df[cur_col], errors='coerce').fillna(0)
    if safe_col and safe_col in inventory_df.columns:
        inventory_df[safe_col] = pd.to_numeric(inventory_df[safe_col], errors='coerce').fillna(0)
        
    if cur_col and safe_col and cur_col in inventory_df.columns and safe_col in inventory_df.columns:
        low_stock_df = inventory_df[inventory_df[cur_col] < inventory_df[safe_col]]
        low_stock_count = len(low_stock_df)

if inbound_df is not None and not inbound_df.empty:
    qty_col = next((c for c in inbound_df.columns if "수량" in c or "입고" in c or "qty" in c.lower()), None)
    if qty_col:
        total_inbound_qty = int(pd.to_numeric(inbound_df[qty_col], errors='coerce').fillna(0).sum())
    else:
        total_inbound_qty = len(inbound_df)

if outbound_df is not None and not outbound_df.empty:
    qty_col = next((c for c in outbound_df.columns if "수량" in c or "출고" in c or "qty" in c.lower()), None)
    if qty_col:
        total_outbound_qty = int(pd.to_numeric(outbound_df[qty_col], errors='coerce').fillna(0).sum())
    else:
        total_outbound_qty = len(outbound_df)

# KPI 카드 배치
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(label="📋 총 관리 품목 수", value=f"{total_items:,} 개")
with kpi2:
    st.metric(label="📥 누적 입고 수량", value=f"{total_inbound_qty:,} 건/개")
with kpi3:
    st.metric(label="📤 누적 출고 수량", value=f"{total_outbound_qty:,} 건/개")
with kpi4:
    st.metric(label="🚨 안전재고 부족 품목", value=f"{low_stock_count} 개", delta=f"-{low_stock_count}" if low_stock_count > 0 else "정상", delta_color="inverse")

st.divider()

# ==============================================================================
# 5. 메인 자동화 대시보드 탭 구성
# ==============================================================================
tab_stock, tab_inbound, tab_outbound, tab_alert, tab_action = st.tabs([
    "📊 통합 재고 현황", 
    "📥 입고 관리", 
    "📤 출고 관리", 
    "⚠️ 재고 부족 경고",
    "📝 입/출고 수동 등록 및 연동"
])

# ------------------------------------------------------------------------------
# TAB 1: 통합 재고 현황 (검색 및 필터 기능 포함)
# ------------------------------------------------------------------------------
with tab_stock:
    st.subheader("실시간 자재 재고 리스트")
    if inventory_df is not None and not inventory_df.empty:
        search_query = st.text_input("🔍 자재명 / 품목코드 / 규격 검색", placeholder="검색어를 입력하세요...")
        filtered_df = inventory_df.copy()
        
        if search_query:
            mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
            filtered_df = filtered_df[mask]
        
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    else:
        st.info("재고 데이터가 비어 있거나 스프레드시트에서 데이터를 불러오지 못했습니다.")

# ------------------------------------------------------------------------------
# TAB 2: 입고 내역 관리
# ------------------------------------------------------------------------------
with tab_inbound:
    st.subheader("자재 입고 기록 및 이력")
    if inbound_df is not None and not inbound_df.empty:
        st.dataframe(inbound_df, use_container_width=True, hide_index=True)
    else:
        st.info("등록된 입고 내역 데이터가 없습니다.")

# ------------------------------------------------------------------------------
# TAB 3: 출고 내역 관리
# ------------------------------------------------------------------------------
with tab_outbound:
    st.subheader("자재 출고 기록 및 이력")
    if outbound_df is not None and not outbound_df.empty:
        st.dataframe(outbound_df, use_container_width=True, hide_index=True)
    else:
        st.info("등록된 출고 내역 데이터가 없습니다.")

# ------------------------------------------------------------------------------
# TAB 4: 안전재고 부족 자재 모니터링
# ------------------------------------------------------------------------------
with tab_alert:
    st.subheader("🚨 발주 필요 (안전재고 미달 품목)")
    if inventory_df is not None and not inventory_df.empty:
        if cur_col and safe_col and cur_col in inventory_df.columns and safe_col in inventory_df.columns:
            alert_df = inventory_df[inventory_df[cur_col] < inventory_df[safe_col]].copy()
            if not alert_df.empty:
                alert_df["부족 수량(권장 발주량)"] = alert_df[safe_col] - alert_df[cur_col]
                st.warning(f"⚠️ 총 {len(alert_df)}개 품목이 안전재고 수준 이하입니다. 긴급 발주 검토가 필요합니다.")
                st.dataframe(alert_df, use_container_width=True, hide_index=True)
            else:
                st.success("🎉 현재 모든 자재가 안전재고 수량 이상을 유지하고 있습니다.")
        else:
            st.info("스프레드시트에 재고 수량과 안전재고를 비교할 수 있는 열이 지정되지 않았습니다.")
    else:
        st.info("재고 데이터를 불러올 수 없습니다.")

# ------------------------------------------------------------------------------
# TAB 5: 자재 입/출고 등록 폼 (시트 자동 연동 준비)
# ------------------------------------------------------------------------------
with tab_action:
    st.subheader("📝 신규 입/출고 작업 등록")
    st.caption("대시보드에서 등록 후 구글 시트에 바로 이력을 기록할 수 있습니다.")
    
    with st.form("inventory_action_form"):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            action_type = st.selectbox("작업 유형", ["입고 (Inbound)", "출고 (Outbound)"])
        with col_b:
            item_name = st.text_input("자재명 / 품목코드", placeholder="예: BOLT-M8")
        with col_c:
            qty = st.number_input("수량", min_value=1, value=1, step=1)
            
        note = st.text_input("비고 / 작업자 사원번호", placeholder="예: 홍길동 (정기 수급)")
        
        submitted = st.form_submit_button("🚀 스프레드시트로 등록 전송")
        if submitted:
            if not item_name:
                st.error("품목명을 입력해주세요.")
            else:
                payload = {
                    "actionType": action_type,
                    "itemName": item_name,
                    "qty": qty,
                    "note": note
                }
                try:
                    response = requests.post(WEB_APP_URL, json=payload, timeout=10)
                    if response.status_code == 200:
                        st.success(f"✅ [{action_type}] '{item_name}' {qty}개 기록 완료!")
                        st.rerun()
                    else:
                        st.error("데이터 전송에 실패했습니다.")
                except Exception as e:
                    st.error(f"서버 통신 중 오류 발생: {e}")
