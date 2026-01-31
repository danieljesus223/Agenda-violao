import streamlit as st
import requests
import urllib.parse

st.set_page_config(page_title="Agenda Violão", page_icon="🎸")

# --- CONFIGURAÇÃO ---
SHEETDB_API_URL = "https://sheetdb.io/api/v1/l8lb0csbymhga"
SEU_CELULAR = "5511999999999"

st.title("🎸 Agende sua Aula")

with st.form(key="form_aula"):
    nome = st.text_input("Seu Nome:")
    data = st.date_input("Escolha o Dia:")
    horario = st.selectbox("Escolha o Horário:", ["09:00", "10:00", "11:00", "14:00", "15:00"])
    estilo = st.selectbox("Estilo:", ["Violão", "Guitarra"])
    submit = st.form_submit_button("Verificar e Reservar")

if submit:
    if not nome:
        st.warning("Por favor, digite seu nome.")
    else:
        # --- PASSO 1: VERIFICAR SE O HORÁRIO JÁ ESTÁ OCUPADO ---
        with st.spinner('Consultando agenda...'):
            response_check = requests.get(SHEETDB_API_URL)
            
            if response_check.status_code == 200:
                agenda_atual = response_check.json()
                
                # Procura na lista da planilha se já tem a mesma data e hora
                # --- PASSO 1: VERIFICAR SE O HORÁRIO JÁ ESTÁ OCUPADO ---
with st.spinner('Consultando agenda...'):
    response_check = requests.get(SHEETDB_API_URL)
    
    if response_check.status_code == 200:
        agenda_atual = response_check.json()
        
        # Se a planilha tiver dados, verificamos. Se estiver vazia, pulamos.
        ocupado = False
        if isinstance(agenda_atual, list) and len(agenda_atual) > 0:
            for aula in agenda_atual:
                # O .get() evita o erro KeyError se a coluna sumir
                d = aula.get('data')
                h = aula.get('hora')
                if str(d) == str(data) and str(h) == str(horario):
                    ocupado = True
                    break
        
        if ocupado:
            st.error(f"❌ O horário de {horario} no dia {data.strftime('%d/%m')} já está ocupado.")
        else:
            # Segue para o código de salvar...

                        # Link do WhatsApp
                        texto_zap = f"Oi! Agendei minha aula de {estilo} para {data} às {horario}."
                        link_whatsapp = f"https://wa.me/{SEU_CELULAR}?text={urllib.parse.quote(texto_zap)}"
                        st.markdown(f'<a href="{link_whatsapp}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px; border-radius: 5px; width: 100%;">📱 Avisar Professor</button></a>', unsafe_allow_html=True)
            else:
                st.error("Erro ao acessar a agenda. Tente novamente.")
