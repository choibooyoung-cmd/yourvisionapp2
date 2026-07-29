"""
7차시 저장 모델로 가상 공장의 다음 15분 수요를 예측하는 Streamlit 앱

실행 방법:
    streamlit run app.py
"""

import os
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import streamlit as st


MODEL_FILENAME = "lesson07_energy_forecast_model.joblib"
MINIMUM_HISTORY = 672  # 15분 간격 7일치 데이터 (24시간 * 4 * 7일)
EXPECTED_FEATURES = [
    "usage_lag_1",
    "usage_lag_4",
    "usage_lag_96",
    "usage_lag_672",
    "usage_mean_4",
    "usage_mean_12",
    "usage_mean_96",
    "usage_std_12",
    "reactive_lag_1",
    "power_factor_lag_1",
    "target_hour_sin",
    "target_hour_cos",
    "target_dow_sin",
    "target_dow_cos",
    "target_is_weekday",
]


def model_candidates() -> list[Path]:
    """Colab 환경 및 로컬 실행 환경의 모델 파일 검색 경로들을 반환합니다."""
    candidates: list[Path] = []
    configured = os.getenv("LESSON07_MODEL_PATH")
    if configured:
        candidates.append(Path(configured).expanduser())
        
    candidates.extend(
        [
            Path("/content/lesson07_timeseries_outputs") / MODEL_FILENAME,
            Path("/content") / MODEL_FILENAME,
            Path.cwd() / MODEL_FILENAME,
            Path.cwd() / "lesson07_timeseries_outputs" / MODEL_FILENAME,
        ]
    )
    
    try:
        script_path = Path(__file__).resolve()
        if len(script_path.parents) >= 3:
            textbook_root = script_path.parents[2]
            candidates.append(
                textbook_root
                / "outputs"
                / "day7_timeseries"
                / MODEL_FILENAME
            )
    except NameError:
        pass  # 대화형 환경 실행 시 __file__ 이 없을 수 있음

    # 중복 경로 제거
    return list(dict.fromkeys(path.resolve() for path in candidates if path))


def find_model_path() -> Path:
    """존재하는 모델 파일 경로를 검색하여 반환합니다."""
    for path in model_candidates():
        if path.is_file():
            return path
            
    searched = "\n".join(f"- {path}" for path in model_candidates())
    raise FileNotFoundError(
        f"'{MODEL_FILENAME}' 파일 또는 저장 모델을 찾지 못했습니다.\n검색한 위치:\n{searched}"
    )


@st.cache_resource
def load_model_bundle(path: str) -> dict[str, Any]:
    """저장된 학습 모델 번들을 불러옵니다."""
    bundle = joblib.load(path)
    required = {
        "model",
        "features",
        "target",
        "forecast_horizon_minutes",
        "data_frequency_minutes",
    }
    missing = required.difference(bundle)
    if missing:
        raise ValueError(
            "모델 번들에 필수 항목이 누락되었습니다: "
            + ", ".join(sorted(missing))
        )
    if list(bundle["features"]) != EXPECTED_FEATURES:
        raise ValueError(
            "앱에서 요구하는 특성(Feature) 이름 또는 순서가 저장된 모델과 일치하지 않습니다."
        )
    if int(bundle["forecast_horizon_minutes"]) != 15:
        raise ValueError("이 앱은 15분 단위 예측 모델 전용입니다.")
    return bundle


def virtual_usage(
    timestamp: pd.Timestamp,
    base_load: float,
    peak_load: float,
    night_factor: float,
    weekend_factor: float,
    noise: float,
) -> float:
    """가상 공장의 시간대별 전력 소비 패턴을 생성합니다."""
    hour = timestamp.hour + timestamp.minute / 60
    morning_peak = np.exp(-0.5 * ((hour - 10.0) / 1.7) ** 2)
    afternoon_peak = np.exp(-0.5 * ((hour - 15.0) / 2.1) ** 2)
    operating = 0.55 * morning_peak + 0.85 * afternoon_peak
    
    if hour < 7 or hour >= 21:
        operating *= night_factor
    if timestamp.dayofweek >= 5:
        operating *= weekend_factor
        
    return max(0.1, base_load + peak_load * operating + noise)


