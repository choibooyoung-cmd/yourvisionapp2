%%writefile app.py
import os
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import streamlit as st
from PIL import Image, UnidentifiedImageError

MODEL_FILENAME = "lesson06_vision_model.joblib"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def model_candidates() -> list[Path]:
    """Streamlit Cloud 및 로컬 실행 환경에서 모델을 찾을 후보 경로를 반환한다."""
    candidates: list[Path] = []
    configured = os.getenv("LESSON06_MODEL_PATH")
    if configured:
        candidates.append(Path(configured).expanduser())

    # Streamlit Cloud 및 일반적인 로컬 실행 환경 기준 경로들
    candidates.extend(
        [
            Path.cwd() / MODEL_FILENAME,
            Path.cwd() / "outputs" / "day6" / MODEL_FILENAME,
            Path.cwd() / "lesson06_outputs" / MODEL_FILENAME,
            Path("/content/lesson06_outputs") / MODEL_FILENAME,
            Path("/content") / MODEL_FILENAME,
        ]
    )

    script_path = Path(__file__).resolve()
    if len(script_path.parents) >= 2:
        candidates.append(script_path.parent / MODEL_FILENAME)
    if len(script_path.parents) >= 3:
        textbook_root = script_path.parents[2]
        candidates.append(
            textbook_root / "outputs" / "day6" / MODEL_FILENAME
        )

    # 순서를 유지하면서 중복 경로를 제거한다.
    return list(dict.fromkeys(path.resolve() for path in candidates))


def find_model_path() -> Path:
    for path in model_candidates():
        if path.is_file():
            return path
    searched = "\n".join(f"- {path}" for path in model_candidates())
    raise FileNotFoundError(
        f"{MODEL_FILENAME}을 찾지 못했습니다.\n검색 위치:\n{searched}"
    )


@st.cache_resource
def load_bundle(model_path: str) -> dict[str, Any]:
    """신뢰할 수 있는 6차시 산출물만 역직렬화한다."""
    bundle = joblib.load(model_path)
    required = {
        "model",
        "feature_size",
        "operating_threshold",
        "quality_limits",
        "class_names",
        "feature_extractor",
    }
    missing = required.difference(bundle)
    if missing:
        raise ValueError(
            "모델 번들에 필요한 항목이 없습니다: "
            + ", ".join(sorted(missing))
        )
    if bundle["feature_extractor"] != "lesson06_hog_intensity_v1":
        raise ValueError(
            "이 앱과 호환되지 않는 특징 추출기입니다: "
            f"{bundle['feature_extractor']}"
        )
    return bundle


def quality_metrics(
    image: Image.Image,
    feature_size: tuple[int, int],
) -> dict[str, float]:
    """6차시 학습 코드와 같은 밝기·대비·선명도 지표를 계산한다."""
    array = np.asarray(image.resize(feature_size), dtype=np.float32)
    gx = np.diff(array, axis=1, prepend=array[:, :1])
    gy = np.diff(array, axis=0, prepend=array[:1, :])
    laplacian = (
        -4 * array
        + np.roll(array, 1, axis=0)
        + np.roll(array, -1, axis=0)
        + np.roll(array, 1, axis=1)
        + np.roll(array, -1, axis=1)
    )
    return {
        "brightness": float(array.mean()),
        "contrast": float(array.std()),
        "sharpness": float(laplacian.var()),
        "mean_gradient": float(np.hypot(gx, gy).mean()),
    }


def extract_features(
    image: Image.Image,
    feature_size: tuple[int, int],
) -> np.ndarray:
    """6차시 모델 학습 때와 동일한 이미지 특징을 추출한다."""
    array = np.asarray(
        image.resize(feature_size, Image.Resampling.BILINEAR),
        dtype=np.float32,
    )
    normalized = array / 255.0
    gx = np.diff(normalized, axis=1, prepend=normalized[:, :1])
    gy = np.diff(normalized, axis=0, prepend=normalized[:1, :])
    magnitude = np.hypot(gx, gy)
    orientation = (np.degrees(np.arctan2(gy, gx)) + 180) % 180

    hog: list[float] = []
    bins = np.linspace(0, 180, 10)
    for row in range(0, feature_size[1], 8):
        for column in range(0, feature_size[0], 8):
            cell_angle = orientation[row : row + 8, column : column + 8]
            cell_weight = magnitude[row : row + 8, column : column + 8]
            histogram, _ = np.histogram(
                cell_angle,
                bins=bins,
                weights=cell_weight,
            )
            histogram = histogram / (histogram.sum() + 1e-6)
            hog.extend(histogram.tolist())

    intensity_histogram, _ = np.histogram(
        normalized,
        bins=16,
        range=(0, 1),
        density=True,
    )
    percentiles = np.percentile(
        normalized,
        [1, 5, 25, 50, 75, 95, 99],
    )
    extra = np.array(
        [
            normalized.mean(),
            normalized.std(),
            magnitude.mean(),
            np.percentile(magnitude, 90),
            np.percentile(magnitude, 99),
        ]
    )
    return np.concatenate(
        [
            np.asarray(hog),
            intensity_histogram,
            percentiles,
            extra,
        ]
    )


