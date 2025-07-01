import streamlit as st
from openai import OpenAI # Updated import
from PIL import Image
import base64
import io

# OpenAI API 키 설정 (Streamlit Secrets에서 가져옴)
# Set OpenAI API key (retrieved from Streamlit Secrets)
# Initialize the OpenAI client
client = OpenAI(api_key=st.secrets["openai"]["api_key"])


st.set_page_config(page_title="Pika 영상 제작 GPT 도우미")
st.title("🎬 Pika 영상 제작 GPT 도우미")

# 사이드바에서 작업 선택
# Select task from sidebar
chat_option = st.sidebar.radio("작업을 선택하세요:", [
    "1. 이야기 점검하기",
    "2. 이야기 나누기",
    "3. 캐릭터/배경 이미지 생성",
    "4. 장면별 영상 프롬프트 점검"
])

# 공통 GPT 호출 함수
# Common GPT call function
def ask_gpt(messages, model="gpt-4o"):
    # Updated API call using the new client syntax
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content

# 이미지 생성 함수 (DALL·E 사용)
# Image generation function (using DALL·E)
def generate_image(prompt):
    # Updated API call using the new client syntax
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        response_format="b64_json"
    )
    # The response structure changed in v1.0.0
    image_data = base64.b64decode(response.data[0].b64_json)
    return Image.open(io.BytesIO(image_data))

# 1. 이야기 점검하기
# 1. Story Review
if chat_option.startswith("1"):
    st.header("1. 이야기 점검하기")
    st.markdown("💬 **목표:** 여러분의 이야기가 영상으로 만들기에 적절한지 GPT와 함께 점검하고 다듬어 보세요.")
    story = st.text_area("여러분이 창작한 이야기를 입력하세요.")
    if st.button("GPT에게 점검받기") and story:
        messages = [
            {"role": "system", "content": (
                "너는 초등학생이 창작한 이야기를 보고, Pika 영상으로 만들 수 있도록 점검해주는 GPT 도우미야.\n"
                "먼저 학생의 이야기를 읽고, 표현하고자 하는 의도가 명확한지 파악해.\n"
                "이해되지 않는 부분이 있다면 반드시 질문을 통해 명확화하도록 유도해.\n"
                "소크라테스식 질문으로 학생 스스로 표현을 다듬도록 도와줘.\n"
                "이야기의 길이(1~1분 30초), 구조(발단-전개-절정-결말), 어색한 문장은 부분 예시 중심으로 피드백하고,\n"
                "마지막에는 종합적인 보완 방향을 격려하는 말투로 안내해줘."
            )},
            {"role": "user", "content": story}
        ]
        with st.spinner("GPT가 이야기를 점검 중입니다..."):
            st.write(ask_gpt(messages))