def create_virtual_history(
    end_time: pd.Timestamp,
    base_load: float,
    peak_load: float,
    night_factor: float,
    weekend_factor: float,
    reactive_ratio: float,
    power_factor: float,
) -> pd.DataFrame:
    """모델 학습 및 예측에 필요한 최근 7일간의 가상 이력 데이터를 만듭니다."""
    timestamps = pd.date_range(
        end=end_time,
        periods=MINIMUM_HISTORY,
        freq="15min",
    )
    generator = np.random.default_rng(42)
    noise_values = generator.normal(0, max(base_load * 0.035, 0.15), len(timestamps))
    
    usage = [
        virtual_usage(
            timestamp,
            base_load,
            peak_load,
            night_factor,
            weekend_factor,
            float(noise),
        )
        for timestamp, noise in zip(timestamps, noise_values)
    ]
    
    usage_array = np.asarray(usage)
    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "usage_kwh": usage_array,
            "reactive_kvarh": usage_array * reactive_ratio,
            "power_factor_pct": power_factor,
            "source": "가상 관측",
        }
    )


def make_next_features(history: pd.DataFrame) -> pd.DataFrame:
    """직전 이력 데이터를 기반으로 다음 15분 예측에 사용할 특성(Feature)들을 생성합니다."""
    if len(history) < MINIMUM_HISTORY:
        raise ValueError(
            f"최소 {MINIMUM_HISTORY}개(7일치)의 데이터 이력이 필요합니다."
        )
        
    usage = history["usage_kwh"].astype(float).to_numpy()
    current = history.iloc[-1]
    target_time = pd.Timestamp(current["timestamp"]) + pd.Timedelta(minutes=15)
    target_hour = target_time.hour + target_time.minute / 60
    target_dow = target_time.dayofweek

    row = {
        "usage_lag_1": usage[-1],
        "usage_lag_4": usage[-4],
        "usage_lag_96": usage[-96],
        "usage_lag_672": usage[-672],
        "usage_mean_4": usage[-4:].mean(),
        "usage_mean_12": usage[-12:].mean(),
        "usage_mean_96": usage[-96:].mean(),
        "usage_std_12": usage[-12:].std(ddof=1),
        "reactive_lag_1": float(current["reactive_kvarh"]),
        "power_factor_lag_1": float(current["power_factor_pct"]),
        "target_hour_sin": np.sin(2 * np.pi * target_hour / 24),
        "target_hour_cos": np.cos(2 * np.pi * target_hour / 24),
        "target_dow_sin": np.sin(2 * np.pi * target_dow / 7),
        "target_dow_cos": np.cos(2 * np.pi * target_dow / 7),
        "target_is_weekday": int(target_dow < 5),
    }
    return pd.DataFrame([row], columns=EXPECTED_FEATURES)


def predict_next(
    history: pd.DataFrame,
    bundle: dict[str, Any],
    reactive_ratio: float,
    power_factor: float,
) -> pd.DataFrame:
    """다음 15분 전력 수요를 예측하여 데이터 프레임에 추가합니다."""
    features = make_next_features(history)
    prediction = max(float(bundle["model"].predict(features)[0]), 0.0)
    
    next_time = pd.Timestamp(history.iloc[-1]["timestamp"]) + pd.Timedelta(minutes=15)
    next_row = pd.DataFrame(
        [
            {
                "timestamp": next_time,
                "usage_kwh": prediction,
                "reactive_kvarh": prediction * reactive_ratio,
                "power_factor_pct": power_factor,
                "source": "모델 예측",
            }
        ]
    )
    return pd.concat([history, next_row], ignore_index=True)