def quality_failures(
    metrics: dict[str, float],
    limits: dict[str, float],
) -> list[str]:
    failures = []
    if metrics["brightness"] < limits["brightness_low"]:
        failures.append("밝기가 학습 범위보다 낮습니다.")
    if metrics["brightness"] > limits["brightness_high"]:
        failures.append("밝기가 학습 범위보다 높습니다.")
    if metrics["contrast"] < limits["contrast_low"]:
        failures.append("대비가 부족합니다.")
    if metrics["sharpness"] < limits["sharpness_low"]:
        failures.append("초점 또는 해상도가 부족합니다.")
    return failures


def render_app() -> None:
    st.set_page_config(
        page_title="6차시 비전검사 모델 체험",
        page_icon="🔍",
        layout="wide",
    )
    st.title("6차시 비전검사 모델 체험")
    st.caption(
        "KSDD 이미지로 학습한 교육용 기준선 모델입니다. "
        "모델 출력은 불량 확정이 아니라 사람 검토 후보입니다."
    )

    try:
        model_path = find_model_path()
        bundle = load_bundle(str(model_path))
    except Exception as error:
        st.error("저장 모델을 불러오지 못했습니다.")
        st.code(str(error))
        st.info(
            f"GitHub 저장소 최상위 루트 디렉토리에 `{MODEL_FILENAME}` 파일이 "
            "정상적으로 업로드되었는지 확인해 주세요."
        )
        st.stop()

    with st.sidebar:
        st.subheader("모델 정보")
        st.write(f"파일: `{model_path.name}`")
        st.write(f"데이터: {bundle.get('dataset', 'UNKNOWN')}")
        st.write(
            "운영 임계값: "
            f"{float(bundle['operating_threshold']):.2f}"
        )
        st.write(f"특징 추출기: `{bundle['feature_extractor']}`")
        st.warning(
            "다른 제품·카메라·조명에서 촬영한 이미지는 "
            "학습 범위 밖 입력일 수 있습니다."
        )

    uploaded = st.file_uploader(
        "검사할 JPG 또는 PNG 이미지 한 장을 선택하세요.",
        type=["jpg", "jpeg", "png"],
    )
    if uploaded is None:
        st.info("이미지를 올리면 촬영 품질을 확인한 뒤 모델을 실행합니다.")
        return
    if uploaded.size > MAX_UPLOAD_BYTES:
        st.error("파일 크기는 10MB 이하여야 합니다.")
        return

    try:
        image = Image.open(uploaded)
        image.verify()
        uploaded.seek(0)
        image = Image.open(uploaded).convert("L")
    except (UnidentifiedImageError, OSError, ValueError):
        st.error("지원되는 정상적인 이미지 파일이 아닙니다.")
        return

    feature_size = tuple(int(value) for value in bundle["feature_size"])
    metrics = quality_metrics(image, feature_size)
    failures = quality_failures(metrics, bundle["quality_limits"])

    image_column, result_column = st.columns([1.15, 1])
    with image_column:
        st.image(image, caption="업로드 이미지", use_container_width=True)

    with result_column:
        st.subheader("1. 이미지 품질 게이트")
        metric_columns = st.columns(3)
        metric_columns[0].metric("밝기", f"{metrics['brightness']:.1f}")
        metric_columns[1].metric("대비", f"{metrics['contrast']:.1f}")
        metric_columns[2].metric("선명도", f"{metrics['sharpness']:.1f}")

        if failures:
            st.error("촬영 조건 부적합 — 재촬영 또는 사람 검토")
            for failure in failures:
                st.write(f"- {failure}")
            st.info(
                "품질 게이트를 통과하지 못해 정상·불량 예측을 표시하지 않습니다."
            )
            return

        st.success("촬영 품질 기준 통과")
        st.subheader("2. 정상·불량 후보 예측")
        feature = extract_features(image, feature_size).reshape(1, -1)
        expected_features = getattr(
            bundle["model"],
            "n_features_in_",
            feature.shape[1],
        )
        if feature.shape[1] != expected_features:
            st.error(
                "특징 수가 저장 모델과 일치하지 않습니다. "
                f"현재 {feature.shape[1]}개, 모델 {expected_features}개"
            )
            return

        defect_probability = float(
            bundle["model"].predict_proba(feature)[0, 1]
        )
        threshold = float(bundle["operating_threshold"])
        is_review_candidate = defect_probability >= threshold

        st.metric("모델 불량 점수", f"{defect_probability * 100:.1f}%")
        st.progress(min(max(defect_probability, 0.0), 1.0))
        st.caption(f"교육용 검토 임계값: {threshold * 100:.1f}%")

        if is_review_candidate:
            st.error("판정: 불량 검토 후보")
        else:
            st.success("판정: 정상 후보")

    st.warning(
        "이 결과만으로 제품을 폐기하거나 공정을 정지하지 마십시오. "
        "승인된 검사 기준에 따라 작업자가 원본 이미지와 제품을 확인해야 합니다."
    )


if __name__ == "__main__":
    render_app()
