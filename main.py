# ... (mantenha o início do código igual)

if submit:
    if not nome:
        st.warning("Por favor, digite seu nome.")
    else:
        # Formata a data para o padrão Brasileiro (ex: 30/01/2026)
        data_br = data.strftime('%d/%m/%Y')
        
        with st.spinner('Consultando agenda...'):
            try:
                response_check = requests.get(SHEETDB_API_URL)
                if response_check.status_code == 200:
                    agenda_atual = response_check.json()
                    
                    ocupado = False
                    if isinstance(agenda_atual, list) and len(agenda_atual) > 0:
                        for aula in agenda_atual:
                            # Comparamos a data como string (garantindo que o formato seja o mesmo)
                            if str(aula.get('data')) == data_br and str(aula.get('hora')) == str(horario):
                                ocupado = True
                                break
                    
                    if ocupado:
                        st.error(f"❌ O horário de {horario} no dia {data_br} já está ocupado.")
                    else:
                        # Salvando na planilha já no formato Brasileiro
                        payload = {"data": [{
                            "aluno": nome, 
                            "data": data_br, 
                            "hora": horario, 
                            "estilo": estilo
                        }]}
                        res = requests.post(SHEETDB_API_URL, json=payload)
                        
                        if res.status_code == 201:
                            st.success(f"✅ Reservado para o dia {data_br}!")
                            
                            # Mensagem do WhatsApp também formatada
                            texto_zap = f"Oi! Agendei minha aula de {estilo} para o dia {data_br} às {horario}."
                            link_whatsapp = f"https://wa.me/{SEU_CELULAR}?text={urllib.parse.quote(texto_zap)}"
                            st.markdown(f'<a href="{link_whatsapp}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px; border-radius: 5px; width: 100%; cursor: pointer;">📱 Avisar Professor</button></a>', unsafe_allow_html=True)
# ... (mantenha o restante do código)
