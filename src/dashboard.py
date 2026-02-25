import streamlit as st
import pandas as pd
import sqlite3
from scipy.stats import chi2_contingency
import os

# 페이지 기본 설정
st.set_page_config(page_title="OptiServe A/B Test Dashboard", page_icon="🚀", layout="wide")

st.title("OptiServe 실시간 A/B 테스트 대시보드")
st.markdown("추천 알고리즘 변경에 따른 **클릭률(CTR)** 변화와 **통계적 유의성(p-value)**을 실시간으로 모니터링합니다.")

def load_data():
    """DB에서 로그 데이터를 불러옵니다."""
    db_path = "optiserve.db"
    if not os.path.exists(db_path):
        return pd.DataFrame()
    
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM user_logs", conn)
    conn.close()
    return df

df = load_data()

if df.empty:
    st.warning("데이터가 없습니다. 터미널에서 `python -m src.mock_data`를 먼저 실행해주세요.")
else:
    # 1. 데이터 집계 (Pivot)
    summary = df.pivot_table(index='ab_group', columns='action_type', aggfunc='size', fill_value=0)
    
    if 'click' not in summary.columns: summary['click'] = 0
    if 'impression' not in summary.columns: summary['impression'] = 0
        
    summary['CTR (%)'] = (summary['click'] / summary['impression']) * 100
    summary['no_click'] = summary['impression'] - summary['click']
    
    # 2. 통계적 검증 (Chi-Square)
    obs = [
        [summary.loc['A', 'click'], summary.loc['A', 'no_click']],
        [summary.loc['B', 'click'], summary.loc['B', 'no_click']]
    ]
    chi2, p_value, dof, expected = chi2_contingency(obs)
    
    # 3. 핵심 지표(Metric) 시각화
    st.subheader("핵심 성과 지표 (KPIs)")
    col1, col2, col3 = st.columns(3)
    
    col1.metric("그룹 A (베스트셀러) CTR", f"{summary.loc['A', 'CTR (%)']:.2f}%", f"노출: {summary.loc['A', 'impression']}회")
    col2.metric("그룹 B (개인화 추천) CTR", f"{summary.loc['B', 'CTR (%)']:.2f}%", f"노출: {summary.loc['B', 'impression']}회")
    
    # 승자 판별 로직
    winner = "B (개인화)" if summary.loc['B', 'CTR (%)'] > summary.loc['A', 'CTR (%)'] else "A (베스트셀러)"
    if p_value < 0.05:
        col3.metric("통계적 승리 알고리즘", f"그룹 {winner}", f"p-value: {p_value:.4f} (유의미함)")
    else:
        col3.metric("승리 알고리즘", "무승부 (데이터 부족)", f"p-value: {p_value:.4f} (차이 없음)")

    st.divider()

    # 4. 차트 및 데이터 표 시각화
    col_chart, col_data = st.columns(2)
    
    with col_chart:
        st.subheader("그룹별 클릭률(CTR) 비교")
        # 스트림릿 내장 바 차트 활용
        st.bar_chart(summary['CTR (%)'], color="#FF4B4B")
        
    with col_data:
        st.subheader("상세 로그 집계")
        # 데이터프레임 예쁘게 출력
        display_df = summary[['impression', 'click', 'CTR (%)']].copy()
        display_df.columns = ['노출 수(회)', '클릭 수(회)', '클릭률(%)']
        st.dataframe(display_df.style.format({"클릭률(%)": "{:.2f}%"}), use_container_width=True)