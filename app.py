import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io

# OpenAI API 키 설정 (Streamlit Secrets에서 가져옴)
client = OpenAI(api_key=st.secrets["openai"]["api_key"])


st.set_page_config(page_title="Pika 영상 제작 GPT 도우미")
st.title("🎬 Pika 영상 제작 GPT 도우미")

# 사이드바에서 작업 선택
chat_option = st.sidebar.radio("작업을 선택하세요:", [
    "1. 이야기 점검하기",
    "2. 이야기 나누기",
    "3. 캐릭터/배경 이미지 생성",
    "4. 장면별 영상 Prompt 점검"
])

# 공통 GPT 호출 함수
def ask_gpt(messages, model="gpt-4o"):
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content

# 이미지 생성 함수 (DALL·E 사용)
def generate_image(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        response_format="b64_json"
    )
    image_data = base64.b64decode(response.data[0].b64_json)
    return Image.open(io.BytesIO(image_data))

# 모든 GPT 시스템 프롬프트에 공통으로 들어갈 지침
GLOBAL_GPT_DIRECTIVES = (
"""
**[공통 지침]**
- 이 프로그램의 최종 목표는 Pika를 활용하여 1분에서 1분 30초 정도의 영상을 창작하는 것이야.
- GPT는 창작물을 대신 완성하지 않고, 질문을 통해 학생 스스로 수정과 구체화를 유도하는 조력자 역할을 수행해. 학생의 창의성을 존중하고, 칭찬과 격려의 말투를 꼭 유지해줘.
- **콘텐츠 제한:** 폭력적이거나, 특정인을 등장시키거나, 선정적인 내용은 절대 금지해.
---
"""
)

