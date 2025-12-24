import random
import streamlit as st
from docx import Document
from gtts import gTTS
import io
import base64
import re
import time
from datetime import datetime
import zipfile
import tempfile
import os

# Path handling
current_dir = os.path.dirname(os.path.abspath(__file__))
DOC_PATH = os.path.join(current_dir, "Law Preparation.docx")
if not os.path.exists(DOC_PATH):
    DOC_PATH = "Law Preparation.docx"

# UI Translations (shortened for conciseness)
UI_TRANSLATIONS = {
    'English': {
        'app_title': "LLB Preparation Flashcards with Voiceover",
        'flashcards': "Flashcards",
        'quiz': "Quiz",
        'download': "Bulk Download",
        'settings_tab': "Settings",
        'play_question': "🔊 Play Question",
        'listen_english': "🔊 Listen in English",
        'listen_urdu': "🔊 Listen in Urdu",
        'show_answer': "Show Answer",
        'next_card': "Next Card",
        'download_english': "⬇️ English Audio",
        'download_urdu': "⬇️ Urdu Audio",
        'shuffle_deck': "Shuffle Deck",
        'first': "⏮️ First",
        'previous': "⏪ Previous",
        'next': "⏩ Next",
        'card_settings': "Card Settings",
        'quick_navigation': "Quick Navigation",
        'combined_qa': "⬇️ Combined Q&A Audio",
        'combined_bilingual': "⬇️ Combined Bilingual Audio",
        'current_language': "Current Language",
        'english': "English",
        'urdu': "Urdu",
        'answer_in_urdu': "جواب:",
        'original_text': "Original Text",
        'urdu_translation': "Urdu Translation",
        'view_translation': "View Urdu Translation",
        'stop': "⏹️ Stop",
        'sidebar_title': "📚 LLB Prep",
        'sidebar_info': "Study LLB materials with interactive flashcards",
        'cards_loaded': "cards loaded",
        'made_with': "Made with ❤️ for LLB students",
        'total_cards': "Total Cards",
        'sample_question': "Sample Question",
        'document_info': "Document Information",
        'no_flashcards': "No flashcards found",
        'format_example': "Q: Question?\nA: Answer...",
        'expected_format': "Expected format:"
    },
    'Urdu': {
        'app_title': "ایل ایل بی تیاری فلش کارڈز",
        'flashcards': "فلش کارڈز",
        'quiz': "کوئز",
        'download': "بلاک ڈاؤن لوڈ",
        'settings_tab': "ترتیبات",
        'play_question': "🔊 سوال سنیں",
        'listen_english': "🔊 انگریزی میں سنیں",
        'listen_urdu': "🔊 اردو میں سنیں",
        'show_answer': "جواب دکھائیں",
        'next_card': "اگلا کارڈ",
        'download_english': "⬇️ انگریزی آڈیو",
        'download_urdu': "⬇️ اردو آڈیو",
        'shuffle_deck': "کارڈ ملائیں",
        'first': "⏮️ پہلا",
        'previous': "⏪ پچھلا",
        'next': "⏩ اگلا",
        'card_settings': "کارڈ کی ترتیبات",
        'quick_navigation': "فوری نیویگیشن",
        'combined_qa': "⬇️ مشترکہ سوال اور جواب آڈیو",
        'combined_bilingual': "⬇️ مشترکہ دو لسانی آڈیو",
        'current_language': "موجودہ زبان",
        'english': "انگریزی",
        'urdu': "اردو",
        'answer_in_urdu': "جواب:",
        'original_text': "اصل متن",
        'urdu_translation': "اردو ترجمہ",
        'view_translation': "اردو ترجمہ دیکھیں",
        'stop': "⏹️ روکیں",
        'sidebar_title': "📚 ایل ایل بی تیاری",
        'sidebar_info': "انٹرایکٹو فلش کارڈز کے ساتھ ایل ایل بی مواد کا مطالعہ کریں",
        'cards_loaded': "کارڈز لوڈ ہوئے",
        'made_with': "ایل ایل بی طلباء کے لیے ❤️ کے ساتھ بنایا گیا",
        'total_cards': "کل کارڈز",
        'sample_question': "نمونہ سوال",
        'document_info': "دستاویز کی معلومات",
        'no_flashcards': "کوئی فلش کارڈ نہیں ملا",
        'format_example': "Q: سوال؟\nA: جواب...",
        'expected_format': "متوقع فارمیٹ:"
    }
}

