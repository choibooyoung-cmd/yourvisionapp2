import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="ERP & Google Sheets SCM Hub",
    page_icon="📦",
    layout="wide"
)

# 커스텀 CSS 스타일 적용 (Tailwind 스타일 에뮬레이션 및 UI 개선)
st.markdown("""
<style>
    .main-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
    }
    .sub-desc {
        color: #64748b;
        font-size: 0.9rem;
    }
    .card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- 세션 상태 초기화 ---
if 'materials' not in st.session_state:
    st.session_state.materials = [
        { "code": "MAT-1001", "name": "SUS304 스테인리스 강판", "category": "원자재", "stock": 120, "safety": 150, "price": 45000, "bin": "A1-Zone-01" },
        { "code": "MAT-1002", "name": "알루미늄 6061 압출재", "category": "원자재", "stock": 85, "safety": 80, "price": 32000, "bin": "A1-Zone-02" },
        { "code": "MAT-2001", "name": "고장력 육각 볼트 M10", "category": "부자재", "stock": 450, "safety": 500, "price": 150, "bin": "B2-Bin-11" },
        { "code": "MAT-2002", "name": "산업용 실링 와셔", "category": "부자재", "stock": 1200, "safety": 1000, "price": 80, "bin": "B2-Bin-15" },
        { "code": "MAT-3001", "name": "MCU 컨트롤러 보드 (ARM Cortex)", "category": "전자부품", "stock": 28, "safety": 30, "price": 78000, "bin": "E3-Sec-04" },
        { "code": "MAT-3002", "name": "통신용 이중 쉴드 케이블", "category": "전자부품", "stock": 320, "safety": 200, "price": 5400, "bin": "E3-Sec-08" },
        { "code": "MAT-4001", "name": "고강도 수출용 파렛트", "category": "포장재", "stock": 15, "safety": 25, "price": 22000, "bin": "P1-Yard-01" },
        { "code": "MAT-4002", "name": "완충용 공기주입 에어패드", "category": "포장재", "stock": 850, "safety": 500, "price": 600, "bin": "P1-Yard-03" }
    ]

if 'inbound_logs' not in st.session_state:
    st.session_state.inbound_logs = [
        { "id": "MIGO-2026-001", "date": "2026-04-10 09:15", "code": "MAT-1002", "name": "알루미늄 6061 압출재", "qty": 50, "vendor": "(주)알루코리아", "bin": "A1-Zone-02" },
        { "id": "MIGO-2026-002", "date": "2026-04-10 11:30", "code": "MAT-2001", "name": "고장력 육각 볼트 M10", "qty": 200, "vendor": "(주)한국볼트", "bin": "B2-Bin-11" }
    ]

if 'outbound_logs' not in st.session_state:
    st.session_state.outbound_logs = [
        { "id": "GI-2026-001", "date": "2026-04-10 13:20", "code": "MAT-3001", "name": "MCU 컨트롤러 보드 (ARM Cortex)", "qty": 10, "dept": "조립 2라인", "requester": "박생산 과장" },
        { "id": "GI-2026-002", "date": "2026-04-10 15:40", "code": "MAT-2002", "name": "산업용 실링 와셔", "qty": 300, "dept": "프레스 공정", "requester": "이공정 대리" }
    ]

# --- 상단 타이틀 및 상태 표시 ---
col_t1, col_t2 = st.columns([4, 1])
with col_t1:
    st.markdown('<p class="main-header">ERP 및 스프레드시트 연동 자재 관리 종합 대시보드</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-desc">실시간 자재 수급 상태 및 Google Sheets / SAP ERP 동기화 트랜잭션을 관리합니다.</p>', unsafe_allow_html=True)
with col_t2:
    # 문제되었던 HTML 태그 영역 수정 (st.markdown 활용)
    st.markdown('<div style="text-align: right; padding-top: 10px;"><span class="text-xs text-emerald-600 font-medium" style="background:#ecfdf5; padding:6px 12px; border-radius:20px; border:1px solid #a7f3d0; font-size:12px; font-weight:600;">● Connected</span></div>', unsafe_allow_html=True)

st.divider()

# --- 사이드바 메뉴 구성 ---
st.sidebar.title("📦 SCM 메뉴")
menu = st.sidebar.radio(
    "이동할 탭을 선택하세요",
    ["대시보드", "자재 입고 관리 (MIGO)", "자재 출고 관리 (GI)", "실시간 재고 현황", "Google Sheets 연동 센터"]
)

# --- 1. 대시보드 탭 ---
if menu == "대시보드":
    st.subheader("📊 주요 지표 (KPI) 현황")
    
    total_items = len(st.session_state.materials)
    low_stock = [m for m in st.session_state.materials if m["stock"] < m["safety"]]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 관리 품목", f"{total_items} 품목")
    with col2:
        st.metric("금일 입고 건수", f"{len(st.session_state.inbound_logs)} 건")
    with col3:
        st.metric("금일 출고 건수", f"{len(st.session_state.outbound_logs)} 건")
    with col4:
        st.metric("안전재고 미달 (경고)", f"{len(low_stock)} 품목", delta=f"-{len(low_stock)}" if low_stock else "정상", delta_color="inverse")

    st.markdown("### ⚠️ 안전재고 미달 자재 리스트")
    if not low_stock:
        st.success("모든 품목의 재고가 안전재고 이상으로 안전하게 유지되고 있습니다.")
    else:
        for item in low_stock:
            st.warning(f"**[{item['code']}] {item['name']}** - 현재고: **{item['stock']} EA** (안전재고: {item['safety']} EA)")

# --- 2. 자재 입고 관리 (MIGO) ---
elif menu == "자재 입고 관리 (MIGO)":
    st.subheader("📥 자재 입고 내역 및 등록 (SAP MIGO)")
    
    with st.form("inbound_form"):
        col1, col2 = st.columns(2)
        with col1:
            mat_options = {f"[{m['code']}] {m['name']}": m['code'] for m in st.session_state.materials}
            selected_mat_label = st.selectbox("입고 자재 선택", list(mat_options.keys()))
            qty = st.number_input("입고 수량 (EA)", min_value=1, value=50)
        with col2:
            vendor = st.text_input("공급사 명", value="(주)신화 메탈")
            bin_loc = st.text_input("창고 Bin 위치", value="A1-Zone-01")
            
        submitted = st.form_submit_button("입고 등록 및 ERP 반영")
        if submitted:
            code = mat_options[selected_mat_label]
            target_mat = next(m for m in st.session_state.materials if m['code'] == code)
            target_mat['stock'] += qty
            
            new_log = {
                "id": f"MIGO-2026-0{len(st.session_state.inbound_logs)+1}",
                "date": "2026-04-10 17:00",
                "code": code,
                "name": target_mat['name'],
                "qty": qty,
                "vendor": vendor,
                "bin": bin_loc
            }
            st.session_state.inbound_logs.insert(0, new_log)
            st.success(f"[{target_mat['name']}] 자재가 성공적으로 입고 처리되었습니다 (+{qty} EA).")

    st.markdown("### 📋 최근 입고 로그")
    st.table(st.session_state.inbound_logs)

# --- 3. 자재 출고 관리 (GI) ---
elif menu == "자재 출고 관리 (GI)":
    st.subheader("📤 생산 라인 자재 불출 (GI / CO 연동)")
    
    with st.form("outbound_form"):
        col1, col2 = st.columns(2)
        with col1:
            mat_options = {f"[{m['code']}] {m['name']} (재고: {m['stock']}EA)": m['code'] for m in st.session_state.materials}
            selected_mat_label = st.selectbox("출고 자재 선택", list(mat_options.keys()))
            qty = st.number_input("출고 수량 (EA)", min_value=1, value=10)
        with col2:
            dept = st.selectbox("청구 부서", ["조립 1라인", "조립 2라인", "프레스 공정", "품질검사팀"])
            requester = st.text_input("청구자 성명", value="김철수 대리")
            
        submitted = st.form_submit_button("출고 승인 및 원가회계 반영")
        if submitted:
            code = mat_options[selected_mat_label]
            target_mat = next(m for m in st.session_state.materials if m['code'] == code)
            if target_mat['stock'] < qty:
                st.error(f"출고 가능 수량이 부족합니다. (현재고: {target_mat['stock']} EA)")
            else:
                target_mat['stock'] -= qty
                new_log = {
                    "id": f"GI-2026-0{len(st.session_state.outbound_logs)+1}",
                    "date": "2026-04-10 17:05",
                    "code": code,
                    "name": target_mat['name'],
                    "qty": qty,
                    "dept": dept,
                    "requester": requester
                }
                st.session_state.outbound_logs.insert(0, new_log)
                st.success(f"[{target_mat['name']}] 자재가 정상 출고되었습니다 (-{qty} EA).")

    st.markdown("### 📋 최근 출고 로그")
    st.table(st.session_state.outbound_logs)

# --- 4. 실시간 재고 현황 ---
elif menu == "실시간 재고 현황":
    st.subheader("📦 창고별 실시간 자재 마스터 및 현재고")
    
    search_query = st.text_input("🔍 자재 검색 (코드 또는 명칭)", "")
    
    filtered_materials = [
        m for m in st.session_state.materials 
        if search_query.lower() in m['code'].lower() or search_query.lower() in m['name'].lower()
    ]
    
    st.table(filtered_materials)

# --- 5. Google Sheets 연동 센터 ---
elif menu == "Google Sheets 연동 센터":
    st.subheader(" 연결된 Google Sheets 및 Apps Script 관리")
    
    st.text_input("Google Apps Script 웹 앱(Web App) URL", value="https://script.google.com/macros/s/AKfycbx.../exec")
    st.text_input("Google Sheet Target ID", value="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 ERP ↔ Google Sheets 수동 동기화"):
            st.success("데이터가 구글 스프레드시트와 성공적으로 동기화되었습니다!")
    with col2:
        if st.button("📤 현재고 리스트 시트로 내보내기"):
            st.success("재고 현황이 시트로 전송되었습니다.")
