"""
main.py
python main.py 실행 시
 → 데이터 분석 → 시각화 → output/ 폴더에 이미지 저장
"""

from analyzer import load_data, analyze_q1, analyze_q2
from Visualizer import (
    plot_q1_scatter,
    plot_q1_stress_bar,
    plot_q2_panels,
    plot_q2_heatmap,
    plot_q2_top_risk,
)

def main():
    print("=" * 50)
    print("수면 및 생활습관 데이터 분석 시작")
    print("=" * 50)

    # ── 데이터 로드 ───────────────────────────────────────────────────
    df = load_data()
    if df.empty:
        print("[오류] 데이터 로드 실패. 종료합니다.")
        return

    # ── Q1 분석 + 시각화 ──────────────────────────────────────────────
    print("\n[Q1] 스트레스 vs 수면의 질 분석 중...")
    q1 = analyze_q1(df)
    print(f"  상관계수 : {q1['stress_sleep_corr']}")
    print(f"  해석     : {q1['interpretation']}")
    plot_q1_scatter(df, q1)
    plot_q1_stress_bar(df, q1)

    # ── Q2 분석 + 시각화 ──────────────────────────────────────────────
    print("\n[Q2] 생활습관 조합 vs 수면장애 분석 중...")
    q2 = analyze_q2(df)
    plot_q2_panels(q2)
    plot_q2_heatmap(df)
    plot_q2_top_risk(q2)

    print("\n" + "=" * 50)
    print("완료! output/ 폴더에서 결과를 확인하세요.")
    print("  - output/q1_scatter.png")
    print("  - output/q1_stress_bar.png")
    print("  - output/q2_panels.png")
    print("  - output/q2_heatmap.png")
    print("  - output/q2_top_risk.png")
    print("=" * 50)


if __name__ == "__main__":
    main()