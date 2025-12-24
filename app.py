import random
import streamlit as st
from docx import Document
from gtts import gTTS
import io
import base64
import os

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

# Simple English to Urdu question mapping based on your document
def create_urdu_question(english_question):
    """Convert English question to Urdu based on patterns in your document"""
    if "founder of the Analytical School" in english_question:
        return "تجزیاتی فقہ کے مدرسہ کا بانی کون سمجھا جاتا ہے؟"
    elif "Austin's definition of law" in english_question:
        return "آسٹن کی قانون کی تعریف کیا ہے؟"
    elif "main features of the Analytical School" in english_question:
        return "تجزیاتی مدرسہ کی اہم خصوصیات کیا ہیں؟"
    elif "critics of Austin's theory" in english_question:
        return "آسٹن کے نظریے کے دو نقادوں کے نام بتائیں۔"
    elif "Historical School of Jurisprudence" in english_question:
        return "تاریخی فقہ کا مدرسہ کس چیز سے متعلق ہے؟"
    elif "father of the Historical School" in english_question:
        return "تاریخی فقہ کے مدرسہ کا بانی کون سمجھا جاتا ہے؟"
    elif "Savigny's main argument against codification" in english_question:
        return "ساوینی نے قانون کی تدوین کے خلاف کیا دلیل دی؟"
    elif "English jurist is associated with the Historical School" in english_question:
        return "کون سا انگریز ماہر قانون تاریخی مدرسہ سے وابستہ ہے؟"
    elif "Maine's famous theory about the evolution of law" in english_question:
        return "مین کا قانون کی ارتقاء کے بارے میں مشہور نظریہ کیا ہے؟"
    elif "Compare Analytical and Historical Schools" in english_question:
        return "تجزیاتی اور تاریخی مدارس کا موازنہ کریں۔"
    else:
        # Default: convert common question words to Urdu
        question = english_question.lower()
        if "who is" in question:
            return "کون ہے" + english_question.replace("Who is", "").replace("who is", "") + "؟"
        elif "what is" in question:
            return "کیا ہے" + english_question.replace("What is", "").replace("what is", "") + "؟"
        elif "what are" in question:
            return "کیا ہیں" + english_question.replace("What are", "").replace("what are", "") + "؟"
        elif "name" in question:
            return "نام بتائیں" + english_question.replace("Name", "").replace("name", "") + "؟"
        else:
            return "سوال: " + english_question + "؟"

# Load flashcards
def load_cards():
    try:
        doc = Document(DOC_PATH)
        cards = []
        q_en, a_en, a_ur = None, None, None
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text: continue
            
            if text.startswith("Q:"):
                if q_en and a_en:  # Save previous card
                    urdu_question = create_urdu_question(q_en)
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
                a_ur = text.replace("A (Urdu):", "").replace("{dir=\"rtl\"}", "").strip()
        
        # Add last card
        if q_en and a_en:
            urdu_question = create_urdu_question(q_en)
            cards.append({
                'en': (q_en, a_en),
                'ur': (urdu_question, a_ur if a_ur else a_en)
            })
        
        return cards
    except Exception as e:
        st.error(f"Error loading: {e}")
        return []

# Initialize
for key, val in [('lang', 'en'), ('show_urdu', False), ('cards', []), ('order', []), ('index', 0), ('show_ans', False)]:
    if key not in st.session_state:
        st.session_state[key] = val

if not st.session_state.cards:
    st.session_state.cards = load_cards()
if st.session_state.cards and not st.session_state.order:
    st.session_state.order = list(range(len(st.session_state.cards)))
    random.shuffle(st.session_state.order)

# Audio functions
def speak(text, lang):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio = io.BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)
        return audio.getvalue()
    except Exception as e:
        st.error(f"Audio error: {e}")
        return None

def audio_player(audio_bytes):
    if audio_bytes:
        b64 = base64.b64encode(audio_bytes).decode()
        return f'<audio controls style="width:100%"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    return ""