def advance_simulation(
    history: pd.DataFrame,
    steps: int,
    bundle: dict[str, Any],
    reactive_ratio: float,
    power_factor: float,
) -> pd.DataFrame:
    """지정한 스텝(15분 단위) 수만큼 시뮬레이션을 진행합니다."""
    for _ in range(steps):
        history = predict_next(
            history,
            bundle,
            reactive_ratio,
            power_factor,
        )
    return history


def initialize_history(
    start_time: pd.Timestamp,
    base_load: float,
    peak_load: float,
    night_factor: float,
    weekend_factor: float,
    reactive_ratio: float,
    power_factor: float,
) -> None:
    """세션 상태의 이력 데이터를 초기화합니다."""
    st.session_state.energy_history = create_virtual_history(
        start_time,
        base_load,
        peak_load,
        night_factor,
        weekend_factor,
        reactive_ratio,
        power_factor,
    )


def render_dashboard() -> None:
    st.set_page_config(
        page_title="가상 공장 실시간 전력수요 예측",
        page_icon="⚡",
        layout="wide",
    )
    
    st.title("⚡ 가상 공장 실시간 전력수요 예측 대시보드")
    st.caption(
        "실제 철강 데이터로 학습된 시계열 AI 모델을 통해 "
        "가상 공장의 다음 15분 단위 전력수요를 실시간으로 순차 예측합니다."
    )

    # 1. 모델 불러오기
    try:
        model_path = find_model_path()
        bundle = load_model_bundle(str(model_path))
    except Exception as error:
        st.error("🚨 학습된 예측 모델을 불러오지 못했습니다.")
        st.code(str(error))
        st.info(
            "👉 모델 파일 (`lesson07_energy_forecast_model.joblib`)이 "
            "현재 app.py 파일과 같은 위치 폴더에 있는지 확인해주세요."
        )
        st.stop()

    # 2. 사이드바 - 설정 조건
    with st.sidebar:
        st.header("⚙️ 가상 공장 가동 조건")
        base_load = st.slider("기본 부하 (kWh/15분)", 2.0, 60.0, 12.0, 1.0)
        peak_load = st.slider("주간 추가 부하", 5.0, 120.0, 55.0, 1.0)
        night_factor = st.slider("야간 가동률", 0.0, 1.0, 0.15, 0.05)
        weekend_factor = st.slider("주말 가동률", 0.0, 1.0, 0.35, 0.05)
        reactive_ratio = st.slider("무효전력 비율", 0.0, 0.8, 0.18, 0.01)
        power_factor = st.slider("역률 (%)", 60.0, 100.0, 92.0, 0.5)
        peak_threshold = st.slider(
            "피크 검토 기준 (kWh/15분)",
            20.0,
            160.0,
            70.0,
            2.0,
        )
        
        start_date = st.date_input("시뮬레이션 시작 날짜")
        start_hour = st.slider("시작 시각 (시)", 0, 23, 8)
        start_time = pd.Timestamp(start_date) + pd.Timedelta(hours=start_hour)

        if st.button("🔄 조건 적용 및 초기화", use_container_width=True):
            initialize_history(
                start_time,
                base_load,
                peak_load,
                night_factor,
                weekend_factor,
                reactive_ratio,
                power_factor,
            )
            st.success("새로운 조건으로 시뮬레이션이 초기화되었습니다.")

        st.divider()
        st.markdown(f"**불러온 모델:** `{model_path.name}`")
        st.markdown("**예측 단위:** 15분")
        st.markdown("**최소 이력:** 7일치 (672개 타임스텝)")

    # 3. 데이터 세션 생성 및 관리
    if "energy_history" not in st.session_state:
        initialize_history(
            start_time,
            base_load,
            peak_load,
            night_factor,
            weekend_factor,
            reactive_ratio,
            power_factor,
        )

    history = st.session_state.energy_history

    # 4. 상단 예측 실행 버튼
    st.markdown("### 🔮 시뮬레이션 예측 진행")
    button_columns = st.columns([1, 1, 1, 3])
    
    if button_columns[0].button("▶ 다음 15분 예측"):
        history = advance_simulation(
            history, 1, bundle, reactive_ratio, power_factor
        )
    if button_columns[1].button("▶ 1시간 진행 (4회)"):
        history = advance_simulation(
            history, 4, bundle, reactive_ratio, power_factor
        )
    if button_columns[2].button("▶ 6시간 진행 (24회)"):
        history = advance_simulation(
            history, 24, bundle, reactive_ratio, power_factor
        )
        
    st.session_state.energy_history = history

    # 5. 주요 지표 표시 (Metrics)
    current = history.iloc[-1]
    forecast_rows = history[history["source"].eq("모델 예측")]
    predicted_count = len(forecast_rows)
    peak_count = int((forecast_rows["usage_kwh"] >= peak_threshold).sum())

    metric_columns = st.columns(4)
    metric_columns[0].metric(
        "현재 시뮬레이션 시각",
        pd.Timestamp(current["timestamp"]).strftime("%m-%d %H:%M"),
    )
    metric_columns[1].metric(
        "최근 예측 전력 수요",
        f"{float(current['usage_kwh']):.2f} kWh",
    )
    metric_columns[2].metric("누적 예측 횟수", f"{predicted_count} 회")
    metric_columns[3].metric("피크 초과 건수", f"{peak_count} 건")

    # 피크 경고 메시지
    if float(current["usage_kwh"]) >= peak_threshold:
        st.error(
            f"⚠️ **피크 경고!** 예측 전력 수요({float(current['usage_kwh']):.2f} kWh)가 "
            f"설정한 기준({peak_threshold} kWh)을 초과했습니다."
        )
    else:
        st.success("✅ 현재 예측 전력 수요는 설정된 피크 기준 이내로 안정적입니다.")

    # 6. 그래프 시각화
    chart = history.tail(96 + predicted_count).copy()
    chart["가상 관측"] = chart["usage_kwh"].where(
        chart["source"].eq("가상 관측")
    )
    chart["모델 예측"] = chart["usage_kwh"].where(
        chart["source"].eq("모델 예측")
    )
    chart["피크 기준"] = peak_threshold

    st.subheader("📈 최근 24시간 관측 및 예측 트렌드")
    st.line_chart(
        chart.set_index("timestamp")[["가상 관측", "모델 예측", "피크 기준"]],
        height=400,
    )

    # 7. 예측 데이터 테이블
    st.subheader("📋 최근 예측 상세 내역")
    if forecast_rows.empty:
        st.info("👆 상단의 버튼을 눌러 다음 시간의 전력 수요를 예측해보세요.")
    else:
        table = forecast_rows.tail(24).copy()
        table["피크 검토"] = np.where(
            table["usage_kwh"] >= peak_threshold,
            "🚨 피크 초과",
            "🟢 정상",
        )
        st.dataframe(
            table[
                [
                    "timestamp",
                    "usage_kwh",
                    "reactive_kvarh",
                    "power_factor_pct",
                    "피크 검토",
                ]
            ].rename(
                columns={
                    "timestamp": "예측 시각",
                    "usage_kwh": "예측 전력(kWh)",
                    "reactive_kvarh": "가상 무효전력(kVArh)",
                    "power_factor_pct": "가상 역률(%)",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    # 주의 안내문
    st.caption(
        "💡 **안내사항:** 이 시뮬레이션의 미래 예측값은 시계열 모델의 순차 예측(Recursive Forecasting)을 시뮬레이션한 것입니다. "
        "예측 단계를 길게 늘릴수록 오차가 누적될 수 있습니다."
    )


if __name__ == "__main__":
    render_dashboard()
