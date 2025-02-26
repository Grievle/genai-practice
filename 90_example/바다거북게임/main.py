import os  
import json
import random
import anthropic
import streamlit as st  
from dotenv import load_dotenv
import uuid

load_dotenv()

import sqlite3
import datetime

def init_db():

    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()

    # 로그 테이블 생성
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs 
                    (id TEXT PRIMARY KEY, 
                    uuid TEXT,
                    name TEXT, 
                    q_number INTEGER,
                    user_question TEXT,
                    ai_answer TEXT,
                    date_time TEXT)''')
    conn.commit()


def log_to_database(uuid, name, q_number, user_question, ai_answer, print_to_console=True):
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()

    current_time = datetime.datetime.now()
    print(f"{current_time}: {id}, {name}, {q_number}, {user_question}, {ai_answer}")
    cursor.execute("INSERT INTO logs (uuid, name, q_number, user_question, ai_answer, date_time) VALUES (?, ?, ?, ?, ?, ?)", 
                   (uuid, name, q_number, user_question, ai_answer, current_time))
    conn.commit()
    
    if print_to_console:
        print(f"{current_time}: {uuid}, {name}, {q_number}, {user_question}, {ai_answer}")

name = st.text_input("이름을 작성해주세요")

if name:
    init_db()
    st.write("오셨군요")
    client = anthropic.Anthropic(
        api_key=os.getenv('CLAUDE')
    )

    with open('questions/words.json', 'r', encoding='utf-8') as file:
        data = json.load(file)


    st.title("바다스프게임")  
    option = st.selectbox(
        "문제를 골라주세요.",
        tuple([f"{i+1}번 문제" for i in range(len(data))]),
    )

    def response_generator(client):
        with client.messages.stream(
            max_tokens=1024,
            system=f"""- 당신은 "바다거북스프게임"을 하는 "바다거북스프봇"입니다.
                    - 현재 [제시 상황]에 대한 질문을 하면 이에 대해 "예", "아니오"라고만 답해야 한다.
                    - [제시 상황]에 대한 질문에 대해서는 정직하게 대답해야만 해.
                    - 절대 [제시 상황]을 말하면 안된다.
                    - 만약에 정답인 [제시 상황]을 말하면 "정답입니다!" 라고 답해.
                    - 너에 대한 소개는 해도 되지만, 그 외 질문은 "예","아니오","그건 중요하지 않아요"로 답할 수 없을 경우, "그건 말씀드릴 수 없어요"라고 해야돼.
                    - 만약에 비슷한 질문을 이미 했다면, "이미 물어보신 내용이에요."
                    [제시 상황]: {st.session_state.word}""",
            messages=st.session_state.messages,
            model="claude-3-5-sonnet-20241022",
        ) as stream:
            for text in stream.text_stream:
                yield text
    if 'messages' not in st.session_state or option not in st.session_state or st.session_state.option != option:  
        st.session_state.messages = []
        st.session_state.option = option
        st.session_state.uuid = str(uuid.uuid4())
    if 'word' not in st.session_state:
        st.session_state.word = data[int(option.split('번')[0])-1]['answer']

    st.markdown(data[int(option.split('번')[0])-1]['question'])

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
        log_to_database(st.session_state.uuid, name, int(option.split('번')[0])-1, prompt, response)
