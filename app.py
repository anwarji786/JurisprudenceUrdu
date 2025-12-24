import random
import streamlit as st
from docx import Document
from gtts import gTTS
import io
import base64
import os
import re

# Path
DOC_PATH = "Law Preparation.docx"

# UI Text
texts = {
    'en': {
        'app_title': "LLB Flashcards",
        'cards': "Flashcards",
        'quiz': "Quiz",
        'download': "Download",
        'settings': "Settings",
        'listen_en': "🔊 English",
        'listen_ur': "🔊 Urdu",
        'show_answer': "Show Answer",
        'next': "Next Card",
        'download_en': "⬇️ English",
        'download_ur': "⬇️ Urdu",
        'shuffle': "Shuffle",
        'prev': "Previous",
        'current': "Current:",
        'total_cards': "Cards:",
        'view_urdu': "Show Urdu",
        'sidebar': "LLB Prep",
        'info': "Study LLB materials",
        'no_flashcards': "No flashcards found.",
        'expected_format': "Expected format:",
        'format_example': "Q: What is...\nA (English): Answer...\nA (Urdu): جواب...",
        'original_text': "Original text:",
        'urdu_translation': "Urdu translation:",
        'answer_in_urdu': "جواب:",
        'stop': "Stop",
        'combined_qa': "Combined Q&A",
        'combined_bilingual': "Combined Bilingual",
        'currently_playing': "Currently playing",
        'stop_all_audio': "Stop All Audio",
        'no_audio': "No audio playing"
    },
    'ur': {
        'app_title': "ایل ایل بی فلش کارڈز",
        'cards': "فلش کارڈز",
        'quiz': "کوئز",
        'download': "ڈاؤن لوڈ",
        'settings': "ترتیبات",
        'listen_en': "🔊 انگریزی",
        'listen_ur': "🔊 اردو",
        'show_answer': "جواب دکھائیں",
        'next': "اگلا کارڈ",
        'download_en': "⬇️ انگریزی",
        'download_ur': "⬇️ اردو",
        'shuffle': "ملائیں",
        'prev': "پچھلا",
        'current': "موجودہ:",
        'total_cards': "کارڈز:",
        'view_urdu': "اردو دکھائیں",
        'sidebar': "ایل ایل بی تیاری",
        'info': "ایل ایل بی مواد کا مطالعہ کریں",
        'no_flashcards': "کوئی فلش کارڈ نہیں ملے۔",
        'expected_format': "متوقع فارمیٹ:",
        'format_example': "Q: کیا ہے...\nA (English): Answer...\nA (Urdu): جواب...",
        'original_text': "اصل متن:",
        'urdu_translation': "اردو ترجمہ:",
        'answer_in_urdu': "جواب:",
        'stop': "روکیں",
        'combined_qa': "مربوط سوال و جواب",
        'combined_bilingual': "مربوط دو زبانی",
        'currently_playing': "فی الحال چل رہا ہے",
        'stop_all_audio': "تمام آڈیو روکیں",
        'no_audio': "کوئی آڈیو نہیں چل رہا"
    }
}

def t(key):
    lang = st.session_state.get('lang', 'en')
    return texts.get(lang, texts['en']).get(key, key)

