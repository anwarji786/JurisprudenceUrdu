# Replace the show_flashcards function with this updated version:

def show_flashcards():
    st.title(t('app_title'))
    with st.container():
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"### {t('current_language')}: **{t('english') if st.session_state.language == 'English' else t('urdu')}**")
        with col2:
            st.markdown("### 🌐")
        with col3:
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button(f"🇺🇸 {t('english')}", type="primary" if st.session_state.language == 'English' else "secondary", use_container_width=True, key="switch_to_english"):
                    st.session_state.language = 'English'
                    st.rerun()
            with btn_col2:
                if st.button(f"🇵🇰 {t('urdu')}", type="primary" if st.session_state.language == 'Urdu' else "secondary", use_container_width=True, key="switch_to_urdu"):
                    st.session_state.language = 'Urdu'
                    st.rerun()
    st.markdown("---")
    
    with st.sidebar:
        st.markdown("---")
        st.subheader(t('display_mode'))
        if st.session_state.language == 'English':
            st.session_state.show_urdu = st.checkbox(t('view_translation'), value=st.session_state.show_urdu)
        else:
            st.session_state.show_urdu = True
        st.markdown("---")
        with st.expander(t('document_info'), expanded=False):
            st.write(f"**{t('document_info')}:** Law Preparation.docx")
            st.write(f"**{t('total_cards')}:** {len(st.session_state.cards) if st.session_state.cards else 0}")
            if st.session_state.cards:
                sample_question = st.session_state.cards[0]['english'][0]
                st.write(f"**{t('sample_question')}:** {sample_question[:50]}...")
        
        if st.session_state.audio_playing:
            st.warning(f"🔊 {t('currently_playing')}")
            if st.button(f"⏹️ {t('stop_all_audio')}", type="primary", use_container_width=True):
                stop_audio()
                st.rerun()
        else:
            st.info(t('no_audio'))
    
    if not st.session_state.cards:
        st.warning(t('no_flashcards'))
        st.info(f"**{t('expected_format')}:**\n```\n{t('format_example')}\n```")
    else:
        idx = st.session_state.order[st.session_state.index]
        card = st.session_state.cards[idx]
        english_question, english_answer = card['english']
        if 'urdu' in card:
            urdu_question, urdu_answer = card['urdu']
        else:
            urdu_question, urdu_answer = f"سوال: {english_question}", english_answer

        if st.session_state.language == 'Urdu':
            st.subheader(f"{urdu_question}")
            if st.session_state.show_urdu:
                st.markdown(f"*{t('original_text')}: {english_question}*")
        else:
            st.subheader(f"Q: {english_question}")
            if st.session_state.show_urdu:
                st.markdown(f"*{t('urdu_translation')}: {urdu_question}*")

        current_audio_id = f"card_{idx}_question"
        is_playing = st.session_state.audio_playing == current_audio_id
        
        # Audio playback section - FIXED
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button(t('listen_english'), key="play_question_en"):
                with st.spinner("Generating audio..."):
                    audio_bytes = text_to_speech(english_question, lang="en")
                    if audio_bytes:
                        # Store audio in session state
                        st.session_state[f"audio_{current_audio_id}_en"] = audio_bytes
                        # Display the audio player
                        st.audio(audio_bytes, format="audio/mp3")
                        st.session_state.audio_playing = current_audio_id
        with col2:
            if st.button(t('listen_urdu'), key="play_question_ur"):
                with st.spinner("Generating audio..."):
                    audio_bytes = text_to_speech(urdu_question, lang="ur")
                    if audio_bytes:
                        # Store audio in session state
                        st.session_state[f"audio_{current_audio_id}_ur"] = audio_bytes
                        # Display the audio player
                        st.audio(audio_bytes, format="audio/mp3")
                        st.session_state.audio_playing = current_audio_id
        with col3:
            if st.button(t('stop'), key="stop_question", type="secondary"):
                stop_audio()
                st.rerun()

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t('download_english'), key=f"dl_q_en_{idx}", use_container_width=True):
                with st.spinner("Generating download..."):
                    audio_bytes = text_to_speech(english_question, lang="en")
                    if audio_bytes:
                        filename = f"question_{idx+1}_en.mp3"
                        b64 = base64.b64encode(audio_bytes).decode()
                        href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">'
                        st.markdown(f'{href}<button style="display:none;" id="download_q_en_{idx}">Download</button></a>', unsafe_allow_html=True)
                        st.markdown(f'<script>document.getElementById("download_q_en_{idx}").click();</script>', unsafe_allow_html=True)
                        st.success(f"Download started: {filename}")
        with col2:
            if st.button(t('download_urdu'), key=f"dl_q_ur_{idx}", use_container_width=True):
                with st.spinner("Generating download..."):
                    audio_bytes = text_to_speech(urdu_question, lang="ur")
                    if audio_bytes:
                        filename = f"question_{idx+1}_ur.mp3"
                        b64 = base64.b64encode(audio_bytes).decode()
                        href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">'
                        st.markdown(f'{href}<button style="display:none;" id="download_q_ur_{idx}">Download</button></a>', unsafe_allow_html=True)
                        st.markdown(f'<script>document.getElementById("download_q_ur_{idx}").click();</script>', unsafe_allow_html=True)
                        st.success(f"Download started: {filename}")

        if st.session_state.show_answer:
            st.markdown("---")
            if st.session_state.language == 'Urdu':
                st.markdown(f"""<div style='color:red; font-size:30px; padding:20px; border-left:5px solid #4CAF50; background-color:#f9f9f9; border-radius:5px; margin:10px 0;'><strong>{t('answer_in_urdu')}</strong><br>{urdu_answer}</div>""", unsafe_allow_html=True)
                if st.session_state.show_urdu:
                    st.markdown(f"*{t('original_text')}: {english_answer}*")
            else:
                st.markdown(f"""<div style='color:red; font-size:30px; padding:20px; border-left:5px solid #4CAF50; background-color:#f9f9f9; border-radius:5px; margin:10px 0;'><strong>A:</strong><br>{english_answer}</div>""", unsafe_allow_html=True)
                if st.session_state.show_urdu:
                    st.markdown(f"*{t('urdu_translation')}: {urdu_answer}*")

            current_audio_id_answer = f"card_{idx}_answer"
            is_playing_answer = st.session_state.audio_playing == current_audio_id_answer
            
            # Answer audio playback section - FIXED
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button(t('listen_english'), key="play_answer_en"):
                    with st.spinner("Generating audio..."):
                        audio_bytes = text_to_speech(english_answer, lang="en")
                        if audio_bytes:
                            # Store audio in session state
                            st.session_state[f"audio_{current_audio_id_answer}_en"] = audio_bytes
                            # Display the audio player
                            st.audio(audio_bytes, format="audio/mp3")
                            st.session_state.audio_playing = current_audio_id_answer
            with col2:
                if st.button(t('listen_urdu'), key="play_answer_ur"):
                    with st.spinner("Generating audio..."):
                        audio_bytes = text_to_speech(urdu_answer, lang="ur")
                        if audio_bytes:
                            # Store audio in session state
                            st.session_state[f"audio_{current_audio_id_answer}_ur"] = audio_bytes
                            # Display the audio player
                            st.audio(audio_bytes, format="audio/mp3")
                            st.session_state.audio_playing = current_audio_id_answer
            with col3:
                if st.button(t('stop'), key="stop_answer", type="secondary"):
                    stop_audio()
                    st.rerun()

            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(t('download_english'), key=f"dl_a_en_{idx}", use_container_width=True):
                    with st.spinner("Generating download..."):
                        audio_bytes = text_to_speech(english_answer, lang="en")
                        if audio_bytes:
                            filename = f"answer_{idx+1}_en.mp3"
                            b64 = base64.b64encode(audio_bytes).decode()
                            href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">'
                            st.markdown(f'{href}<button style="display:none;" id="download_a_en_{idx}">Download</button></a>', unsafe_allow_html=True)
                            st.markdown(f'<script>document.getElementById("download_a_en_{idx}").click();</script>', unsafe_allow_html=True)
                            st.success(f"Download started: {filename}")
            with col2:
                if st.button(t('download_urdu'), key=f"dl_a_ur_{idx}", use_container_width=True):
                    with st.spinner("Generating download..."):
                        audio_bytes = text_to_speech(urdu_answer, lang="ur")
                        if audio_bytes:
                            filename = f"answer_{idx+1}_ur.mp3"
                            b64 = base64.b64encode(audio_bytes).decode()
                            href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">'
                            st.markdown(f'{href}<button style="display:none;" id="download_a_ur_{idx}">Download</button></a>', unsafe_allow_html=True)
                            st.markdown(f'<script>document.getElementById("download_a_ur_{idx}").click();</script>', unsafe_allow_html=True)
                            st.success(f"Download started: {filename}")

            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(t('combined_qa') + " (EN)", key=f"dl_combined_en_{idx}", type="primary", use_container_width=True):
                    with st.spinner("Generating combined audio..."):
                        combined_audio = generate_combined_audio(english_question, english_answer, lang="en")
                        if combined_audio:
                            filename = f"flashcard_{idx+1}_en.mp3"
                            b64 = base64.b64encode(combined_audio).decode()
                            href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">'
                            st.markdown(f'{href}<button style="display:none;" id="download_combined_en_{idx}">Download</button></a>', unsafe_allow_html=True)
                            st.markdown(f'<script>document.getElementById("download_combined_en_{idx}").click();</script>', unsafe_allow_html=True)
                            st.success(f"Download started: {filename}")
            with col2:
                if st.button(t('combined_bilingual'), key=f"dl_bilingual_{idx}", type="primary", use_container_width=True):
                    with st.spinner("Generating bilingual audio..."):
                        english_content = f"Question: {english_question} Answer: {english_answer}"
                        urdu_content = f"سوال: {english_question} جواب: {urdu_answer}"
                        bilingual_audio = generate_bilingual_audio(english_content, urdu_content)
                        if bilingual_audio:
                            filename = f"flashcard_{idx+1}_bilingual.mp3"
                            b64 = base64.b64encode(bilingual_audio).decode()
                            href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">'
                            st.markdown(f'{href}<button style="display:none;" id="download_bilingual_{idx}">Download</button></a>', unsafe_allow_html=True)
                            st.markdown(f'<script>document.getElementById("download_bilingual_{idx}").click();</script>', unsafe_allow_html=True)
                            st.success(f"Download started: {filename}")