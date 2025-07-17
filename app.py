import streamlit as st
from openai import OpenAI, APIError, RateLimitError, APIConnectionError, APITimeoutError
from PIL import Image
import base64
import io
import time

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

def generate_image(prompt):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            response_format="b64_json"
        )
        image_data = base64.b64decode(response.data[0].b64_json)
        return Image.open(io.BytesIO(image_data))
    except RateLimitError:
        st.error("잠시만요! 너무 많은 이미지 요청이 있었어요. 😥 1분 후에 다시 시도해 주세요.")
        
        # 버튼을 잠시 비활성화하고 사용자에게 대기 시간을 안내합니다.
        # 이 상태를 Streamlit session state에 저장하여 새로고침 시에도 유지되도록 합니다.
        st.session_state.image_generation_disabled = True
        st.session_state.image_generation_disable_until = time.time() + 60 # 60초(1분) 동안 비활성화
        
        # print(f"[RateLimitError] 발생 시간: {time.ctime()}") # 디버깅용 로그
        return None
    except APIError as e:
        error_message = e.response.json().get('error', {}).get('message', '알 수 없는 오류')
        st.error(f"이미지 생성 중 OpenAI API 오류가 발생했습니다: ({e.status_code}) {error_message}")
        return None
    except APIConnectionError as e:
        st.error(f"인터넷 연결 문제로 이미지 생성에 실패했어요. 네트워크 상태를 확인해 주세요. 오류: {e}")
        return None
    except APITimeoutError:
        st.error("이미지 생성 요청이 너무 오래 걸려 취소되었어요. 다시 시도해 주세요.")
        return None
    except Exception as e:
        st.error(f"예상치 못한 오류가 발생했습니다: {e}. 잠시 후 다시 시도해 주세요.")
        return None

