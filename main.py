import streamlit as st
import requests
import urllib.parse
import pandas as pd

# Configurações Iniciais
st.set_page_config(page_title="Agenda de Violão", page_icon="🎸", layout="centered")

# --- ESTILIZAÇÃO (CSS) ---
# Aqui adicionamos a imagem de fundo e deixamos os campos mais bonitos
# --- ESTILIZAÇÃO (CSS) ---

# --- ESTILIZAÇÃO (CSS) ---
# --- ESTILIZAÇÃO (CSS) ---
# --- ESTILIZAÇÃO (CSS) ---
st.markdown(
    f"""
    <style>
    /* 1. Remove o botão de Deploy e o badge do GitHub */
    .stDeployButton {{
        display: none !important;
    }}
    .st-emotion-cache-12fmjuu {{
        display: none !important;
    }}
    
    /* 2. Remove o menu da direita (Hambúrguer de opções extras) */
    #MainMenu {{
        visibility: hidden;
    }}

    /* 3. Garante que o Sidebar (Menu do Professor) esteja sempre acessível */
    section[data-testid="stSidebar"] {{
        background-color: rgba(255, 255, 255, 0.95);
    }}

    /* Mantém sua imagem de fundo */
    .stApp {{
        background-image: url("https://images.unsplash.com/photo-1550985543-f47f38aee65e?q=80&w=1500");
        background-attachment: fixed;
        background-size: cover;
    }}
    
    /* Melhora a visibilidade do formulário */
    [data-testid="stForm"] {{
        background-color: rgba(255, 255, 255, 0.9);
        padding: 30px;
        border-radius: 15px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# --- CONFIGURAÇÕES DA API (AJUSTE AQUI) ---
SHEETDB_API_URL = "https://sheetdb.io/api/v1/SEU_ID_AQUI"
SEU_CELULAR = "5511999999999" 
SENHA_MESTRE = "1234"

if 'professor_logado' not in st.session_state:
    st.session_state['professor_logado'] = False

menu = st.sidebar.selectbox("Navegação", ["Agendar Aula", "Painel do Professor"])

# --- TELA 1: AGENDAMENTO ---
if menu == "Agendar Aula":
    # Cabeçalho com Imagem e Título
    st.image("https://images.unsplash.com/photo-1510915361894-db8b60106cb1?q=80&w=800", use_column_width=True)
    st.title("🎸 Sua Jornada Musical Começa Aqui!")
    st.write("Reserve seu horário e venha dominar as cordas.")

    # Container Branco para o formulário se destacar no fundo
    with st.container():
        with st.form(key="form_aula", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome Completo:")
                whatsapp_aluno = st.text_input("WhatsApp (com DDD):")
            with col2:
                email_aluno = st.text_input("E-mail:")
                estilo = st.selectbox("O que quer aprender?", ["Violão Iniciante", "Violão Intermediário", "Guitarra", "Fingerstyle"])
            
            col3, col4 = st.columns(2)
            with col3:
                data = st.date_input("Escolha o Dia:", format="DD/MM/YYYY")
            with col4:
                horario = st.selectbox("Escolha o Horário:", ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"])
            
            submit = st.form_submit_button("🚀 Reservar Agora")

    if submit:
        if not nome or not whatsapp_aluno or not email_aluno:
            st.warning("⚠️ Preencha todos os campos para continuar!")
        else:
            data_br = data.strftime('%d/%m/%Y')
            hora_texto = str(horario)
            
            with st.spinner('Consultando agenda...'):
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
                        st.error(f"❌ Desculpe, o horário de {hora_texto} no dia {data_br} já foi reservado.")
                    else:
                        payload = {"data": [{
                            "aluno": nome, "data": f"'{data_br}", "hora": f"'{hora_texto}", 
                            "whatsapp": f"'{whatsapp_aluno}", "email": email_aluno, "estilo": estilo
                        }]}
                        requests.post(SHEETDB_API_URL, json=payload)
                        
                        st.success(f"🎉 Tudo pronto, {nome}! Sua aula está marcada.")
                        st.balloons()
                        
                        msg = f"Olá! Agendei uma aula de {estilo} para o dia {data_br} às {hora_texto}."
                        link = f"https://wa.me/{SEU_CELULAR}?text={urllib.parse.quote(msg)}"
                        st.markdown(f'''<a href="{link}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 15px; border-radius: 10px; width: 100%; cursor: pointer; font-weight: bold; font-size: 18px;">📱 Confirmar no WhatsApp do Professor</button></a>''', unsafe_allow_html=True)
                except:
                    st.error("Erro técnico. Tente novamente em instantes.")

# --- TELA 2: PAINEL ---
elif menu == "Painel do Professor":
    st.title("🔐 Acesso Restrito")
    if not st.session_state['professor_logado']:
        senha_input = st.text_input("Senha do Professor:", type="password")
        if st.button("Entrar"):
            if senha_input == SENHA_MESTRE:
                st.session_state['professor_logado'] = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
    else:
        st.sidebar.button("Sair", on_click=lambda: st.session_state.update({'professor_logado': False}))
        if st.button("🔄 Sincronizar Agenda"):
            res = requests.get(SHEETDB_API_URL)
            if res.status_code == 200:
                dados = res.json()
                if dados:
                    df = pd.DataFrame(dados)
                    for col in df.columns:
                        df[col] = df[col].astype(str).str.replace("'", "")
                    st.write("### Suas próximas aulas:")
                    st.dataframe(df[["data", "hora", "aluno", "whatsapp", "email", "estilo"]], use_container_width=True)
                else:
                    st.info("Nenhuma reserva encontrada.")