# 2. 이야기 나누기
# 2. Story Segmentation
elif chat_option.startswith("2"):
    st.header("2. 이야기 나누기 (장면 분할)")
    st.markdown("✂️ **목표:** 긴 이야기를 10초 내외의 짧은 영상 장면으로 나누고, 각 장면의 핵심 요소를 명확히 해보세요.")

    if "scenes" not in st.session_state:
        st.session_state.scenes = {}
    if "scene_count" not in st.session_state:
        st.session_state.scene_count = 1

    # 장면 입력 필드
    # Scene input fields
    for i in range(1, st.session_state.scene_count + 1):
        st.session_state.scenes[f"part_{i}"] = st.text_area(
            f"장면 {i} 입력",
            value=st.session_state.scenes.get(f"part_{i}", ""),
            key=f"part_{i}"
        )
        if st.session_state.scenes[f"part_{i}"]:
            messages = [
                {"role": "system", "content": (
                    "너는 학생의 이야기를 10초 내외로 나눠서 Pika 영상 장면으로 구성하도록 돕는 조력자야.\n"
                    "각 장면에서 시간, 장소, 등장인물, 사건을 파악하고, 이전 장면과 구분되는 요소인지 질문을 통해 확인해.\n"
                    "이미 입력된 정보는 묻지 않고, 누락된 정보만 자연스럽게 질문해줘.\n"
                    "필요하다면 이 장면을 나누거나 앞 장면과 합치는 것이 더 자연스러운지도 알려줘."
                )},
                {"role": "user", "content": st.session_state.scenes[f"part_{i}"]}
            ]
            st.markdown(f"**GPT 피드백 (장면 {i})**")
            with st.spinner(f"GPT가 장면 {i}를 점검 중입니다..."):
                st.write(ask_gpt(messages))
        st.markdown("---") # 각 장면 구분을 위한 시각적 구분자
                             # Visual separator for each scene

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.scene_count < 9: # 최대 9개 장면 제한
                                             # Maximum 9 scenes limit
            if st.button("새 장면 추가"):
                st.session_state.scene_count += 1
                st.experimental_rerun()
    with col2:
        if st.button("모든 장면 입력 완료 및 최종 피드백 받기"):
            all_scenes_content = "\n".join([
                f"장면 {i}: {st.session_state.scenes[f'part_{i}']}"
                for i in range(1, st.session_state.scene_count + 1)
                if st.session_state.scenes.get(f'part_{i}')
            ])

            if all_scenes_content.strip(): # 공백만 있는 경우를 방지
                                          # Prevent case where only whitespace exists
                final_feedback_messages = [
                    {"role": "system", "content": (
                        "너는 초등학생이 나눈 이야기 장면들의 전체적인 흐름을 검토하고 최종적인 피드백을 제공하는 GPT 도우미야.\n"
                        "학생이 입력한 전체 장면들을 보고, 이야기의 흐름이 자연스러운지, 빠지거나 중복되는 부분은 없는지 확인해줘.\n"
                        "각 장면이 Pika를 사용한 10초 내외의 영상으로 구성하기에 적절한지, 전체적으로 1분~1분 30초 분량의 영상이 나올 수 있을지 조언해줘.\n"
                        "필요하다면 장면의 순서 조정이나 통합, 재분할에 대한 조언을 격려하는 말투로 제시해줘."
                    )},
                    {"role": "user", "content": f"학생이 나눈 전체 이야기는 다음과 같습니다:\n\n{all_scenes_content}\n\n이 전체 이야기에 대해 최종적으로 점검하고 피드백을 부탁드립니다."}
                ]
                st.subheader("💡 최종 이야기 흐름 점검 GPT 피드백")
                with st.spinner("GPT가 전체 이야기를 점검 중입니다..."):
                    st.write(ask_gpt(final_feedback_messages))
            else:
                st.warning("먼저 하나 이상의 장면을 입력해주세요.")

