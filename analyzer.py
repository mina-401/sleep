"""
analyzer.py
수면 및 생활습관 데이터셋 로드 + 전처리
"""

import pandas as pd
import os

# ── 데이터 경로 ───────────────────────────────────────────────────────
DATA_PATH = "data/Sleep_health_and_lifestyle_dataset.csv"

# ── 컬럼 한글화 매핑 ──────────────────────────────────────────────────
COLUMN_MAP = {
    "Person ID":               "ID",
    "Gender":                  "성별",
    "Age":                     "나이",
    "Occupation":              "직업",
    "Sleep Duration":          "수면시간",
    "Quality of Sleep":        "수면의질",
    "Physical Activity Level": "운동량",
    "Stress Level":            "스트레스",
    "BMI Category":            "BMI",
    "Blood Pressure":          "혈압",
    "Heart Rate":              "심박수",
    "Daily Steps":             "걸음수",
    "Sleep Disorder":          "수면장애",
}


def load_data() -> pd.DataFrame:
    """
    CSV 파일을 불러와서 전처리 후 DataFrame 반환

    전처리 순서:
    1. 파일 존재 여부 확인
    2. CSV 로드
    3. 결측값 처리
    4. 컬럼 한글화
    """

    # 1. 파일 존재 여부 확인
    if not os.path.exists(DATA_PATH):
        print(f"[오류] 파일을 찾을 수 없습니다: {DATA_PATH}")
        print("  → data/ 폴더에 CSV 파일이 있는지 확인하세요.")
        return pd.DataFrame()

    # 2. CSV 로드
    df = pd.read_csv(DATA_PATH)
    print(f"[로드 완료] {len(df)}행 {len(df.columns)}열")

    # 3. 결측값 처리
    # Sleep Disorder 컬럼: 비어있는 칸 → "None" 으로 채움
    df["Sleep Disorder"] = df["Sleep Disorder"].fillna("None")

    # 결측값이 있는 다른 컬럼 확인 후 해당 행 제거
    before = len(df)
    df = df.dropna()
    after = len(df)
    if before != after:
        print(f"[결측값 제거] {before - after}행 제거됨 → 남은 행: {after}")

    # 4. 컬럼 한글화
    df = df.rename(columns=COLUMN_MAP)
    print(f"[전처리 완료] 컬럼: {list(df.columns)}")

    return df


# ── Q1 분석: 스트레스 vs 수면의 질 ──────────────────────────────────
def analyze_q1(df: pd.DataFrame) -> dict:
    """
    Q1. 스트레스 수준과 수면의 질 사이에 어떤 관계가 있나?

    반환하는 데이터:
    - stress_sleep_corr : 전체 상관계수 (−1 ~ 1)
    - by_occupation     : 직업별 스트레스·수면의질 평균 DataFrame
    - interpretation    : 상관계수 해석 문자열
    """

    result = {}

    # 1. 전체 상관계수
    corr = df["스트레스"].corr(df["수면의질"])
    result["stress_sleep_corr"] = round(corr, 3)

    # 상관계수 해석
    if corr <= -0.7:
        interp = "강한 음의 상관관계 → 스트레스가 높을수록 수면의 질이 크게 낮아짐"
    elif corr <= -0.4:
        interp = "중간 음의 상관관계 → 스트레스가 높을수록 수면의 질이 낮아지는 경향"
    elif corr <= -0.1:
        interp = "약한 음의 상관관계 → 약간의 연관성 있음"
    else:
        interp = "거의 상관없음"
    result["interpretation"] = interp

    # 2. 스트레스 구간별 수면의 질 평균
    df = df.copy()
    df["스트레스구간"] = pd.cut(
        df["스트레스"],
        bins=[0, 4, 7, 10],
        labels=["낮음(1~4)", "중간(5~7)", "높음(8~10)"]
    )

    by_stress_group = (
        df.groupby("스트레스구간", observed=True)["수면의질"]
        .mean()
        .round(2)
        .reset_index()
        .rename(columns={"수면의질": "수면의질 평균"})
    )
    result["by_stress_group"] = by_stress_group

    return result


