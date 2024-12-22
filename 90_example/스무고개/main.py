import os  
import json
import random
import anthropic
import streamlit as st  
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv('CLAUDE')
)

with open('assets/words.json', 'r', encoding='utf-8') as file:
    data = json.load(file)


st.title("스무고개")  

def response_generator(client):
    with client.messages.stream(
        max_tokens=1024,
        system=f"""- 당신은 스무고개를 하는 "스무고개봇"입니다.
                - 현재 [제시어]에 대한 질문을 하면 이에 대해 "예", "아니오"라고만 답해야 한다.
                - [제시어]에 대한 질문에 대해서는 정직하게 대답해야만 해.
                - 절대 [제시어]를 말하면 안된다.
                - 만약에 정답인 [제시어]를 말하면 "정답입니다!" 라고 답해.
                - 너에 대한 소개는 해도 되지만, 그 외 질문은 "예","아니오"로 답할 수 없을 경우, "그건 말씀드릴 수 없어요"라고 해야돼.
                - 만약에 비슷한 질문을 이미 했다면, "이미 물어보신 내용이에요."
                [제시어]: {st.session_state.word}""",
        messages=st.session_state.messages,
        model="claude-3-5-sonnet-20241022",
    ) as stream:
        for text in stream.text_stream:
            yield text

if 'messages' not in st.session_state:  
    st.session_state.messages = []  
if 'tickets' not in st.session_state:  
    st.session_state.tickets = 0  
if 'question_num' not in st.session_state:
    st.session_state.question_num = 20
if 'category' not in st.session_state:
    category = random.choice(list(data.keys()))
    st.session_state.word = random.choice(data[category])
    st.session_state.category = category

st.write(st.session_state.category)

for message in st.session_state.messages:  
    with st.chat_message(message['role']):  
        if message['role'] == 'user':  
            st.write(message['content'])  
        else:  
            st.write(message['content'])

prompt = st.chat_input(f"질문을 해봐요!")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message('user'):
        st.write(prompt)  
    with st.chat_message('assistant'):  
        response = st.write_stream(response_generator(client))
        st.session_state.messages.append({"role": "assistant", "content": response})  # st.write(f"User has sent the following prompt: {prompt}")
        
        if response == "예" or response == "아니오":
            st.session_state.tickets += 1
            announce = f"\n * **{st.session_state.question_num}번 중 {st.session_state.question_num-st.session_state.tickets}번 남았어요!**"
            st.write(announce)
            st.session_state.messages.append({"role": "assistant", "content": announce}) 