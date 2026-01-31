import streamlit as st
import requests
import urllib.parse
import pandas as pd

st.set_page_config(page_title="Agenda de Violão", page_icon="🎸")

# --- CONFIGURAÇÕES ---
SHEETDB_API_URL = "https://sheetdb.io/api/v1/l8lb0csbymhga"
SEU_CELULAR = "5511999999999" 
SENHA_ADMIN = "1234"

menu = st.sidebar.selectbox("Navegação", ["Agendar Aula", "Painel do Professor"])

# --- TELA 1: AGENDAMENTO ---
if menu == "Agendar Aula":
    st.title("🎸 Agende sua Aula")
    
    with st.form(key="form_aula", clear_on_submit=True):
        nome = st.text_input("Seu Nome:")
        # O format="DD/MM/YYYY" muda a exibição para o usuário
        data = st.date_input("Dia:", format="DD/MM/YYYY")
        horario = st.selectbox("Horário:", ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00"])
        estilo = st.selectbox("Estilo:", ["Violão", "Guitarra"])
        submit = st.form_submit_button("Reservar")

    if submit:
        if not nome:
            st.warning("Coloque seu nome.")
        else:
            # Criamos a data formatada para exibição e salvamento
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
                        payload = {"data": [{
                            "aluno": nome, 
                            "data": f"'{data_br}", 
                            "hora": f"'{hora_texto}", 
                            "estilo": estilo
                        }]}
                        requests.post(SHEETDB_API_URL, json=payload)
                        
                        # Aqui o usuário vê a data certa na mensagem de sucesso
                        st.success(f"✅ Agendado para {data_br} às {hora_texto}!")
                        st.balloons()
                        
                        msg = f"Oi! Agendei minha aula de {estilo} para o dia {data_br} às {hora_texto}."
                        link = f"https://wa.me/{SEU_CELULAR}?text={urllib.parse.quote(msg)}"
                        st.markdown(f'''<a href="{link}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px; border-radius: 5px; width: 100%; cursor: pointer; font-weight: bold;">📱 Avisar Professor no WhatsApp</button></a>''', unsafe_allow_html=True)
                except:
                    st.error("Erro na conexão com a agenda.")

# --- TELA 2: ADMIN ---
elif menu == "Painel do Professor":
    st.title("📅 Gestão de Aulas")
    senha = st.text_input("Senha de acesso:", type="password")
    
    if senha == SENHA_ADMIN:
        if st.button("Atualizar Lista"):
            res = requests.get(SHEETDB_API_URL)
            if res.status_code == 200:
                dados = res.json()
                if dados:
                    df = pd.DataFrame(dados)
                    for col in df.columns:
                        df[col] = df[col].astype(str).str.replace("'", "")
                    
                    st.write("Agendamentos:")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Nenhuma aula agendada ainda.")
    elif senha != "":
        st.error("Senha incorreta!")
