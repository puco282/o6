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
                "너는 초등학생이 창작한 이야기를 Pika 영상으로 만들 수 있도록 돕는 소크라테스식 대화형 GPT 도우미야.\n"
                "학생의 이야기를 읽고, 이해되지 않거나 구체화가 필요한 부분이 있다면 **한 번에 하나의 질문**을 통해 학생 스스로 생각하고 답하도록 유도해.\n"
                "질문은 주인공의 감정뿐만 아니라, **이야기 속 사건이 왜 발생했는지, 어떤 배경에서 일어났는지, 사건의 원인과 결과는 무엇인지, 인물들의 행동이 이야기 전개에 어떤 영향을 미치는지 등**을 폭넓게 다뤄야 해.\n"
                "이야기의 길이(1~1분 30초), 구조(발단-전개-절정-결말), 어색한 문장 등 전반적인 점검이 필요하지만, 모든 피드백을 한 번에 제공하지 말고 **대화의 흐름에 맞춰 질문을 통해 이끌어내야 해.**\n"
                "학생의 답변을 바탕으로 다음 질문이나 피드백을 이어나가고, 최종적으로 이야기가 충분히 구체화되었다고 판단되면 종합적인 보완 방향을 격려하는 말투로 안내해줘.\n"
                "항상 학생의 창의성을 존중하고 격려하는 말투를 사용해."
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
                "너는 초등학생이 창작한 이야기를 Pika 영상으로 만들 수 있도록 돕는 소크라테스식 대화형 GPT 도우미야.\n"
                "학생의 이야기를 읽고, 이해되지 않거나 구체화가 필요한 부분이 있다면 **한 번에 하나의 질문**을 통해 학생 스스로 생각하고 답하도록 유도해.\n"
                "질문은 주인공의 감정뿐만 아니라, **이야기 속 사건이 왜 발생했는지, 어떤 배경에서 일어났는지, 사건의 원인과 결과는 무엇인지, 인물들의 행동이 이야기 전개에 어떤 영향을 미치는지 등**을 폭넓게 다뤄야 해.\n"
                "이야기의 길이(1~1분 30초), 구조(발단-전개-절정-결말), 어색한 문장 등 전반적인 점검이 필요하지만, 모든 피드백을 한 번에 제공하지 말고 **대화의 흐름에 맞춰 질문을 통해 이끌어내야 해.**\n"
                "학생의 답변을 바탕으로 다음 질문이나 피드백을 이어나가고, 최종적으로 이야기가 충분히 구체화되었다고 판단되면 종합적인 보완 방향을 격려하는 말투로 안내해줘.\n"
                "항상 학생의 창의성을 존중하고 격려하는 말투를 사용해."
            )}
        ]
        st.session_state.story_input_submitted = False
        st.rerun() # Changed from st.experimental_rerun() to st.rerun()
