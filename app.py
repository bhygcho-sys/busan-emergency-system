
import streamlit as st
import pandas as pd

# --------------------------------
# 1. 앱 기본 설정
# --------------------------------

st.set_page_config(
    page_title="부산 응급의료 자원 최적화",
    page_icon="🚑",
    layout="wide"
)

# --------------------------------
# 2. 제목
# --------------------------------

st.title("🚑 부산 응급의료 자원 최적화 시스템")

st.write(
    "응급환자 발생 위치와 필요한 의료 조건을 바탕으로 "
    "부산 병원들의 적합도를 분석합니다."
)

st.warning(
    "교육용 시뮬레이션입니다. 실제 응급환자 이송이나 "
    "병원 선택에 사용하지 마세요. 현재 병원 정보와 "
    "이동시간, 의료자원 수치는 가상 데이터입니다."
)

st.divider()

# --------------------------------
# 3. 병원 데이터
# --------------------------------

hospitals = [
    {
        "병원명": "부산대학교병원",
        "이동시간": 18,
        "병상여유도": 72,
        "의료진여유도": 68,
        "수용상태": "가능",
        "전문진료": ["외상", "심혈관", "뇌혈관"],
        "장비": ["CT", "MRI", "인공호흡기"]
    },
    {
        "병원명": "동아대학교병원",
        "이동시간": 20,
        "병상여유도": 62,
        "의료진여유도": 75,
        "수용상태": "가능",
        "전문진료": ["외상", "심혈관"],
        "장비": ["CT", "MRI", "인공호흡기"]
    },
    {
        "병원명": "고신대학교복음병원",
        "이동시간": 23,
        "병상여유도": 58,
        "의료진여유도": 63,
        "수용상태": "확인 필요",
        "전문진료": ["심혈관", "뇌혈관"],
        "장비": ["CT", "MRI"]
    },
    {
        "병원명": "인제대학교 부산백병원",
        "이동시간": 16,
        "병상여유도": 65,
        "의료진여유도": 70,
        "수용상태": "가능",
        "전문진료": ["외상", "뇌혈관"],
        "장비": ["CT", "MRI", "인공호흡기"]
    },
    {
        "병원명": "인제대학교 해운대백병원",
        "이동시간": 29,
        "병상여유도": 76,
        "의료진여유도": 82,
        "수용상태": "가능",
        "전문진료": ["외상", "심혈관"],
        "장비": ["CT", "MRI", "인공호흡기"]
    },
    {
        "병원명": "부산광역시의료원",
        "이동시간": 14,
        "병상여유도": 54,
        "의료진여유도": 57,
        "수용상태": "가능",
        "전문진료": ["외상"],
        "장비": ["CT", "인공호흡기"]
    }
]

# --------------------------------
# 4. 사용자 입력 화면
# --------------------------------

st.header("STEP 1. 응급환자 발생 위치")

start_location = st.text_input(
    "응급환자가 발생한 위치를 입력하세요.",
    value="서면역",
    placeholder="예: 서면역"
)

st.header("STEP 2. 필요한 의료 조건")

specialty = st.selectbox(
    "필요한 전문 진료를 선택하세요.",
    ["외상", "심혈관", "뇌혈관"]
)

equipment = st.selectbox(
    "필수 의료 장비를 선택하세요.",
    ["CT", "MRI", "인공호흡기"]
)

st.header("STEP 3. 이동수단")

transport = st.radio(
    "이동수단을 선택하세요.",
    ["자동차"],
    horizontal=True
)

st.divider()

# --------------------------------
# 5. 분석 버튼
# --------------------------------

if st.button(
    "적합 병원 분석하기",
    type="primary",
    use_container_width=True
):

    if start_location.strip() != "서면역":

        st.error(
            "현재 테스트 버전은 서면역 기준 데이터만 지원합니다."
        )

    else:

        candidates = []
        unconfirmed = []

        # 병원별 필수 조건 검사
        for hospital in hospitals:

            specialty_ok = (
                specialty in hospital["전문진료"]
            )

            equipment_ok = (
                equipment in hospital["장비"]
            )

            acceptance_ok = (
                hospital["수용상태"] == "가능"
            )

            if (
                specialty_ok
                and equipment_ok
                and acceptance_ok
            ):
                candidates.append(hospital)

            elif hospital["수용상태"] == "확인 필요":
                unconfirmed.append(hospital["병원명"])

        st.divider()
        st.header("📊 병원 분석 결과")

        st.write(
            f"출발 위치: {start_location} | "
            f"전문 진료: {specialty} | "
            f"필수 장비: {equipment} | "
            f"이동수단: {transport}"
        )

        # --------------------------------
        # 6. 적합도 점수 계산
        # --------------------------------

        if len(candidates) == 0:

            st.warning(
                "현재 선택한 조건을 모두 충족하는 "
                "가상 추천 후보가 없습니다."
            )

        else:

            df = pd.DataFrame(candidates)

            min_time = df["이동시간"].min()
            max_time = df["이동시간"].max()

            if min_time == max_time:
                df["이동점수"] = 100

            else:
                df["이동점수"] = (
                    (max_time - df["이동시간"])
                    / (max_time - min_time)
                    * 100
                )

            df["종합점수"] = (
                df["이동점수"] * 0.4
                + df["병상여유도"] * 0.3
                + df["의료진여유도"] * 0.3
            )

            df = df.sort_values(
                by="종합점수",
                ascending=False
            ).reset_index(drop=True)

            st.success(
                f"조건을 통과한 후보 병원: {len(df)}곳"
            )

            # --------------------------------
            # 7. 병원별 결과 출력
            # --------------------------------

            for i, row in df.iterrows():

                with st.container(border=True):

                    st.subheader(
                        f"{i + 1}위. {row['병원명']}"
                    )

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "가상 이동시간",
                        f"{row['이동시간']}분"
                    )

                    col2.metric(
                        "가상 병상 여유도",
                        f"{row['병상여유도']}/100"
                    )

                    col3.metric(
                        "가상 의료진 여유도",
                        f"{row['의료진여유도']}/100"
                    )

                    st.write(
                        f"전문 진료: {specialty} (가상 조건 충족)"
                    )

                    st.write(
                        f"필수 장비: {equipment} (가상 조건 충족)"
                    )

                    st.write(
                        f"종합 점수: {row['종합점수']:.1f}점"
                    )

            # --------------------------------
            # 8. 그래프 출력
            # --------------------------------

            st.subheader("병원별 종합 점수 비교")

            chart = df.set_index("병원명")[["종합점수"]]

            st.bar_chart(chart)

            # --------------------------------
            # 9. 결과 파일 다운로드
            # --------------------------------

            csv = df.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                "분석 결과 다운로드",
                data=csv,
                file_name="병원_분석결과.csv",
                mime="text/csv"
            )

        # --------------------------------
        # 10. 확인이 필요한 병원
        # --------------------------------

        if unconfirmed:

            st.subheader("별도 확인이 필요한 병원")

            for name in unconfirmed:
                st.write("•", name)

            st.caption(
                "수용 상태가 확인되지 않은 병원은 "
                "추천 순위에서 제외했습니다."
            )

# --------------------------------
# 11. 앱 하단 안내
# --------------------------------

st.divider()

st.caption(
    "본 앱은 고등학생의 정보·생명과학 융합 탐구를 위한 "
    "교육용 시뮬레이션이며 실제 의료정보가 아닙니다."
)