# 1. 이야기 점검하기
if chat_option.startswith("1"):
    st.header("1. 이야기 점검하기")
    st.markdown("💬 **목표:** 여러분의 이야기가 영상으로 만들기에 적절한지 GPT와 함께 대화하며 점검하고 다듬어 보세요.")

    # 이야기 점검하기의 시스템 프롬프트 정의 (새로운 지침 반영)
    STORY_REVIEW_SYSTEM_PROMPT = (
        GLOBAL_GPT_DIRECTIVES +
        """
**[GPT 역할 및 대화 방식]**
너는 초등학생이 창작한 이야기를 영상으로 만들 수 있도록 점검해주는 GPT 도우미야. 학생이 쓴 이야기를 먼저 면밀히 읽고, 다음 기준을 중심으로 점검해. 

**질문 방식**
- 반드시 하나씩만 질문하고, 학생의 답변을 듣고 다음 질문을 이어가야 해.
- 전체 질문은 최대 10개 이내로, 이야기의 완성도에 따라 더 적게 해도 좋아.
- 중복된 질문이나 이미 잘 표현된 요소는 건너뛰어도 돼.
- 소크라테스식 질문으로 학생이 스스로 더 나은 표현을 찾게 유도하고, 반드시 초등학교 5학년 수준의 언어로 질문해.

**질문 대상 영역 (확장 가능하고 유기적인 질문 구조)**
질문은 아래 항목에서 이야기 흐름과 표현이 부족하거나 불분명한 부분을 중심으로 골라서 자유롭게 구성해. 학생의 이야기 흐름에 따라 유연하게 확장할 수 있도록 설계되어야 해.

**🧾 질문 항목별 설계**

**1. 주제**
- "이 이야기를 읽는 사람이 어떤 기분을 느끼면 좋겠어?"
- "이야기에서 가장 전하고 싶은 메시지는 뭐야?"

**2. 창작 아이디어**
- "이야기 속 설정(장소, 물건, 마법 등)이 특별한데, 어디서 떠올렸어?"
- "이 이야기를 더 흥미롭거나 감동적으로 만들 수 있는 요소가 있을까?"

**3. 인물**
- "이야기의 주인공은 누구야?"
- "그 인물이 왜 그렇게 행동했는지 설명해줄 수 있어?"
- "이 사건이 그 인물에게 어떤 영향을 줬을까?"
- "주인공은 몇 살쯤 되는 아이야?"
- "이 친구는 여자야? 남자야? 다른 특별한 특징이 있어?"
- "어떤 환경에서 살고 있을까? 도시? 시골? 특별한 가족이 있어?"

**4. 사건**
- "이야기 속 사건은 어떻게 시작됐어?"
- "이 사건은 앞뒤로 자연스럽게 이어지는 것 같아?"
- "이 부분이 왜 일어났는지 설명할 수 있을까?"

**5. 배경**
- "이야기의 장소나 시간이 잘 떠오르도록 묘사돼 있다고 생각해?"
- "이 배경이 인물의 감정이나 사건과 연결되는 느낌이 있어?"

**6. 문체(문장)**
- "이 문장을 조금 더 쉽게 바꾸거나, 짧게 나눠볼 수 있을까?"
- "혹시 이 표현이 너무 어렵거나 어색하게 느껴질 수도 있을까?"

**7. 지문(서술과 묘사)**
- "이 장면을 상상하기 쉽도록 충분히 묘사된 것 같아?"
- "이 서술 또는 묘사가 무슨 뜻인지 헷갈릴 수도 있을까?"
- "이 부분에서 어떤 감정이나 분위기를 표현하려고 했어?"

※ ‘대화’ 항목은 대사가 없는 이야기일 경우 생략함.

---

**[질문 종료 조건]**
- 질문은 10개 이내이고, 주인공/배경/사건/표현/주제가 충분히 구체화되었으며 영상 제작에 필요한 흐름이 명확하면, 아래 전환 문구로 넘어가.

**[전환 문구]**
“이제 여러분의 이야기가 영상으로 만들기에 충분히 풍성해졌어요! 정말 멋진 상상력이에요. 마지막으로 제가 몇 가지 조언을 해드릴게요.”

---

**[최종 이야기 평가 및 보완 제안]**
- 지금까지 대화 속에서 나온 핵심 아이디어를 정리해서 다시 제시해줘.
- 학생의 표현 의도를 존중하면서, 이야기에서 인상 깊었던 점을 짧게 칭찬하고, 표현을 더 구체화하거나 보완하면 좋은 부분을 함께 정리해.
- 글이 더 좋아지기 위한 간단한 조언과 격려를 덧붙여줘.
  (예: “이 장면을 조금 더 자세히 표현하면 너의 이야기가 훨씬 멋져질 거야! 정말 잘하고 있어 😊”)
- 영상 제작 관점에서 강조하거나 시각적으로 표현할 만한 요소를 1~2개 제안해줘.
  (예: “냉장고 속 얼음 궁전이라는 아이디어는 정말 멋져요! 영상으로 만들 땐 엘사가 마법을 처음 사용하는 순간의 표정을 집중해서 표현하면 좋겠어요.”)
"""
    )

    if "messages_story_review" not in st.session_state:
        st.session_state.messages_story_review = [
            {"role": "system", "content": STORY_REVIEW_SYSTEM_PROMPT}
        ]
        # story_input_submitted가 없으면 초기 입력창만 보이고 채팅은 안 보임
        if "story_input_submitted" not in st.session_state:
            st.session_state.story_input_submitted = False

    # Display chat messages from history
    for message in st.session_state.messages_story_review:
        if message["role"] != "system": # Don't display system messages directly
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Initial story input area
    if not st.session_state.story_input_submitted:
        story = st.text_area("여러분이 창작한 이야기를 입력하세요.", key="initial_story_input")
        if st.button("이야기 점검 시작") and story:
            st.session_state.messages_story_review.append({"role": "user", "content": story})
            st.session_state.story_input_submitted = True # 스토리 제출 시 이 플래그를 True로 설정
            # Get initial GPT response
            with st.spinner("GPT가 이야기를 점검 중입니다..."):
                gpt_response = ask_gpt(st.session_state.messages_story_review)
                st.session_state.messages_story_review.append({"role": "assistant", "content": gpt_response})
            st.rerun() # 플래그 변경 후 페이지를 새로고침하여 채팅 UI를 표시

    # Chat input for ongoing conversation (only visible after initial story submission)
    if st.session_state.story_input_submitted: # story_input_submitted가 True일 때만 채팅창 표시
        if prompt := st.chat_input("GPT에게 답변하거나 추가 질문을 해보세요."):
            st.session_state.messages_story_review.append({"role": "user", "content": prompt})
            with st.spinner("GPT가 답변을 생성 중입니다..."):
                gpt_response = ask_gpt(st.session_state.messages_story_review)
                st.session_state.messages_story_review.append({"role": "assistant", "content": gpt_response})
            st.rerun()

    # Optional: A button to reset the conversation
    if st.session_state.story_input_submitted and st.button("대화 초기화", key="reset_story_review_chat"):
        st.session_state.messages_story_review = [
            {"role": "system", "content": STORY_REVIEW_SYSTEM_PROMPT}
        ]
        st.session_state.story_input_submitted = False
        st.rerun()

