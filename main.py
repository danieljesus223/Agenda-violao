import streamlit as st
import requests
import urllib.parse
import pandas as pd

st.set_page_config(page_title="Agenda de Violão", page_icon="🎸")

# --- CONFIGURAÇÕES ---
# Verifique se o seu ID está correto aqui!
SHEETDB_API_URL = "https://sheetdb.io/api/v1/l8lb0csbymhga"
SEU_CELULAR = "5511999999999" 
SENHA_ADMIN = "1234"

menu = st.sidebar.selectbox("Navegação", ["Agendar Aula", "Painel do Professor"])

if menu == "Agendar Aula":
    st.title("🎸 Agende sua Aula")
    
    with st.form(key="form_aula", clear_on_submit=True):
        nome = st.text_input("Seu Nome:")
        data = st.date_input("Dia:")
        horario = st.selectbox("Horário:", ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00"])
        estilo = st.selectbox("Estilo:", ["Violão", "Guitarra"])
        submit = st.form_submit_button("Reservar")

    if submit:
        if not nome:
            st.warning("Coloque seu nome.")
        else:
            data_br = data.strftime('%d/%m/%Y')
            # Garantimos que a hora seja tratada como texto puro
            hora_texto = str(horario)
            
            with st.spinner('Verificando...'):
                try:
                    res_check = requests.get(SHEETDB_API_URL)
                    ocupado = False
                    if res_check.status_code == 200:
                        agenda = res_check.json()
                        if isinstance(agenda, list):
                            for aula in agenda:
                                # Limpa qualquer símbolo estranho para comparar
                                d_plan = str(aula.get('data')).replace("'", "")
                                h_plan = str(aula.get('hora')).replace("'", "")
                                if d_plan == data_br and h_plan == hora_texto:
                                    ocupado = True
                                    break
                    
                    if ocupado:
                        st.error("Horário já ocupado!")
                    else:
                        # Enviamos com o apóstrofo (') para "travar" como texto no Google
                        payload = {"data": [{
                            "aluno": nome, 
                            "data": f"'{data_br}", 
                            "hora": f"'{hora_texto}", 
                            "estilo": estilo
                        }]}
                        requests.post(SHEETDB_API_URL, json=payload)
                        st.success("Agendado!")
                        
                        link = f"https://wa.me/{SEU_CELULAR}?text=Agendei para {data_br} às {hora_texto}"
                        st.markdown(f'[📱 Avisar no WhatsApp]({link})')
                except:
                    st.error("Erro na conexão.")

elif menu == "Painel do Professor":
    st.title("📅 Suas Aulas")
    senha = st.text_input("Senha:", type="password")
    if senha == SENHA_ADMIN:
        if st.button("Ver Agenda"):
            res = requests.get(SHEETDB_API_URL)
            if res.status_code == 200:
                dados = res.json()
                if dados:
                    df = pd.DataFrame(dados)
                    # Forçamos a limpeza visual dos apóstrofos na tabela
                    for col in ['data', 'hora']:
                        if col in df.columns:
                            df[col] = df[col].astype(str).str.replace("'", "")
                    st.table(df)