# Main app
def main():
    st.set_page_config(page_title="LLB Flashcards", layout="wide")
    
    # Sidebar
    with st.sidebar:
        st.title(t('sidebar'))
        st.info(t('info'))
        if st.session_state.cards:
            st.success(f"**{len(st.session_state.cards)} {t('total_cards')}**")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🇺🇸 English", use_container_width=True):
                st.session_state.lang = 'en'
                st.rerun()
        with col2:
            if st.button("🇵🇰 Urdu", use_container_width=True):
                st.session_state.lang = 'ur'
                st.rerun()
        st.markdown("---")
        st.caption("For LLB students ❤️")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs([f"🎴 {t('cards')}", f"📝 {t('quiz')}", f"⚙️ {t('settings')}"])
    
    with tab1:
        show_flashcards()
    with tab2:
        show_quiz()
    with tab3:
        show_settings()

def show_flashcards():
    st.title(t('title'))
    
    # Language
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**{t('current')}** {'English' if st.session_state.lang == 'en' else 'اردو'}")
    with col2:
        col_en, col_ur = st.columns(2)
        with col_en:
            if st.button("EN", key="to_en"):
                st.session_state.lang = 'en'
                st.rerun()
        with col_ur:
            if st.button("UR", key="to_ur"):
                st.session_state.lang = 'ur'
                st.rerun()
    
    st.markdown("---")
    
    if not st.session_state.cards:
        st.warning("No flashcards found. Check your document.")
        return
    
    # Current card
    idx = st.session_state.order[st.session_state.index]
    card = st.session_state.cards[idx]
    q_en, a_en = card['en']
    q_ur, a_ur = card['ur']
    
    # Debug: Show what's being loaded
    with st.expander("🔍 Debug Info", expanded=False):
        st.write(f"**Card {idx + 1}:**")
        st.write(f"English Q: {q_en}")
        st.write(f"Urdu Q: {q_ur}")
        st.write(f"English A: {a_en}")
        st.write(f"Urdu A: {a_ur}")
    
    # Show question
    if st.session_state.lang == 'ur':
        # Show actual Urdu question
        st.subheader(f"{q_ur}")
        if st.session_state.show_urdu:
            st.caption(f"English: {q_en}")
    else:
        # Show English question
        st.subheader(f"Q: {q_en}")
        if st.session_state.show_urdu:
            st.caption(f"Urdu: {q_ur}")
    
    # Audio for question
    st.write("### 🔊 Listen to Question")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(t('listen_en'), key=f"qen{idx}", use_container_width=True):
            audio = speak(q_en, "en")
            if audio:
                st.session_state[f"a_qen{idx}"] = audio
                st.success("English audio ready!")
    
    with col2:
        if st.button(t('listen_ur'), key=f"qur{idx}", use_container_width=True):
            # Speak the actual Urdu question
            audio = speak(q_ur, "ur")
            if audio:
                st.session_state[f"a_qur{idx}"] = audio
                st.success("Urdu audio ready!")
    
    # Play audio if available
    if f"a_qen{idx}" in st.session_state:
        st.write("**English Audio:**")
        st.markdown(audio_player(st.session_state[f"a_qen{idx}"]), unsafe_allow_html=True)
    
    if f"a_qur{idx}" in st.session_state:
        st.write("**Urdu Audio:**")
        st.markdown(audio_player(st.session_state[f"a_qur{idx}"]), unsafe_allow_html=True)
    
    # Download audio
    st.write("### 📥 Download Audio")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t('download_en'), key=f"dlen{idx}", use_container_width=True):
            audio = speak(q_en, "en")
            if audio:
                b64 = base64.b64encode(audio).decode()
                st.markdown(f'<a href="data:audio/mp3;base64,{b64}" download="question_{idx+1}_en.mp3" style="display:none;" id="dl{idx}en">DL</a><script>document.getElementById("dl{idx}en").click();</script>', unsafe_allow_html=True)
                st.success("Downloading English audio...")
    
    with col2:
        if st.button(t('download_ur'), key=f"dlur{idx}", use_container_width=True):
            audio = speak(q_ur, "ur")
            if audio:
                b64 = base64.b64encode(audio).decode()
                st.markdown(f'<a href="data:audio/mp3;base64,{b64}" download="question_{idx+1}_ur.mp3" style="display:none;" id="dl{idx}ur">DL</a><script>document.getElementById("dl{idx}ur").click();</script>', unsafe_allow_html=True)
                st.success("Downloading Urdu audio...")
    
    # Show answer section
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t('show_answer'), key=f"show{idx}", use_container_width=True):
            st.session_state.show_ans = True
            st.rerun()
    
    # Display answer if shown
    if st.session_state.show_ans:
        st.markdown("## 📝 Answer")
        
        if st.session_state.lang == 'ur':
            st.markdown(f"**جواب:** {a_ur}")
            if st.session_state.show_urdu:
                st.caption(f"English: {a_en}")
        else:
            st.markdown(f"**A:** {a_en}")
            if st.session_state.show_urdu:
                st.caption(f"Urdu: {a_ur}")
        
        # Audio for answer
        st.write("### 🔊 Listen to Answer")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"{t('listen_en')} Answer", key=f"aen{idx}", use_container_width=True):
                audio = speak(a_en, "en")
                if audio:
                    st.session_state[f"a_aen{idx}"] = audio
                    st.success("English answer audio ready!")
        
        with col2:
            if st.button(f"{t('listen_ur')} Answer", key=f"aur{idx}", use_container_width=True):
                audio = speak(a_ur, "ur")
                if audio:
                    st.session_state[f"a_aur{idx}"] = audio
                    st.success("Urdu answer audio ready!")
        
        # Play answer audio
        if f"a_aen{idx}" in st.session_state:
            st.write("**English Answer Audio:**")
            st.markdown(audio_player(st.session_state[f"a_aen{idx}"]), unsafe_allow_html=True)
        
        if f"a_aur{idx}" in st.session_state:
            st.write("**Urdu Answer Audio:**")
            st.markdown(audio_player(st.session_state[f"a_aur{idx}"]), unsafe_allow_html=True)
    
    # Next card button
    with col2:
        if st.button(t('next'), key=f"next{idx}", use_container_width=True):
            st.session_state.index = (st.session_state.index + 1) % len(st.session_state.order)
            st.session_state.show_ans = False
            st.rerun()
    
    # Controls
    st.markdown("---")
    with st.expander("⚙️ Controls"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t('shuffle'), use_container_width=True):
                random.shuffle(st.session_state.order)
                st.session_state.index = 0
                st.session_state.show_ans = False
                st.success("Cards shuffled!")
                st.rerun()
        
        with col2:
            if st.button(t('prev'), use_container_width=True):
                st.session_state.index = (st.session_state.index - 1) % len(st.session_state.order)
                st.session_state.show_ans = False
                st.rerun()
        
        st.write(f"**Card {st.session_state.index + 1} of {len(st.session_state.order)}**")
        st.session_state.show_urdu = st.checkbox(t('view_urdu'), st.session_state.show_urdu)

def show_quiz():
    st.title("Quiz")
    st.info("Quiz feature coming soon! Use flashcards for now.")
    if st.session_state.cards:
        st.write(f"You have {len(st.session_state.cards)} cards to study.")

def show_settings():
    st.title("Settings")
    
    st.write(f"**Document:** {DOC_PATH}")
    st.write(f"**Status:** {'✅ Found' if os.path.exists(DOC_PATH) else '❌ Not found'}")
    st.write(f"**Loaded cards:** {len(st.session_state.cards)}")
    
    if st.button("🔄 Reset App", type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("App reset! Refresh page.")
        st.rerun()

if __name__ == "__main__":
    main()