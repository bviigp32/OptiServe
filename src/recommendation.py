import pandas as pd
import sqlite3
from sklearn.metrics.pairwise import cosine_similarity
import os
from functools import lru_cache 

DB_PATH = "optiserve.db"

@lru_cache(maxsize=1024) 
def get_popular_items(n=3):
    """[Model A: 인기도 기반 추천] (캐싱 적용)"""
    if not os.path.exists(DB_PATH):
        return ["베스트셀러_A", "베스트셀러_B", "베스트셀러_C"]

    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT item_name, COUNT(*) as click_count 
        FROM user_logs 
        WHERE action_type='click' 
        GROUP BY item_name 
        ORDER BY click_count DESC 
        LIMIT ?
    """
    df = pd.read_sql(query, conn, params=(n,))
    conn.close()

    if df.empty:
        return ["맥북 프로", "아이폰 15", "에어팟 프로"]
    return df['item_name'].tolist()

@lru_cache(maxsize=1024) 
def get_cf_recommendation(user_id, n=3):
    """[Model B: 협업 필터링] (캐싱 적용)"""
    if not os.path.exists(DB_PATH):
        return get_popular_items(n)

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT user_id, item_name FROM user_logs WHERE action_type='click'", conn)
    conn.close()

    if df.empty or user_id not in df['user_id'].values:
        return get_popular_items(n)

    df['clicked'] = 1
    user_item_matrix = df.pivot_table(index='user_id', columns='item_name', values='clicked', fill_value=0)

    user_sim = cosine_similarity(user_item_matrix)
    user_sim_df = pd.DataFrame(user_sim, index=user_item_matrix.index, columns=user_item_matrix.index)

    similar_users = user_sim_df[user_id].sort_values(ascending=False)[1:]
    if similar_users.empty:
        return get_popular_items(n)
        
    most_similar_user = similar_users.index[0]

    target_user_clicked = user_item_matrix.loc[user_id]
    unclicked_items = target_user_clicked[target_user_clicked == 0].index.tolist()

    similar_user_clicked = user_item_matrix.loc[most_similar_user]
    recommendations = similar_user_clicked[(similar_user_clicked == 1) & (similar_user_clicked.index.isin(unclicked_items))].index.tolist()

    if len(recommendations) < n:
        popular = get_popular_items(n)
        for item in popular:
            if item not in recommendations and len(recommendations) < n:
                recommendations.append(item)

    return recommendations[:n]