# ── Q2 분석: 생활습관 조합 vs 수면장애 ──────────────────────────────
def analyze_q2(df: pd.DataFrame) -> dict:
    """
    Q2. 어떤 생활습관 조합이 수면장애와 가장 연관이 높나?

    분석 방법:
    - BMI / 스트레스 / 운동량 3가지 기준으로 각 사람을 등급화
    - 등급 조합별로 수면장애 비율 계산
    - 가장 위험한 조합 / 가장 안전한 조합 도출

    반환하는 데이터:
    - disorder_by_bmi      : BMI별 수면장애 비율
    - disorder_by_stress   : 스트레스 구간별 수면장애 비율
    - disorder_by_activity : 운동량 구간별 수면장애 비율
    - top_risk             : 수면장애 비율 가장 높은 조합 TOP3
    - top_safe             : 수면장애 비율 가장 낮은 조합 TOP3
    """

    result = {}

    # ── 1. BMI별 수면장애 비율 ────────────────────────────────────────
    # 수면장애 있음 = Insomnia 또는 Sleep Apnea
    df = df.copy()
    df["수면장애여부"] = df["수면장애"].apply(
        lambda x: "있음" if x != "None" else "없음"
    )

    bmi_disorder = (
        df.groupby("BMI")["수면장애여부"]
        .apply(lambda x: round((x == "있음").sum() / len(x) * 100, 1))
        .reset_index()
        .rename(columns={"수면장애여부": "수면장애비율(%)"})
        .sort_values("수면장애비율(%)", ascending=False)
    )
    result["disorder_by_bmi"] = bmi_disorder

    # ── 2. 스트레스 구간별 수면장애 비율 ─────────────────────────────
    # 스트레스 1~10 → 낮음(1~4) / 중간(5~7) / 높음(8~10) 으로 구간화
    df["스트레스구간"] = pd.cut(
        df["스트레스"],
        bins=[0, 4, 7, 10],
        labels=["낮음(1~4)", "중간(5~7)", "높음(8~10)"]
    )

    stress_disorder = (
        df.groupby("스트레스구간", observed=True)["수면장애여부"]
        .apply(lambda x: round((x == "있음").sum() / len(x) * 100, 1))
        .reset_index()
        .rename(columns={"수면장애여부": "수면장애비율(%)"})
    )
    result["disorder_by_stress"] = stress_disorder

    # ── 3. 운동량 구간별 수면장애 비율 ───────────────────────────────
    # 운동량 0~90 → 적음(0~30) / 보통(31~60) / 많음(61~90) 으로 구간화
    df["운동량구간"] = pd.cut(
        df["운동량"],
        bins=[0, 30, 60, 90],
        labels=["적음(0~30)", "보통(31~60)", "많음(61~90)"]
    )

    activity_disorder = (
        df.groupby("운동량구간", observed=True)["수면장애여부"]
        .apply(lambda x: round((x == "있음").sum() / len(x) * 100, 1))
        .reset_index()
        .rename(columns={"수면장애여부": "수면장애비율(%)"})
    )
    result["disorder_by_activity"] = activity_disorder

    # ── 4. 조합별 위험도 (BMI + 스트레스구간 + 운동량구간) ───────────
    combo = (
        df.groupby(["BMI", "스트레스구간", "운동량구간"], observed=True)["수면장애여부"]
        .apply(lambda x: round((x == "있음").sum() / len(x) * 100, 1))
        .reset_index()
        .rename(columns={"수면장애여부": "수면장애비율(%)"})
        .dropna()
        .sort_values("수면장애비율(%)", ascending=False)
    )

    result["top_risk"] = combo.head(3).reset_index(drop=True)   # 위험 TOP3
    result["top_safe"] = combo.tail(3).reset_index(drop=True)   # 안전 TOP3

    return result


