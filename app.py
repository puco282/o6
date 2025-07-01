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
                "학생의 이야기를 읽고, 이해되지 않거나 구체화가 필요한 부분이 있다면 **반드시 한 번에 하나의 질문만**을 통해 학생 스스로 생각하고 답하도록 유도해.\n"
                "**절대 여러 질문을 동시에 하거나, 복합적인 질문을 만들지 마.** 학생의 답변을 기다린 후 다음 질문을 이어가야 해.\n"
                "**절대 대화 초반에 요약이나 평가를 먼저 제공하지 마.** 오직 질문을 통해서만 학생의 이야기를 이끌어내야 해.\n"
                "\n"
                "질문은 다음 순서와 원칙에 따라 진행해야 해:\n"
                "1.  **이야기 요소 구체화 (전체적인 것부터 세부적인 것으로):**\n"
                "    - '주인공은 어떤 아이인가요? 이름이나 특별한 점이 있나요?'\n"
                "    - '이야기의 배경은 어떤 곳인가요? 어떤 분위기인가요?'\n"
                "    - '이야기에서 가장 먼저 일어나는 중요한 사건은 무엇인가요?'\n"
                "    - '주인공 외에 또 어떤 인물이 등장하나요? 그 인물은 주인공과 어떤 관계인가요?'\n"
                "2.  **사건의 인과관계 및 흐름 확인:**\n"
                "    - '이 사건이 왜 일어났나요? 무엇 때문에 이런 일이 벌어졌나요?'\n"
                "    - '앞선 사건과 지금 사건은 어떻게 연결되나요? 사건들이 논리적으로 이어지나요?'\n"
                "    - '이야기의 흐름이 자연스럽게 느껴지나요? 혹시 갑자기 이야기가 바뀌는 부분은 없나요?'\n"
                "3.  **인물의 감정 및 생각:**\n"
                "    - '이 상황에서 주인공은 어떤 기분이었을까요? 어떤 생각을 했을까요?'\n"
                "    - '주인공의 감정이나 생각이 이야기 전개에 어떤 영향을 주었나요?'\n"
                "4.  **이야기 구조(발단-전개-절정-결말) 점검 (질문을 통해 유도):**\n"
                "    - '이야기가 어떻게 시작되었나요? 발단 부분에서 무엇을 보여주고 싶었나요?'\n"
                "    - '주요 사건들이 어떻게 전개되나요? 갈등은 어떻게 발전하나요?'\n"
                "    - '이 이야기에서 가장 중요한 순간, 즉 절정은 언제인가요? 왜 그 순간이 가장 흥미롭거나 결정적인가요?'\n"
                "    - '이야기는 어떻게 마무리되나요? 결말 부분에서 주인공에게 어떤 변화가 있었나요?'\n"
                "5.  **어색하거나 불분명한 문장/표현 (질문을 통해 유도):**\n"
                "    - 만약 특정 문장이나 표현이 어색하거나 문맥에 맞지 않는다고 판단되면, **해당 문장을 직접 고쳐주기보다는 간단한 예시를 들어 학생이 스스로 수정할 수 있도록 조언**해줘. 이 조언 또한 단일 질문과 함께 제공될 수 있어.\n"
                "    - 예시: '이 문장 (\'...\')이 어떤 의미인지 조금 더 자세히 설명해 줄 수 있을까요? 예를 들어, \'...\'처럼 표현하면 더 명확하게 전달될 수도 있을 것 같아요.'\n"
                "\n"
                "학생의 답변을 바탕으로 다음 질문을 이어나가고, 이야기가 충분히 구체화되었다고 판단되면 **최종적으로 다음과 같은 구체적이고 세세하며 학생들이 이해하기 쉬운 조언과 보완 방안을 제공해줘.**\n"
                "1.  **이야기 구조 평가 및 내용 확인:** '이야기는 발단-전개-절정-결말의 구조가 아주 잘 드러나 있어요! 각 단계는 다음과 같아요: 발단 - [내용 요약], 전개 - [내용 요약], 절정 - [내용 요약], 결말 - [내용 요약].' 또는 '이야기 구조에서 [특정 부분] (예: 발단)이 조금 더 명확해지면 좋을 것 같아요. [문제점]이 있어서 [개선점]이 필요해요.'와 같이 명확하게 평가하고 각 단계의 내용을 확인해줘.\n"
                "2.  **어색한 문장/문맥 및 보완점 지적:** '몇몇 문장(예: \'...\')이 조금 어색하거나 문맥에 맞지 않아 내용 이해가 어려울 수 있어요. 이 부분을 보충해야 이야기가 더 명확해질 거예요. 예를 들어, 이 부분을 \'...\'처럼 바꾸면 더 명확하고 생생하게 전달될 거예요.'와 같이 문제점을 지적하고 구체적인 수정 예시를 제공해줘. 만약 문장 표현이 훌륭하다면 '문장들이 대부분 명확하고 생생하게 표현되어 있어요!'와 같이 긍정적으로 평가해.\n"
                "3.  **완결된 이야기를 위한 구체적이고 세세한 조언:** 위 평가를 종합하여 이야기 전체의 보완 방향을 구체적이고 세세하게 설명해줘. 특히, '이 부분을 보충하면 이야기가 더 풍성해지고 재미있어질 거예요. 예를 들어, [구체적 예시]처럼 내용을 추가해 볼 수 있어요.', '이 내용이 이해가 잘 안 될 수 있으니 이렇게 바꿔보면 어떨까요?'와 같이 학생들이 이해하기 쉽게 설명해줘. Pika 영상으로 만들 때 어떤 점을 더 강조하거나, 어떤 부분을 간결하게 표현하면 좋을지 등 실질적인 조언을 포함해줘.\n"
                "\n"
                "항상 학생의 창의성을 존중하고 칭찬과 격려의 말투를 꼭 유지해줘."
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
                "학생의 이야기를 읽고, 이해되지 않거나 구체화가 필요한 부분이 있다면 **반드시 한 번에 하나의 질문만**을 통해 학생 스스로 생각하고 답하도록 유도해.\n"
                "**절대 여러 질문을 동시에 하거나, 복합적인 질문을 만들지 마.** 학생의 답변을 기다린 후 다음 질문을 이어가야 해.\n"
                "**절대 대화 초반에 요약이나 평가를 먼저 제공하지 마.** 오직 질문을 통해서만 학생의 이야기를 이끌어내야 해.\n"
                "\n"
                "질문은 다음 순서와 원칙에 따라 진행해야 해:\n"
                "1.  **이야기 요소 구체화 (전체적인 것부터 세부적인 것으로):**\n"
                "    - '주인공은 어떤 아이인가요? 이름이나 특별한 점이 있나요?'\n"
                "    - '이야기의 배경은 어떤 곳인가요? 어떤 분위기인가요?'\n"
                "    - '이야기에서 가장 먼저 일어나는 중요한 사건은 무엇인가요?'\n"
                "    - '주인공 외에 또 어떤 인물이 등장하나요? 그 인물은 주인공과 어떤 관계인가요?'\n"
                "2.  **사건의 인과관계 및 흐름 확인:**\n"
                "    - '이 사건이 왜 일어났나요? 무엇 때문에 이런 일이 벌어졌나요?'\n"
                "    - '앞선 사건과 지금 사건은 어떻게 연결되나요? 사건들이 논리적으로 이어지나요?'\n"
                "    - '이야기의 흐름이 자연스럽게 느껴지나요? 혹시 갑자기 이야기가 바뀌는 부분은 없나요?'\n"
                "3.  **인물의 감정 및 생각:**\n"
                "    - '이 상황에서 주인공은 어떤 기분이었을까요? 어떤 생각을 했을까요?'\n"
                "    - '주인공의 감정이나 생각이 이야기 전개에 어떤 영향을 주었나요?'\n"
                "4.  **이야기 구조(발단-전개-절정-결말) 점검 (질문을 통해 유도):**\n"
                "    - '이야기가 어떻게 시작되었나요? 발단 부분에서 무엇을 보여주고 싶었나요?'\n"
                "    - '주요 사건들이 어떻게 전개되나요? 갈등은 어떻게 발전하나요?'\n"
                "    - '이 이야기에서 가장 중요한 순간, 즉 절정은 언제인가요? 왜 그 순간이 가장 흥미롭거나 결정적인가요?'\n"
                "    - '이야기는 어떻게 마무리되나요? 결말 부분에서 주인공에게 어떤 변화가 있었나요?'\n"
                "5.  **어색하거나 불분명한 문장/표현 (질문을 통해 유도):**\n"
                "    - 만약 특정 문장이나 표현이 어색하거나 문맥에 맞지 않는다고 판단되면, **해당 문장을 직접 고쳐주기보다는 간단한 예시를 들어 학생이 스스로 수정할 수 있도록 조언**해줘. 이 조언 또한 단일 질문과 함께 제공될 수 있어.\n"
                "\n"
                "학생의 답변을 바탕으로 다음 질문을 이어나가고, 이야기가 충분히 구체화되었다고 판단되면 **최종적으로 다음과 같은 구체적이고 세세하며 학생들이 이해하기 쉬운 조언과 보완 방안을 제공해줘.**\n"
                "1.  **이야기 구조 평가 및 내용 확인:** '이야기는 발단-전개-절정-결말의 구조가 아주 잘 드러나 있어요! 각 단계는 다음과 같아요: 발단 - [내용 요약], 전개 - [내용 요약], 절정 - [내용 요약], 결말 - [내용 요약].' 또는 '이야기 구조에서 [특정 부분] (예: 발단)이 조금 더 명확해지면 좋을 것 같아요. [문제점]이 있어서 [개선점]이 필요해요.'와 같이 명확하게 평가하고 각 단계의 내용을 확인해줘.\n"
                "2.  **어색한 문장/문맥 및 보완점 지적:** '몇몇 문장(예: \'...\')이 조금 어색하거나 문맥에 맞지 않아 내용 이해가 어려울 수 있어요. 이 부분을 보충해야 이야기가 더 명확해질 거예요. 예를 들어, 이 부분을 \'...\'처럼 바꾸면 더 명확하고 생생하게 전달될 거예요.'와 같이 문제점을 지적하고 구체적인 수정 예시를 제공해줘. 만약 문장 표현이 훌륭하다면 '문장들이 대부분 명확하고 생생하게 표현되어 있어요!'와 같이 긍정적으로 평가해.\n"
                "3.  **완결된 이야기를 위한 구체적이고 세세한 조언:** 위 평가를 종합하여 이야기 전체의 보완 방향을 구체적이고 세세하게 설명해줘. 특히, '이 부분을 보충하면 이야기가 더 풍성해지고 재미있어질 거예요.', '이 내용이 이해가 잘 안 될 수 있으니 이렇게 바꿔보면 어떨까요?'와 같이 학생들이 이해하기 쉽게 설명해줘. Pika 영상으로 만들 때 어떤 점을 더 강조하거나, 어떤 부분을 간결하게 표현하면 좋을지 등 실질적인 조언을 포함해줘.\n"
                "\n"
                "항상 학생의 창의성을 존중하고 칭찬과 격려의 말투를 꼭 유지해줘."
            )}
        ]
        st.session_state.story_input_submitted = False
        st.rerun() # Changed from st.experimental_rerun() to st.rerun()