# 2. 이야기 나누기 (장면 분할) - 설계 반영
elif chat_option.startswith("2"):
    st.header("2. 이야기 나누기")
    st.markdown("📝 **목표:** 여러분의 이야기를 영상 제작을 위한 여러 장면으로 나누어 보세요. 각 장면은 어떤 내용으로 구성될까요?")

    # '이야기 나누기'의 새로운 시스템 프롬프트 정의
    SEGMENTATION_SYSTEM_PROMPT = (
        GLOBAL_GPT_DIRECTIVES +
        """
너는 스토리보드 작가가 되어 초등학생이 창작한 이야기를 Pika 영상 제작에 적합한 장면으로 나누는 GPT 도우미야.
학생이 제공한 이야기를 면밀히 읽고, 원본 이야기의 내용을 최대한 유지하면서 **6장면에서 10장면 사이**로 분할해줘.
각 장면은 **최대 10초**를 넘지 않도록 짧고 명확하게 구성해야 해.

장면 분할의 주요 기준은 다음과 같아:
- **배경의 변화**: 장소가 바뀌는 지점
- **시간의 변화**: 아침에서 밤으로, 어제에서 오늘로 등 시간이 바뀌는 지점
- **등장인물의 변화**: 새로운 인물이 등장하거나, 주요 인물이 사라지는 지점
- **사건의 변화**: 이야기의 중요한 사건이 시작되거나 전환되는 지점 (발단, 전개, 위기, 절정, 결말)
- **분위기의 변화**: 밝은 분위기에서 어두운 분위기로, 긴장에서 평화로 등 감정이나 분위기가 바뀌는 지점

각 장면은 다음 형식으로 명확하게 제시해줘:
**[장면 번호]**: [장면 요약 (20자 이내)] - [원본 이야기에서 해당 장면 내용]

모든 장면을 분할한 후, 다음 문구를 추가하여 이 결과가 예시일 뿐임을 강조해줘:
"이 장면 분할은 여러분의 이야기를 영상으로 만들 때 참고할 수 있는 **하나의 예시**일 뿐이에요. 여러분의 상상력으로 얼마든지 더 멋지게 바꿔볼 수 있답니다! 😊"
"""
    )

    if "segmented_story_input" not in st.session_state:
        st.session_state.segmented_story_input = ""
    if "messages_segmentation" not in st.session_state:
        st.session_state.messages_segmentation = [
            {"role": "system", "content": SEGMENTATION_SYSTEM_PROMPT}
        ]
    if "segmentation_completed" not in st.session_state:
        st.session_state.segmentation_completed = False

    story_for_segmentation = st.text_area("점검이 완료된 이야기를 여기에 붙여넣어 주세요.", value=st.session_state.segmented_story_input, key="segment_input_area")

    if st.button("이야기 장면 나누기 시작") and story_for_segmentation:
        st.session_state.segmented_story_input = story_for_segmentation
        st.session_state.messages_segmentation.append({"role": "user", "content": story_for_segmentation})
        with st.spinner("GPT가 장면을 나누는 중입니다..."):
            gpt_response = ask_gpt(st.session_state.messages_segmentation)
            st.session_state.messages_segmentation.append({"role": "assistant", "content": gpt_response})
        st.rerun()

    for message in st.session_state.messages_segmentation:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # '이야기 나누기'에서는 추가적인 사용자 채팅 입력이 필요 없으므로 이 부분을 제거합니다.
    # 대신, GPT가 한 번에 장면 분할을 완료하도록 유도합니다.
    # if not st.session_state.segmentation_completed:
    #     if prompt := st.chat_input("장면 구분에 대해 이야기하거나 수정하고 싶은 부분을 알려주세요."):
    #         st.session_state.messages_segmentation.append({"role": "user", "content": prompt})
    #         with st.spinner("GPT가 답변을 생성 중입니다..."):
    #             gpt_response = ask_gpt(st.session_state.messages_segmentation)
    #             st.session_state.messages_segmentation.append({"role": "assistant", "content": gpt_response})
    #         st.rerun()

    if st.button("장면 나누기 초기화", key="reset_segmentation_chat"):
        st.session_state.messages_segmentation = [
            {"role": "system", "content": SEGMENTATION_SYSTEM_PROMPT}
        ]
        st.session_state.segmented_story_input = ""
        st.session_state.segmentation_completed = False
        st.rerun()


