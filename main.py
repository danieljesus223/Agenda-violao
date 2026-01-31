import streamlit as st
import requests
import urllib.parse
import pandas as pd

st.set_page_config(page_title="Agenda de Violão", page_icon="🎸")

# --- 1. CONFIGURAÇÕES ---
SHEETDB_API_URL = "https://sheetdb.io/api/v1/SEU_ID_AQUI"
SEU_CELULAR = "5511999999999" 
SENHA_MESTRE = "1234"

if 'professor_logado' not in st.session_state:
    st.session_state['professor_logado'] = False

menu = st.sidebar.selectbox("Navegação", ["Agendar Aula", "Painel do Professor"])

# --- TELA 1: AGENDAMENTO ---
if menu == "Agendar Aula":
    st.title("🎸 Agende sua Aula")
    
    with st.form(key="form_aula", clear_on_submit=True):
        nome = st.text_input("Seu Nome Completo:")
        whatsapp_aluno = st.text_input("Seu WhatsApp (com DDD):", placeholder="Ex: 11999998888")
        email_aluno = st.text_input("Seu E-mail:")
        data = st.date_input("Escolha o Dia:", format="DD/MM/YYYY")
        horario = st.selectbox("Horário:", ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"])
        estilo = st.selectbox("Estilo:", ["Violão Iniciante", "Violão Intermediário", "Guitarra", "Fingerstyle"])
        submit = st.form_submit_button("Confirmar Reserva")

    if submit:
        if not nome or not whatsapp_aluno or not email_aluno:
            st.warning("Por favor, preencha o Nome, WhatsApp e E-mail.")
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
                                if str(aula.get('data')).replace("'", "") == data_br and str(aula.get('hora')).replace("'", "") == hora_texto:
                                    ocupado = True
                                    break
                    
                    if ocupado:
                        st.error(f"❌ O horário {hora_texto} no dia {data_br} já está ocupado.")
                    else:
                        # Salva todos os dados na planilha
                        payload = {"data": [{
                            "aluno": nome, 
                            "whatsapp": f"'{whatsapp_aluno}", 
                            "email": email_aluno,
                            "data": f"'{data_br}", 
                            "hora": f"'{hora_texto}", 
                            "estilo": estilo
                        }]}
                        requests.post(SHEETDB_API_URL, json=payload)
                        
                        st.success(f"✅ Agendado para {data_br} às {hora_texto}!")
                        st.balloons()
                        
                        msg = f"Oi! Sou o {nome}. Agendei minha aula de {estilo} para o dia {data_br} às {hora_texto}."
                        link = f"https://wa.me/{SEU_CELULAR}?text={urllib.parse.quote(msg)}"
                        st.markdown(f'''<a href="{link}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 12px; border-radius: 8px; width: 100%; cursor: pointer; font-weight: bold;">📱 Avisar Professor no WhatsApp</button></a>''', unsafe_allow_html=True)
                except:
                    st.error("Erro na conexão.")

# --- TELA 2: PAINEL DO PROFESSOR ---
elif menu == "Painel do Professor":
    st.title("🔐 Área do Professor")

    if not st.session_state['professor_logado']:
        senha_input = st.text_input("Senha:", type="password")
        if st.button("Entrar"):
            if senha_input == SENHA_MESTRE:
                st.session_state['professor_logado'] = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
    else:
        st.sidebar.button("Sair", on_click=lambda: st.session_state.update({'professor_logado': False}))
        
        if st.button("🔄 Atualizar Lista"):
            res = requests.get(SHEETDB_API_URL)
            if res.status_code == 200:
                dados = res.json()
                if dados:
                    df = pd.DataFrame(dados)
                    for col in df.columns:
                        df[col] = df[col].astype(str).str.replace("'", "")
                    
                    st.write("### Próximas Aulas:")
                    # Exibe a tabela completa com e-mail e whatsapp
                    st.dataframe(df[["data", "hora", "aluno", "whatsapp", "email", "estilo"]], use_container_width=True)
                else:
                    st.info("Nenhum agendamento encontrado.")
