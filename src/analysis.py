import sqlite3
import pandas as pd
from scipy.stats import chi2_contingency

def analyze_ab_test():
    # 1. DB에 연결해서 데이터 가져오기
    conn = sqlite3.connect("optiserve.db")
    df = pd.read_sql_query("SELECT * FROM user_logs", conn)
    conn.close()
    
    if df.empty:
        print("데이터가 없습니다. 먼저 src/mock_data.py를 실행하세요.")
        return

    print("[OptiServe A/B 테스트 결과 분석]")
    print("-" * 40)
    
    # 2. 그룹별 노출(impression)과 클릭(click) 수 집계 (Pivot Table)
    summary = df.pivot_table(index='ab_group', columns='action_type', aggfunc='size', fill_value=0)
    
    # 클릭이 아예 없을 경우를 대비한 방어 로직
    if 'click' not in summary.columns:
        summary['click'] = 0
        
    # 3. 클릭률(CTR) 계산
    summary['CTR (%)'] = (summary['click'] / summary['impression']) * 100
    
    print(summary[['impression', 'click', 'CTR (%)']].round(2))
    print("-" * 40)
    
    # 4. 통계적 유의성 검증 (카이제곱 검정 - Chi-Square Test)
    # 노출되었으나 클릭하지 않은 횟수 계산
    summary['no_click'] = summary['impression'] - summary['click']
    
    # 검정용 데이터: [[A군 클릭, A군 노클릭], [B군 클릭, B군 노클릭]]
    obs = [
        [summary.loc['A', 'click'], summary.loc['A', 'no_click']],
        [summary.loc['B', 'click'], summary.loc['B', 'no_click']]
    ]
    
    # 카이제곱 검정 수행
    chi2, p_value, dof, expected = chi2_contingency(obs)
    
    print("🧪 [통계적 가설 검정 (Chi-Square)]")
    print(f"   - p-value: {p_value:.5f}")
    
    # 5. 최종 결론 도출 (유의수준 5% 기준)
    if p_value < 0.05:
        print("\n[결론] p-value가 0.05 미만이므로, 두 그룹 간의 클릭률 차이는 통계적으로 유의미합니다!")
        winner = summary['CTR (%)'].idxmax()
        print(f"   최종 승리 알고리즘: 그룹 {winner} (CTR: {summary.loc[winner, 'CTR (%)']:.2f}%)")
    else:
        print("\n[결론] p-value가 0.05 이상이므로, 두 그룹 간의 차이는 우연일 수 있습니다. (유의미한 차이 없음)")

if __name__ == "__main__":
    analyze_ab_test()