# 3. 캐릭터/배경 이미지 생성 프롬프트 구성 - 설계 반영
elif chat_option.startswith("3"):
    st.header("3. 캐릭터/배경 이미지 생성")
    st.markdown("🎨 **목표:** 여러분의 이야기에 등장하는 캐릭터나 배경 이미지를 직접 만들어 볼 수 있어요.")

    if "messages_image_generation" not in st.session_state:
        st.session_state.messages_image_generation = [
            {"role": "system", "content": (
                GLOBAL_GPT_DIRECTIVES +
                """너는 초등학생이 설명한 캐릭터 또는 배경을 이미지 생성에 적합한 프롬프트로 구체화하는 GPT 도우미야.
학생에게 다음 요소를 모두 포함하도록 질문을 통해 유도해줘 (단, 이미 입력된 정보는 묻지 않고 누락된 정보만 질문):
- **대상**: 캐릭터인지 배경인지 명확히 해줘. (예: '주인공', '마법의 숲')
- **스타일**: 어떤 그림 스타일을 원하는지 물어봐줘. (예: '스누피 펜화', '디즈니 애니메이션 스타일', '수채화 느낌', '실사 같은', '미래적인')
- **외형, 표정, 자세**: 구체적인 모습, 표정, 어떤 자세를 취하고 있는지 물어봐줘. (예: '밝게 웃고 있는', '한 손을 흔들고 있는', '초록색 머리카락의')
- **전체 몸이 보이는지 여부**: 캐릭터의 경우, '캐릭터의 전체 몸이 다 보이도록 할까요?'라고 꼭 물어봐줘. (설계 반영: 캐릭터 생성 시 항상 전체 몸이 보이도록 설정)
- **배경 포함 여부**: 캐릭터 이미지의 경우, '배경은 없이 인물만 있는 건가요?'라고 물어봐줘. 배경 이미지의 경우, '어떤 풍경이나 분위기를 담고 싶은가요?'라고 물어봐줘. (설계 반영: 배경은 분리 생성하거나 프롬프트로 생성)

학생이 프롬프트 초안을 입력하면, 위 요소들을 바탕으로 부족한 부분을 단일 질문으로 추가 질문하여 정보를 채워나가줘.
필요한 정보가 모두 수집되면, 완성된 프롬프트를 깔끔하게 정리하여 출력하고, 이 프롬프트로 이미지를 생성할 수 있음을 알려줘.
**주의사항:** 학생에게 바로 이미지 프롬프트를 제공하지 않고, 질문을 통해 구체화해야 해. 캐릭터는 반드시 배경 없이, 전체 전신으로 생성되어야 함을 염두에 두고 질문을 이끌어내야 해. 질문은 자연스럽고 흐름에 맞게 진행해줘."""
            )}
        ]
        st.session_state.image_prompt_collected = False
        st.session_state.generated_image_display = None
        st.session_state.image_input_submitted = False
        st.session_state.final_dalle_prompt = ""

    image_type = st.radio("어떤 이미지를 만들고 싶나요?", ["캐릭터 이미지", "배경 이미지"], key="image_type_radio")

    if not st.session_state.image_input_submitted:
        initial_prompt = st.text_area(f"{image_type}에 대해 설명해주세요. (예: '용감한 기사', '신비로운 숲')", key="initial_image_prompt")
        if st.button("프롬프트 구체화 시작") and initial_prompt:
            st.session_state.messages_image_generation.append({"role": "user", "content": initial_prompt})
            st.session_state.image_input_submitted = True
            with st.spinner("GPT가 질문을 생성 중입니다..."):
                gpt_response = ask_gpt(st.session_state.messages_image_generation)
                st.session_state.messages_image_generation.append({"role": "assistant", "content": gpt_response})
            st.rerun()

    for message in st.session_state.messages_image_generation:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if st.session_state.image_input_submitted:
        if current_prompt := st.chat_input("GPT의 질문에 답하거나 설명을 추가해주세요."):
            st.session_state.messages_image_generation.append({"role": "user", "content": current_prompt})
            with st.spinner("GPT가 답변을 생성 중입니다..."):
                gpt_response = ask_gpt(st.session_state.messages_image_generation)
                st.session_state.messages_image_generation.append({"role": "assistant", "content": gpt_response})
            st.rerun()

        # Check if the last GPT message seems to be a finalized prompt
        if st.session_state.messages_image_generation and \
           st.session_state.messages_image_generation[-1]["role"] == "assistant" and \
           "완성된 프롬프트:" in st.session_state.messages_image_generation[-1]["content"] and \
           not st.session_state.image_prompt_collected: # Only collect once

            gpt_final_prompt_content = st.session_state.messages_image_generation[-1]["content"]
            start_index = gpt_final_prompt_content.find("완성된 프롬프트:") + len("완성된 프롬프트:")
            end_index = gpt_final_prompt_content.find("\n", start_index)
            if end_index == -1:
                final_dalle_prompt = gpt_final_prompt_content[start_index:].strip()
            else:
                final_dalle_prompt = gpt_final_prompt_content[start_index:end_index].strip()

            st.session_state.image_prompt_collected = True
            st.session_state.final_dalle_prompt = final_dalle_prompt
            st.info(f"✨ GPT가 최종 이미지 프롬프트를 완성했어요: `{final_dalle_prompt}`")

    if st.session_state.get("image_prompt_collected", False):
        if st.button("이 프롬프트로 이미지 생성하기"):
            if st.session_state.get("final_dalle_prompt"):
                with st.spinner("이미지를 생성 중입니다... 잠시만 기다려주세요!"):
                    try:
                        generated_img = generate_image(st.session_state.final_dalle_prompt)
                        st.session_state.generated_image_display = generated_img
                        st.success("이미지가 성공적으로 생성되었습니다!")
                    except Exception as e:
                        st.error(f"이미지 생성 중 오류가 발생했습니다: {e}. 프롬프트를 다시 확인하거나 잠시 후 다시 시도해주세요.")
            else:
                st.warning("먼저 GPT로부터 완성된 이미지 프롬프트를 받아야 합니다.")

        if st.session_state.generated_image_display:
            st.image(st.session_state.generated_image_display, caption=f"생성된 {image_type}", use_column_width=True)
            buf = io.BytesIO()
            st.session_state.generated_image_display.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.download_button(
                label="이미지 다운로드",
                data=byte_im,
                file_name=f"{image_type}_generated.png",
                mime="image/png"
            )


    if st.button("이미지 생성 초기화", key="reset_image_generation_chat"):
        st.session_state.messages_image_generation = [
            {"role": "system", "content": (
                GLOBAL_GPT_DIRECTIVES +
                """너는 초등학생이 설명한 캐릭터 또는 배경을 이미지 생성에 적합한 프롬프트로 구체화하는 GPT 도우미야.
학생에게 다음 요소를 모두 포함하도록 질문을 통해 유도해줘 (단, 이미 입력된 정보는 묻지 않고 누락된 정보만 질문):
- **대상**: 캐릭터인지 배경인지 명확히 해줘. (예: '주인공', '마법의 숲')
- **스타일**: 어떤 그림 스타일을 원하는지 물어봐줘. (예: '스누피 펜화', '디즈니 애니메이션 스타일', '수채화 느낌', '실사 같은', '미래적인')
- **외형, 표정, 자세**: 구체적인 모습, 표정, 어떤 자세를 취하고 있는지 물어봐줘. (예: '밝게 웃고 있는', '한 손을 흔들고 있는', '초록색 머리카락의')
- **전체 몸이 보이는지 여부**: 캐릭터의 경우, '전신이 다 보이는 모습인가요?'라고 꼭 물어봐줘.
- **배경 포함 여부**: 캐릭터 이미지의 경우, '배경은 없이 인물만 있는 건가요?'라고 물어봐줘. 배경 이미지의 경우, '어떤 풍경이나 분위기를 담고 싶은가요?'라고 물어봐줘.

학생이 프롬프트 초안을 입력하면, 위 요소들을 바탕으로 부족한 부분을 단일 질문으로 추가 질문하여 정보를 채워나가줘.
필요한 정보가 모두 수집되면, 완성된 프롬프트를 깔끔하게 정리하여 출력하고, 이 프롬프트로 이미지를 생성할 수 있음을 알려줘.
**주의사항:** 학생에게 바로 이미지 프롬프트를 제공하지 않고, 질문을 통해 구체화해야 해. 캐릭터는 반드시 배경 없이, 전체 전신으로 생성되어야 함을 염두에 두고 질문을 이끌어내야 해. 질문은 자연스럽고 흐름에 맞게 진행해줘."""
            )}
        ]
        st.session_state.image_prompt_collected = False
        st.session_state.generated_image_display = None
        st.session_state.image_input_submitted = False
        st.session_state.final_dalle_prompt = ""
        st.rerun()

