import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="ERP & Google Sheets 연동 자재 관리 대시보드",
    page_icon="📦",
    layout="wide"
)

# ==========================================
# 2. 구글 스프레드시트 연동 함수
# ==========================================
@st.cache_resource(ttl=60)
def init_gspread():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # secrets.toml 의 gcp_service_account 설정 사용
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )
    client = gspread.authorize(credentials)
    spreadsheet_name = st.secrets.get("spreadsheet_name", "자재관리_DB")
    return client.open(spreadsheet_name)

def get_sheet_data(sheet_name):
    try:
        doc = init_gspread()
        sheet = doc.worksheet(sheet_name)
        data = sheet.get_all_records()
        return pd.DataFrame(data), sheet
    except Exception as e:
        st.error(f"구글 스프레드시트 '{sheet_name}' 시트를 불러오는데 실패했습니다: {e}")
        return pd.DataFrame(), None

# ==========================================
# 3. 사이드바 (ERP 상태 및 새로고침)
# ==========================================
with st.sidebar:
    st.title("📦 AUTO-ERP SCM")
    st.caption("구글 스프레드시트 실시간 연동")
    
    st.success("🟢 Google Sheets API 연결됨")
    
    if st.button("🔄 데이터 실시간 동기화", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.markdown("### 👤 사용자 정보")
    st.write("**김자재 관리자** (구매자재팀)")

# ==========================================
# 4. 데이터 로드 (스프레드시트 시트명 지정)
# ==========================================
# ※ 구글 스프레드시트에 각각 'inventory', 'inbound', 'outbound' 워크시트가 존재해야 합니다.
df_inventory, sheet_inv = get_sheet_data("inventory")
df_inbound, sheet_in = get_sheet_data("inbound")
df_outbound, sheet_out = get_sheet_data("outbound")

# 데이터 기본 구조 체크 및 빈 프레임 예외 처리
if df_inventory.empty:
    df_inventory = pd.DataFrame(columns=["id", "name", "category", "stock", "safety", "unitPrice", "rack"])

# ==========================================
# 5. 대시보드 헤더 & KPI Card
# ==========================================
st.title("ERP 연동 자재 관리 대시보드")
st.caption("구글 스프레드시트 기반 실시간 수급 현황 및 트랜잭션 관리")

# KPI 제어 계산
total_items = len(df_inventory)
low_stock_df = df_inventory[df_inventory["stock"] < df_inventory["safety"]] if not df_inventory.empty else pd.DataFrame()
low_stock_count = len(low_stock_df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("전체 관리 자재", f"{total_items} 품목")
col2.metric("금일 입고 건수", f"{len(df_inbound)} 건")
col3.metric("금일 출고 건수", f"{len(df_outbound)} 건")
col4.metric("안전재고 부족 경고", f"{low_stock_count} 품목", delta_color="inverse")

st.divider()

# ==========================================
# 6. 메인 탭 구성
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 재고 현황 (Google Sheets)", "📥 입고 등록", "📤 출고 등록", "🚨 안전재고 미달 품목"])

# ------------------------------------------
# TAB 1: 통합 재고 현황
# ------------------------------------------
with tab1:
    st.subheader("실시간 통합 자재 재고 현황")
    
    # 카테고리 필터
    if not df_inventory.empty and "category" in df_inventory.columns:
        categories = ["전체"] + list(df_inventory["category"].unique())
        selected_cat = st.selectbox("카테고리 필터", categories)
        
        filtered_df = df_inventory.copy()
        if selected_cat != "전체":
            filtered_df = filtered_df[filtered_df["category"] == selected_cat]
            
        # 재고 자산 금액 계산
        filtered_df["총 평가액(원)"] = filtered_df["stock"] * filtered_df["unitPrice"]
        
        st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={
                "id": "자재 코드",
                "name": "자재명",
                "category": "분류",
                "stock": st.column_config.NumberColumn("현재 재고", format="%d EA"),
                "safety": st.column_config.NumberColumn("안전 재고", format="%d EA"),
                "unitPrice": st.column_config.NumberColumn("단가", format="₩%d"),
                "총 평가액(원)": st.column_config.NumberColumn("총 평가액", format="₩%d"),
                "rack": "보관 위치"
            },
            hide_index=True
        )

# ------------------------------------------
# TAB 2: 입고 처리
# ------------------------------------------
with tab2:
    st.subheader("신규 자재 입고 처리")
    st.info("입고 내역 등록 시 구글 스프레드시트에 자동 기록되고 재고 수량이 즉시 증가합니다.")
    
    with st.form("inbound_form"):
        if not df_inventory.empty:
            mat_options = [f"{row['id']} | {row['name']} (현재: {row['stock']})" for _, row in df_inventory.iterrows()]
            selected_mat = st.selectbox("입고 자재 선택", mat_options)
        else:
            selected_mat = None
            
        in_qty = st.number_input("입고 수량", min_value=1, value=100)
        vendor = st.text_input("공급 업체 (Vendor)", placeholder="(주)한국소재")
        location = st.text_input("보관 창고/랙 위치", placeholder="A1-Zone-04")
        
        submit_inbound = st.form_submit_button("입고 확정 및 구글 시트 저장")
        
        if submit_inbound and selected_mat:
            mat_id = selected_mat.split(" | ")[0]
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            inbound_id = f"IN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # 1. Inbound 시트 기록
            if sheet_in:
                sheet_in.append_row([inbound_id, now_str, mat_id, in_qty, vendor, location, "완료"])
            
            # 2. Inventory 시트 수량 반영
            if sheet_inv:
                cell = sheet_inv.find(mat_id)
                if cell:
                    current_val = int(sheet_inv.cell(cell.row, 4).value) # 4번째 열: stock
                    sheet_inv.update_cell(cell.row, 4, current_val + in_qty)
                    
            st.success(f"입고 처리 완료! [{mat_id}] 수량 +{in_qty} EA")
            st.cache_data.clear()
            st.rerun()

    st.divider()
    st.markdown("##### 최근 입고 기록")
    st.dataframe(df_inbound, use_container_width=True, hide_index=True)

# ------------------------------------------
# TAB 3: 출고 처리
# ------------------------------------------
with tab3:
    st.subheader("신규 자재 출고 불출")
    st.info("출고 승인 시 재고 차감 내역이 구글 스프레드시트에 실시간 반영됩니다.")
    
    with st.form("outbound_form"):
        if not df_inventory.empty:
            mat_options = [f"{row['id']} | {row['name']} (현재: {row['stock']})" for _, row in df_inventory.iterrows()]
            selected_mat_out = st.selectbox("출고 자재 선택", mat_options)
        else:
            selected_mat_out = None
            
        out_qty = st.number_input("출고 수량", min_value=1, value=10)
        dept = st.text_input("사용 부서 / 프로젝트", placeholder="생산1팀")
        requester = st.text_input("불출 요청자", placeholder="홍길동 대리")
        
        submit_outbound = st.form_submit_button("출고 승인 및 차감")
        
        if submit_outbound and selected_mat_out:
            mat_id = selected_mat_out.split(" | ")[0]
            
            # 재고 수량 부족 검증
            target_item = df_inventory[df_inventory["id"] == mat_id].iloc[0]
            if target_item["stock"] < out_qty:
                st.error(f"출고 불가: 현재 재고({target_item['stock']} EA)가 요청 수량({out_qty} EA)보다 적습니다.")
            else:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                outbound_id = f"OUT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                # 1. Outbound 시트에 기록
                if sheet_out:
                    sheet_out.append_row([outbound_id, now_str, mat_id, out_qty, dept, requester, "완료"])
                
                # 2. Inventory 시트 수량 차감
                if sheet_inv:
                    cell = sheet_inv.find(mat_id)
                    if cell:
                        current_val = int(sheet_inv.cell(cell.row, 4).value)
                        sheet_inv.update_cell(cell.row, 4, current_val - out_qty)
                        
                st.success(f"출고 완료! [{mat_id}] 수량 -{out_qty} EA 차감되었습니다.")
                st.cache_data.clear()
                st.rerun()

    st.divider()
    st.markdown("##### 최근 출고 기록")
    st.dataframe(df_outbound, use_container_width=True, hide_index=True)

# ------------------------------------------
# TAB 4: 안전재고 미달 품목
# ------------------------------------------
with tab4:
    st.subheader("⚠️ 안전재고 미달 품목 목록")
    if not low_stock_df.empty:
        st.warning(f"현재 {len(low_stock_df)}개 품목이 안전재고 수량에 미달합니다. 발주를 진행해 주세요.")
        st.dataframe(low_stock_df, use_container_width=True, hide_index=True)
    else:
        st.success("모든 자재가 안전재고 수량을 충족하고 있습니다.")
