import pandas as pd
import sqlite3
from sklearn.metrics.pairwise import cosine_similarity
import os

DB_PATH = "optiserve.db"

def get_popular_items(n=3):
    """
    [Model A: 인기도 기반 추천]
    DB에서 클릭(Click)이 가장 많이 발생한 베스트셀러 Top N을 반환합니다.
    """
    if not os.path.exists(DB_PATH):
        return ["베스트셀러_A", "베스트셀러_B", "베스트셀러_C"]

    conn = sqlite3.connect(DB_PATH)
    # 클릭 로그를 그룹핑해서 내림차순 정렬
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

def get_cf_recommendation(user_id, n=3):
    """
    [Model B: 협업 필터링 (User-Based CF)]
    타겟 유저와 취향(클릭 기록)이 가장 비슷한 유저를 찾아, 그 사람이 클릭한 상품을 추천합니다.
    """
    if not os.path.exists(DB_PATH):
        return get_popular_items(n)

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT user_id, item_name FROM user_logs WHERE action_type='click'", conn)
    conn.close()

    # 클릭 기록이 아예 없는 신규 유저라면? -> 베스트셀러를 추천해준다
    if df.empty or user_id not in df['user_id'].values:
        return get_popular_items(n)

    # 1. User-Item 매트릭스 생성 (클릭했으면 1, 아니면 0)
    df['clicked'] = 1
    user_item_matrix = df.pivot_table(index='user_id', columns='item_name', values='clicked', fill_value=0)

    # 2. 유저 간 코사인 유사도(Cosine Similarity) 계산
    user_sim = cosine_similarity(user_item_matrix)
    user_sim_df = pd.DataFrame(user_sim, index=user_item_matrix.index, columns=user_item_matrix.index)

    # 3. 나와 가장 유사한 유저 찾기 (자기 자신 제외)
    similar_users = user_sim_df[user_id].sort_values(ascending=False)[1:]
    
    if similar_users.empty:
        return get_popular_items(n)
        
    most_similar_user = similar_users.index[0]

    # 4. 유사한 유저가 클릭한 상품 중, 내가 아직 안 본 상품 찾기
    target_user_clicked = user_item_matrix.loc[user_id]
    unclicked_items = target_user_clicked[target_user_clicked == 0].index.tolist()

    similar_user_clicked = user_item_matrix.loc[most_similar_user]
    recommendations = similar_user_clicked[(similar_user_clicked == 1) & (similar_user_clicked.index.isin(unclicked_items))].index.tolist()

    # 5. 추천할 상품이 n개보다 부족하면 베스트셀러로 채워 넣기 (Fallback)
    if len(recommendations) < n:
        popular = get_popular_items(n)
        for item in popular:
            if item not in recommendations and len(recommendations) < n:
                recommendations.append(item)

    return recommendations[:n]