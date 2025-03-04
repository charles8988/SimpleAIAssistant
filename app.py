# 简化版AutoAgent应用
# 保存为app.py

import streamlit as st
import requests
import json
import os
from datetime import datetime

# 页面配置
st.set_page_config(page_title="简易智能助手系统", layout="wide")

# 初始化API密钥和模型選擇
if 'api_keys' not in st.session_state:
    st.session_state['api_keys'] = {
        "OpenAI": "",
        "DeepSeek": "",
        # 可以繼續添加其他模型，比如 "Grok": "" 等
    }

if 'selected_model' not in st.session_state:
    st.session_state['selected_model'] = "OpenAI"

# 側邊欄 - API設置和模型選擇
with st.sidebar:
    st.title("設置")
    
    # 選擇大模型
    st.session_state['selected_model'] = st.selectbox(
        "選擇大模型",
        ["OpenAI", "DeepSeek"]  # 可以繼續添加其他模型
    )
    
    # 根據選擇的模型顯示對應的API密钥輸入框
    model = st.session_state['selected_model']
    api_key = st.text_input(f"輸入 {model} API 密钥", type="password", value=st.session_state['api_keys'][model])
    if st.button("保存API密钥"):
        st.session_state['api_keys'][model] = api_key
        st.success(f"{model} API 密钥已保存!")
    
    st.divider()
    st.markdown("## 助手角色")
    agent_type = st.selectbox(
        "選擇助手類型",
        ["通用助手", "創意寫作助手", "程式設計助手", "數據分析助手"]
    )

# 主界面
st.title("简易智能助手系统")
st.markdown(f"這是一個簡化版的多功能AI助手系統，使用 {model} 模型回答問題。")

# 初始化聊天歷史
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# 顯示聊天歷史
for message in st.session_state['messages']:
    role = message['role']
    content = message['content']
    with st.chat_message(role):
        st.write(content)

# 聊天輸入
prompt = st.chat_input("輸入您的問題...")

# 角色提示詞
agent_prompts = {
    "通用助手": "你是一個通用AI助手，請回答用戶的問題。",
    "創意寫作助手": "你是一個專注於創意寫作的AI助手，擅長生成有創意的內容。",
    "程式設計助手": "你是一個程式設計AI助手，專注於提供程式碼和技術解決方案。",
    "數據分析助手": "你是一個數據分析AI助手，擅長解釋數據和提供分析見解。"
}

# 定義不同模型的API配置
MODEL_CONFIGS = {
    "OpenAI": {
        "api_url": "https://api.openai.com/v1/chat/completions",
        "model_name": "gpt-3.5-turbo",
        "headers": lambda api_key: {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        "payload": lambda messages: {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": 0.7
        }
    },
    "DeepSeek": {
        "api_url": "https://api.deepseek.com/v1/chat/completions",
        "model_name": "deepseek-chat",
        "headers": lambda api_key: {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        "payload": lambda messages: {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7
        }
    }
    # 你可以在這裡添加其他模型的配置，例如：
    # "Grok": {
    #     "api_url": "https://api.xai.com/v1/chat/completions",
    #     "model_name": "grok",
    #     "headers": lambda api_key: {...},
    #     "payload": lambda messages: {...}
    # }
}

# 當用戶提交問題時
if prompt and st.session_state['api_keys'][model]:
    # 添加用戶消息到歷史
    st.session_state['messages'].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # 準備發送到 API 的消息
    api_messages = [
        {"role": "system", "content": agent_prompts[agent_type]},
    ]
    
    # 添加聊天歷史
    for message in st.session_state['messages']:
        api_messages.append(message)
    
    # 顯示正在處理的消息
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.write("思考中...")
        
        try:
            # 獲取當前模型的配置
            config = MODEL_CONFIGS[model]
            api_key = st.session_state['api_keys'][model]
            
            # 構建請求
            headers = config["headers"](api_key)
            payload = config["payload"](api_messages)
            
            # 發送請求
            response = requests.post(
                config["api_url"],
                headers=headers,
                json=payload
            )
            
            # 解析並顯示回應
            if response.status_code == 200:
                result = response.json()
                assistant_response = result["choices"][0]["message"]["content"]
                message_placeholder.write(assistant_response)
                # 將助手回應添加到聊天歷史
                st.session_state['messages'].append({"role": "assistant", "content": assistant_response})
            else:
                message_placeholder.write(f"錯誤: {response.text}")
        except Exception as e:
            message_placeholder.write(f"發生錯誤: {str(e)}")
            
elif prompt and not st.session_state['api_keys'][model]:
    st.error(f"請先在側邊欄設置您的 {model} API 密钥!")