# 모든 GPT 시스템 프롬프트에 공통으로 들어갈 지침
GLOBAL_GPT_DIRECTIVES = (
"""
**[공통 지침]**
- 이 프로그램의 최종 목표는 Pika를 활용하여 1분에서 1분 30초 정도의 영상을 창작하는 것이야.
- GPT는 창작물을 대신 완성하지 않고, 질문을 통해 학생 스스로 수정과 구체화를 유도하는 조력자 역할을 수행해. 학생의 창의성을 존중하고, 칭찬과 격려의 말투를 꼭 유지해줘.
- **콘텐츠 제한:** 폭력적이거나, 혐오스러운장면, 특정인을 등장시키거나, 선정적인 내용은 절대 금지해.
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
    #      if prompt := st.chat_input("장면 구분에 대해 이야기하거나 수정하고 싶은 부분을 알려주세요."):
    #           st.session_state.messages_segmentation.append({"role": "user", "content": prompt})
    #           with st.spinner("GPT가 답변을 생성 중입니다..."):
    #                gpt_response = ask_gpt(st.session_state.messages_segmentation)
    #                st.session_state.messages_segmentation.append({"role": "assistant", "content": gpt_response})
    #                st.rerun()

    if st.button("장면 나누기 초기화", key="reset_segmentation_chat"):
        st.session_state.messages_segmentation = [
            {"role": "system", "content": SEGMENTATION_SYSTEM_PROMPT}
        ]
        st.session_state.segmented_story_input = ""
        st.session_state.segmentation_completed = False
        st.rerun()

# --- 3. 캐릭터/배경 이미지 생성 프롬프트 구성 ---
# chat_option 변수가 "3. 캐릭터/배경 이미지 생성"일 때만 이 블록이 실행됩니다.
elif chat_option.startswith("3"):
    st.header("3. 캐릭터/배경 이미지 생성")
    st.markdown("🎨 **목표:** 여러분의 이야기에 등장하는 캐릭터나 배경 이미지를 직접 만들어 볼 수 있어요.")

    # 3번 섹션을 위한 GPT 시스템 프롬프트 (최신 논의 반영)
    IMAGE_GENERATION_SYSTEM_PROMPT = (
        GLOBAL_GPT_DIRECTIVES +
      r"""너는 초등학생이 설명한 캐릭터 또는 배경을 이미지 생성에 적합한 프롬프트로 구체화하는 GPT 도우미야.
학생의 창의성을 존중하고, 칭찬과 격려의 말투를 꼭 유지해줘.

**[GPT 역할 및 대화 방식]**
- 학생이 제공한 정보가 아래 항목 중 누락되었거나 불분명하면, **해당 항목에 대한 질문과 함께 적절한 예시를 하나씩 제시**하여 학생이 스스로 더 나은 표현을 찾도록 유도해줘.
- 반드시 한 번에 하나씩만 질문하고, 학생의 답변을 듣고 다음 질문을 이어가야 해.
- 전체 질문은 최대 5개 이내로, 이야기의 완성도에 따라 더 적게 해도 좋아.
- 중복된 질문이나 이미 잘 표현된 요소는 건너뛰어도 돼.

**[질문 대상 항목 및 예시]**

1.  **대상 (가장 먼저 질문)**: "만들고 싶은 이미지가 어떤 대상인가요? 사람 캐릭터, 동물 캐릭터, 아니면 움직이는 물건 같은 건가요?"
    * **예시:** '용감한 기사 (사람 캐릭터)', '말하는 고양이 (동물 캐릭터)', '움직이는 장난감 로봇 (물건 캐릭터)'

2.  **나이/연령대 (캐릭터가 사람일 경우만 해당)**: "이 캐릭터는 몇 살쯤 되는 것 같아? 아니면 어떤 연령대의 느낌이야?"
    * **예시:** '10살 여자아이', '고등학생 남자', '친절한 할머니'

3.  **성별 (캐릭터가 사람일 경우만 해당)**: "이 친구는 여자 캐릭터야, 남자 캐릭터야, 아니면 성별을 딱 정하지 않은 중성적인 느낌이야?"
    * **예시:** '여자', '남자', '중성적인'

4.  **외형 특징**: "캐릭터의 머리 모양, 머리색, 피부색, 눈색, 체형 같은 특별한 특징이 있어? (동물이나 물건이라면 어떤 색깔이나 모양인가요?)"
    * **예시:** '긴 갈색 머리', '파란 눈의 하얀 피부', '통통한 몸매', '빨간색 털을 가진 고양이', '반짝이는 금속 로봇'

5.  **의상/소품**: "이 캐릭터는 어떤 옷을 입고 있거나 어떤 소품을 가지고 있으면 좋겠어? (동물이나 물건이라면 특징적인 액세서리나 부품이 있나요?)"
    * **예시:** '노란색 후드티', '낡은 청바지', '빨간색 망토', '마법 지팡이', '낡은 책가방', '작은 탐정 모자를 쓴 고양이'

6.  **표정/감정**: "지금 캐릭터가 어떤 표정을 짓고 있으면 좋을까? 어떤 감정을 보여줬으면 좋겠어?" (배경 없이 캐릭터의 기본 표정)
    * **예시:** '밝게 웃는 표정', '호기심 가득한 표정', '살짝 찡그린 얼굴'

7.  **스타일/화풍**: "이 그림이 어떤 스타일로 보이면 좋겠어? 만화 같을까, 그림책 같을까?"
    * **예시:** '디즈니 애니메이션 스타일', '픽사 3D 애니메이션 스타일', '디지털 수채화 느낌', '스누피 펜화 스타일'

**[캐릭터 이미지 생성 규칙 (GPT가 자동으로 적용)]**
- 무조건 정면을 보고 서 있는 중립적인 자세(standing facing front, neutral pose)를 프롬프트에 자동으로 포함**하여 가장 활용하기 좋게 만들어줘. (단, 동물이나 물건 캐릭터의 경우, '서 있는' 대신 '자연스럽게 놓여 있는' 등 해당 대상에게 적합한 중립적인 상태를 반영해줘.)
- 학생이 어떤 자세를 언급했든 관계없이, **배경은 없도록(no background)** 프롬프트에 포함해줘.
- 캐릭터 이미지는 항상 **전신이 보이도록(full-body, head to toe)** 생성해야 해. 대표이미지로서 활용될 수 있게.

**[프롬프트 완성 및 전달]**
모든 필요한 정보가 수집되면, **DALL-E 모델에 전달할 영어 프롬프트와 함께, 그것의 자연스러운 한국어 번역본을 다음 형식으로 출력해줘. 다른 불필요한 설명은 일절 추가하지 마.**

**DALL-E 프롬프트 (영어):** [여기에 영어 프롬프트 텍스트]
**한국어 번역:** [여기에 한국어 번역 텍스트]

**예시:**
**DALL-E 프롬프트 (영어):** A 10-year-old girl, female, with short brown hair and bright blue eyes, wearing a pink dress and holding a small teddy bear, brightly smiling expression, Disney animation style, standing facing front, no background, full body.
**한국어 번역:** 10살 여자아이, 짧은 갈색 머리와 파란 눈을 가졌고, 분홍색 원피스를 입고 작은 곰인형을 들고 있는 모습. 밝게 웃는 표정. 디즈니 애니메이션 스타일. 정면을 보고 서 있는 전신 이미지. 배경 없음.

**주의사항:** 학생에게 바로 이미지 프롬프트를 제공하지 않고, 질문을 통해 구체화해야 해. 질문은 자연스럽고 흐름에 맞게 진행해줘."""
    )

    # 세션 상태 초기화 또는 로드
    # 이 섹션에 들어올 때만 초기화되도록 조건 추가 (이미 다른 섹션에서 세션 상태가 존재할 경우 방지)
    if "messages_image_generation" not in st.session_state or \
       st.session_state.messages_image_generation[0]["content"] != IMAGE_GENERATION_SYSTEM_PROMPT:
        st.session_state.messages_image_generation = [
            {"role": "system", "content": IMAGE_GENERATION_SYSTEM_PROMPT}
        ]
        st.session_state.image_prompt_collected = False
        st.session_state.generated_image_display = None
        st.session_state.image_input_submitted = False
        st.session_state.final_dalle_prompt = "" # 최종 DALL-E 프롬프트 저장용
        st.session_state.image_generation_disabled = False 
        st.session_state.image_generation_disable_until = 0 

    # 캐릭터/배경 선택 라디오 버튼
    image_type = st.radio("어떤 이미지를 만들고 싶나요?", ["캐릭터 이미지", "배경 이미지"], key="image_type_radio")
    
    # 초기 프롬프트 입력창 (첫 제출 전까지 보임)
    if not st.session_state.image_input_submitted:
        initial_prompt = st.text_area(f"{image_type}에 대해 설명해주세요. (예: '용감한 기사', '신비로운 숲')", key="initial_image_prompt")
        if st.button("프롬프트 구체화 시작") and initial_prompt:
            st.session_state.messages_image_generation.append({"role": "user", "content": initial_prompt})
            st.session_state.image_input_submitted = True # 스토리 제출 시 이 플래그를 True로 설정
            with st.spinner("GPT가 질문을 생성 중입니다..."):
                gpt_response = ask_gpt(st.session_state.messages_image_generation)
                st.session_state.messages_image_generation.append({"role": "assistant", "content": gpt_response})
            st.rerun() # 플래그 변경 후 페이지를 새로고침하여 채팅 UI를 표시
        if not st.session_state.image_input_submitted and initial_prompt:
             st.info("⬆️ '프롬프트 구체화 시작' 버튼을 눌러 GPT와 대화를 시작하세요!")


    # 대화 기록 표시
    for message in st.session_state.messages_image_generation:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # 지속적인 채팅 입력창 (초기 프롬프트 제출 후 보임)
    if st.session_state.image_input_submitted:
        if current_prompt := st.chat_input("GPT의 질문에 답하거나 설명을 추가해주세요."):
            st.session_state.messages_image_generation.append({"role": "user", "content": current_prompt})
            with st.spinner("GPT가 답변을 생성 중입니다..."):
                gpt_response = ask_gpt(st.session_state.messages_image_generation)
                st.session_state.messages_image_generation.append({"role": "assistant", "content": gpt_response})
            st.rerun()

         # GPT의 마지막 메시지에서 '완성된 프롬프트:'를 찾아 추출 (파싱 로직 개선)
        if st.session_state.messages_image_generation and \
           st.session_state.messages_image_generation[-1]["role"] == "assistant" and \
           "DALL-E 프롬프트 (영어):" in st.session_state.messages_image_generation[-1]["content"] and \
           "한국어 번역:" in st.session_state.messages_image_generation[-1]["content"] and \
           not st.session_state.messages_image_generation[-1]["content"].strip().endswith("?") and \
           not st.session_state.image_prompt_collected: # '?'로 끝나는 질문이 아닐 때만 프롬프트로 인식
            
            gpt_final_prompt_content = st.session_state.messages_image_generation[-1]["content"]
            
            try:
                # 영어 프롬프트 추출
                start_english_index = gpt_final_prompt_content.find("DALL-E 프롬프트 (영어):")
                if start_english_index != -1:
                    english_prompt_start = start_english_index + len("DALL-E 프롬프트 (영어):")
                    # '한국어 번역:' 시작 전까지의 내용을 영어 프롬프트로 간주
                    end_english_index = gpt_final_prompt_content.find("한국어 번역:", english_prompt_start)
                    if end_english_index == -1: # 한국어 번역이 없을 경우, 끝까지
                        final_dalle_prompt = gpt_final_prompt_content[english_prompt_start:].strip()
                    else:
                        final_dalle_prompt = gpt_final_prompt_content[english_prompt_start:end_english_index].strip()
                    
                    # 한국어 번역 추출
                    start_korean_index = gpt_final_prompt_content.find("한국어 번역:")
                    if start_korean_index != -1:
                        korean_translation_start = start_korean_index + len("한국어 번역:")
                        korean_dalle_prompt = gpt_final_prompt_content[korean_translation_start:].strip()
                    else:
                        korean_dalle_prompt = "번역을 가져올 수 없습니다." # 번역이 없을 경우

                    st.session_state.image_prompt_collected = True
                    st.session_state.final_dalle_prompt = final_dalle_prompt # DALL-E 모델에 전달할 영어 프롬프트
                    st.session_state.korean_dalle_prompt_display = korean_dalle_prompt # 사용자에게 보여줄 한국어 번역

                    st.info(f"✨ GPT가 최종 이미지 프롬프트를 완성했어요 (DALL-E용): `{final_dalle_prompt}`")
                    st.success(f"💡 **[한국어 번역]** : {korean_dalle_prompt}")
                else:
                    st.session_state.image_prompt_collected = False # 아직 프롬프트 완성 안 됨
                    st.session_state.final_dalle_prompt = ""
                    st.session_state.korean_dalle_prompt_display = ""
            except Exception as e:
                st.error(f"프롬프트 파싱 중 오류가 발생했습니다: {e}. GPT 응답 형식을 확인해주세요.")
                st.session_state.image_prompt_collected = False
                st.session_state.final_dalle_prompt = ""
                st.session_state.korean_dalle_prompt_display = ""

    # 최종 프롬프트가 수집되었을 때 이미지 생성 버튼 및 이미지 표시
    # --- 여기서부터 정렬 수정 ---
    if st.session_state.get("image_prompt_collected", False):
        # 버튼 활성화 여부 확인
        is_button_disabled = st.session_state.get("image_generation_disabled", False)
        if is_button_disabled:
            # 비활성화 시간 확인
            remaining_time = int(st.session_state.get("image_generation_disable_until", 0) - time.time())
            if remaining_time > 0:
                st.warning(f"⏰ 이미지 생성은 {remaining_time}초 후에 다시 가능합니다. 잠시 기다려주세요.")
                # 버튼을 비활성화 상태로 렌더링
                st.button("이미지 생성 중 (잠시 기다려주세요)", disabled=True) 
            else:
                # 시간 만료, 버튼 다시 활성화
                st.session_state.image_generation_disabled = False
                is_button_disabled = False # 버튼 상태 업데이트

        # 버튼이 활성화된 경우에만 클릭 가능하도록
        if not is_button_disabled:
            if st.button("이 프롬프트로 이미지 생성하기"):
                if st.session_state.get("final_dalle_prompt"):
                    with st.spinner("이미지를 생성 중입니다... 잠시만 기다려주세요!"):
                        generated_img = generate_image(st.session_state.final_dalle_prompt) 
                        if generated_img:
                            st.session_state.generated_image_display = generated_img
                            st.success("이미지가 성공적으로 생성되었습니다!")
                        # 오류 메시지는 generate_image 함수 내에서 이미 표시됨
                else:
                    st.warning("먼저 GPT로부터 완성된 이미지 프롬프트를 받아야 합니다.")
        
        # 생성된 이미지가 있으면 화면에 표시하고 다운로드 버튼 제공
        if st.session_state.generated_image_display:
            st.image(st.session_state.generated_image_display, caption=f"생성된 {image_type} (프롬프트: {st.session_state.korean_dalle_prompt_display})", use_container_width=True)
            buf = io.BytesIO()
            st.session_state.generated_image_display.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.download_button(
                label="이미지 다운로드",
                data=byte_im,
                file_name=f"{image_type}_generated.png",
                mime="image/png"
            )

    # 대화 초기화 버튼
    # --- 여기서부터 정렬 수정 ---
    if st.button("이미지 생성 초기화", key="reset_image_generation_chat"):
        st.session_state.messages_image_generation = [
            {"role": "system", "content": IMAGE_GENERATION_SYSTEM_PROMPT} 
        ]
        st.session_state.image_prompt_collected = False
        st.session_state.generated_image_display = None
        st.session_state.image_input_submitted = False
        st.session_state.final_dalle_prompt = ""
        st.session_state.image_generation_disabled = False 
        st.session_state.image_generation_disable_until = 0 
        st.rerun()
# 4. 장면별 영상 Prompt 점검 - 설계 반영
elif chat_option.startswith("4"):
    st.header("4. 장면별 영상 Prompt 점검")
    st.markdown("🎬 **목표:** 각 장면에 맞는 Pika 영상 프롬프트를 만들고, 더 좋은 프롬프트로 다듬어 보세요.")

    st.warning("이 기능은 '2. 이야기 나누기'에서 장면 구분이 완료된 후에 사용하는 것이 좋습니다.")

    # '장면별 영상 Prompt 점검'의 시스템 프롬프트 정의 (최종본)
    VIDEO_PROMPT_REVIEW_SYSTEM_PROMPT = (
        GLOBAL_GPT_DIRECTIVES +
        """너는 초등학생이 작성한 장면 설명을 기반으로, **10초 이내의 영상으로 구성 가능한지 확인**하고 Pika AI가 멋진 영상을 만들 수 있도록 프롬프트를 구체적이고 생생하게 개선해주는 GPT 도우미야. 너의 목표는 학생의 아이디어를 Pika에 최적화된 시각적인 프롬프트로 변환하는 것이야. **컴퓨터는 '푸근한 아줌마'처럼 모호한 표현을 이해하기 어렵다는 것을 학생들이 잘 모른다는 점을 항상 기억하고, 이를 구체적인 시각적 묘사로 바꾸도록 적극적으로 도와줘.**

**[GPT 역할 및 대화 방식]**
- 학생의 프롬프트 초안을 면밀히 검토하고, **모호하거나(예: '좋은 분위기'), 한 장면에 너무 많은 이야기가 담겨있거나, 영상으로 표현하기에 설명이 부족한 부분이 있다면 구체적으로 지적**해줘.
- 부족하거나 더 구체화할 수 있는 부분이 있다면 다음 요소들을 중심으로 **최대 3개 이내의 단일 질문**을 통해 정보를 채워나가줘.
- 반드시 한 번에 하나씩만 질문하고, 학생의 답변을 듣고 다음 질문을 이어가야 해.
- 전체 질문은 최대 7개 이내로, 대화의 효율성을 중요하게 생각해줘. 중복된 질문이나 이미 잘 표현된 요소는 건너뛰어도 돼.
- 질문은 항상 초등학교 5학년 수준의 언어로, 친절하고 격려하는 말투로 해줘. 학생의 창의성을 존중하면서도, 영상 제작 관점에서 필요한 부분을 놓치지 않도록 도와줘.

**[문제점 지적 및 질문 대상 항목 (누락 또는 모호할 시 질문)]**

1.  **장면 길이/정보 과다**: "이 한 장면에 혹시 여러 가지 일이 동시에 일어나고 있지는 않을까? Pika 영상은 한 장면이 10초 정도라서 너무 많은 이야기가 담기면 복잡해 보일 수 있어. 만약 그렇다면, **이 장면을 2개 또는 3개의 더 작은 장면으로 나누어 볼 수 있을까요?** 각 장면에 가장 중요하게 보여주고 싶은 것 하나씩만 생각해 볼까?" (예시: '아침에 일어나 학교에 갔다가 친구들을 만나는 장면' -> '아침에 일어나는 장면', '학교 가는 길 장면', '친구들과 만나는 장면'으로 제안)
2.  **영상 스타일**: "이 장면이 어떤 그림 스타일로 보이면 좋을까? **진짜 사진이나 영화처럼 실사 같았으면 좋겠니? 아니면 디즈니 만화처럼 귀여운 느낌? 아니면 물감으로 그린 수채화 느낌? 또는 애니메이션 영화 같았으면 좋겠니?**" (예시: '실사', '디즈니 애니메이션 스타일', '수채화 일러스트', '픽사 3D 애니메이션 스타일', '재패니메이션 스타일')
3.  **모호한 표현 구체화 (매우 중요!)**: "네가 말한 '**[학생의 모호한 표현, 예: '좋은 분위기']**'를 영상으로 어떻게 보여줄 수 있을까? 컴퓨터는 그걸 바로 알 수 없어. 예를 들어, '좋은 분위기'라면 **'따뜻한 햇살이 비치고 꽃잎이 휘날리는 배경에서 인물들이 밝게 웃고 있는 모습'**처럼 어떤 장면을 상상했는지 좀 더 구체적으로 말해줄 수 있을까?"
4.  **동작**: "인물이나 사물이 어떤 움직임을 보이는지 더 자세히 말해줄 수 있을까? 단순히 '걷는다'고만 하면 Pika가 어떤 모습으로 걸어야 할지 알기 어려워. **'주인공이 신나서 팔짝팔짝 뛰는 모습'**처럼 더 생생하게 표현해 볼까?"
5.  **감정/표정**: "이 장면에서 인물이 어떤 감정을 느끼고 어떤 표정을 짓고 있는지 알려줄 수 있을까? **'슬픔'이라면 눈물을 흘리거나 고개를 숙인 모습**처럼, 감정을 직접적으로 드러내는 행동이나 표정이 필요해!"
6.  **구도/시점**: "카메라가 인물을 어떻게 보여줬으면 좋겠어? 전체 몸이 다 보이는 **'전신 샷'**, 얼굴이 크게 보이는 **'클로즈업 샷'**, 아니면 아래에서 올려다보는 **'로우 앵글 샷'** 같은 것들이 있어. 어떤 구도가 가장 좋을까?"
7.  **강조하고 싶은 요소**: "이 장면에 특별히 반짝이거나, 움직이거나, 가장 눈에 띄게 하고 싶은 것이 있다면 무엇이니? 예를 들어, '마법 효과'만 있다면 **'주인공의 손에서 반짝이는 파란색 마법 불꽃이 피어오르는 모습'**처럼 더 구체적으로 말해줄 수 있을까?"

**[Pika 최적화 프롬프트 작성 지침 (GPT가 항상 염두에 둘 것)]**
- Pika AI는 **짧고 간결하며 시각적인 영어 프롬프트**에 가장 잘 반응하고 멋진 영상을 만들 수 있어.
- 최종 프롬프트는 한 장면당 **1~2개의 핵심적인 시각적 요소를 중심으로, 명확한 동작과 분위기, 구도를 담아** 구성해야 해.
- 문장이 너무 길거나 불필요한 설명은 최대한 줄여야 해.
- 캐릭터나 배경의 외형 묘사는 이 창에서 다루지 않아. (이는 '캐릭터/배경 이미지 생성'에서 이미 결정된 부분임을 명심해.)
- **필요하다면 Pika의 특정 명령어(-gs, -ar, -fps 등)를 자연스럽게 포함하여 프롬프트의 품질을 높여줘.** (예: 'A smiling girl running in a park --gs 8 --ar 16:9')

**[대화 지속 및 종료 조건]**
- **학생이 '장면 완성!' 또는 '이제 이대로 괜찮아요!'와 같이 명확하게 대화 종료를 선언할 때까지는 계속 대화를 이어가며 프롬프트 구체화 및 수정을 도와줘.**
- 만약 학생이 **"이대로 프롬프트 만들어주세요!"**라고 요청하면, 현재까지의 대화 내용을 바탕으로 최종 프롬프트를 생성해줘.
- 학생이 **"영상이 이상해요"**, **"이 부분이 마음에 들지 않아요"**, **"다르게 표현하고 싶어요"** 와 같이 구체적인 피드백을 주면, **GPT는 별도의 질문 없이 해당 피드백을 바탕으로 프롬프트를 바로 수정하고 새로운 최종 프롬프트 제안을 해줘.** (예: "주인공 얼굴이 좀 슬퍼 보였어요." -> "아, 주인공 표정이 상상과 달랐구나! 그럼 프롬프트에서 주인공의 표정을 '밝게 웃는' 또는 '환하게 미소 짓는' 등으로 바꿔볼까? 새로운 프롬프트를 다시 만들어 줄게.")
- **최대 7번의 대화 질문(초기 프롬프트 제출 후 이어지는 질문)을 모두 사용하거나, 학생이 명확히 종료를 선언하면,** 지금까지 논의된 내용을 바탕으로 **Pika 영상 제작에 활용될 최종 프롬프트를 아래 형식으로 단 1~2문장으로 간결하게 정리하여 제시**하고 격려 문구를 덧붙여줘. **반드시 Pika AI가 잘 이해할 수 있는 시각적인 언어로 변환해야 해. 학생이 모호한 표현을 썼더라도 네가 가장 적합하게, 그리고 구체적으로 변환해줘.**

**[최종 프롬프트 출력 형식]**
---
✨ **완성된 영상 프롬프트 (한국어):** [여기에 최종적으로 정리된 간결하고 시각적인 Pika 영상 프롬프트 한국어 번역]
🎬 **Pika AI용 영어 프롬프트:** [여기에 최종적으로 정리된 Pika AI용 영어 프롬프트]
이제 이 프롬프트로 멋진 영상을 만들 수 있을 거예요! 정말 잘했어요! 😊
---
"""
    )

    # st.session_state 초기화 시 시스템 프롬프트도 다시 로드하도록 조건 추가
    if "messages_video_prompt" not in st.session_state or \
       st.session_state.messages_video_prompt[0]["content"] != VIDEO_PROMPT_REVIEW_SYSTEM_PROMPT:
        st.session_state.messages_video_prompt = [
            {"role": "system", "content": VIDEO_PROMPT_REVIEW_SYSTEM_PROMPT}
        ]
        st.session_state.current_scene_prompt = ""
        st.session_state.video_prompt_finalized = False 

    # --- 입력 칸 구분 명확화 코드 시작 ---
    st.subheader("1단계: 이 장면은 어떤 내용인가요?")
    scene_summary = st.text_input(
        "**이 장면을 한 문장으로 요약해주세요.** (예: 주인공이 마법의 숲에 도착하는 장면)", 
        key="scene_summary_input",
        placeholder="예: 주인공이 마법의 숲에 도착하는 장면"
    )

    st.subheader("2단계: 영상 프롬프트 초안을 작성해주세요.")
    user_prompt_draft = st.text_area(
        "**이 장면을 Pika AI 영상으로 만들려면 어떻게 표현할까요?** (구체적으로 작성해보세요!)", 
        key="video_prompt_draft_input", 
        value=st.session_state.current_scene_prompt,
        placeholder="예: 소녀가 신비로운 숲길을 걷는 모습. 나뭇잎 사이로 햇살이 비치고 작은 요정들이 주변을 날아다님."
    )
    # --- 입력 칸 구분 명확화 코드 끝 ---

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

    # video_prompt_finalized가 True가 될 때까지 채팅 입력 필드 표시
    if not st.session_state.video_prompt_finalized:
        if prompt := st.chat_input("GPT의 제안에 대해 이야기하거나 프롬프트를 수정해주세요. (예: '주인공이 좀 더 신났으면 좋겠어요', '배경이 더 밝았으면 좋겠어요')"):
            st.session_state.messages_video_prompt.append({"role": "user", "content": prompt})
            with st.spinner("GPT가 답변을 생성 중입니다..."):
                gpt_response = ask_gpt(st.session_state.messages_video_prompt)
                st.session_state.messages_video_prompt.append({"role": "assistant", "content": gpt_response})
            st.rerun()

        # GPT가 최종 프롬프트를 제시했는지 확인 (파싱 로직)
        if st.session_state.messages_video_prompt and \
           st.session_state.messages_video_prompt[-1]["role"] == "assistant":
            last_gpt_message = st.session_state.messages_video_prompt[-1]["content"]
            
            # 새로운 출력 형식에 맞춰 파싱
            if "✨ **완성된 영상 프롬프트 (한국어):**" in last_gpt_message and \
               "🎬 **Pika AI용 영어 프롬프트:**" in last_gpt_message:
                
                # 한국어 프롬프트 추출
                start_korean_index = last_gpt_message.find("✨ **완성된 영상 프롬프트 (한국어):**") + len("✨ **완성된 영상 프롬프트 (한국어):**")
                end_korean_index = last_gpt_message.find("🎬 **Pika AI용 영어 프롬프트:**", start_korean_index)
                korean_final_prompt = last_gpt_message[start_korean_index:end_korean_index].strip()

                # 영어 프롬프트 추출
                start_english_index = last_gpt_message.find("🎬 **Pika AI용 영어 프롬프트:**") + len("🎬 **Pika AI용 영어 프롬프트:**")
                end_english_index = last_gpt_message.find("이제 이 프롬프트로", start_english_index)
                if end_english_index != -1:
                    english_final_prompt = last_gpt_message[start_english_index:end_english_index].strip()
                else:
                    english_final_prompt = last_gpt_message[start_english_index:].strip()

                # 격려 메시지 추출
                encouragement_message = ""
                encouragement_start_index = last_gpt_message.find("이제 이 프롬프트로", end_english_index if end_english_index != -1 else start_english_index)
                if encouragement_start_index != -1:
                    encouragement_message = last_gpt_message[encouragement_start_index:].strip()

                st.success("✅ GPT가 새로운 프롬프트 초안을 제안했어요! 마음에 드나요?")
                st.markdown("---") 

                st.subheader("💡 완성된 영상 프롬프트")
                st.write(f"**한국어:** {korean_final_prompt}")
                st.markdown(f"**Pika AI용 영어:** ```{english_final_prompt}```") # 코드 블록으로 강조

                st.markdown("---") 
                st.info(f"👍 {encouragement_message}")
                st.markdown("---")
                st.markdown("⬆️ 이 프롬프트가 마음에 든다면 **'장면 완성!'** 이라고 말해주세요. 혹시 수정하고 싶은 부분이 있다면 어떤 점이 마음에 들지 않는지 구체적으로 설명해주세요.")
                
            # 기존 종료 조건도 함께 유지 (이전 형식의 최종 프롬프트가 혹시 출력될 경우를 대비)
            elif "최종 프롬프트:" in last_gpt_message or \
                 "이 프롬프트로 멋진 영상을 만들 수 있을 거예요!" in last_gpt_message:
                if "✨ **완성된 영상 프롬프트 (한국어):**" not in last_gpt_message:
                    st.success("✅ 영상 프롬프트 점검이 완료되었습니다! (이전 형식)")
                    with st.chat_message("assistant"):
                        st.markdown(last_gpt_message)
                    st.info("⬆️ 이 프롬프트가 마음에 든다면 **'장면 완성!'** 이라고 말해주세요. 혹시 수정하고 싶은 부분이 있다면 어떤 점이 마음에 들지 않는지 구체적으로 설명해주세요.")
                    # 이전 형식일 경우에도 대화는 계속되도록 video_prompt_finalized는 False 유지
                    # st.session_state.video_prompt_finalized = False # <-- 이 줄은 불필요. 기본값이 False이므로.


    if st.button("프롬프트 점검 초기화", key="reset_video_prompt_chat"):
        st.session_state.messages_video_prompt = [
            {"role": "system", "content": VIDEO_PROMPT_REVIEW_SYSTEM_PROMPT}
        ]
        st.session_state.current_scene_prompt = ""
        st.session_state.video_prompt_finalized = False 
        st.rerun()