# ── 수면장애 그룹 vs 정상 그룹 생활습관 비교 ─────────────────────────
def analyze_group_diff(df: pd.DataFrame) -> dict:
    """
    수면장애 있음 vs 없음 그룹의 생활습관 평균 비교

    반환하는 데이터:
    - comparison   : 두 그룹 평균 비교 DataFrame
    - diff_ratio   : 각 항목별 차이 비율 (몇 % 차이나는지)
    - key_insight  : 가장 차이가 큰 항목 문자열
    """

    df = df.copy()
    df["수면장애여부"] = df["수면장애"].apply(
        lambda x: "있음" if x != "None" else "없음"
    )

    # 비교할 항목
    cols = ["스트레스", "운동량", "수면시간", "수면의질", "심박수", "걸음수"]

    # 그룹별 평균
    group_mean = (
        df.groupby("수면장애여부")[cols]
        .mean()
        .round(2)
        .T  # 행/열 전치 → 항목이 행, 그룹이 열
        .reset_index()
        .rename(columns={"index": "항목", "없음": "정상그룹", "있음": "수면장애그룹"})
    )

    # 차이 비율 계산 (수면장애그룹이 정상그룹보다 몇 % 높고 낮은지)
    group_mean["차이(%)"] = (
        (group_mean["수면장애그룹"] - group_mean["정상그룹"])
        / group_mean["정상그룹"] * 100
    ).round(1)

    result = {}
    result["comparison"] = group_mean

    # 차이가 가장 큰 항목 찾기
    max_diff_row = group_mean.loc[group_mean["차이(%)"].abs().idxmax()]
    항목 = max_diff_row["항목"]
    차이 = max_diff_row["차이(%)"]
    방향 = "높음" if 차이 > 0 else "낮음"
    result["key_insight"] = (
        f"수면장애 그룹은 정상 그룹보다 '{항목}'이 {abs(차이)}% {방향}"
    )

    return result


# ── 단독 실행 시 확인용 ───────────────────────────────────────────────
if __name__ == "__main__":
    df = load_data()

    if not df.empty:
        print("\n── 미리보기 (상위 5행) ──")
        print(df.head().to_string(index=False))

        print("\n── 기본 정보 ──")
        print(f"총 인원수  : {len(df)}명")
        print(f"나이 범위  : {df['나이'].min()}세 ~ {df['나이'].max()}세")
        print(f"직업 종류  : {df['직업'].nunique()}가지")
        print(f"수면장애 분포:\n{df['수면장애'].value_counts()}")

        print("\n── Q1 분석 결과 ──")
        q1 = analyze_q1(df)
        print(f"전체 상관계수 : {q1['stress_sleep_corr']}")
        print(f"해석          : {q1['interpretation']}")
        print("\n스트레스 구간별 수면의 질 평균:")
        print(q1["by_stress_group"].to_string(index=False))

        print("\n── Q2 분석 결과 ──")
        q2 = analyze_q2(df)

        print("\nBMI별 수면장애 비율:")
        print(q2["disorder_by_bmi"].to_string(index=False))

        print("\n스트레스 구간별 수면장애 비율:")
        print(q2["disorder_by_stress"].to_string(index=False))

        print("\n운동량 구간별 수면장애 비율:")
        print(q2["disorder_by_activity"].to_string(index=False))

        print("\n수면장애 위험 조합 TOP3:")
        print(q2["top_risk"].to_string(index=False))

        print("\n수면장애 안전 조합 TOP3:")
        print(q2["top_safe"].to_string(index=False))

        print("\n── 그룹 비교 분석 결과 ──")
        gd = analyze_group_diff(df)
        print("\n수면장애 있음 vs 없음 생활습관 평균 비교:")
        print(gd["comparison"].to_string(index=False))
        print(f"\n핵심 인사이트: {gd['key_insight']}")
