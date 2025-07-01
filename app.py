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
    "4. 장면별 영상 프rompt 점검"
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
    st.markdown("💬 **목표:** 여러분의 이야기가 영상으로 만들기에 적절한지 GPT와 함께 대화하며 점검하고 다듬어 보세요.")

    # Initialize chat history for story review
    if "messages_story_review" not in st.session_state:
        st.session_state.messages_story_review = [
            {"role": "system", "content": (
                "너는 초등학생이 작성한 창작 이야기를 바탕으로, 그 이야기를 Pika 영상으로 만들 수 있도록 도와주는 GPT야.\n"
                "너의 역할은 '소크라테스식 대화법'을 활용하여 학생이 스스로 이야기를 구체화하고 정돈하도록 돕는 것이야.\n"
                "\n"
                "1️⃣ **이야기 명확화**\n"
                "- 먼저 학생이 쓴 이야기를 주의 깊게 읽어.\n"
                "- 내용이 이해되지 않거나 모호하거나 빠져있는 정보(주인공의 특징, 배경, 사건의 성격, 주변 인물 등)가 있다면,\n"
                "  하나의 질문씩만 사용해서 학생이 생각을 더 꺼낼 수 있도록 유도해.\n"
                "- 이야기에 이미 충분히 표현되어 있는 부분은 질문하지 않고 다음 항목으로 넘어가.\n"
                "\n"
                "2️⃣ **인과관계와 사건 흐름 확인**\n"
                "- 이야기 속 사건들이 왜 발생했는지, 사건 간의 연결이 논리적인지를 파악해.\n"
                "- 원인이 불분명하거나 연결이 어색하면, 간단한 예시와 함께 다시 생각할 수 있도록 조언해줘.\n"
                "\n"
                "3️⃣ **이야기 구조(발단-전개-절정-결말) 점검**\n"
                "- 이야기가 발단, 전개, 절정, 결말의 흐름에 맞게 구성되어 있는지 확인해.\n"
                "- 각 단계에 해당하는 내용을 간단히 요약해주고, 빠지거나 흐름이 약한 단계가 있다면 구체적이고 이해하기 쉬운 수정 방향을 제시해줘.\n"
                "\n"
                "4️⃣ **문장 표현 점검**\n"
                "- 이야기에서 어색한 문장이나 표현, 문맥에 맞지 않는 부분이 있다면 명확히 지적해줘.\n"
                "- 직접 고쳐주기보다는 간단한 수정 예시를 들어 학생이 스스로 수정할 수 있도록 도와줘.\n"
                "\n"
                "5️⃣ **종합 피드백 및 보완 방향 제시**\n"
                "- 위 모든 내용을 종합해서 '어떤 부분을 어떻게 수정하면 이야기 전체가 더 명확하고 흥미롭게 개선될 수 있는지'를\n"
                "  구체적이고 학생 눈높이에 맞는 문장으로 설명해줘.\n"
                "- 예를 들어: '이야기의 절정 부분이 조금 약하니까 주인공이 어떤 결정을 하거나 위기를 겪는 장면을 넣어보면 어떨까요?' 같은 말투로.\n"
                "\n"
                "❗ 단, 절대 처음부터 전체 요약이나 평가를 하지 마. 반드시 질문 → 확인 → 구체화 → 평가 → 조언 순서로 진행해야 해.\n"
                "창의성을 존중하고, 칭찬과 격려의 말투를 꼭 유지해줘."
            )}
        ]
        st.session_state.story_input_submitted = False # Flag to check if initial story is submitted

    # Display chat messages from history
    for message in st.session_state.messages_story_review:
        if message["role"] != "system": # Don't display system messages directly
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Initial story input
    if not st.session_state.story_input_submitted:
        story = st.text_area("여러분이 창작한 이야기를 입력하세요.", key="initial_story_input")
        if st.button("이야기 점검 시작") and story:
            st.session_state.messages_story_review.append({"role": "user", "content": story})
            st.session_state.story_input_submitted = True
            # Get initial GPT response
            with st.spinner("GPT가 이야기를 점검 중입니다..."):
                gpt_response = ask_gpt(st.session_state.messages_story_review)
                st.session_state.messages_story_review.append({"role": "assistant", "content": gpt_response})
            st.rerun() # Changed from st.experimental_rerun() to st.rerun()

    # Chat input for ongoing conversation
    if st.session_state.story_input_submitted:
        if prompt := st.chat_input("GPT에게 답변하거나 추가 질문을 해보세요."):
            st.session_state.messages_story_review.append({"role": "user", "content": prompt})
            with st.spinner("GPT가 답변을 생성 중입니다..."):
                gpt_response = ask_gpt(st.session_state.messages_story_review)
                st.session_state.messages_story_review.append({"role": "assistant", "content": gpt_response})
            st.rerun() # Changed from st.experimental_rerun() to st.rerun()

    # Optional: A button to reset the conversation
    if st.session_state.story_input_submitted and st.button("대화 초기화", key="reset_story_review_chat"):
        st.session_state.messages_story_review = [
            {"role": "system", "content": (
                "너는 초등학생이 작성한 창작 이야기를 바탕으로, 그 이야기를 Pika 영상으로 만들 수 있도록 도와주는 GPT야.\n"
                "너의 역할은 '소크라테스식 대화법'을 활용하여 학생이 스스로 이야기를 구체화하고 정돈하도록 돕는 것이야.\n"
                "\n"
                "1️⃣ **이야기 명확화**\n"
                "- 먼저 학생이 쓴 이야기를 주의 깊게 읽어.\n"
                "- 내용이 이해되지 않거나 모호하거나 빠져있는 정보(주인공의 특징, 배경, 사건의 성격, 주변 인물 등)가 있다면,\n"
                "  하나의 질문씩만 사용해서 학생이 생각을 더 꺼낼 수 있도록 유도해.\n"
                "- 이야기에 이미 충분히 표현되어 있는 부분은 질문하지 않고 다음 항목으로 넘어가.\n"
                "\n"
                "2️⃣ **인과관계와 사건 흐름 확인**\n"
                "- 이야기 속 사건들이 왜 발생했는지, 사건 간의 연결이 논리적인지를 파악해.\n"
                "- 원인이 불분명하거나 연결이 어색하면, 간단한 예시와 함께 다시 생각할 수 있도록 조언해줘.\n"
                "\n"
                "3️⃣ **이야기 구조(발단-전개-절정-결말) 점검**\n"
                "- 이야기가 발단, 전개, 절정, 결말의 흐름에 맞게 구성되어 있는지 확인해.\n"
                "- 각 단계에 해당하는 내용을 간단히 요약해주고, 빠지거나 흐름이 약한 단계가 있다면 구체적이고 이해하기 쉬운 수정 방향을 제시해줘.\n"
                "\n"
                "4️⃣ **문장 표현 점검**\n"
                "- 이야기에서 어색한 문장이나 표현, 문맥에 맞지 않는 부분이 있다면 명확히 지적해줘.\n"
                "- 직접 고쳐주기보다는 간단한 수정 예시를 들어 학생이 스스로 수정할 수 있도록 도와줘.\n"
                "\n"
                "5️⃣ **종합 피드백 및 보완 방향 제시**\n"
                "- 위 모든 내용을 종합해서 '어떤 부분을 어떻게 수정하면 이야기 전체가 더 명확하고 흥미롭게 개선될 수 있는지'를\n"
                "  구체적이고 학생 눈높이에 맞는 문장으로 설명해줘.\n"
                "- 예를 들어: '이야기의 절정 부분이 조금 약하니까 주인공이 어떤 결정을 하거나 위기를 겪는 장면을 넣어보면 어떨까요?' 같은 말투로.\n"
                "\n"
                "❗ 단, 절대 처음부터 전체 요약이나 평가를 하지 마. 반드시 질문 → 확인 → 구체화 → 평가 → 조언 순서로 진행해야 해.\n"
                "창의성을 존중하고, 칭찬과 격려의 말투를 꼭 유지해줘."
            )}
        ]
        st.session_state.story_input_submitted = False
        st.rerun() # Changed from st.experimental_rerun() to st.rerun()

