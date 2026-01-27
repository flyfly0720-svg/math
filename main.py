import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="점수 분석 대시보드", layout="wide")
st.title("📊 회차별 점수 분석 대시보드")

# ======================
# 1. 데이터 로드
# ======================
@st.cache_data
def load_base_data():
    return pd.read_csv("이동선_수학.csv")

base_df = load_base_data()

st.sidebar.header("📂 데이터 업로드")
uploaded_file = st.sidebar.file_uploader(
    "같은 형식의 CSV 업로드",
    type="csv"
)

if uploaded_file:
    upload_df = pd.read_csv(uploaded_file)
    df = pd.concat([base_df, upload_df], ignore_index=True)
    st.sidebar.success("데이터 병합 완료 ✅")
else:
    df = base_df.copy()



# ======================
# 2. 컬럼 자동 판별 (🔥 핵심)
# ======================
numeric_cols = df.select_dtypes(include="number").columns.tolist()
non_numeric_cols = df.select_dtypes(exclude="number").columns.tolist()

if len(numeric_cols) == 0 or len(non_numeric_cols) == 0:
    st.error("❌ 데이터 형식 오류: 회차 또는 점수 컬럼을 찾을 수 없습니다.")
    st.stop()

score_col = numeric_cols[0]
round_col = non_numeric_cols[0]

st.caption(f"✔ 회차 컬럼: **{round_col}**, 점수 컬럼: **{score_col}**")

# ======================
# 3. 회차 선택
# ======================
df[round_col] = df[round_col].astype(str)
rounds = sorted(df[round_col].unique())

selected_round = st.selectbox("📌 분석할 회차 선택", rounds)

round_df = df[df[round_col] == selected_round]

# ======================
# 4. 통계 계산
# ======================
my_score = round_df[score_col].iloc[-1]
max_score = round_df[score_col].max()
top_30_score = round_df[score_col].quantile(0.7)

# ======================
# 5. 지표 표시
# ======================
c1, c2, c3 = st.columns(3)

c1.metric("🧑 내 점수", my_score)
c2.metric("🏆 최고점", max_score, f"{max_score - my_score:+.1f}")
c3.metric("📊 상위 30%", round(top_30_score, 1), f"{top_30_score - my_score:+.1f}")

# ======================
# 6. 점수 분포
# ======================
fig_dist = px.histogram(
    round_df,
    x=score_col,
    nbins=20,
    title=f"{selected_round} 회차 점수 분포"
)


# ======================
# 점수 분포 그래프 (NameError 방지 버전)
# ======================
fig_dist = None  # 🔒 먼저 정의

if not round_df.empty:
    fig_dist = px.histogram(
        round_df,
        x=score_col,
        nbins=20,
        title=f"{selected_round} 회차 점수 분포"
    )

    fig_dist.add_vline(
        x=my_score,
        line_dash="dash",
        annotation_text="내 점수"
    )

    fig_dist.add_hline(
        y=top_30_score,
        line_dash="dot",
        annotation_text="상위 30% 기준",
        annotation_position="top left"
    )

if fig_dist is not None:
    st.plotly_chart(fig_dist, use_container_width=True)
else:
    st.warning("해당 회차에 표시할 데이터가 없습니다.")





# ======================
# 7. 회차별 평균 추이
# ======================
trend_df = df.groupby(round_col)[score_col].mean().reset_index()




import re

def normalize_round(x):
    """
    어떤 형태든 → 'N회'로 통일
    예: 1, 1.0, '01', '1회', '제1회' → '1회'
    """
    nums = re.findall(r"\d+", str(x))
    return f"{int(nums[0])}회" if nums else "0회"

df[round_col] = df[round_col].apply(normalize_round)



