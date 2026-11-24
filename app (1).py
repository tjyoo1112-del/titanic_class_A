
# ===== 라이브러리 불러오기 =====
import streamlit as st
import pandas as pd
import plotly.express as px

# ===== 페이지 설정 =====
st.set_page_config(
    page_title="Titanic 대시보드",
    layout="wide"
)


# ===== 데이터 불러오기 =====
@st.cache_data
def load_data():
    # CSV 파일을 한 번 읽어서 저장
    return pd.read_csv("titanic.csv")

df = load_data()


# ===== 데이터 필터링 함수 =====
def filter_data(df, sexes, classes, age_range):

    # 성별, 객실 등급 조건을 만족하는 승객 선택
    filtered = df[
        (df["sex"].isin(sexes)) &
        (df["pclass"].isin(classes))
    ]

    # [수정] 나이 범위가 전체 범위이면 결측 나이도 포함
    if age_range == (0, 80):
        filtered = filtered[
            filtered["age"].isna() |
            (
                (filtered["age"] >= age_range[0]) &
                (filtered["age"] <= age_range[1])
            )
        ]
    else:
        # [수정] 전체 범위가 아니면 선택한 나이 범위만 적용
        filtered = filtered[
            (filtered["age"] >= age_range[0]) &
            (filtered["age"] <= age_range[1])
        ]

    return filtered


# ===== KPI 계산 함수 =====
def kpi(df):
    # 데이터가 비어 있으면 0 반환
    if df.empty:
        return (0, 0, 0)

    # 승객 수 계산
    passengers = len(df)

    # 생존율 계산 및 소수 첫째 자리 반올림
    survival_rate = round(df["survived"].mean() * 100, 1)

    # 평균 나이 계산 및 소수 첫째 자리 반올림
    avg_age = round(df["age"].mean(), 1)

    # KPI 3개 반환
    return (passengers, survival_rate, avg_age)


# ===== 객실 등급별 생존율 그래프 함수 =====
def class_rate_bar(df):
    # 객실 등급별 생존율 계산
    rate = df.groupby("pclass")["survived"].mean().reset_index()
    rate["survived"] = rate["survived"] * 100

    # 막대그래프 생성
    fig = px.bar(
        rate,
        x="pclass",
        y="survived",
        text="survived",
        title="객실 등급별 생존율",
        labels={
            "pclass": "객실 등급",
            "survived": "생존율(%)"
        }
    )

    # 막대 위에 생존율 표시
    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    return fig


# ===== 나이 히스토그램 함수 =====
def age_hist(df):
    # 생존 여부에 따라 색상을 구분한 히스토그램 생성
    fig = px.histogram(
        df,
        x="age",
        color="survived",
        barmode="overlay",
        opacity=0.6,
        title="생존 여부별 승객 나이 분포",
        labels={
            "age": "나이",
            "survived": "생존 여부"
        }
    )

    return fig


# ===== 대시보드 제목 =====
st.title("타이타닉, 누가살아남았나?")


# ===== 사이드바 필터 =====
st.sidebar.header("승객 조건 선택")

# 성별 선택
sexes = st.sidebar.multiselect(
    "성별",
    options=["male", "female"],
    default=["male", "female"]
)

# 객실 등급 선택
classes = st.sidebar.multiselect(
    "객실 등급",
    options=[1, 2, 3],
    default=[1, 2, 3]
)

# 나이 범위 선택
age_range = st.sidebar.slider(
    "나이 범위",
    min_value=0,
    max_value=80,
    value=(0, 80)
)


# ===== 필터 선택 여부 확인 [수정] =====
if not sexes:
    st.warning("성별을 하나 이상 선택해주세요.")
    st.stop()

if not classes:
    st.warning("객실 등급을 하나 이상 선택해주세요.")
    st.stop()


# ===== 데이터 필터링 =====
filtered_df = filter_data(
    df,
    sexes,
    classes,
    age_range
)


# ===== 필터 결과 확인 [수정] =====
if filtered_df.empty:
    st.warning("조건에 맞는 승객이 없습니다.")
    st.stop()


# ===== KPI 숫자카드 =====
passengers, survival_rate, avg_age = kpi(filtered_df)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("승객수(명)", passengers)

with col2:
    st.metric("생존율(%)", survival_rate)

with col3:
    st.metric("평균나이(세)", avg_age)


# ===== 차트 2개 표시 =====
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.plotly_chart(
        class_rate_bar(filtered_df),
        use_container_width=True
    )

with chart_col2:
    st.plotly_chart(
        age_hist(filtered_df),
        use_container_width=True
    )


# ===== 데이터 보기 =====
with st.expander("데이터보기"):
    st.dataframe(filtered_df, use_container_width=True)
