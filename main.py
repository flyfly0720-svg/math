# -*- coding: utf-8 -*-
"""
사회적 약자(취약계층) 통계 대시보드
- 통계청(국가데이터처)·보건복지부 발표 자료를 기반으로 한 예시 데이터가 내장되어 있습니다.
- 실행: streamlit run social_vulnerable_dashboard.py
- 필요 패키지: streamlit, pandas, plotly  (requirements.txt 참고)

※ 데이터 출처 표기
  - 등록장애인 현황: 보건복지부「등록장애인현황」, KOSIS
  - 고령인구/1인가구: 국가데이터처(통계청)「장래인구추계」,「인구주택총조사」,「2025 통계로 보는 1인가구」
  - 기초생활수급자: 보건복지부「국민기초생활보장 수급자 현황」, e-나라지표
  - 차상위계층/한부모가족/미혼모 등은 최신 확정치를 KOSIS에서 직접 조회해 CSV로 교체하는 것을 권장합니다.
    (아래 "데이터 갱신 방법" 섹션 참고 — KOSIS OpenAPI 연동 코드 포함)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------------
st.set_page_config(
    page_title="사회적 약자 통계 대시보드",
    page_icon="📊",
    layout="wide",
)

st.title("📊 사회적 약자(취약계층) 통계 대시보드")
st.caption("통계청(국가데이터처) · 보건복지부 발표 자료 기반 | 세특·발표 자료용 예시 대시보드")

# ------------------------------------------------------------------
# 1. 데이터 정의 (실제 발표 수치 반영, 일부는 추세 예시값)
# ------------------------------------------------------------------

# 1) 등록장애인 현황 (보건복지부, 각 연도 말 기준)
df_disability = pd.DataFrame({
    "연도": [2019, 2020, 2021, 2022, 2023, 2024],
    "등록장애인수(명)": [2_618_918, 2_633_026, 2_644_700, 2_652_860, 2_633_262, 2_631_356],
    "전체인구대비비율(%)": [5.1, 5.1, 5.1, 5.2, 5.1, 5.1],
})
DISABILITY_NOTE = (
    "2024년 말 기준 등록장애인은 263만 1,356명(전체 인구의 5.1%)이며, "
    "이 중 65세 이상이 55.3%(145만 5,782명)로 고령화가 뚜렷합니다. "
    "장애유형별 비중은 지체장애 43.0%, 청각장애 16.8%, 시각장애 9.4% 순입니다. "
    "(출처: 보건복지부 「2024년도 등록장애인 현황 통계」)"
)
df_disability_type = pd.DataFrame({
    "장애유형": ["지체장애", "청각장애", "시각장애", "뇌병변장애", "지적장애", "기타"],
    "비중(%)": [43.0, 16.8, 9.4, 8.9, 8.9, 13.0],
})

# 2) 고령인구(65세 이상) 비율 추이
df_elderly = pd.DataFrame({
    "연도": [2020, 2021, 2022, 2023, 2024, 2025],
    "고령인구비율(%)": [15.7, 16.5, 17.4, 18.2, 19.2, 20.0],
})
ELDERLY_NOTE = (
    "2024년 65세 이상 고령인구는 약 993만 8천 명으로 전체 인구의 19.2%이며, "
    "2025년 20%를 넘어 초고령사회에 진입할 것으로 전망됩니다. "
    "여성 고령인구 비중(21.5%)이 남성(17.0%)보다 높습니다. "
    "(출처: 국가데이터처 「2024 고령자통계」)"
)

# 3) 1인가구 비율 추이
df_single = pd.DataFrame({
    "연도": [2019, 2020, 2021, 2022, 2023, 2024],
    "1인가구수(만가구)": [614.8, 664.3, 716.6, 750.2, 782.9, 804.5],
    "1인가구비중(%)": [30.2, 31.7, 33.4, 34.5, 35.5, 36.1],
})
SINGLE_NOTE = (
    "2024년 1인가구는 804만 5천 가구로 처음 800만 가구를 돌파했으며, "
    "전체 가구의 36.1%로 관련 통계 작성(2015년) 이래 최고치를 매년 경신 중입니다. "
    "70세 이상 비중(19.8%)이 20대(17.8%)를 앞질러 가장 큰 비중을 차지합니다. "
    "(출처: 국가데이터처 「2025 통계로 보는 1인가구」)"
)

# 4) 기초생활수급자(저소득층) 추이
df_livelihood = pd.DataFrame({
    "연도": [2018, 2019, 2020, 2021, 2022, 2023],
    "수급자수(만명)": [174, 188, 213, 236, 245, 255],
    "수급가구수(만가구)": [116.5, 128.2, 145.9, 163.8, 169.9, 178.8],
})
LIVELIHOOD_NOTE = (
    "부양의무자 기준 완화 등 제도 개선으로 기초생활수급자 수가 지속 증가해, "
    "2023년 기준 약 255만 명(178만 8천 가구)입니다. "
    "가구 유형 중 노인·모자(한부모)·장애인 가구 비중이 계속 늘고 있습니다. "
    "(출처: 보건복지부, e-나라지표 「국민기초생활보장 수급 현황」)"
)

# 5) 차상위계층 (예시 추정치 — 반드시 KOSIS 최신값으로 교체 권장)
df_near_poverty = pd.DataFrame({
    "연도": [2019, 2020, 2021, 2022, 2023],
    "차상위계층수(만명)": [43, 45, 47, 48, 46],
})
NEAR_POVERTY_NOTE = (
    "⚠️ 차상위계층 수치는 예시(추정) 데이터입니다. "
    "정확한 값은 KOSIS '차상위계층 현황' 또는 보건복지부 사회보장정보시스템 자료로 교체하세요."
)

# 6) 한부모가족 (예시 추정치 — 여성가족부/통계청 자료로 교체 권장)
df_single_parent = pd.DataFrame({
    "연도": [2019, 2020, 2021, 2022, 2023],
    "한부모가구수(만가구)": [153, 152, 150, 149, 147],
    "미혼모가구비중(%)": [15.4, 16.0, 16.8, 17.2, 17.5],
})
SINGLE_PARENT_NOTE = (
    "⚠️ 한부모가족/미혼모 수치는 예시(추정) 데이터입니다. "
    "정확한 값은 여성가족부 '한부모가족 실태조사' 또는 KOSIS 인구총조사(가족유형별 가구)로 교체하세요."
)

CATEGORY_INFO = {
    "장애인": {
        "df": df_disability, "note": DISABILITY_NOTE,
        "x": "연도", "y": "등록장애인수(명)", "y2": "전체인구대비비율(%)",
        "unit": "명",
    },
    "고령인구": {
        "df": df_elderly, "note": ELDERLY_NOTE,
        "x": "연도", "y": "고령인구비율(%)", "y2": None,
        "unit": "%",
    },
    "1인가구": {
        "df": df_single, "note": SINGLE_NOTE,
        "x": "연도", "y": "1인가구수(만가구)", "y2": "1인가구비중(%)",
        "unit": "만가구",
    },
    "저소득층(기초생활수급자)": {
        "df": df_livelihood, "note": LIVELIHOOD_NOTE,
        "x": "연도", "y": "수급자수(만명)", "y2": "수급가구수(만가구)",
        "unit": "만명",
    },
    "차상위계층": {
        "df": df_near_poverty, "note": NEAR_POVERTY_NOTE,
        "x": "연도", "y": "차상위계층수(만명)", "y2": None,
        "unit": "만명",
    },
    "한부모가족·미혼모": {
        "df": df_single_parent, "note": SINGLE_PARENT_NOTE,
        "x": "연도", "y": "한부모가구수(만가구)", "y2": "미혼모가구비중(%)",
        "unit": "만가구",
    },
}

# ------------------------------------------------------------------
# 2. 사이드바 - 표시할 영역 선택
# ------------------------------------------------------------------
st.sidebar.header("🔍 조회 옵션")
selected_categories = st.sidebar.multiselect(
    "표시할 영역을 선택하세요",
    options=list(CATEGORY_INFO.keys()),
    default=list(CATEGORY_INFO.keys()),
)
chart_type = st.sidebar.radio("그래프 종류", ["막대그래프", "선그래프"], index=1)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**데이터 출처**\n\n"
    "- 보건복지부 「등록장애인현황」\n"
    "- 국가데이터처 「고령자통계」, 「인구주택총조사」\n"
    "- 국가데이터처 「통계로 보는 1인가구」\n"
    "- 보건복지부·e-나라지표 「국민기초생활보장 수급 현황」\n\n"
    "⚠️ 차상위계층/한부모가족 항목은 예시값이니 KOSIS 최신 자료로 교체하세요."
)

# ------------------------------------------------------------------
# 3. 요약 대시보드 (핵심 지표 카드)
# ------------------------------------------------------------------
st.subheader("🧾 핵심 지표 요약 (최신 연도 기준)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("등록장애인수 (2024)", "263.1만 명", "인구 대비 5.1%")
c2.metric("65세 이상 고령인구 (2024)", "993.8만 명", "19.2%  (+1.0%p)")
c3.metric("1인가구 비중 (2024)", "36.1%", "804.5만 가구")
c4.metric("기초생활수급자 (2023)", "255만 명", "+10만 명")

st.markdown("---")

# ------------------------------------------------------------------
# 4. 영역별 표 + 그래프
# ------------------------------------------------------------------
for cat in selected_categories:
    info = CATEGORY_INFO[cat]
    df = info["df"]
    x_col, y_col, y2_col = info["x"], info["y"], info["y2"]

    st.subheader(f"📌 {cat}")
    st.info(info["note"])

    col_table, col_chart = st.columns([1, 1.4])

    with col_table:
        st.markdown("**📋 데이터 표**")
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="CSV 다운로드",
            data=csv,
            file_name=f"{cat}_통계.csv",
            mime="text/csv",
            key=f"dl_{cat}",
        )

    with col_chart:
        st.markdown("**📈 그래프**")
        if chart_type == "선그래프":
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df[x_col], y=df[y_col], mode="lines+markers",
                name=y_col, line=dict(width=3),
            ))
            if y2_col:
                fig.add_trace(go.Scatter(
                    x=df[x_col], y=df[y2_col], mode="lines+markers",
                    name=y2_col, yaxis="y2", line=dict(dash="dot"),
                ))
                fig.update_layout(
                    yaxis2=dict(title=y2_col, overlaying="y", side="right")
                )
            fig.update_layout(
                xaxis_title=x_col, yaxis_title=y_col,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                margin=dict(t=40, b=20, l=20, r=20),
                height=380,
            )
        else:
            fig = px.bar(df, x=x_col, y=y_col, text_auto=".2s")
            fig.update_layout(
                margin=dict(t=40, b=20, l=20, r=20), height=380
            )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

# 장애유형 세부 그래프 (장애인 카테고리 선택 시 추가로 표시)
if "장애인" in selected_categories:
    st.subheader("📌 장애유형별 비중 (2024년 기준)")
    fig_pie = px.pie(
        df_disability_type, names="장애유형", values="비중(%)", hole=0.4
    )
    fig_pie.update_layout(height=420)
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("---")

# ------------------------------------------------------------------
# 5. 전체 비교(정규화) 그래프 - 여러 영역을 한 눈에
# ------------------------------------------------------------------
st.subheader("🔗 영역별 최신 비율/비중 비교")
compare_df = pd.DataFrame({
    "영역": ["등록장애인 비율", "고령인구 비율", "1인가구 비중",
             "기초생활수급률(추정)", "미혼모가구비중(예시)"],
    "비율(%)": [5.1, 19.2, 36.1, 4.9, 17.5],
})
fig_compare = px.bar(
    compare_df, x="영역", y="비율(%)", color="영역", text_auto=".1f",
)
fig_compare.update_layout(showlegend=False, height=420)
st.plotly_chart(fig_compare, use_container_width=True)

st.caption(
    "※ 기초생활수급률(추정) = 수급자 255만 명 ÷ 인구 약 5,175만 명. "
    "정확한 공식 수급률은 KOSIS 확인 필요."
)

# ------------------------------------------------------------------
# 6. 데이터 갱신 방법 (KOSIS OpenAPI 연동 가이드)
# ------------------------------------------------------------------
with st.expander("🔧 실제 KOSIS 데이터로 자동 갱신하는 방법 (선택 사항)"):
    st.markdown(
        """
