import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import altair as alt
import time
import zipfile

import openai
from dotenv import load_dotenv, find_dotenv
import streamlit as st
import requests
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv(find_dotenv())

# Configurar a API da OpenAI com a chave API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Função para gerar respostas usando a API da OpenAI
def gerar_resposta(mensagens):
    resposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=mensagens
    )
    return resposta['choices'][0]['message']['content'].strip()

# Função para obter dicas de fitness do Fitness Coach
def obter_dica_fitness():
    url = "https://api.fitnesscoach.ai/dicas"
    headers = {
        "Authorization": "Bearer SEU_TOKEN_AQUI"  # Substitua pelo token de autenticação fornecido pela API
    }
    resposta = requests.get(url, headers=headers)
    if resposta.status_code == 200:
        dados = resposta.json()
        return dados["dica"]
    else:
        return "Desculpe, não consegui obter uma dica de fitness no momento."

# Interface do Usuário com Streamlit
st.title("Assistente Personal Trainer")

# Variáveis de sessão para armazenar o estado da conversa
if 'mensagens' not in st.session_state:
    st.session_state['mensagens'] = [{"role": "system", "content": "Você é um assistente personal trainer."}]
if 'historico' not in st.session_state:
    st.session_state['historico'] = []
if 'nome' not in st.session_state:
    st.session_state['nome'] = ""
if 'input_key' not in st.session_state:
    st.session_state['input_key'] = "input_1"

# Mostrar o nome do usuário
if st.session_state['nome']:
    st.write(f"Olá, {st.session_state['nome']}!")

# Mostrar histórico da conversa
for chat in st.session_state['historico']:
    st.write(f"{chat['role']}: {chat['content']}")

# Entrada do usuário
def enviar_mensagem():
    entrada_usuario = st.session_state[st.session_state['input_key']]
    if entrada_usuario:
        # Adicionar a mensagem do usuário ao histórico
        st.session_state['mensagens'].append({"role": "user", "content": entrada_usuario})
        st.session_state['historico'].append({"role": "Você", "content": entrada_usuario})
        
        # Se a mensagem do usuário solicitar uma dica de fitness
        if "dica" in entrada_usuario.lower():
            # Obter a dica de fitness do Fitness Coach
            dica_fitness = obter_dica_fitness()
            # Adicionar a dica de fitness ao histórico
            st.session_state['mensagens'].append({"role": "assistant", "content": dica_fitness})
            st.session_state['historico'].append({"role": "Assistente", "content": dica_fitness})
        else:
            # Gerar resposta do assistente
            resposta = gerar_resposta(st.session_state['mensagens'])
        
            # Adicionar a resposta do assistente ao histórico
            st.session_state['mensagens'].append({"role": "assistant", "content": resposta})
            st.session_state['historico'].append({"role": "Assistente", "content": resposta})
        
        # Extrair o nome do usuário se ainda não foi feito
        if not st.session_state['nome']:
            st.session_state['nome'] = entrada_usuario
        
        # Resetar o input
        st.session_state[st.session_state['input_key']] = ""

# Configurar o input para enviar a mensagem ao pressionar Enter
input_key = st.session_state['input_key']
if st.session_state['nome']:
    st.text_input(f"Olá, {st.session_state['nome']}, digite aqui:", key=input_key, on_change=enviar_mensagem)
else:
    st.text_input("Olá, digite aqui seu nome:", key=input_key, on_change=enviar_mensagem)

# Inicializar a conversa
if 'iniciado' not in st.session_state:
    st.session_state['mensagens'].append({"role": "assistant", "content": "Olá, sou seu Personal Trainer. Qual é o seu nome?"})
    st.session_state['historico'].append({"role": "Assistente", "content": "Olá, sou seu Personal Trainer. Qual é o seu nome?"})
    st.session_state['iniciado'] = True
