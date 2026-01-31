import streamlit as st
import requests
import urllib.parse
import pandas as pd

st.set_page_config(page_title="Agenda de Violão", page_icon="🎸")

# --- 1. CONFIGURAÇÕES (COLOQUE SEUS DADOS AQUI) ---
SHEETDB_API_URL = "https://sheetdb.io/api/v1/SEU_ID_AQUI"
SEU_CELULAR = "5511999999999" 
SENHA_MESTRE = "1234" # Senha para você acessar a lista de alunos

# Inicializa o estado de login do professor
if 'professor_logado' not in st.session_state:
    st.session_state['professor_logado'] = False

# Menu Lateral
menu = st.sidebar.selectbox("Escolha uma opção", ["Agendar Aula", "Painel do Professor"])

# --- TELA 1: AGENDAMENTO (PARA O ALUNO) ---
if menu == "Agendar Aula":
    st.title("🎸 Agende sua Aula de Violão")
    st.write("Escolha seu horário e estilo preferido abaixo.")

    with st.form(key="form_aula", clear_on_submit=True):
        nome = st.text_input("Seu Nome Completo:")
        data = st.date_input("Escolha o Dia:", format="DD/MM/YYYY")
        horario = st.selectbox("Escolha o Horário:", ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"])
        estilo = st.selectbox("O que quer aprender?", ["Violão Iniciante", "Violão Intermediário", "Guitarra", "Fingerstyle"])
        submit = st.form_submit_button("Confirmar Reserva")

    if submit:
        if not nome:
            st.warning("Por favor, digite seu nome.")
        else:
            data_br = data.strftime('%d/%m/%Y')
            hora_texto = str(horario)
            
            with st.spinner('Verificando disponibilidade...'):
                try:
                    res_check = requests.get(SHEETDB_API_URL)
                    ocupado = False
                    if res_check.status_code == 200:
                        agenda = res_check.json()
                        if isinstance(agenda, list):
                            for aula in agenda:
                                d_plan = str(aula.get('data')).replace("'", "")
                                h_plan = str(aula.get('hora')).replace("'", "")
                                if d_plan == data_br and h_plan == hora_texto:
                                    ocupado = True
                                    break
                    
                    if ocupado:
                        st.error(f"❌ O horário {hora_texto} no dia {data_br} já está ocupado.")
                    else:
                        # Salva com apóstrofo para garantir formato texto no Sheets
                        payload = {"data": [{"aluno": nome, "data": f"'{data_br}", "hora": f"'{hora_texto}", "estilo": estilo}]}
                        requests.post(SHEETDB_API_URL, json=payload)
                        
                        st.success(f"✅ Agendado para {data_br} às {hora_texto}!")
                        st.balloons()
                        
                        msg = f"Oi! Agendei minha aula de {estilo} para o dia {data_br} às {hora_texto}."
                        link = f"https://wa.me/{SEU_CELULAR}?text={urllib.parse.quote(msg)}"
                        st.markdown(f'''<a href="{link}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 12px; border-radius: 8px; width: 100%; cursor: pointer; font-weight: bold;">📱 Avisar Professor no WhatsApp</button></a>''', unsafe_allow_html=True)
                except:
                    st.error("Erro ao conectar. Tente novamente.")

# --- TELA 2: PAINEL DO PROFESSOR (COM SENHA) ---
elif menu == "Painel do Professor":
    st.title("🔐 Área Restrita")

    if not st.session_state['professor_logado']:
        senha_input = st.text_input("Digite a senha de professor:", type="password")
        if st.button("Acessar Painel"):
            if senha_input == SENHA_MESTRE:
                st.session_state['professor_logado'] = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
    else:
        st.sidebar.button("Sair/Deslogar", on_click=lambda: st.session_state.update({'professor_logado': False}))
        st.success("Acesso autorizado.")
        
        if st.button("🔄 Atualizar Lista de Alunos"):
            res = requests.get(SHEETDB_API_URL)
            if res.status_code == 200:
                dados = res.json()
                if dados:
                    df = pd.DataFrame(dados)
                    # Limpa os dados para exibição
                    for col in df.columns:
                        df[col] = df[col].astype(str).str.replace("'", "")
                    
                    st.write("### Lista de Agendamentos:")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Ainda não há agendamentos na planilha.")
