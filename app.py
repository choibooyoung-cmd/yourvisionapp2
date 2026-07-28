import pandas as pd
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="팀 예산 현황 및 취합 시스템",
    page_icon="📊",
    layout="wide"
)

# 세션 스테이트 초기화 (데이터 저장용)
if "budget_data" not in st.session_state:
    st.session_state.budget_data = []

# 타이틀
st.markdown("<h1 style='text-align: center;'>📊 팀 예산 관리 시스템</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>부장님 보고용 월별 예산 취합 및 대시보드</p>", unsafe_allow_html=True)
st.markdown("---")

# 탭 메뉴 생성
tab1, tab2 = st.tabs(["📝 데이터 입력", "📈 전체 대시보드"])

# --- [탭 1] 데이터 입력 ---
with tab1:
    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.subheader("내역 입력")
        with st.form("budget_form", clear_on_submit=True):
            member = st.selectbox("팀원 선택", ["부장님", "팀원1", "팀원2", "팀원3", "팀원4"])
            month = st.text_input("해당 월 (YYYY-MM)", value=pd.Timestamp.now().strftime("%Y-%m"))
            category = st.selectbox("예산 항목", ["수선유지비", "비품", "개량공사"])
            amount = st.number_input("사용 금액 (원)", min_value=0, step=1000)

            submitted = st.form_submit_button("기록 저장하기")
            if submitted:
                if month:
                    new_entry = {
                        "id": pd.Timestamp.now().timestamp(),
                        "member": member,
                        "month": month,
                        "category": category,
                        "amount": amount
                    }
                    st.session_state.budget_data.insert(0, new_entry)
                    st.success("예산 데이터가 정상적으로 기록되었습니다.")
                    st.rerun()
                else:
                    st.error("해당 월을 올바르게 입력해주세요.")

    with col2:
        st.subheader("📂 최근 입력 내역")

        if st.session_state.budget_data:
            # 데이터프레임 변환
            df = pd.DataFrame(st.session_state.budget_data)

            # 테이블 표시용 컬럼 정리
            display_df = df[["month", "member", "category", "amount"]].copy()
            display_df.columns = ["날짜", "팀원", "항목", "금액"]
            display_df["금액"] = display_df["금액"].apply(lambda x: f"{x:,}원")

            st.dataframe(display_df, use_container_width=True)

            if st.button("모든 데이터 초기화", type="primary"):
                st.session_state.budget_data = []
                st.success("모든 데이터가 초기화되었습니다.")
                st.rerun()
        else:
            st.info("등록된 데이터가 없습니다.")

# --- [탭 2] 전체 대시보드 ---
with tab2:
    if not st.session_state.budget_data:
        st.warning("대시보드에 표시할 데이터가 없습니다. '데이터 입력' 탭에서 데이터를 먼저 등록해주세요.")
    else:
        df = pd.DataFrame(st.session_state.budget_data)

        # 상단 요약 지표
        total_amount = df["amount"].sum()
        total_count = len(df)

        cat_grouped = df.groupby("category")["amount"].sum()
        top_category = cat_grouped.idxmax() if not cat_grouped.empty else "-"
        top_cat_val = cat_grouped.max() if not cat_grouped.empty else 0

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("전체 누적 사용액", f"{total_amount:,}원")
        with col_m2:
            st.metric("이번 달 최대 사용 항목", f"{top_category} ({top_cat_val:,}원)" if top_category != "-" else "-")
        with col_m3:
            st.metric("데이터 건수", f"{total_count}건")

        st.markdown("---")

        # 차트 영역
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            st.subheader("🏠 항목별 예산 분포")
            cat_df = df.groupby("category")["amount"].sum().reset_index()
            st.bar_chart(cat_df.set_index("category"))

        with col_c2:
            st.subheader("👥 팀원별 누적 사용액")
            mem_df = df.groupby("member")["amount"].sum().reset_index()
            st.bar_chart(mem_df.set_index("member"))

        st.markdown("---")

        # 월별/항목별 요약 테이블
        st.subheader("📅 월별/항목별 요약 테이블 (취합본)")
        pivot_df = df.pivot_table(
            index="month",
            columns="category",
            values="amount",
            aggfunc="sum",
            fill_value=0
        )

        # 필요한 카테고리 컬럼 보장
        for cat in ["수선유지비", "비품", "개량공사"]:
            if cat not in pivot_df.columns:
                pivot_df[cat] = 0

        pivot_df = pivot_df[["수선유지비", "비품", "개량공사"]]
        pivot_df["합계"] = pivot_df.sum(axis=1)
        pivot_df = pivot_df.sort_index(ascending=False)

        # Pandas 버전에 따른 자동 대응 (map vs applymap)
        if hasattr(pivot_df, "map"):
            formatted_pivot = pivot_df.map(lambda x: f"{x:,}원")
        else:
            formatted_pivot = pivot_df.applymap(lambda x: f"{x:,}원")

        st.dataframe(formatted_pivot, use_container_width=True)
