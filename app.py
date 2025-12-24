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
        'title': "LLB Flashcards",
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
        'info': "Study LLB materials"
    },
    'ur': {
        'title': "ایل ایل بی فلش کارڈز",
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
        'info': "ایل ایل بی مواد کا مطالعہ کریں"
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
                        'en': (q_en, a_en),
                        'ur': (urdu_question, a_ur if a_ur else a_en)
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
                'en': (q_en, a_en),
                'ur': (urdu_question, a_ur if a_ur else a_en)
            })
        
        # Store for debugging
        st.session_state.debug_cards = cards[:3] if cards else []
        
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
        'show_ans': False,
        'debug_mode': False
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
        
        tts = gTTS(text=text, lang=lang, slow=False, lang_check=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.getvalue()
    
    except Exception as e:
        st.error(f"TTS Error ({lang}): {str(e)}")
        return None

def create_audio_player(audio_bytes, label=""):
    """Create HTML audio player"""
    if audio_bytes:
        try:
            audio_b64 = base64.b64encode(audio_bytes).decode()
            player_html = f"""
            <div style="margin: 10px 0;">
                <audio controls style="width: 100%; height: 40px;">
                    <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                    Your browser does not support audio playback.
                </audio>
            </div>
            """
            return player_html
        except:
            return "<p>Audio player error</p>"
    return ""

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
        st.subheader("🌐 " + t('current'))
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
        st.session_state.debug_mode = st.checkbox("🔧 Debug Mode", False)
        
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
    """Display flashcards interface"""
    st.title(t('title'))
    
    # Header with language info
    col1, col2 = st.columns([4, 1])
    with col1:
        current_lang = "English" if st.session_state.lang == 'en' else "اردو"
        st.write(f"**{t('current')} {current_lang}**")
    
    st.markdown("---")
    
    # Check if cards exist
    if not st.session_state.cards:
        st.warning("No flashcards loaded. Please check your document.")
        st.info("Make sure 'Law Preparation.docx' is in the same folder.")
        return
    
    # Get current card
    idx = st.session_state.order[st.session_state.index]
    card = st.session_state.cards[idx]
    q_en, a_en = card['en']
    q_ur, a_ur = card['ur']
    
    # Debug information
    if st.session_state.debug_mode:
        with st.expander("🔍 Debug Information", expanded=True):
            st.write(f"**Card Index:** {idx}")
            st.write(f"**English Question:** {q_en}")
            st.write(f"**Generated Urdu Question:** {q_ur}")
            st.write(f"**English Answer:** {a_en}")
            st.write(f"**Urdu Answer:** {a_ur}")
    
    # Display question based on language
    st.subheader("📝 Question")
    if st.session_state.lang == 'ur':
        # Urdu mode - show Urdu question
        st.markdown(f"<div style='text-align: right; direction: rtl; font-size: 20px;'><strong>{q_ur}</strong></div>", 
                   unsafe_allow_html=True)
        if st.session_state.show_urdu:
            st.caption(f"*English: {q_en}*")
    else:
        # English mode - show English question
        st.markdown(f"<div style='font-size: 20px;'><strong>Q: {q_en}</strong></div>", 
                   unsafe_allow_html=True)
        if st.session_state.show_urdu:
            st.caption(f"*Urdu: {q_ur}*")
    
    # Audio section for question
    st.markdown("---")
    st.subheader("🔊 Question Audio")
    
    col1, col2 = st.columns(2)
    
    # English audio button
    with col1:
        audio_key_en = f"audio_q_en_{idx}"
        if st.button(f"🎵 {t('listen_en')}", key=f"btn_q_en_{idx}", use_container_width=True):
            with st.spinner("Generating English audio..."):
                audio_data = text_to_speech(q_en, "en")
                if audio_data:
                    st.session_state[audio_key_en] = audio_data
                    st.success("English audio ready!")
    
    # Urdu audio button
    with col2:
        audio_key_ur = f"audio_q_ur_{idx}"
        if st.button(f"🎵 {t('listen_ur')}", key=f"btn_q_ur_{idx}", use_container_width=True):
            with st.spinner("Generating Urdu audio..."):
                audio_data = text_to_speech(q_ur, "ur")
                if audio_data:
                    st.session_state[audio_key_ur] = audio_data
                    st.success("Urdu audio ready!")
    
    # Display audio players
    if audio_key_en in st.session_state:
        st.write("**English Audio:**")
        st.markdown(create_audio_player(st.session_state[audio_key_en]), unsafe_allow_html=True)
    
    if audio_key_ur in st.session_state:
        st.write("**Urdu Audio:**")
        st.markdown(create_audio_player(st.session_state[audio_key_ur]), unsafe_allow_html=True)
    
    # Answer controls
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"📖 {t('show_answer')}", key=f"show_{idx}", use_container_width=True):
            st.session_state.show_ans = True
            st.rerun()
    
    # Display answer if shown
    if st.session_state.show_ans:
        st.markdown("## 📝 Answer")
        
        if st.session_state.lang == 'ur':
            # Show Urdu answer
            st.markdown(f"<div style='text-align: right; direction: rtl; font-size: 18px;'>"
                       f"<strong>جواب:</strong><br>{a_ur}</div>", unsafe_allow_html=True)
            if st.session_state.show_urdu:
                st.caption(f"*English: {a_en}*")
        else:
            # Show English answer
            st.markdown(f"<div style='font-size: 18px;'><strong>A:</strong><br>{a_en}</div>", 
                       unsafe_allow_html=True)
            if st.session_state.show_urdu:
                st.caption(f"*Urdu: {a_ur}*")
        
        # Answer audio
        st.markdown("---")
        st.subheader("🔊 Answer Audio")
        
        col1, col2 = st.columns(2)
        
        # English answer audio
        with col1:
            audio_key_a_en = f"audio_a_en_{idx}"
            if st.button(f"🎵 {t('listen_en')} Answer", key=f"btn_a_en_{idx}", use_container_width=True):
                with st.spinner("Generating English answer audio..."):
                    audio_data = text_to_speech(a_en, "en")
                    if audio_data:
                        st.session_state[audio_key_a_en] = audio_data
                        st.success("English answer audio ready!")
        
        # Urdu answer audio
        with col2:
            audio_key_a_ur = f"audio_a_ur_{idx}"
            if st.button(f"🎵 {t('listen_ur')} Answer", key=f"btn_a_ur_{idx}", use_container_width=True):
                with st.spinner("Generating Urdu answer audio..."):
                    audio_data = text_to_speech(a_ur, "ur")
                    if audio_data:
                        st.session_state[audio_key_a_ur] = audio_data
                        st.success("Urdu answer audio ready!")
        
        # Display answer audio players
        if audio_key_a_en in st.session_state:
            st.write("**English Answer Audio:**")
            st.markdown(create_audio_player(st.session_state[audio_key_a_en]), unsafe_allow_html=True)
        
        if audio_key_a_ur in st.session_state:
            st.write("**Urdu Answer Audio:**")
            st.markdown(create_audio_player(st.session_state[audio_key_a_ur]), unsafe_allow_html=True)
    
    # Navigation
    st.markdown("---")
    with st.expander("⚙️ Navigation & Controls", expanded=True):
        # Card counter
        st.write(f"**Card {st.session_state.index + 1} of {len(st.session_state.order)}**")
        
        # Navigation buttons
        nav_cols = st.columns(5)
        
        with nav_cols[0]:
            if st.button("⏮️ First", use_container_width=True):
                st.session_state.index = 0
                st.session_state.show_ans = False
                st.rerun()
        
        with nav_cols[1]:
            if st.button("◀️ " + t('prev'), use_container_width=True):
                st.session_state.index = (st.session_state.index - 1) % len(st.session_state.order)
                st.session_state.show_ans = False
                st.rerun()
        
        with nav_cols[2]:
            if st.button(t('shuffle'), use_container_width=True):
                random.shuffle(st.session_state.order)
                st.session_state.index = 0
                st.session_state.show_ans = False
                st.success("Cards shuffled!")
                st.rerun()
        
        with nav_cols[3]:
            if st.button("▶️ " + t('next'), key=f"nav_next_{idx}", use_container_width=True):
                st.session_state.index = (st.session_state.index + 1) % len(st.session_state.order)
                st.session_state.show_ans = False
                st.rerun()
        
        with nav_cols[4]:
            if st.button("⏭️ Last", use_container_width=True):
                st.session_state.index = len(st.session_state.order) - 1
                st.session_state.show_ans = False
                st.rerun()

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
                st.write(f"  English Q: {card['en'][0][:60]}...")
                st.write(f"  Urdu Q: {card['ur'][0][:60]}...")
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