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
                "학생의 이야기를 읽고, 이해되지 않거나 구체화가 필요한 부분이 있다면 **오직 하나의 질문만**을 통해 학생 스스로 생각하고 답하도록 유도해.\n"
                "**절대 요약이나 평가를 먼저 제공하지 마.** 오직 질문을 통해서만 학생의 이야기를 이끌어내야 해.\n"
                "질문은 다음 요소들을 순차적으로 또는 필요에 따라 깊이 있게 다뤄야 해:\n"
                "- 이야기의 시작(발단): 왜 이런 일이 시작되었는지, 배경은 무엇인지, 주인공은 어떤 상황에 처해 있는지 등.\n"
                "- 사건의 전개: 주요 사건들이 어떻게 연결되는지, 인물들의 행동이 다음 사건에 어떤 영향을 미치는지, 갈등은 어떻게 발전하는지 등.\n"
                "- 이야기의 전환점/절정: 가장 중요한 순간은 언제인지, 왜 그 순간이 중요한지, 주인공에게 어떤 변화가 일어나는지 등.\n"
                "- 이야기의 마무리(결말): 모든 갈등이 어떻게 해결되는지, 주인공은 무엇을 배웠는지, 이야기가 주는 메시지는 무엇인지 등.\n"
                "- 이야기의 전체적인 흐름과 자연스러움: 사건들이 논리적으로 연결되는지, 시간의 흐름은 명확한지 등.\n"
                "- 어색하거나 불분명한 문장: 해당 문장을 직접 고쳐주지 말고, 예를 들어 '이 부분을 좀 더 생생하게 표현하려면 어떤 단어를 쓸 수 있을까?' 와 같이 학생이 스스로 더 명확하게 표현하도록 조언해.\n"
                "학생의 답변을 바탕으로 다음 질문을 이어나가고, 이야기가 충분히 구체화되었다고 판단되면 **최종적으로 Pika 영상 제작을 위한 종합적인 조언과 보완 방향**을 격려하는 말투로 안내해줘. 이때까지는 질문만 해야 해.\n"
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
                "**절대 요약이나 평가를 먼저 제공하지 마.** 오직 질문을 통해서만 학생의 이야기를 이끌어내야 해.\n"
                "질문은 다음 요소들을 순차적으로 또는 필요에 따라 깊이 있게 다뤄야 해:\n"
                "- 이야기의 시작(발단): 왜 이런 일이 시작되었는지, 배경은 무엇인지, 주인공은 어떤 상황에 처해 있는지 등.\n"
                "- 사건의 전개: 주요 사건들이 어떻게 연결되는지, 인물들의 행동이 다음 사건에 어떤 영향을 미치는지, 갈등은 어떻게 발전하는지 등.\n"
                "- 이야기의 전환점/절정: 가장 중요한 순간은 언제인지, 왜 그 순간이 중요한지, 주인공에게 어떤 변화가 일어나는지 등.\n"
                "- 이야기의 마무리(결말): 모든 갈등이 어떻게 해결되는지, 주인공은 무엇을 배웠는지, 이야기가 주는 메시지는 무엇인지 등.\n"
                "- 이야기의 전체적인 흐름과 자연스러움: 사건들이 논리적으로 연결되는지, 시간의 흐름은 명확한지 등.\n"
                "- 어색하거나 불분명한 문장: 해당 문장을 직접 고쳐주지 말고, 예를 들어 '이 부분을 좀 더 생생하게 표현하려면 어떤 단어를 쓸 수 있을까?' 와 같이 학생이 스스로 더 명확하게 표현하도록 조언해.\n"
                "학생의 답변을 바탕으로 다음 질문을 이어나가고, 이야기가 충분히 구체화되었다고 판단되면 **최종적으로 Pika 영상 제작을 위한 종합적인 조언과 보완 방향**을 격려하는 말투로 안내해줘. 이때까지는 질문만 해야 해.\n"
                "항상 학생의 창의성을 존중하고 격려하는 말투를 사용해."
            )}
        ]
        st.session_state.story_input_submitted = False
        st.rerun() # Changed from st.experimental_rerun() to st.rerun()
