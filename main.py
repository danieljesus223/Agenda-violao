import streamlit as st
import requests
import urllib.parse
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Agenda de Violão", page_icon="🎸")

# --- 1. CONFIGURAÇÕES (AJUSTE AQUI) ---
SHEETDB_API_URL = "https://sheetdb.io/api/v1/l8lb0csbymhga"
SEU_CELULAR = "5511999999999" 
SENHA_ADMIN = "1234"

# --- MENU LATERAL ---
menu = st.sidebar.selectbox("Navegação", ["Agendar Aula", "Painel do Professor"])

# --- TELA 1: AGENDAMENTO ---
if menu == "Agendar Aula":
    st.title("🎸 Agende sua Aula de Violão")
    st.write("Escolha o melhor horário para começarmos a tocar!")

    with st.form(key="form_aula", clear_on_submit=True):
        nome = st.text_input("Seu Nome Completo:")
        data = st.date_input("Escolha o Dia:")
        horario = st.selectbox("Escolha o Horário:", ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"])
        estilo = st.selectbox("O que quer aprender?", ["Violão Iniciante", "Violão Intermediário", "Guitarra", "Fingerstyle"])
        
        submit = st.form_submit_button("Verificar Disponibilidade e Reservar")

    if submit:
        if not nome:
            st.warning("Por favor, preencha seu nome.")
        else:
            data_br = data.strftime('%d/%m/%Y')
            
            with st.spinner('Consultando agenda...'):
                try:
                    response_check = requests.get(SHEETDB_API_URL)
                    ocupado = False
                    
                    if response_check.status_code == 200:
                        agenda_atual = response_check.json()
                        if isinstance(agenda_atual, list):
                            for aula in agenda_atual:
                                # Remove apóstrofos para comparar corretamente
                                d_planilha = str(aula.get('data')).replace("'", "")
                                h_planilha = str(aula.get('hora')).replace("'", "")
                                if d_planilha == data_br and h_planilha == str(horario):
                                    ocupado = True
                                    break
                    
                    if ocupado:
                        st.error(f"❌ O horário de {horario} no dia {data_br} já está ocupado.")
                    else:
                        # O segredo: "'" antes da data e da hora força o formato texto
                        payload = {"data": [{
                            "aluno": nome, 
                            "data": f"'{data_br}", 
                            "hora": f"'{horario}", 
                            "estilo": estilo
                        }]}
                        res = requests.post(SHEETDB_API_URL, json=payload)
                        
                        if res.status_code == 201:
                            st.success(f"✅ Sucesso! Aula marcada para {data_br} às {horario}.")
                            st.balloons()
                            
                            mensagem = f"Oi! Sou o {nome} e agendei uma aula de {estilo} para o dia {data_br} às {horario}."
                            link_zap = f"https://wa.me/{SEU_CELULAR}?text={urllib.parse.quote(mensagem)}"
                            
                            st.markdown(f'''
                                <a href="{link_zap}" target="_blank">
                                    <button style="background-color: #25D366; color: white; border: none; padding: 12px; border-radius: 8px; width: 100%; cursor: pointer; font-weight: bold; font-size: 16px;">
                                        📱 Avisar Professor no WhatsApp
                                    </button>
                                </a>
                            ''', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Erro de conexão: {e}")

# --- TELA 2: PAINEL DO PROFESSOR ---
elif menu == "Painel do Professor":
    st.title("📅 Gestão de Aulas")
    senha = st.text_input("Senha de acesso:", type="password")
    
    if senha == SENHA_ADMIN:
        if st.button("Atualizar Lista de Aulas"):
            res = requests.get(SHEETDB_API_URL)
            if res.status_code == 200:
                dados = res.json()
                if dados:
                    df = pd.DataFrame(dados)
                    # Limpa os apóstrofos da visualização para a tabela ficar limpa
                    df['data'] = df['data'].astype(str).str.replace("'", "")
                    df['hora'] = df['hora'].astype(str).str.replace("'", "")
                    st.table(df[["data", "hora", "aluno", "estilo"]])
                else:
                    st.info("Nenhuma aula agendada ainda.")
