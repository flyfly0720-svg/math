import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="점수 분석 대시보드", layout="wide")

st.title("📊 회차별 점수 분석 대시보드")

# ======================
# 1. 기본 데이터 로드
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

# ======================
# 2. 데이터 병합
# ======================
if uploaded_file:
    upload_df = pd.read_csv(uploaded_file)
    df = pd.concat([base_df, upload_df], ignore_index=True)
    st.sidebar.success("데이터 업로드 & 병합 완료 ✅")
else:
    df = base_df.copy()

# ======================
# 3. 회차 선택
# ======================
rounds = sorted(df["회차"].unique())
selected_round = st.selectbox("📌 분석할 회차 선택", rounds)

round_df = df[df["회차"] == selected_round]

# ======================
# 4. 통계 계산
# ======================
my_score = round_df["점수"].iloc[-1]
max_score = round_df["점수"].max()
top_30_score = round_df["점수"].quantile(0.7)

diff_max = max_score - my_score
diff_top30 = top_30_score - my_score

# ======================
# 5. 수치 카드
# ======================
c1, c2, c3 = st.columns(3)

c1.metric("🧑 내 점수", my_score)
c2.metric("🏆 최고점", max_score, f"{diff_max:+.1f}")
c3.metric("📊 상위 30% 점수", round(top_30_score, 1), f"{diff_top30:+.1f}")

# ======================
# 6. 점수 분포 그래프
# ======================
fig_dist = px.histogram(
    round_df,
    x="점수",
    nbins=20,
    title=f"{selected_round}회차 점수 분포",
)

fig_dist.add_vline(
    x=my_score,
    line_dash="dash",
    annotation_text="내 점수",
)

st.plotly_chart(fig_dist, use_container_width=True)

# ======================
# 7. 회차별 점수 추이
# ======================
trend_df = df.groupby("회차")["점수"].mean().reset_index()

fig_trend = px.line(
    trend_df,
    x="회차",
    y="점수",
    markers=True,
    title="📈 회차별 평균 점수 추이"
)

st.plotly_chart(fig_trend, use_container_width=True)