# Advanced Urdu question generator
def generate_urdu_question(en_question, ur_answer):
    """Generate Urdu question from English question and Urdu answer"""
    
    # Clean the Urdu answer
    ur_answer_clean = ur_answer.replace("{dir=\"rtl\"}", "").strip()
    
    # Pattern matching for common question types
    en_question_lower = en_question.lower()
    
    # Check for specific patterns in English question
    if "who is considered" in en_question_lower or "who is regarded" in en_question_lower:
        # Extract the subject from the answer
        if "جان آسٹن" in ur_answer_clean:
            return "تجزیاتی فقہ کے مدرسہ کا بانی کون سمجھا جاتا ہے؟"
        elif "فریڈرک کارل وان ساوینی" in ur_answer_clean:
            return "تاریخی فقہ کے مدرسہ کا بانی کون سمجھا جاتا ہے؟"
        elif "سر ہنری مین" in ur_answer_clean:
            return "کون سا انگریز ماہر قانون تاریخی مدرسہ سے وابستہ ہے؟"
        else:
            return "اس کا بانی کون سمجھا جاتا ہے؟"
    
    elif "definition" in en_question_lower:
        return "کی تعریف کیا ہے؟"
    
    elif "main features" in en_question_lower or "features" in en_question_lower:
        return "کی اہم خصوصیات کیا ہیں؟"
    
    elif "critics" in en_question_lower or "critic" in en_question_lower:
        return "کے نقادوں کے نام بتائیں۔"
    
    elif "concerned with" in en_question_lower:
        return "کس چیز سے متعلق ہے؟"
    
    elif "argument against" in en_question_lower:
        return "کے خلاف کیا دلیل دی؟"
    
    elif "theory about" in en_question_lower or "theory" in en_question_lower:
        if "status to contract" in en_question_lower.lower():
            return "قانون کی ارتقاء کے بارے میں کیا مشہور نظریہ ہے؟"
        return "کے بارے میں کیا نظریہ ہے؟"
    
    elif "compare" in en_question_lower:
        return "کا موازنہ کریں۔"
    
    elif "name" in en_question_lower:
        return "کے نام بتائیں۔"
    
    elif "what is" in en_question_lower:
        # Extract subject from question
        if "law" in en_question_lower:
            return "کیا ہے؟"
        return "کس چیز کا تذکرہ ہے؟"
    
    elif "what are" in en_question_lower:
        return "کیا ہیں؟"
    
    # Default: Create a generic Urdu question based on the answer
    # Try to extract key terms from Urdu answer to form a question
    urdu_keywords = ["جان آسٹن", "ساوینی", "مین", "ہارٹ", "قانون", "فقہ", "مدرسہ", "تاریخی", "تجزیاتی"]
    for keyword in urdu_keywords:
        if keyword in ur_answer_clean:
            if "آسٹن" in keyword:
                return "آسٹن کی قانون کی تعریف کیا ہے؟"
            elif "ساوینی" in keyword:
                return "ساوینی نے قانون کی تدوین کے خلاف کیا دلیل دی؟"
            elif "مین" in keyword:
                return "مین کا قانون کی ارتقاء کے بارے میں کیا نظریہ ہے؟"
    
    # Final fallback
    return "اس بارے میں سوال کیا ہے؟"

# Load flashcards with intelligent Urdu question generation
def load_cards():
    try:
        doc = Document(DOC_PATH)
        cards = []
        q_en, a_en, a_ur = None, None, None
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text: 
                continue
            
            # Remove RTL tags for cleaner processing
            text = text.replace("{dir=\"rtl\"}", "")
            
            if text.startswith("Q:"):
                if q_en and a_en:  # Save previous card
                    # Generate Urdu question based on English question and Urdu answer
                    urdu_question = generate_urdu_question(q_en, a_ur if a_ur else "")
                    cards.append({
                        'english': (q_en, a_en),
                        'urdu': (urdu_question, a_ur if a_ur else a_en)
                    })
                
                q_en = text[2:].strip()
                a_en = None
                a_ur = None
            
            elif text.startswith("A (English):") and q_en:
                a_en = text.replace("A (English):", "").strip()
            
            elif text.startswith("A (Urdu):") and q_en:
                a_ur = text.replace("A (Urdu):", "").strip()
        
        # Add last card
        if q_en and a_en:
            urdu_question = generate_urdu_question(q_en, a_ur if a_ur else "")
            cards.append({
                'english': (q_en, a_en),
                'urdu': (urdu_question, a_ur if a_ur else a_en)
            })
        
        return cards
    
    except Exception as e:
        st.error(f"Error loading document: {str(e)}")
        return []

# Initialize session state
def init_session_state():
    defaults = {
        'lang': 'en',
        'show_urdu': False,
        'cards': [],
        'order': [],
        'index': 0,
        'show_answer': False,
        'audio_playing': None,
        'stop_requested': False,
        'quiz_started': False,
        'quiz_completed': False,
        'current_question_index': 0,
        'quiz_cards': [],
        'quiz_answers': {},
        'quiz_feedback': {}
    }
    
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
    
    # Load cards if not loaded
    if not st.session_state.cards:
        st.session_state.cards = load_cards()
    
    # Initialize order if cards exist
    if st.session_state.cards and not st.session_state.order:
        st.session_state.order = list(range(len(st.session_state.cards)))
        random.shuffle(st.session_state.order)