def t(key):
    return UI_TRANSLATIONS.get(st.session_state.language, UI_TRANSLATIONS['English']).get(key, key)

def load_bilingual_flashcards(doc_path):
    try:
        document = Document(doc_path)
        cards = []
        current_q, current_a_en, current_a_ur = None, None, None
        
        for para in document.paragraphs:
            text = para.text.strip()
            if not text: continue
            
            if text.startswith("Q:"):
                if current_q and current_a_en:
                    cards.append({
                        'english': (current_q, current_a_en),
                        'urdu': (f"سوال: {current_q}", current_a_ur if current_a_ur else current_a_en)
                    })
                current_q = text[2:].strip()
                current_a_en = None
                current_a_ur = None
            elif text.startswith("A (English):") and current_q:
                current_a_en = text.replace("A (English):", "").strip()
            elif text.startswith("A (Urdu):") and current_q:
                current_a_ur = text.replace("A (Urdu):", "").replace("{dir=\"rtl\"}", "").strip()
        
        if current_q and current_a_en:
            cards.append({
                'english': (current_q, current_a_en),
                'urdu': (f"سوال: {current_q}", current_a_ur if current_a_ur else current_a_en)
            })
        return cards
    except:
        return []

# Initialize session states
default_states = {
    'language': 'English',
    'show_urdu': False,
    'cards': [],
    'order': [],
    'index': 0,
    'show_answer': False,
    'audio_playing': None
}

for key, default in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = default

if not st.session_state.cards:
    st.session_state.cards = load_bilingual_flashcards(DOC_PATH)
if st.session_state.cards and not st.session_state.order:
    st.session_state.order = list(range(len(st.session_state.cards)))
    random.shuffle(st.session_state.order)

# Audio functions
def text_to_speech(text, lang="en"):
    try:
        if not text: return None
        tts = gTTS(text=text, lang=lang, slow=False)
        audio = io.BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)
        return audio.getvalue()
    except:
        return None

def create_audio_player(audio_bytes):
    if audio_bytes:
        b64 = base64.b64encode(audio_bytes).decode()
        return f'<audio controls><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    return ""

# Main app
def main():
    st.set_page_config(page_title="LLB Flashcards", page_icon="📚", layout="wide")
    
    # Sidebar
    with st.sidebar:
        st.title(t('sidebar_title'))
        st.info(t('sidebar_info'))
        if st.session_state.cards:
            st.success(f"**{len(st.session_state.cards)} {t('cards_loaded')}**")
        st.markdown("---")
        st.markdown(f"**{t('current_language')}:**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🇺🇸", key="en_btn", use_container_width=True):
                st.session_state.language = 'English'
                st.rerun()
        with col2:
            if st.button("🇵🇰", key="ur_btn", use_container_width=True):
                st.session_state.language = 'Urdu'
                st.rerun()
        st.markdown("---")
        st.caption(t('made_with'))
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([f"🎴 {t('flashcards')}", f"📝 {t('quiz')}", f"📥 {t('download')}", f"⚙️ {t('settings_tab')}"])
    
    with tab1:
        show_flashcards()
    with tab2:
        show_quiz()
    with tab3:
        show_bulk_download()
    with tab4:
        show_settings()