현재 앱은 발표 자료 기반 **예시 데이터**로 구성되어 있습니다.
실시간·최신 데이터를 자동으로 가져오려면 KOSIS(국가통계포털) Open API를 사용할 수 있습니다.

**1단계.** [KOSIS Open API](https://kosis.kr/openapi) 에서 서비스 인증키(API KEY)를 발급받습니다.

**2단계.** 원하는 통계표의 `orgId`(기관코드)와 `tblId`(통계표ID)를 KOSIS 통계표 조회 화면 URL에서 확인합니다.

**3단계.** 아래와 같은 함수로 데이터를 받아와 데이터프레임으로 변환합니다.
        """
    )
    st.code(
        '''
import requests
import pandas as pd

def fetch_kosis(org_id, tbl_id, api_key,
                 start_prd="2019", end_prd="2024"):
    """KOSIS 통계자료 Open API 호출 예시"""
    url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
    params = {
        "method": "getList",
        "apiKey": api_key,
        "itmId": "ALL",
        "objL1": "ALL",
        "format": "json",
        "jsonVD": "Y",
        "prdSe": "Y",           # 연간 자료
        "startPrdDe": start_prd,
        "endPrdDe": end_prd,
        "orgId": org_id,
        "tblId": tbl_id,
    }
    res = requests.get(url, params=params, timeout=10)
    data = res.json()
    return pd.DataFrame(data)

# 사용 예 (등록장애인수 통계표라면 orgId, tblId를 KOSIS에서 확인 후 대입)
# df_live = fetch_kosis(org_id="117", tbl_id="DT_11761_N003", api_key="발급받은_API_KEY")
# st.dataframe(df_live)
'''
    , language="python")
    st.markdown(
        "이렇게 받아온 `df_live`를 위 코드의 `df_disability`, `df_elderly` 등과 "
        "동일한 컬럼 구조로 가공하면, 이 대시보드에 그대로 연결해 자동 갱신되는 앱으로 "
        "확장할 수 있습니다."
    )

st.markdown("---")
st.caption(
    "본 대시보드는 세특(세부능력 및 특기사항) 탐구·발표 자료 제작을 돕기 위한 예시입니다. "
    "인용 시 반드시 원자료 출처(보건복지부, 국가데이터처/통계청, KOSIS)를 함께 표기하세요."
)
