import streamlit as st
import requests
import urllib.parse

st.set_page_config(page_title="Agenda Violão", page_icon="🎸")

st.image("https://images.unsplash.com/photo-1510915361894-db8b60106cb1?q=80&w=500", caption="A música transforma vidas.")

# --- CONFIGURAÇÃO ---
# Verifique se o ID abaixo é o mesmo do seu SheetDB
SHEETDB_API_URL = "https://sheetdb.io/api/v1/l8lb0csbymhga"
SEU_CELULAR = "5511999999999" 

st.title("🎸 Agende sua Aula"

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
        with st.spinner('Consultando agenda...'):
            try:
                response_check = requests.get(SHEETDB_API_URL)
                if response_check.status_code == 200:
                    agenda_atual = response_check.json()
                    
                    # Lógica para evitar o KeyError
                    ocupado = False
                    if isinstance(agenda_atual, list) and len(agenda_atual) > 0:
                        for aula in agenda_atual:
                            # .get evita erro se a coluna não existir
                            if str(aula.get('data')) == str(data) and str(aula.get('hora')) == str(horario):
                                ocupado = True
                                break
                    
                    if ocupado:
                        st.error(f"❌ O horário de {horario} no dia {data.strftime('%d/%m')} já está ocupado.")
                    else:
                        # PASSO 2: SALVAR
                        payload = {"data": [{"aluno": nome, "data": str(data), "hora": horario, "estilo": estilo}]}
                        res = requests.post(SHEETDB_API_URL, json=payload)
                        
                        if res.status_code == 201:
                            st.success("✅ Reservado com sucesso!")
                            texto_zap = f"Oi! Agendei minha aula de {estilo} para {data} às {horario}."
                            link_whatsapp = f"https://wa.me/{SEU_CELULAR}?text={urllib.parse.quote(texto_zap)}"
                            st.markdown(f'<a href="{link_whatsapp}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px; border-radius: 5px; width: 100%; cursor: pointer;">📱 Avisar Professor</button></a>', unsafe_allow_html=True)
                else:
                    st.error("Erro ao acessar a planilha. Verifique o ID do SheetDB.")
            except Exception as e:
                st.error(f"Erro inesperado: {e}")