# Audio functions
def text_to_speech(text, lang="en"):
    """Convert text to speech audio"""
    try:
        if not text:
            return None
        
        # Clean text for TTS
        text = str(text).strip()
        if not text:
            return None
        
        # Handle Urdu text encoding
        if lang == "ur":
            # Ensure Urdu text is properly encoded
            text = text.encode('utf-8').decode('utf-8')
        
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.getvalue()
    
    except Exception as e:
        st.error(f"TTS Error ({lang}): {str(e)}")
        return None

def generate_combined_audio(question_text, answer_text, lang="en"):
    """Generate combined audio of question and answer"""
    try:
        question_audio = text_to_speech(question_text, lang=lang)
        answer_audio = text_to_speech(answer_text, lang=lang)
        
        if question_audio and answer_audio:
            # Simple concatenation of bytes
            return question_audio + answer_audio
        
        return None
    except Exception as e:
        st.error(f"Error generating combined audio: {e}")
        return None

def generate_bilingual_audio(english_text, urdu_text):
    """Generate bilingual audio (English + Urdu)"""
    try:
        english_audio = text_to_speech(english_text, lang="en")
        urdu_audio = text_to_speech(urdu_text, lang="ur")
        
        if english_audio and urdu_audio:
            # Concatenate English and Urdu audio
            return english_audio + urdu_audio
        
        return None
    except Exception as e:
        st.error(f"Error generating bilingual audio: {e}")
        return None

def stop_audio():
    """Stop all audio playback"""
    st.session_state.stop_requested = True
    st.session_state.audio_playing = None

# Main app layout
def main():
    st.set_page_config(
        page_title="LLB Flashcards - English/Urdu",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("📚 " + t('sidebar'))
        st.info(t('info'))
        
        # Stats
        if st.session_state.cards:
            st.success(f"**{len(st.session_state.cards)} {t('total_cards')}**")
        
        st.markdown("---")
        
        # Language selector
        st.subheader("🌐 Language")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🇺🇸 English", use_container_width=True, 
                        type="primary" if st.session_state.lang == 'en' else "secondary"):
                st.session_state.lang = 'en'
                st.rerun()
        with col2:
            if st.button("🇵🇰 Urdu", use_container_width=True,
                        type="primary" if st.session_state.lang == 'ur' else "secondary"):
                st.session_state.lang = 'ur'
                st.rerun()
        
        st.markdown("---")
        
        # Settings
        st.session_state.show_urdu = st.checkbox(t('view_urdu'), st.session_state.show_urdu)
        
        # Audio status
        st.markdown("---")
        if st.session_state.audio_playing:
            st.warning(f"🔊 {t('currently_playing')}")
            if st.button(f"⏹️ {t('stop_all_audio')}", type="primary", use_container_width=True):
                stop_audio()
                st.rerun()
        else:
            st.info(t('no_audio'))
        
        st.markdown("---")
        st.caption("Made with ❤️ for LLB students")

    # Main tabs
    tab1, tab2, tab3 = st.tabs([
        f"🎴 {t('cards')}",
        f"📝 {t('quiz')}",
        f"⚙️ {t('settings')}"
    ])
    
    with tab1:
        show_flashcards()
    with tab2:
        show_quiz()
    with tab3:
        show_settings()

