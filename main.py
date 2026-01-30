
import streamlit as st
import requests
import urllib.parse # Para formatar o texto do WhatsApp

st.set_page_config(page_title="Agenda Violão", page_icon="🎸")

# --- CONFIGURAÇÃO ---
# Substitua pelo seu ID do SheetDB
SHEETDB_API_URL = "https://sheetdb.io/api/v1/SEU_ID_AQUI"
SEU_CELULAR = "5511999999999"  # Seu número com DDD (ex: 55 + DDD + Numero)

menu = st.sidebar.selectbox("Ir para:", ["Agendar Aula", "Painel Professor"])

if menu == "Agendar Aula":
    st.title("🎸 Agende sua Aula")
    
    with st.form(key="form_aula"):
        nome = st.text_input("Seu Nome:")
        data = st.date_input("Data:")
        horario = st.selectbox("Horário:", ["09:00", "10:00", "14:00", "15:00"])
        estilo = st.selectbox("Estilo:", ["Violão", "Guitarra"])
        
        submit = st.form_submit_button("Confirmar na Agenda")

    if submit:
        if nome:
            # 1. Salva na Planilha via SheetDB
            payload = {"data": [{"aluno": nome, "data": str(data), "hora": horario, "estilo": estilo}]}
            res = requests.post(SHEETDB_API_URL, json=payload)
            
            if res.status_code == 201:
                st.success("✅ Reservado na agenda!")
                
                # 2. Gera link do WhatsApp
                texto_zap = f"Oi! Sou o {nome} e acabei de agendar uma aula de {estilo} para o dia {data} às {horario}."
                texto_formatado = urllib.parse.quote(texto_zap)
                link_whatsapp = f"https://wa.me/{SEU_CELULAR}?text={texto_formatado}"
                
                # Botão especial de WhatsApp
                st.markdown(f"""
                    <a href="{link_whatsapp}" target="_blank">
                        <button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; width: 100%;">
                            📱 Avisar Professor no WhatsApp
                        </button>
                    </a>
                """, unsafe_allow_stdio=False, unsafe_allow_html=True)
            else:
                st.error("Erro ao salvar. Verifique o ID da API.")
        else:
            st.warning("Por favor, digite seu nome.")

elif menu == "Painel Professor":
    # (Código do painel que fizemos antes...)
    st.title("Admin")
    st.write("Aqui você visualiza os dados salvos.")