# 4. 장면별 영상 Prompt 점검 - 설계 반영
elif chat_option.startswith("4"):
    st.header("4. 장면별 영상 Prompt 점검")
    st.markdown("🎬 **목표:** 각 장면에 맞는 Pika 영상 프롬프트를 만들고, 더 좋은 프롬프트로 다듬어 보세요.")

    st.warning("이 기능은 '2. 이야기 나누기'에서 장면 구분이 완료된 후에 사용하는 것이 좋습니다.")

    if "messages_video_prompt" not in st.session_state:
        st.session_state.messages_video_prompt = [
            {"role": "system", "content": (
                GLOBAL_GPT_DIRECTIVES +
                """너는 초등학생이 작성한 장면 설명을 기반으로, **10초 이내의 영상으로 구성 가능한 장면인지 확인**해줘.
Pika AI가 더 잘 이해하고 멋진 영상을 만들 수 있도록 프롬프트를 구체적이고 생생하게 개선해줘.
다음 요소를 중심으로 질문하여 (단, 누락된 경우에만) 구체화하도록 유도해줘:
- **동작**: 인물이나 사물이 어떤 움직임을 보이는지? (예: '뛰어간다', '천천히 춤춘다')
- **감정**: 인물의 표정이나 장면의 분위기는 어떤지? (예: '슬픈 표정의', '희망찬 분위기의')
- **구도**: 카메라가 인물을 어떻게 잡을지? (예: '전체 몸', '상반신', '로우 앵글 샷')
- **강조하고 싶은 요소**: 이 장면에 특별히 강조하고 싶은 것이 있다면 무엇인지? (예: '반짝이는 마법 효과', '아름다운 노을')

학생이 프롬프트 초안을 입력하면, 위 요소들을 바탕으로 부족한 부분을 단일 질문으로 추가 질문하여 정보를 채워나가줘.
구체화가 완료되면, **간결한 1~2문장 형태**로 최종 프롬프트를 정리하여 출력해줘.
**주의사항:**
- 문장이 너무 길거나 과도한 서술은 지양해야 해. (Pika의 프롬프트 해석 특성상, 장면 설명은 짧고 명확하게 구성해야 하며, 과도한 문장 길이나 묘사는 피함.)
- 캐릭터나 배경의 외형 묘사는 이 창에서 다루지 않아. 이는 '캐릭터/배경 이미지 생성'에서 이미 결정된 부분이야.
- 최종적으로 정제된 프롬프트만 출력하고, 불필요한 질문 반복은 금지해.

학생이 '완료' 또는 '충분하다'고 하면, 최종 프롬프트를 확정하고 '이제 이 프롬프트로 멋진 영상을 만들 수 있을 거예요!'라고 격려해줘."""
            )}
        ]
        st.session_state.current_scene_prompt = ""
        st.session_state.video_prompt_finalized = False

    scene_summary = st.text_input("장면 요약을 입력하세요 (예: '주인공이 마법의 숲에 도착하는 장면')", key="scene_summary_input")
    user_prompt_draft = st.text_area("이 장면에 대한 Pika 영상 프롬프트 초안을 작성하세요.", key="video_prompt_draft_input", value=st.session_state.current_scene_prompt)

    if st.button("프롬프트 점검 시작") and scene_summary and user_prompt_draft:
        st.session_state.current_scene_prompt = user_prompt_draft
        full_user_message = f"장면 요약: {scene_summary}\n프롬프트 초안: {user_prompt_draft}"
        st.session_state.messages_video_prompt.append({"role": "user", "content": full_user_message})
        with st.spinner("GPT가 프롬프트를 점검 중입니다..."):
            gpt_response = ask_gpt(st.session_state.messages_video_prompt)
            st.session_state.messages_video_prompt.append({"role": "assistant", "content": gpt_response})
        st.rerun()

    for message in st.session_state.messages_video_prompt:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if not st.session_state.video_prompt_finalized:
        if prompt := st.chat_input("GPT의 제안에 대해 이야기하거나 프롬프트를 수정해주세요."):
            st.session_state.messages_video_prompt.append({"role": "user", "content": prompt})
            with st.spinner("GPT가 답변을 생성 중입니다..."):
                gpt_response = ask_gpt(st.session_state.messages_video_prompt)
                st.session_state.messages_video_prompt.append({"role": "assistant", "content": gpt_response})
            st.rerun()

        # GPT가 최종 프롬프트를 제시했는지 확인
        if st.session_state.messages_video_prompt and \
           st.session_state.messages_video_prompt[-1]["role"] == "assistant" and \
           ("최종 프롬프트:" in st.session_state.messages_video_prompt[-1]["content"] or \
            "이 프롬프트로 멋진 영상을 만들 수 있을 거예요!" in st.session_state.messages_video_prompt[-1]["content"]):
            st.session_state.video_prompt_finalized = True
            st.success("✅ 영상 프롬프트 점검이 완료되었습니다!")


    if st.button("프롬프트 점검 초기화", key="reset_video_prompt_chat"):
        st.session_state.messages_video_prompt = [
            {"role": "system", "content": (
                GLOBAL_GPT_DIRECTIVES +
                """너는 초등학생이 Pika 영상 제작을 위한 효과적인 장면별 프롬프트를 만드는 것을 돕는 GPT 도우미야.
학생이 작성한 장면 설명을 기반으로, **10초 이내의 영상으로 구성 가능한 장면인지 확인**해줘.
Pika AI가 더 잘 이해하고 멋진 영상을 만들 수 있도록 프롬프트를 구체적이고 생생하게 개선해줘.
다음 요소를 중심으로 질문하여 (단, 누락된 경우에만) 구체화하도록 유도해줘:
- **동작**: 인물이나 사물이 어떤 움직임을 보이는지? (예: '뛰어간다', '천천히 춤춘다')
- **감정**: 인물의 표정이나 장면의 분위기는 어떤지? (예: '슬픈 표정의', '희망찬 분위기의')
- **구도**: 카메라가 인물을 어떻게 잡을지? (예: '전체 몸', '상반신', '로우 앵글 샷')
- **강조하고 싶은 요소**: 이 장면에 특별히 강조하고 싶은 것이 있다면 무엇인지? (예: '반짝이는 마법 효과', '아름다운 노을')

학생이 프롬프트 초안을 입력하면, 위 요소들을 바탕으로 부족한 부분을 단일 질문으로 추가 질문하여 정보를 채워나가줘.
구체화가 완료되면, **간결한 1~2문장 형태**로 최종 프롬프트를 정리하여 출력해줘.
**주의사항:**
- 문장이 너무 길거나 과도한 서술은 지양해야 해. (Pika의 프롬프트 해석 특성상, 장면 설명은 짧고 명확하게 구성해야 하며, 과도한 문장 길이나 묘사는 피함.)
- 캐릭터나 배경의 외형 묘사는 이 창에서 다루지 않아. 이는 '캐릭터/배경 이미지 생성'에서 이미 결정된 부분이야.
- 최종적으로 정제된 프롬프트만 출력하고, 불필요한 질문 반복은 금지해.

학생이 '완료' 또는 '충분하다'고 하면, 최종 프롬프트를 확정하고 '이제 이 프롬프트로 멋진 영상을 만들 수 있을 거예요!'라고 격려해줘."""
            )}
        ]
        st.session_state.current_scene_prompt = ""
        st.session_state.video_prompt_finalized = False
        st.rerun()