def show_flashcards():
    st.title(t('app_title'))
    
    if not st.session_state.cards:
        st.warning(t('no_flashcards'))
        st.info(f"**{t('expected_format')}:**\n```\n{t('format_example')}\n```")
        return
    
    idx = st.session_state.order[st.session_state.index]
    card = st.session_state.cards[idx]
    english_question, english_answer = card['english']
    urdu_question, urdu_answer = card['urdu']
    
    # Display question
    if st.session_state.lang == 'ur':
        st.subheader(f"{urdu_question}")
        if st.session_state.show_urdu:
            st.markdown(f"*{t('original_text')}: {english_question}*")
    else:
        st.subheader(f"Q: {english_question}")
        if st.session_state.show_urdu:
            st.markdown(f"*{t('urdu_translation')}: {urdu_question}*")
    
    # Question audio buttons
    st.markdown("---")
    st.write("**Listen to question:**")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button(t('listen_en'), key=f"play_q_en_{idx}", use_container_width=True):
            with st.spinner("Generating English audio..."):
                audio_bytes = text_to_speech(english_question, lang="en")
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                    st.success("English audio ready!")
    
    with col2:
        if st.button(t('listen_ur'), key=f"play_q_ur_{idx}", use_container_width=True):
            with st.spinner("Generating Urdu audio..."):
                audio_bytes = text_to_speech(urdu_question, lang="ur")
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                    st.success("Urdu audio ready!")
    
    with col3:
        if st.button(t('stop'), key=f"stop_q_{idx}", type="secondary", use_container_width=True):
            stop_audio()
            st.rerun()
    
    # Question download buttons
    st.write("**Download question audio:**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t('download_en'), key=f"dl_q_en_{idx}", use_container_width=True):
            with st.spinner("Generating download..."):
                audio_bytes = text_to_speech(english_question, lang="en")
                if audio_bytes:
                    filename = f"question_{idx+1}_en.mp3"
                    b64 = base64.b64encode(audio_bytes).decode()
                    href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">Download</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.success(f"Ready to download: {filename}")
    
    with col2:
        if st.button(t('download_ur'), key=f"dl_q_ur_{idx}", use_container_width=True):
            with st.spinner("Generating download..."):
                audio_bytes = text_to_speech(urdu_question, lang="ur")
                if audio_bytes:
                    filename = f"question_{idx+1}_ur.mp3"
                    b64 = base64.b64encode(audio_bytes).decode()
                    href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">Download</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.success(f"Ready to download: {filename}")
    
    # Show answer button
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t('show_answer'), key=f"show_ans_{idx}", use_container_width=True):
            st.session_state.show_answer = True
            st.rerun()
    
    with col2:
        if st.button(t('next'), key=f"next_{idx}", use_container_width=True):
            st.session_state.index = (st.session_state.index + 1) % len(st.session_state.order)
            st.session_state.show_answer = False
            st.rerun()
    
    # Display answer if shown
    if st.session_state.show_answer:
        st.markdown("---")
        if st.session_state.lang == 'ur':
            st.markdown(f"""<div style='color:green; font-size:20px; padding:15px; border-left:5px solid #4CAF50; background-color:#f9f9f9; border-radius:5px; margin:10px 0;'><strong>{t('answer_in_urdu')}</strong><br>{urdu_answer}</div>""", unsafe_allow_html=True)
            if st.session_state.show_urdu:
                st.markdown(f"*{t('original_text')}: {english_answer}*")
        else:
            st.markdown(f"""<div style='color:green; font-size:20px; padding:15px; border-left:5px solid #4CAF50; background-color:#f9f9f9; border-radius:5px; margin:10px 0;'><strong>A:</strong><br>{english_answer}</div>""", unsafe_allow_html=True)
            if st.session_state.show_urdu:
                st.markdown(f"*{t('urdu_translation')}: {urdu_answer}*")
        
        # Answer audio buttons
        st.markdown("---")
        st.write("**Listen to answer:**")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button(t('listen_en'), key=f"play_a_en_{idx}", use_container_width=True):
                with st.spinner("Generating English audio..."):
                    audio_bytes = text_to_speech(english_answer, lang="en")
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                        st.success("English audio ready!")
        
        with col2:
            if st.button(t('listen_ur'), key=f"play_a_ur_{idx}", use_container_width=True):
                with st.spinner("Generating Urdu audio..."):
                    audio_bytes = text_to_speech(urdu_answer, lang="ur")
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                        st.success("Urdu audio ready!")
        
        with col3:
            if st.button(t('stop'), key=f"stop_a_{idx}", type="secondary", use_container_width=True):
                stop_audio()
                st.rerun()
        
        # Answer download buttons
        st.write("**Download answer audio:**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t('download_en'), key=f"dl_a_en_{idx}", use_container_width=True):
                with st.spinner("Generating download..."):
                    audio_bytes = text_to_speech(english_answer, lang="en")
                    if audio_bytes:
                        filename = f"answer_{idx+1}_en.mp3"
                        b64 = base64.b64encode(audio_bytes).decode()
                        href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">Download</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        st.success(f"Ready to download: {filename}")
        
        with col2:
            if st.button(t('download_ur'), key=f"dl_a_ur_{idx}", use_container_width=True):
                with st.spinner("Generating download..."):
                    audio_bytes = text_to_speech(urdu_answer, lang="ur")
                    if audio_bytes:
                        filename = f"answer_{idx+1}_ur.mp3"
                        b64 = base64.b64encode(audio_bytes).decode()
                        href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">Download</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        st.success(f"Ready to download: {filename}")
        
        # Combined audio buttons
        st.markdown("---")
        st.write("**Download combined audio:**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(t('combined_qa'), key=f"dl_qa_en_{idx}", use_container_width=True):
                with st.spinner("Generating combined Q&A audio..."):
                    combined_audio = generate_combined_audio(english_question, english_answer, lang="en")
                    if combined_audio:
                        filename = f"qa_{idx+1}_en.mp3"
                        b64 = base64.b64encode(combined_audio).decode()
                        href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">Download</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        st.success(f"Ready to download: {filename}")
        
        with col2:
            if st.button(t('combined_bilingual'), key=f"dl_qa_bil_{idx}", use_container_width=True):
                with st.spinner("Generating bilingual audio..."):
                    english_content = f"Question: {english_question}. Answer: {english_answer}"
                    urdu_content = f"سوال: {urdu_question}. جواب: {urdu_answer}"
                    bilingual_audio = generate_bilingual_audio(english_content, urdu_content)
                    if bilingual_audio:
                        filename = f"qa_{idx+1}_bilingual.mp3"
                        b64 = base64.b64encode(bilingual_audio).decode()
                        href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">Download</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        st.success(f"Ready to download: {filename}")
    
    # Navigation controls
    st.markdown("---")
    with st.expander("🔧 Navigation Controls", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("⏮️ First", use_container_width=True):
                st.session_state.index = 0
                st.session_state.show_answer = False
                st.rerun()
        
        with col2:
            if st.button("⏪ " + t('prev'), use_container_width=True):
                st.session_state.index = (st.session_state.index - 1) % len(st.session_state.order)
                st.session_state.show_answer = False
                st.rerun()
        
        with col3:
            if st.button("⏩ " + t('next'), use_container_width=True):
                st.session_state.index = (st.session_state.index + 1) % len(st.session_state.order)
                st.session_state.show_answer = False
                st.rerun()
        
        with col4:
            if st.button("🔀 " + t('shuffle'), use_container_width=True):
                if st.session_state.cards:
                    st.session_state.order = list(range(len(st.session_state.cards)))
                    random.shuffle(st.session_state.order)
                    st.session_state.index = 0
                    st.session_state.show_answer = False
                    st.success("Deck shuffled!")
                    st.rerun()
        
        st.write(f"**{t('current')} {st.session_state.index + 1} of {len(st.session_state.order)}**")

def show_quiz():
    """Quiz interface"""
    st.title("🧠 " + t('quiz'))
    
    if not st.session_state.cards:
        st.warning("Please load flashcards first.")
        return
    
    st.info("Quiz feature is under development.")
    st.write(f"You have **{len(st.session_state.cards)}** flashcards available for practice.")
    
    # Simple quiz preview
    if st.button("Start Practice Quiz", type="primary"):
        st.session_state.quiz_mode = True
        st.rerun()

def show_settings():
    """Settings interface"""
    st.title("⚙️ " + t('settings'))
    
    # Document info
    st.subheader("📄 Document Information")
    st.write(f"**Document:** {DOC_PATH}")
    st.write(f"**Status:** {'✅ Found' if os.path.exists(DOC_PATH) else '❌ Not found'}")
    st.write(f"**Cards loaded:** {len(st.session_state.cards)}")
    
    # Preview loaded cards
    if st.session_state.cards:
        with st.expander("📋 Preview loaded cards", expanded=False):
            for i, card in enumerate(st.session_state.cards[:5]):
                st.write(f"**Card {i+1}:**")
                st.write(f"  English Q: {card['english'][0][:60]}...")
                st.write(f"  Urdu Q: {card['urdu'][0][:60]}...")
                st.write("---")
    
    # Reset button
    st.subheader("🔄 Reset Application")
    if st.button("Reset All Data", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Application reset complete!")
        st.rerun()
    
    # About section
    with st.expander("ℹ️ About this app", expanded=False):
        st.write("""
        **LLB Flashcards App - English/Urdu**
        
        Features:
        - 📚 Bilingual flashcards (English & Urdu)
        - 🔊 Text-to-speech in both languages
        - 🎯 Intelligent Urdu question generation
        - 📥 Audio download capability
        - 🔄 Interactive navigation
        
        For LLB students preparing for exams.
        
        *Note: Requires internet connection for audio generation.*
        """)

if __name__ == "__main__":
    main()