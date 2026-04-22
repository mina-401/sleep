"""
visualizer.py
Q2 분석 결과 시각화
- 3개 카드형 패널: 스트레스 / BMI / 운동량 vs 수면장애 비율
- 히트맵: 스트레스 x 운동량 조합
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
import platform
import subprocess

# ── 한글 폰트 설정 (코랩/주피터 공통) ────────────────────────────────
if platform.system() == "Linux":
    # 코랩 환경 → 나눔고딕 설치
    subprocess.run(["apt-get", "install", "-y", "-q", "fonts-nanum"], capture_output=True)
    fm._load_fontmanager(try_read_cache=False)
    plt.rcParams["font.family"] = "NanumGothic"
else:
    # 로컬 Windows
    plt.rcParams["font.family"] = "Malgun Gothic"

plt.rcParams["axes.unicode_minus"] = False

# ── 공통 색상 규칙 ────────────────────────────────────────────────────
# 수면장애 비율 낮음 → 파랑, 높음 → 빨강 (전체 통일)
CMAP = "RdYlBu_r"


def _bar_colors(values: list, cmap=CMAP) -> list:
    """비율 값을 0~1로 정규화해서 색상 리스트 반환"""
    arr  = np.array(values, dtype=float)
    norm = (arr - arr.min()) / (arr.max() - arr.min() + 1e-9)
    return [plt.get_cmap(cmap)(v) for v in norm]


def _add_value_labels(ax, bars, suffix="%"):
    """막대 위에 값 라벨 표시"""
    for bar in bars:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + 1.2,
            f"{h:.1f}{suffix}",
            ha="center", va="bottom", fontsize=10, fontweight="bold", color="#333"
        )


def _style_ax(ax, title: str, xlabel: str, highlight_msg: str = None):
    """공통 축 스타일 적용"""
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel("수면장애 비율 (%)", fontsize=10)
    ax.set_ylim(0, 115)
    ax.grid(axis="y", alpha=0.2, linestyle="--")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # 강조 텍스트 (BMI 등 특이 패턴 설명용)
    if highlight_msg:
        ax.text(
            0.5, 0.96, highlight_msg,
            transform=ax.transAxes,
            ha="center", va="top", fontsize=9, color="#555",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#fff8e1", alpha=0.9)
        )


# ══════════════════════════════════════════════════════════════════════
# Q2-A: 3개 카드형 패널
# ══════════════════════════════════════════════════════════════════════

def plot_q2_panels(q2_result: dict):
    """
    스트레스 / BMI / 운동량 구간별 수면장애 비율
    → 동일한 디자인 규칙의 3개 패널로 나란히
    """

    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    fig.suptitle(
        "생활 요인이 수면장애에 미치는 영향",
        fontsize=16, fontweight="bold", y=1.03
    )

    # 요약 인사이트 1줄
    fig.text(
        0.5, 0.98,
        "스트레스가 가장 큰 영향 요인",
        ha="center", fontsize=11, color="#666", style="italic"
    )

    # ── 패널 1: 스트레스 구간 ─────────────────────────────────────────
    ax1    = axes[0]
    s_data = q2_result["disorder_by_stress"]
    labels = list(s_data["스트레스구간"].astype(str))
    vals   = list(s_data["수면장애비율(%)"])
    colors = _bar_colors(vals)

    bars = ax1.bar(labels, vals, color=colors, edgecolor="white",
                   linewidth=0.8, width=0.55)
    _add_value_labels(ax1, bars)
    _style_ax(ax1, "스트레스 구간별\n수면장애 비율", "스트레스 수준")

    # 최고값 강조 화살표
    max_idx = int(np.argmax(vals))
    ax1.annotate(
        "최고",
        xy=(max_idx, vals[max_idx]),
        xytext=(max_idx, vals[max_idx] + 18),
        ha="center", fontsize=9, color="#c0392b", fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.5)
    )

    # ── 패널 2: BMI ───────────────────────────────────────────────────
    ax2     = axes[1]
    b_data  = q2_result["disorder_by_bmi"]

    # BMI 순서 고정 (저체중→정상→과체중→비만)
    bmi_order = ["Normal", "Normal Weight", "Overweight", "Obese"]
    b_data = b_data.set_index("BMI").reindex(
        [b for b in bmi_order if b in b_data["BMI"].values]
    ).dropna().reset_index()

    b_labels = list(b_data["BMI"])
    b_vals   = list(b_data["수면장애비율(%)"])
    b_colors = _bar_colors(b_vals)

    bars2 = ax2.bar(b_labels, b_vals, color=b_colors, edgecolor="white",
                    linewidth=0.8, width=0.55)
    _add_value_labels(ax2, bars2)
    _style_ax(
        ax2,
        "BMI별\n수면장애 비율",
        "BMI 구분",
        highlight_msg="정상 대비 비만 구간에서 수면장애 급증"
    )

    # ── 패널 3: 운동량 구간 ───────────────────────────────────────────
    ax3    = axes[2]
    a_data = q2_result["disorder_by_activity"]
    a_labels = list(a_data["운동량구간"].astype(str))
    a_vals   = list(a_data["수면장애비율(%)"])

    # 운동량은 반대 방향 (많을수록 위험 낮음)
    a_colors = _bar_colors(a_vals)

    bars3 = ax3.bar(a_labels, a_vals, color=a_colors, edgecolor="white",
                    linewidth=0.8, width=0.55)
    _add_value_labels(ax3, bars3)
    _style_ax(ax3, "운동량 구간별\n수면장애 비율", "일일 운동량 (분)")

    # 공통 범례 (색 규칙 설명)
    low_patch  = mpatches.Patch(color=plt.get_cmap(CMAP)(0.1), label="수면장애 비율 낮음")
    high_patch = mpatches.Patch(color=plt.get_cmap(CMAP)(0.9), label="수면장애 비율 높음")
    fig.legend(
        handles=[low_patch, high_patch],
        loc="lower center", ncol=2,
        fontsize=10, framealpha=0.9,
        bbox_to_anchor=(0.5, -0.04)
    )

    plt.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════════════
# Q2-B: 히트맵 (스트레스 x 운동량)
# ══════════════════════════════════════════════════════════════════════

def plot_q2_heatmap(df: pd.DataFrame):
    """
    스트레스 구간 x 운동량 구간 → 수면장애 비율 히트맵
    색만 봐도 "스트레스 높고 운동 적으면 빨갛다" 바로 보임
    """

    # 구간 컬럼 생성
    df = df.copy()
    df["수면장애여부"] = df["수면장애"].apply(lambda x: 1 if x != "None" else 0)

    df["스트레스구간"] = pd.cut(
        df["스트레스"],
        bins=[0, 4, 7, 10],
        labels=["낮음\n(1~4)", "중간\n(5~7)", "높음\n(8~10)"]
    )
    df["운동량구간"] = pd.cut(
        df["운동량"],
        bins=[0, 30, 60, 90],
        labels=["적음\n(0~30)", "보통\n(31~60)", "많음\n(61~90)"]
    )

    # 피벗 테이블
    pivot = df.pivot_table(
        values="수면장애여부",
        index="운동량구간",
        columns="스트레스구간",
        aggfunc=lambda x: round(x.mean() * 100, 1),
        observed=True
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    fig.suptitle(
        "스트레스 × 운동량 조합별 수면장애 비율",
        fontsize=14, fontweight="bold"
    )

    im = ax.imshow(pivot.values, cmap=CMAP, aspect="auto", vmin=0, vmax=100)

    # 축 라벨
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, fontsize=11)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=11)
    ax.set_xlabel("스트레스 구간", fontsize=11, labelpad=8)
    ax.set_ylabel("운동량 구간", fontsize=11, labelpad=8)

    # 셀 안에 수치 표시
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            if np.isnan(val):
                continue
            # 배경색에 따라 텍스트 흰색/검정 자동 선택
            bg_brightness = plt.get_cmap(CMAP)(val / 100)[:3]
            lum = 0.299 * bg_brightness[0] + 0.587 * bg_brightness[1] + 0.114 * bg_brightness[2]
            txt_color = "white" if lum < 0.5 else "#333333"

            ax.text(j, i, f"{val:.1f}%",
                    ha="center", va="center",
                    fontsize=13, fontweight="bold", color=txt_color)

    # 컬러바
    cbar = fig.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label("수면장애 비율 (%)", fontsize=10)
    cbar.set_ticks([0, 25, 50, 75, 100])

    # 결론 박스
    ax.text(
        0.5, -0.22,
        "스트레스 높고 운동량 적을수록 수면장애 위험이 증가",
        transform=ax.transAxes, ha="center", fontsize=10,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff3e0", alpha=0.95)
    )

    plt.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════════════
# 단독 실행
# ══════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════
# Q1: 스트레스 vs 수면의 질 산점도
# ══════════════════════════════════════════════════════════════════════

def plot_q1_scatter(df: pd.DataFrame, q1_result: dict):
    """
    스트레스(x) vs 수면의 질(y) 산점도
    - 색: 스트레스 낮음 → 파랑, 높음 → 빨강
    - 점 크기: 수면의 질 좋을수록 크게
    - 추세선 + 상관계수 표시
    """

    fig, ax = plt.subplots(figsize=(9, 6))

    stress  = df["스트레스"].values.astype(float)
    quality = df["수면의질"].values.astype(float)

    # NaN 제거
    mask = ~np.isnan(stress) & ~np.isnan(quality)
    stress  = stress[mask]
    quality = quality[mask]

    # 색 정규화 (스트레스 기준)
    s_min, s_max = stress.min(), stress.max()
    norm_stress = (stress - s_min) / (s_max - s_min + 1e-9)

    # 점 크기 정규화 (수면의 질 기준) - 음수 방지
    q_min, q_max = quality.min(), quality.max()
    norm_quality = (quality - q_min) / (q_max - q_min + 1e-9)
    sizes = np.clip(norm_quality * 120 + 30, 10, 200)  # 최소 10 보장

    sc = ax.scatter(
        stress, quality,
        c=norm_stress,
        cmap="RdYlBu_r",        # 파랑(낮음) → 노랑 → 빨강(높음)
        s=sizes,
        alpha=0.75,
        edgecolors="white",
        linewidths=0.5,
    )

    # 추세선
    mask = ~np.isnan(stress) & ~np.isnan(quality)
    if mask.sum() >= 2:
        z = np.polyfit(stress[mask], quality[mask], 1)
        p = np.poly1d(z)
        x_line = np.linspace(stress[mask].min(), stress[mask].max(), 100)
        ax.plot(x_line, p(x_line),
                color="#444", linewidth=2, linestyle="--",
                alpha=0.7, label="추세선")

    # 상관계수 텍스트 박스
    corr = q1_result["stress_sleep_corr"]
    interp = q1_result["interpretation"]
    ax.text(
        0.03, 0.97,
        f"r = {corr}\n{interp}",
        transform=ax.transAxes,
        fontsize=10, va="top",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.85)
    )

    # 컬러바
    cbar = fig.colorbar(sc, ax=ax, pad=0.02)
    cbar.set_label("스트레스 수준", fontsize=10)
    cbar.set_ticks([0, 0.5, 1])
    cbar.set_ticklabels(["낮음", "중간", "높음"])

    # 점 크기 범례
    for q_val, label in [(q_min, "수면 질 낮음"), ((q_min+q_max)/2, "수면 질 보통"), (q_max, "수면 질 높음")]:
        norm_v = (q_val - q_min) / (q_max - q_min + 1e-9)
        s = np.clip(norm_v * 120 + 30, 10, 200)
        ax.scatter([], [], s=s, color="gray", alpha=0.6, label=label)
    ax.legend(fontsize=9, loc="upper right")

    ax.set_xlabel("스트레스 수준 (1~10)", fontsize=11)
    ax.set_ylabel("수면의 질 (1~10)", fontsize=11)
    ax.set_title("스트레스와 수면의 질의 관계", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlim(stress.min() - 0.5, stress.max() + 0.5)
    ax.set_ylim(quality.min() - 0.5, quality.max() + 0.5)
    ax.grid(True, alpha=0.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════════════
# Q1-B: 스트레스 구간별 수면의 질 평균 막대 + 전체 평균선
# ══════════════════════════════════════════════════════════════════════

def plot_q1_stress_bar(df: pd.DataFrame, q1_result: dict):
    """
    스트레스 구간(낮음/중간/높음)별 수면의 질 평균 막대그래프
    + 전체 평균선으로 기준 대비 비교
    - 색: 스트레스 낮음 → 파랑, 높음 → 빨강
    - 전체 평균선: 점선으로 표시
    """

    fig, ax = plt.subplots(figsize=(8, 6))

    by_group = q1_result["by_stress_group"]
    labels   = list(by_group["스트레스구간"].astype(str))
    vals     = list(by_group["수면의질 평균"])

    # 전체 평균
    overall_mean = round(df["수면의질"].mean(), 2)

    # 색: 낮음→파랑, 중간→노랑, 높음→빨강
    bar_colors = [
        plt.get_cmap("RdYlBu_r")(0.1),   # 낮음 → 파랑
        plt.get_cmap("RdYlBu_r")(0.5),   # 중간 → 노랑
        plt.get_cmap("RdYlBu_r")(0.9),   # 높음 → 빨강
    ]

    bars = ax.bar(labels, vals, color=bar_colors,
                  edgecolor="white", linewidth=0.8, width=0.5)

    # 막대 위 값 라벨
    for bar, val in zip(bars, vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.08,
            f"{val}",
            ha="center", va="bottom",
            fontsize=12, fontweight="bold", color="#333"
        )

    # 전체 평균선
    ax.axhline(
        y=overall_mean,
        color="#333", linewidth=1.8,
        linestyle="--", alpha=0.75,
        label=f"전체 평균  {overall_mean}"
    )

    # 평균선 라벨 (오른쪽 끝에 표시)
    ax.text(
        2.38, overall_mean + 0.08,
        f"전체 평균\n{overall_mean}",
        ha="right", va="bottom",
        fontsize=9, color="#333",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8)
    )

    # 각 구간이 평균보다 얼마나 차이나는지 화살표로 표시
    for i, (bar, val) in enumerate(zip(bars, vals)):
        diff = round(val - overall_mean, 2)
        color = "#1a6fb5" if diff > 0 else "#c0392b"
        sign  = "+" if diff > 0 else ""
        ax.annotate(
            f"{sign}{diff}",
            xy=(bar.get_x() + bar.get_width() / 2, overall_mean),
            xytext=(bar.get_x() + bar.get_width() / 2,
                    overall_mean + (diff / 2)),
            ha="center", va="center",
            fontsize=10, color=color, fontweight="bold",
        )

    ax.set_xlabel("스트레스 구간", fontsize=11)
    ax.set_ylabel("수면의 질 평균 (1~10)", fontsize=11)
    ax.set_title(
        "스트레스 구간별 수면의 질 평균\n(전체 평균 대비 비교)",
        fontsize=13, fontweight="bold", pad=12
    )
    ax.set_ylim(0, 10.5)
    ax.grid(axis="y", alpha=0.2, linestyle="--")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════════════
# Q2-C: 위험 조합 TOP3 수평 막대그래프
# ══════════════════════════════════════════════════════════════════════

def plot_q2_top_risk(q2_result: dict):
    """
    수면장애 위험 조합 TOP5 수평 막대그래프
    BMI + 스트레스 + 운동량 3가지 조합을 한눈에 비교
    """

    top_risk = q2_result["top_risk"]

    # 조합 라벨 생성 (BMI + 스트레스구간 + 운동량구간)
    def make_label(row):
        return f"{row['BMI']} · {row['스트레스구간']} · {row['운동량구간']}"

    risk_labels = [make_label(row) for _, row in top_risk.iterrows()]
    risk_vals   = list(top_risk["수면장애비율(%)"])

    # 색: 비율 높을수록 진한 빨강
    norm = np.linspace(0.95, 0.55, len(risk_vals))
    colors_risk = [plt.get_cmap(CMAP)(v) for v in norm]

    fig, ax = plt.subplots(figsize=(10, 10))
    fig.suptitle(
        "수면장애와 가장 연관 높은 생활습관 조합 TOP15",
        fontsize=14, fontweight="bold", y=1.02
    )

    bars = ax.barh(risk_labels[::-1], risk_vals[::-1],
                   color=colors_risk[::-1],
                   edgecolor="white", linewidth=0.8, height=0.6)

    # 막대 끝에 수치 라벨
    for bar, val in zip(bars, risk_vals[::-1]):
        ax.text(
            bar.get_width() + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{val}%",
            va="center", fontsize=11, fontweight="bold", color="#c0392b"
        )

    ax.set_xlim(0, 115)
    ax.set_xlabel("수면장애 비율 (%)", fontsize=11)
    ax.set_title("위험 조합 TOP5", fontsize=12, fontweight="bold",
                 color="#c0392b", pad=10)
    ax.grid(axis="x", alpha=0.2, linestyle="--")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # 결론 박스
    ax.text(
        0.5, -0.15,
        "비만(Obese) + 스트레스 높음 + 운동 부족 조합에서 수면장애 위험 집중",
        transform=ax.transAxes, ha="center", fontsize=10,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff3e0", alpha=0.95)
    )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    from analyzer import load_data, analyze_q1, analyze_q2

    df = load_data()
    if df.empty:
        print("[오류] 데이터 없음")
    else:
        q1 = analyze_q1(df)
        plot_q1_scatter(df, q1)
        plot_q1_stress_bar(df, q1)

        q2 = analyze_q2(df)
        plot_q2_panels(q2)
        plot_q2_heatmap(df)
        plot_q2_top_risk(q2)