# 3. 이미지 생성
# 3. Image Generation
elif chat_option.startswith("3"):
    st.header("3. 캐릭터/배경 이미지 프롬프트 구성 및 생성")
    st.markdown("🎨 **목표:** Pika 영상에 사용할 캐릭터나 배경의 대표 이미지를 만들 프롬프트를 GPT와 함께 구체화하고 직접 이미지를 생성해 보세요.")
    st.markdown("**💡 팁:** Pika 영상에 쓰일 대표 이미지이므로, **캐릭터는 꼭 배경 없이 전신**으로, **단순하고 명확하게** 묘사하는 것이 좋아요!")

    if "image_history" not in st.session_state:
        st.session_state.image_history = []
        st.session_state.current_prompt = ""

    concept = st.text_area("만들고 싶은 캐릭터나 배경을 설명해주세요 (예: 숲 속을 탐험하는 용감한 소년)")
    if st.button("GPT에게 프롬프트 구성 요청") and concept:
        system_prompt = (
            "너는 학생의 상상을 바탕으로 Pika 영상에 사용할 캐릭터나 배경 이미지를 만들기 위한 프롬프트를 구성해주는 GPT야.\n"
            "이 이미지는 Pika에서 영상을 생성할 때 사용할 대표 이미지임을 인지하고, 과도한 묘사 없이 핵심 특징을 잘 나타내도록 도와줘.\n"
            "입력된 설명에 포함되지 않은 정보(대상 구분(캐릭터/배경), 스타일(예: 스누피 펜화, 디즈니풍), 외형, 표정, 자세 등)를 질문해서 보완해줘.\n"
            "특히, **캐릭터 이미지는 반드시 배경 없이 전체 몸이 보이도록** 해야 하고, 다양한 구도보다는 캐릭터의 특징을 잘 보여주는 하나의 명확한 이미지를 목표로 해.\n"
            "충분한 정보가 수집되면, 마지막에 '완성된 이미지 프롬프트는 다음과 같아요:' 형식으로 프롬프트를 보여주고,\n"
            "그 프롬프트로 이미지를 생성해서 보여줘."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": concept}
        ]
        with st.spinner("GPT가 프롬프트를 구성 중입니다..."):
            gpt_response = ask_gpt(messages)
        st.write(gpt_response)

        if "완성된 이미지 프롬프트는 다음과 같아요:" in gpt_response:
            prompt_line = gpt_response.split("완성된 이미지 프롬프트는 다음과 같아요:")[-1].strip()
            # 프롬프트 앞뒤의 따옴표나 공백 제거
            # Remove quotes or spaces from the beginning/end of the prompt
            prompt = prompt_line.strip("'").strip("\"")
            st.session_state.current_prompt = prompt
            with st.spinner("이미지를 생성 중입니다..."):
                image = generate_image(prompt)
            st.session_state.image_history = [(prompt, image)]

    # 이미지 피드백 루프
    # Image feedback loop
    if st.session_state.image_history:
        prompt, image = st.session_state.image_history[-1]
        st.image(image, caption="생성된 이미지", use_column_width=True)

        buf = io.BytesIO()
        image.save(buf, format="PNG")
        st.download_button(
            label="이미지 다운로드",
            data=buf.getvalue(),
            file_name="generated_image.png",
            mime="image/png"
        )

        st.subheader("이미지 확인 및 수정")
        feedback = st.radio("이 이미지가 마음에 드시나요?", ["네, 다음 그림으로 넘어가기", "아니요, 수정하고 싶어요"], key="img_feedback")

        if feedback == "아니요, 수정하고 싶어요":
            revise = st.text_input("어떤 부분을 수정하고 싶나요? (예: 모자 색깔을 빨간색으로, 표정을 더 밝게)", key="img_revise")
            if st.button("수정된 이미지 생성") and revise:
                # Pika 특성을 고려하여, 수정 사항을 기존 프롬프트에 단순하게 추가
                # Considering Pika's characteristics, simply add revisions to the existing prompt
                revised_prompt = f"{st.session_state.current_prompt}, 단 {revise}"
                with st.spinner("수정된 이미지 생성 중입니다..."):
                    revised_image = generate_image(revised_prompt)
                    st.session_state.image_history.append((revised_prompt, revised_image))
                    st.experimental_rerun() # 수정된 이미지 바로 표시
                                            # Display revised image immediately
        elif feedback == "네, 다음 그림으로 넘어가기":
            st.success("다음 캐릭터 또는 배경 입력 단계로 넘어갈 준비가 되었습니다.")
            # 다음 이미지 생성을 위해 상태 초기화 (선택 사항, 필요에 따라 유지 가능)
            # Reset state for next image generation (optional, can be maintained if needed)
            # st.session_state.image_history = []
            # st.session_state.current_prompt = ""


# 4. 장면별 영상 프롬프트 점검
# 4. Scene-by-Scene Video Prompt Review
elif chat_option.startswith("4"):
    st.header("4. 장면별 영상 프롬프트 점검")
    st.markdown("🎥 **목표:** 각 장면을 Pika 영상으로 만들기 위한 프롬프트를 GPT와 함께 최종 점검하고 간결하게 완성해 보세요.")
    st.markdown("**💡 팁:** Pika는 복잡한 프롬프트보다 **짧고 핵심적인 문장**에 더 잘 반응해요! 동작, 감정, 구도에 집중하세요.")

    scene = st.text_area("영상으로 만들 장면 설명을 입력하세요 (예: 토끼가 숲 속을 뛰어다니며 당근을 발견한다.)")
    if st.button("GPT에게 프롬프트 점검 요청") and scene:
        messages = [
            {"role": "system", "content": (
                "너는 학생이 입력한 장면 설명을 바탕으로 Pika에서 사용할 10초 분량 영상 프롬프트가 적절한지 검토하는 GPT야.\n"
                "Pika의 프롬프트 해석 특성상, **짧고 간결하며 명확한 1~2문장**의 프롬프트가 중요해. 과도한 문장 길이, 서술적인 묘사는 피해야 해.\n"
                "캐릭터와 배경 이미지는 따로 생성하므로, 이 창에서는 장면의 **동작, 감정, 구도(전체 몸, 시점), 강조하고 싶은 요소** 중심으로 질문하고 보완해.\n"
                "질문은 필요한 경우에만 하고, 정보가 충분하면 간결한 1~2문장 형태로 최종 프롬프트를 출력해줘. 이때, 불필요한 서두는 제외하고 프롬프트만 명확히 제시해야 해."
            )},
            {"role": "user", "content": scene}
        ]
        with st.spinner("GPT가 영상 프롬프트를 점검 중입니다..."):
            st.write(ask_gpt(messages))