def show_flashcards():
    st.title(t('app_title'))
    
    # Language switcher
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        st.markdown(f"### {t('current_language')}: **{t('english') if st.session_state.language == 'English' else t('urdu')}**")
    with col3:
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button(f"🇺🇸 {t('english')}", key="to_en"):
                st.session_state.language = 'English'
                st.rerun()
        with btn_col2:
            if st.button(f"🇵🇰 {t('urdu')}", key="to_ur"):
                st.session_state.language = 'Urdu'
                st.rerun()
    
    st.markdown("---")
    
    # Document info
    with st.expander(t('document_info'), expanded=False):
        st.write(f"**{t('total_cards')}:** {len(st.session_state.cards)}")
        if st.session_state.cards:
            st.write(f"**{t('sample_question')}:** {st.session_state.cards[0]['english'][0][:50]}...")
    
    # Check if cards exist
    if not st.session_state.cards:
        st.warning(t('no_flashcards'))
        st.info(f"**{t('expected_format')}:**\n```\n{t('format_example')}\n```")
        return
    
    # Display current card
    idx = st.session_state.order[st.session_state.index]
    card = st.session_state.cards[idx]
    en_q, en_a = card['english']
    ur_q, ur_a = card['urdu']
    
    # Show question
    if st.session_state.language == 'Urdu':
        st.subheader(f"{ur_q}")
        if st.session_state.show_urdu:
            st.markdown(f"*{t('original_text')}: {en_q}*")
    else:
        st.subheader(f"Q: {en_q}")
        if st.session_state.show_urdu:
            st.markdown(f"*{t('urdu_translation')}: {ur_q}*")
    
    # Audio buttons for question
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t('listen_english'), key=f"q_en_{idx}"):
            with st.spinner("Generating..."):
                audio = text_to_speech(en_q, "en")
                if audio:
                    st.session_state[f"audio_q_en_{idx}"] = audio
                    st.success("✅ Ready!")
    with col2:
        if st.button(t('listen_urdu'), key=f"q_ur_{idx}"):
            with st.spinner("Generating..."):
                audio = text_to_speech(ur_q, "ur")
                if audio:
                    st.session_state[f"audio_q_ur_{idx}"] = audio
                    st.success("✅ Ready!")
    
    # Show audio players if available
    if f"audio_q_en_{idx}" in st.session_state:
        st.markdown("**English:**")
        st.markdown(create_audio_player(st.session_state[f"audio_q_en_{idx}"]), unsafe_allow_html=True)
    
    if f"audio_q_ur_{idx}" in st.session_state:
        st.markdown("**Urdu:**")
        st.markdown(create_audio_player(st.session_state[f"audio_q_ur_{idx}"]), unsafe_allow_html=True)
    
    # Download buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t('download_english'), key=f"dl_q_en_{idx}"):
            audio = text_to_speech(en_q, "en")
            if audio:
                b64 = base64.b64encode(audio).decode()
                href = f'<a href="data:audio/mp3;base64,{b64}" download="question_{idx+1}_en.mp3" style="display:none;" id="dl_q_en_{idx}">Download</a>'
                st.markdown(href + '<script>document.getElementById("dl_q_en_{idx}").click();</script>', unsafe_allow_html=True)
    with col2:
        if st.button(t('download_urdu'), key=f"dl_q_ur_{idx}"):
            audio = text_to_speech(ur_q, "ur")
            if audio:
                b64 = base64.b64encode(audio).decode()
                href = f'<a href="data:audio/mp3;base64,{b64}" download="question_{idx+1}_ur.mp3" style="display:none;" id="dl_q_ur_{idx}">Download</a>'
                st.markdown(href + '<script>document.getElementById("dl_q_ur_{idx}").click();</script>', unsafe_allow_html=True)
    
    # Show answer button
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t('show_answer'), key=f"show_{idx}"):
            st.session_state.show_answer = True
            st.rerun()
    
    # Display answer if shown
    if st.session_state.show_answer:
        st.markdown("---")
        if st.session_state.language == 'Urdu':
            st.markdown(f"**{t('answer_in_urdu')}** {ur_a}")
            if st.session_state.show_urdu:
                st.markdown(f"*{t('original_text')}: {en_a}*")
        else:
            st.markdown(f"**A:** {en_a}")
            if st.session_state.show_urdu:
                st.markdown(f"*{t('urdu_translation')}: {ur_a}*")
        
        # Audio for answer
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"{t('listen_english')} (A)", key=f"a_en_{idx}"):
                audio = text_to_speech(en_a, "en")
                if audio:
                    st.session_state[f"audio_a_en_{idx}"] = audio
                    st.success("✅ Ready!")
        with col2:
            if st.button(f"{t('listen_urdu')} (A)", key=f"a_ur_{idx}"):
                audio = text_to_speech(ur_a, "ur")
                if audio:
                    st.session_state[f"audio_a_ur_{idx}"] = audio
                    st.success("✅ Ready!")
        
        # Show answer audio players
        if f"audio_a_en_{idx}" in st.session_state:
            st.markdown("**English Answer:**")
            st.markdown(create_audio_player(st.session_state[f"audio_a_en_{idx}"]), unsafe_allow_html=True)
        
        if f"audio_a_ur_{idx}" in st.session_state:
            st.markdown("**Urdu Answer:**")
            st.markdown(create_audio_player(st.session_state[f"audio_a_ur_{idx}"]), unsafe_allow_html=True)
    
    # Next card button
    with col2:
        if st.button(t('next_card'), key=f"next_{idx}"):
            st.session_state.index = (st.session_state.index + 1) % len(st.session_state.order)
            st.session_state.show_answer = False
            st.rerun()
    
    # Card controls
    with st.expander(f"⚙️ {t('card_settings')}"):
        if st.button(t('shuffle_deck')):
            random.shuffle(st.session_state.order)
            st.session_state.index = 0
            st.session_state.show_answer = False
            st.success("Shuffled!")
            st.rerun()
        
        st.write(f"**Card {st.session_state.index + 1} of {len(st.session_state.order)}**")
        
        # Translation toggle
        st.session_state.show_urdu = st.checkbox(t('view_translation'), st.session_state.show_urdu)
    
    # Navigation
    st.markdown("---")
    st.write(f"**{t('quick_navigation')}:**")
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    with nav_col1:
        if st.button(t('first')):
            st.session_state.index = 0
            st.session_state.show_answer = False
            st.rerun()
    with nav_col2:
        if st.button(t('previous')):
            st.session_state.index = (st.session_state.index - 1) % len(st.session_state.order)
            st.session_state.show_answer = False
            st.rerun()
    with nav_col3:
        if st.button(t('next')):
            st.session_state.index = (st.session_state.index + 1) % len(st.session_state.order)
            st.session_state.show_answer = False
            st.rerun()

def show_quiz():
    st.title("LLB Preparation Quiz")
    st.info("Quiz feature coming soon!")
    st.write("For now, use the flashcards tab to study.")

def show_bulk_download():
    st.title("Bulk Audio Download")
    st.info("Bulk download feature coming soon!")
    st.write("You can download individual audio files from the flashcards tab.")

def show_settings():
    st.subheader("Application Settings")
    
    if st.session_state.cards:
        st.success(f"✅ {len(st.session_state.cards)} flashcards loaded")
    else:
        st.error("No cards loaded")
    
    st.write(f"**Document:** {DOC_PATH}")
    st.write(f"**Exists:** {'✅ Yes' if os.path.exists(DOC_PATH) else '❌ No'}")
    
    if st.button("🔄 Reset Application"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    with st.expander("About This App"):
        st.write("""
        **LLB Preparation Flashcards (Bilingual)**
        - Study in English and Urdu
        - Audio support for both languages
        - Interactive flashcards
        - Made for LLB students
        """)

if __name__ == "__main__":
    main()