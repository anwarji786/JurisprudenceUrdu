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

# ====================== PATH HANDLING ======================
current_dir = os.path.dirname(os.path.abspath(__file__))
DOC_PATH = os.path.join(current_dir, "Law Preparation.docx")
if not os.path.exists(DOC_PATH):
    possible_paths = [
        DOC_PATH,
        "Law Preparation.docx",
        "./Law Preparation.docx",
        "../Law Preparation.docx",
        os.path.join(os.getcwd(), "Law Preparation.docx")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            DOC_PATH = path
            break
    else:
        st.error("❌ Document not found. Please ensure 'Law Preparation.docx' is in the repository.")
        st.stop()
# ==========================================================

# UI TRANSLATIONS
UI_TRANSLATIONS = {
    'English': {
        'app_title': "LLB Preparation Flashcards with Voiceover",
        'quiz_title': "LLB Preparation Quiz",
        'bulk_download': "Bulk Audio Download",
        'settings': "Application Settings",
        'flashcards': "Flashcards",
        'quiz': "Quiz",
        'download': "Bulk Download",
        'settings_tab': "Settings",
        'document_info': "Document Information",
        'total_cards': "Total Cards",
        'sample_question': "Sample Question",
        'currently_playing': "Currently playing audio",
        'stop_all_audio': "Stop All Audio",
        'no_audio': "No audio currently playing",
        'no_flashcards': "No flashcards found. Ensure your document uses Q:/A: lines.",
        'expected_format': "Expected format:",
        'format_example': "Q: What is the definition of law?\nA: Law is a system of rules...",
        'play_question': "🔊 Play Question",
        'stop': "⏹️ Stop",
        'question_audio': "⬇️ Question Audio",
        'playing_loop': "🔁 Playing question audio on loop...",
        'show_answer': "Show Answer",
        'next_card': "Next Card",
        'play_answer': "🔊 Play Answer",
        'answer_audio': "⬇️ Answer Audio",
        'combined_qa': "⬇️ Combined Q&A Audio",
        'card_settings': "Card Settings",
        'shuffle_deck': "Shuffle Deck",
        'quick_navigation': "Quick Navigation",
        'first': "⏮️ First",
        'previous': "⏪ Previous",
        'next': "⏩ Next",
        'test_knowledge': "Test your knowledge with this interactive quiz!",
        'cards_available': "Total flashcards available",
        'num_questions': "Number of questions:",
        'start_quiz': "🚀 Start Quiz",
        'questions': "Questions",
        'progress': "Progress",
        'select_answer': "Select the correct answer:",
        'correct_answer': "Correct answer:",
        'next_question': "➡️ Next Question",
        'choose_answer': "Choose your answer:",
        'skip_question': "⏭️ Skip Question",
        'quiz_completed': "🎉 Quiz Completed!",
        'total_questions': "Total Questions",
        'correct_answers': "Correct Answers",
        'score': "Score",
        'excellent': "🏆 Excellent! You're mastering the material!",
        'good_job': "👍 Good job! Solid understanding!",
        'keep_practicing': "📚 Keep practicing! You're getting there!",
        'review_material': "💪 Review the material and try again!",
        'retry_quiz': "🔄 Retry Quiz",
        'new_quiz': "📝 New Quiz",
        'generate_download': "Generate and download audio files for your flashcards",
        'bulk_note': "⚠️ Note: Bulk download generates audio on-demand and may take time for large sets.",
        'select_type': "Select download type:",
        'question_only': "Question only",
        'answer_only': "Answer only",
        'question_then_answer': "Question then Answer",
        'generate_package': "🛠️ Generate Download Package",
        'downloading': "Download Audio Files",
        'generated_files': "Generated audio files!",
        'zip_info': "The zip file contains audio files in MP3 format.",
        'loaded_cards': "Loaded flashcards",
        'no_cards_loaded': "No flashcards loaded",
        'document_path': "Document Path",
        'file_exists': "File Exists",
        'sample_cards': "Sample Cards",
        'reset_state': "🔄 Reset Application State",
        'about_app': "ℹ️ About This App",
        'sidebar_title': "📚 LLB Prep",
        'sidebar_info': "Study LLB materials with interactive flashcards and voice support",
        'cards_loaded': "cards loaded",
        'made_with': "Made with ❤️ for LLB students",
        'language': "🌐 Language",
        'english': "English",
        'urdu': "Urdu",
        'display_mode': "Display Mode",
        'voice_language': "Voice Language",
        'urdu_voice': "Urdu Voice",
        'english_voice': "English Voice",
        'view_translation': "View Urdu Translation",
        'hide_translation': "Hide Urdu Translation",
        'original_text': "Original Text",
        'urdu_translation': "Urdu Translation",
        'listen_urdu': "🔊 Listen in Urdu",
        'listen_english': "🔊 Listen in English",
        'download_urdu': "⬇️ Urdu Audio",
        'download_english': "⬇️ English Audio",
        'combined_bilingual': "⬇️ Combined Bilingual Audio",
        'question_in_urdu': "سوال:",
        'answer_in_urdu': "جواب:",
        'translation_loading': "Translating to Urdu...",
        'translation_error': "Translation not available",
        'enter_urdu': "Enter Urdu Translation",
        'manual_translation': "Manual Translation",
        'save_translation': "💾 Save Translation",
        'translation_saved': "✅ Translation saved!",
        'urdu_text_placeholder': "Type Urdu translation here...",
        'switch_to_urdu': "Switch to Urdu",
        'switch_to_english': "Switch to English",
        'current_language': "Current Language",
        'language_switch': "🌐 Language Switch",
        'quiz_not_available': "⚠️ Quiz not available - no flashcards loaded",
        'load_cards_first': "Please load flashcards first from the Flashcards tab."
    },
    'Urdu': {
        'app_title': "ایل ایل بی تیاری فلیش کارڈز وائس اوور کے ساتھ",
        'quiz_title': "ایل ایل بی تیاری کوئز",
        'bulk_download': "بڑے پیمانے پر آڈیو ڈاؤن لوڈ",
        'settings': "ایپلیکیشن کی ترتیبات",
        'flashcards': "فلیش کارڈز",
        'quiz': "کوئز",
        'download': "بڑے پیمانے پر ڈاؤن لوڈ",
        'settings_tab': "ترتیبات",
        'document_info': "دستاویز کی معلومات",
        'total_cards': "کل کارڈز",
        'sample_question': "نمونہ سوال",
        'currently_playing': "فی الحال آڈیو چل رہا ہے",
        'stop_all_audio': "تمام آڈیو روکیں",
        'no_audio': "فی الحال کوئی آڈیو نہیں چل رہا",
        'no_flashcards': "کوئی فلیش کارڈز نہیں ملے۔ یقینی بنائیں کہ آپ کا دستاویز Q:/A: لائنز استعمال کرتا ہے۔",
        'expected_format': "متوقع فارمیٹ:",
        'format_example': "Q: قانون کی تعریف کیا ہے؟\nA: قانون اصولوں کا ایک نظام ہے...",
        'play_question': "🔊 سوال سنیں",
        'stop': "⏹️ روکیں",
        'question_audio': "⬇️ سوال آڈیو",
        'playing_loop': "🔁 سوال کا آڈیو لوپ پر چل رہا ہے...",
        'show_answer': "جواب دکھائیں",
        'next_card': "اگلا کارڈ",
        'play_answer': "🔊 جواب سنیں",
        'answer_audio': "⬇️ جواب آڈیو",
        'combined_qa': "⬇️ مربوط سوال اور جواب آڈیو",
        'card_settings': "کارڈ کی ترتیبات",
        'shuffle_deck': "کارڈز کو ہلائیں",
        'quick_navigation': "فوری نیوی گیشن",
        'first': "⏮️ پہلا",
        'previous': "⏪ پچھلا",
        'next': "⏩ اگلا",
        'test_knowledge': "اس انٹرایکٹو کوئز کے ساتھ اپنے علم کا آزمائش کریں!",
        'cards_available': "کل دستیاب فلیش کارڈز",
        'num_questions': "سوالات کی تعداد:",
        'start_quiz': "🚀 کوئز شروع کریں",
        'questions': "سوالات",
        'progress': "پیشرفت",
        'select_answer': "درست جواب منتخب کریں:",
        'correct_answer': "درست جواب:",
        'next_question': "➡️ اگلا سوال",
        'choose_answer': "اپنا جواب منتخب کریں:",
        'skip_question': "⏭️ سوال چھوڑیں",
        'quiz_completed': "🎉 کوئز مکمل ہو گیا!",
        'total_questions': "کل سوالات",
        'correct_answers': "صحیح جوابات",
        'score': "اسکور",
        'excellent': "🏆 شاندار! آپ مواد پر عبور حاصل کر رہے ہیں!",
        'good_job': "👍 اچھا کام! مضبوط سمجھ!",
        'keep_practicing': "📚 مشق جاری رکھیں! آپ قریب پہنچ گئے ہیں!",
        'review_material': "💪 مواد کا جائزہ لیں اور دوبارہ کوشش کریں!",
        'retry_quiz': "🔄 کوئز دوبارہ کریں",
        'new_quiz': "📝 نیا کوئز",
        'generate_download': "اپنے فلیش کارڈز کے لیے آڈیو فائلیں بنائیں اور ڈاؤن لوڈ کریں",
        'bulk_note': "⚠️ نوٹ: بڑے پیمانے پر ڈاؤن لوڈ آن ڈیمانڈ آڈیو تیار کرتا ہے اور بڑے سیٹس کے لیے وقت لے سکتا ہے۔",
        'select_type': "ڈاؤن لوڈ کی قسم منتخب کریں:",
        'question_only': "صرف سوال",
        'answer_only': "صرف جواب",
        'question_then_answer': "سوال پھر جواب",
        'generate_package': "🛠️ ڈاؤن لوڈ پیکیج تیار کریں",
        'downloading': "آڈیو فائلیں ڈاؤن لوڈ کریں",
        'generated_files': "آڈیو فائلیں تیار ہو گئیں!",
        'zip_info': "زپ فائل MP3 فارمیٹ میں آڈیو فائلیں پر مشتمل ہے۔",
        'loaded_cards': "فلیش کارڈز لوڈ ہو گئے",
        'no_cards_loaded': "کوئی کارڈ لوڈ نہیں ہوا",
        'document_path': "دستاویز کا راستہ",
        'file_exists': "فائل موجود ہے",
        'sample_cards': "نمونہ کارڈز",
        'reset_state': "🔄 ایپلیکیشن کی حالت ری سیٹ کریں",
        'about_app': "ℹ️ اس ایپ کے بارے میں",
        'sidebar_title': "📚 ایل ایل بی تیاری",
        'sidebar_info': "انٹرایکٹو فلیش کارڈز اور وائس سپورٹ کے ساتھ ایل ایل بی مواد کا مطالعہ کریں",
        'cards_loaded': "کارڈز لوڈ ہو گئے",
        'made_with': "ایل ایل بی طلباء کے لیے ❤️ کے ساتھ بنایا گیا",
        'language': "🌐 زبان",
        'english': "انگریزی",
        'urdu': "اردو",
        'display_mode': "ڈسپلے موڈ",
        'voice_language': "آواز کی زبان",
        'urdu_voice': "اردو آواز",
        'english_voice': "انگریزی آواز",
        'view_translation': "اردو ترجمہ دیکھیں",
        'hide_translation': "اردو ترجمہ چھپائیں",
        'original_text': "اصل متن",
        'urdu_translation': "اردو ترجمہ",
        'listen_urdu': "🔊 اردو میں سنیں",
        'listen_english': "🔊 انگریزی میں سنیں",
        'download_urdu': "⬇️ اردو آڈیو",
        'download_english': "⬇️ انگریزی آڈیو",
        'combined_bilingual': "⬇️ مربوط دو زبانی آڈیو",
        'question_in_urdu': "سوال:",
        'answer_in_urdu': "جواب:",
        'translation_loading': "اردو میں ترجمہ ہو رہا ہے...",
        'translation_error': "ترجمہ دستیاب نہیں",
        'enter_urdu': "اردو ترجمہ درج کریں",
        'manual_translation': "دستی ترجمہ",
        'save_translation': "💾 ترجمہ محفوظ کریں",
        'translation_saved': "✅ ترجمہ محفوظ ہو گیا!",
        'urdu_text_placeholder': "اردو ترجمہ یہاں ٹائپ کریں...",
        'switch_to_urdu': "اردو میں تبدیل کریں",
        'switch_to_english': "انگریزی میں تبدیل کریں",
        'current_language': "موجودہ زبان",
        'language_switch': "🌐 زبان تبدیل کریں",
        'quiz_not_available': "⚠️ کوئز دستیاب نہیں - کوئی فلیش کارڈز لوڈ نہیں ہوئے",
        'load_cards_first': "براہ کرم پہلے فلیش کارڈز ٹیب سے فلیش کارڈز لوڈ کریں۔"
    }
}

def t(key):
    lang = st.session_state.language
    if lang in UI_TRANSLATIONS and key in UI_TRANSLATIONS[lang]:
        return UI_TRANSLATIONS[lang][key]
    return UI_TRANSLATIONS['English'].get(key, key)

def remove_emojis(text):
    if not text:
        return ""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

def load_bilingual_flashcards(doc_path):
    try:
        document = Document(doc_path)
        cards = []
        english_question = None
        english_answer = None
        urdu_answer = None
        for para in document.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            if text.startswith("Q:") and "(Urdu)" not in text:
                if english_question and english_answer:
                    cards.append({
                        'english': (english_question, english_answer),
                        'urdu': (f"سوال: {english_question}", urdu_answer if urdu_answer else english_answer)
                    })
                english_question = text[2:].strip()
                english_answer = None
                urdu_answer = None
            elif text.startswith("A:") and "(Urdu)" not in text and english_question:
                english_answer = text[2:].strip()
            elif "A" in text and "(Urdu)" in text and english_question and english_answer:
                urdu_answer = text.split(":", 1)[1].strip() if ":" in text else text.replace("A (Urdu)", "").strip()
        if english_question and english_answer:
            cards.append({
                'english': (english_question, english_answer),
                'urdu': (f"سوال: {english_question}", urdu_answer if urdu_answer else english_answer)
            })
        if not cards:
            st.warning(t('no_flashcards'))
            st.info(f"{t('expected_format')}\n```\n{t('format_example')}\n```")
        return cards
    except Exception as e:
        st.error(f"Error reading document: {e}")
        return []

# Initialize session states
if 'language' not in st.session_state:
    st.session_state.language = 'English'
if 'translations' not in st.session_state:
    st.session_state.translations = {}
if 'show_urdu' not in st.session_state:
    st.session_state.show_urdu = False
if 'manual_translations' not in st.session_state:
    st.session_state.manual_translations = {}
if "cards" not in st.session_state:
    try:
        st.session_state.cards = load_bilingual_flashcards(DOC_PATH)
    except Exception as e:
        st.error(f"Error loading flashcards: {e}")
        st.session_state.cards = []
if "order" not in st.session_state and st.session_state.cards:
    st.session_state.order = list(range(len(st.session_state.cards)))
    random.shuffle(st.session_state.order)
if "index" not in st.session_state:
    st.session_state.index = 0
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False
if 'audio_playing' not in st.session_state:
    st.session_state.audio_playing = None
if 'stop_requested' not in st.session_state:
    st.session_state.stop_requested = False
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}
if 'quiz_feedback' not in st.session_state:
    st.session_state.quiz_feedback = {}
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'quiz_cards' not in st.session_state:
    st.session_state.quiz_cards = []
if 'quiz_type' not in st.session_state:
    st.session_state.quiz_type = "Question to Answer"

# Utility Functions
def text_to_speech(text, lang="en"):
    try:
        if not text:
            st.warning("No text to convert to speech.")
            return None
        clean_text = remove_emojis(text)
        clean_text = ' '.join(clean_text.split())
        if not clean_text.strip():
            clean_text = "No text available"
        tts = gTTS(text=clean_text, lang=lang, slow=False, timeout=10)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes.getvalue()
    except Exception as e:
        st.error(f"❌ Audio generation failed: {e}")
        st.info("Note: Audio generation requires internet connection. Try again later.")
        return None

def stop_audio():
    st.session_state.stop_requested = True
    st.session_state.audio_playing = None

def generate_combined_audio(question_text, answer_text, lang="en"):
    try:
        question_audio = text_to_speech(question_text, lang=lang)
        answer_audio = text_to_speech(answer_text, lang=lang)
        if question_audio and answer_audio:
            return question_audio + answer_audio
        return None
    except Exception as e:
        st.error(f"Error generating combined audio: {e}")
        return None

def generate_bilingual_audio(english_text, urdu_text):
    try:
        english_audio = text_to_speech(english_text, lang="en")
        urdu_audio = text_to_speech(urdu_text, lang="ur")
        if english_audio and urdu_audio:
            return english_audio + urdu_audio
        return None
    except Exception as e:
        st.error(f"Error generating bilingual audio: {e}")
        return None

# Tab Functions
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
    with st.sidebar:
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
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button(t('listen_english'), key="play_question_en", disabled=is_playing):
                with st.spinner("Generating audio..."):
                    audio_bytes = text_to_speech(english_question, lang="en")
                    if audio_bytes:
                        st.session_state[f"audio_{current_audio_id}"] = audio_bytes
                        st.session_state.audio_playing = current_audio_id
                        st.rerun()
        with col2:
            if st.button(t('listen_urdu'), key="play_question_ur", disabled=is_playing):
                with st.spinner("Generating audio..."):
                    audio_bytes = text_to_speech(urdu_question, lang="ur")
                    if audio_bytes:
                        st.session_state[f"audio_{current_audio_id}"] = audio_bytes
                        st.session_state.audio_playing = current_audio_id
                        st.rerun()
        with col3:
            if is_playing:
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
                        href = f'<a href="audio/mp3;base64,{b64}" download="{filename}">'
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
                        href = f'<a href="audio/mp3;base64,{b64}" download="{filename}">'
                        st.markdown(f'{href}<button style="display:none;" id="download_q_ur_{idx}">Download</button></a>', unsafe_allow_html=True)
                        st.markdown(f'<script>document.getElementById("download_q_ur_{idx}").click();</script>', unsafe_allow_html=True)
                        st.success(f"Download started: {filename}")

        if is_playing and not st.session_state.stop_requested:
            audio_bytes = st.session_state.get(f"audio_{current_audio_id}")
            if audio_bytes:
                audio_html = f"""
                <audio autoplay loop style="display:none;">
                <source src="audio/mp3;base64,{base64.b64encode(audio_bytes).decode()}" type="audio/mp3">
                Your browser does not support the audio element.
                </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
                st.success(t('playing_loop'))

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
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button(t('listen_english'), key="play_answer_en", disabled=is_playing_answer):
                    with st.spinner("Generating audio..."):
                        audio_bytes = text_to_speech(english_answer, lang="en")
                        if audio_bytes:
                            st.session_state[f"audio_{current_audio_id_answer}"] = audio_bytes
                            st.session_state.audio_playing = current_audio_id_answer
                            st.rerun()
            with col2:
                if st.button(t('listen_urdu'), key="play_answer_ur", disabled=is_playing_answer):
                    with st.spinner("Generating audio..."):
                        audio_bytes = text_to_speech(urdu_answer, lang="ur")
                        if audio_bytes:
                            st.session_state[f"audio_{current_audio_id_answer}"] = audio_bytes
                            st.session_state.audio_playing = current_audio_id_answer
                            st.rerun()
            with col3:
                if is_playing_answer:
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
                            href = f'<a href="audio/mp3;base64,{b64}" download="{filename}">'
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
                            href = f'<a href="audio/mp3;base64,{b64}" download="{filename}">'
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
                            href = f'<a href="audio/mp3;base64,{b64}" download="{filename}">'
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
                            href = f'<a href="audio/mp3;base64,{b64}" download="{filename}">'
                            st.markdown(f'{href}<button style="display:none;" id="download_bilingual_{idx}">Download</button></a>', unsafe_allow_html=True)
                            st.markdown(f'<script>document.getElementById("download_bilingual_{idx}").click();</script>', unsafe_allow_html=True)
                            st.success(f"Download started: {filename}")

            if is_playing_answer and not st.session_state.stop_requested:
                audio_bytes = st.session_state.get(f"audio_{current_audio_id_answer}")
                if audio_bytes:
                    audio_html = f"""
                    <audio autoplay loop style="display:none;">
                    <source src="audio/mp3;base64,{base64.b64encode(audio_bytes).decode()}" type="audio/mp3">
                    Your browser does not support the audio element.
                    </audio>
                    """
                    st.markdown(audio_html, unsafe_allow_html=True)
                    st.success(t('playing_loop'))

def handle_show_answer():
    st.session_state.show_answer = True

def handle_next_card():
    if "order" in st.session_state and st.session_state.order:
        st.session_state.index = (st.session_state.index + 1) % len(st.session_state.order)
    st.session_state.show_answer = False
    st.session_state.audio_playing = None
    st.session_state.stop_requested = False

col1, col2 = st.columns(2)
col1.button(t('show_answer'), on_click=handle_show_answer)
col2.button(t('next_card'), on_click=handle_next_card)

with st.expander(f"⚙️ {t('card_settings')}"):
    if st.button(t('shuffle_deck')):
        if st.session_state.cards:
            st.session_state.order = list(range(len(st.session_state.cards)))
            random.shuffle(st.session_state.order)
            st.session_state.index = 0
            st.session_state.show_answer = False
            st.session_state.audio_playing = None
            st.session_state.stop_requested = False
            st.success("Deck shuffled!")
        else:
            st.warning("No flashcards to shuffle.")
    
    if "order" in st.session_state and st.session_state.order:
        st.write(f"**{t('card_settings')} {st.session_state.index + 1} of {len(st.session_state.order)}**")
    else:
        st.write(f"**{t('card_settings')} — No cards available**")

    st.markdown("---")
    st.write(f"**{t('quick_navigation')}:**")
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    with nav_col1:
        if st.button(t('first')):
            if "order" in st.session_state and st.session_state.order:
                st.session_state.index = 0
                st.session_state.show_answer = False
                st.session_state.audio_playing = None
                st.rerun()
    with nav_col2:
        if st.button(t('previous')):
            if "order" in st.session_state and st.session_state.order:
                st.session_state.index = (st.session_state.index - 1) % len(st.session_state.order)
                st.session_state.show_answer = False
                st.session_state.audio_playing = None
                st.rerun()
    with nav_col3:
        if st.button(t('next')):
            if "order" in st.session_state and st.session_state.order:
                st.session_state.index = (st.session_state.index + 1) % len(st.session_state.order)
                st.session_state.show_answer = False
                st.session_state.audio_playing = None
                st.rerun()

def show_quiz():
    st.title(t('quiz_title'))
    with st.container():
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"### {t('current_language')}: **{t('english') if st.session_state.language == 'English' else t('urdu')}**")
        with col2:
            st.markdown("### 🌐")
        with col3:
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button(f"🇺🇸 {t('english')}", type="primary" if st.session_state.language == 'English' else "secondary", use_container_width=True, key="quiz_switch_to_english"):
                    st.session_state.language = 'English'
                    st.rerun()
            with btn_col2:
                if st.button(f"🇵🇰 {t('urdu')}", type="primary" if st.session_state.language == 'Urdu' else "secondary", use_container_width=True, key="quiz_switch_to_urdu"):
                    st.session_state.language = 'Urdu'
                    st.rerun()
    st.markdown("---")
    if not st.session_state.cards:
        st.warning(t('quiz_not_available'))
        st.info(t('load_cards_first'))
        return

    if not st.session_state.quiz_started:
        st.write(t('test_knowledge'))
        st.write(f"{t('cards_available')}: {len(st.session_state.cards)}")
        total_cards = len(st.session_state.cards)
        if total_cards == 0:
            st.error("No flashcards available for quiz.")
            return
        min_questions = 3
        max_questions = min(20, total_cards)
        default_questions = min(10, total_cards)
        if min_questions > max_questions:
            st.error(f"Need at least {min_questions} flashcards for a quiz. Currently have {total_cards}.")
            return
        num_questions = st.slider(
            t('num_questions'),
            min_value=min_questions,
            max_value=max_questions,
            value=default_questions
        )
        quiz_lang = st.radio(
            t('language'),
            ["English", "Urdu"],
            horizontal=True
        )
        if st.button(t('start_quiz'), type="primary"):
            if len(st.session_state.cards) < 4:
                st.error("Need at least 4 flashcards to create a quiz with options.")
                return
            st.session_state.quiz_started = True
            st.session_state.quiz_completed = False
            st.session_state.quiz_answers = {}
            st.session_state.quiz_feedback = {}
            st.session_state.current_question_index = 0
            st.session_state.quiz_language = quiz_lang
            if len(st.session_state.cards) <= num_questions:
                quiz_cards = st.session_state.cards.copy()
            else:
                quiz_cards = random.sample(st.session_state.cards, num_questions)
            st.session_state.quiz_cards = quiz_cards
            st.session_state.quiz_type = "Question to Answer"
            st.rerun()
    else:
        quiz_cards = st.session_state.quiz_cards
        current_index = st.session_state.current_question_index
        if not st.session_state.quiz_completed:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.metric(t('questions'), f"{current_index + 1}/{len(quiz_cards)}")
            with col2:
                percentage = ((current_index) / len(quiz_cards)) * 100 if quiz_cards else 0
                st.metric(t('progress'), f"{percentage:.0f}%")
            st.markdown("---")
            if current_index < len(quiz_cards):
                card = quiz_cards[current_index]
                english_question, english_answer = card['english']
                if 'urdu' in card:
                    urdu_question, urdu_answer = card['urdu']
                else:
                    urdu_question, urdu_answer = f"سوال: {english_question}", english_answer

                question_num = current_index + 1
                st.subheader(f"{t('questions')} {question_num} of {len(quiz_cards)}")
                if st.session_state.quiz_language == "Urdu":
                    display_question = urdu_question
                    st.markdown(f'<h3 style="color:#FF0000;">{display_question}</h3>', unsafe_allow_html=True)
                else:
                    display_question = english_question
                    st.markdown(f'<h3 style="color:#FF0000;">{display_question}</h3>', unsafe_allow_html=True)

                st.write(f"{t('select_answer')}")
                if current_index in st.session_state.quiz_answers:
                    selected_answer = st.session_state.quiz_answers[current_index]
                    if st.session_state.quiz_language == "Urdu":
                        display_answer = urdu_answer
                        st.info(f"**{t('correct_answer')}:** {display_answer}")
                    else:
                        display_answer = english_answer
                        st.info(f"**{t('correct_answer')}:** {display_answer}")
                    if st.button(t('next_question'), key=f"next_{current_index}", type="primary"):
                        if current_index + 1 < len(quiz_cards):
                            st.session_state.current_question_index = current_index + 1
                        else:
                            st.session_state.quiz_completed = True
                        st.rerun()
                else:
                    correct_answer = urdu_answer if st.session_state.quiz_language == "Urdu" else english_answer
                    options = [correct_answer]
                    other_cards = [c for c in st.session_state.cards if c != card]
                    if len(other_cards) >= 3:
                        other_options = random.sample(other_cards, 3)
                        for opt_card in other_options:
                            wrong_answer = opt_card['urdu'][1] if st.session_state.quiz_language == "Urdu" else opt_card['english'][1]
                            options.append(wrong_answer)
                    else:
                        if st.session_state.quiz_language == "Urdu":
                            options.extend([
                                "یہ سیاق و سباق میں لاگو نہیں ہوتا",
                                "یہ ایک غلط تشریح ہے",
                                "اس کے برعکس صحیح ہے"
                            ])
                        else:
                            options.extend([
                                "Not applicable in this context",
                                "This is an incorrect interpretation",
                                "The opposite is true"
                            ])
                    random.shuffle(options)
                    radio_key = f"quiz_radio_{current_index}"
                    selected_answer = st.radio(
                        f"{t('choose_answer')}",
                        options,
                        key=radio_key,
                        index=None
                    )
                    if selected_answer:
                        st.session_state.quiz_answers[current_index] = selected_answer
                        if selected_answer == correct_answer:
                            st.success("✅ Correct!")
                            st.balloons()
                        else:
                            st.error("❌ Incorrect")
                            st.info(f"**{t('correct_answer')}:** {correct_answer}")
                        time.sleep(2)
                        if current_index + 1 < len(quiz_cards):
                            st.session_state.current_question_index = current_index + 1
                        else:
                            st.session_state.quiz_completed = True
                        st.rerun()
                    if st.button(t('skip_question'), key=f"skip_{current_index}", type="secondary"):
                        st.session_state.quiz_answers[current_index] = "SKIPPED"
                        if current_index + 1 < len(quiz_cards):
                            st.session_state.current_question_index = current_index + 1
                        else:
                            st.session_state.quiz_completed = True
                        st.rerun()
            else:
                st.session_state.quiz_completed = True
                st.rerun()
        else:
            st.balloons()
            st.success(t('quiz_completed'))
            total_questions = len(quiz_cards)
            correct_answers = 0
            for i in range(total_questions):
                user_answer = st.session_state.quiz_answers.get(i, "")
                card = quiz_cards[i]
                correct_answer = card['urdu'][1] if st.session_state.quiz_language == "Urdu" else card['english'][1]
                if user_answer == correct_answer:
                    correct_answers += 1
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(t('total_questions'), total_questions)
            with col2:
                st.metric(t('correct_answers'), correct_answers)
            with col3:
                percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
                st.metric(t('score'), f"{percentage:.1f}%")
            if percentage >= 80:
                st.success(t('excellent'))
            elif percentage >= 60:
                st.info(t('good_job'))
            elif percentage >= 40:
                st.warning(t('keep_practicing'))
            else:
                st.error(t('review_material'))
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(t('retry_quiz'), use_container_width=True):
                    st.session_state.quiz_started = True
                    st.session_state.quiz_completed = False
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_feedback = {}
                    st.session_state.current_question_index = 0
                    st.rerun()
            with col2:
                if st.button(t('new_quiz'), use_container_width=True, type="primary"):
                    st.session_state.quiz_started = False
                    st.session_state.quiz_completed = False
                    st.session_state.current_question_index = 0
                    st.rerun()

def show_bulk_download():
    st.title(t('bulk_download'))
    with st.container():
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"### {t('current_language')}: **{t('english') if st.session_state.language == 'English' else t('urdu')}**")
        with col2:
            st.markdown("### 🌐")
        with col3:
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button(f"🇺🇸 {t('english')}", type="primary" if st.session_state.language == 'English' else "secondary", use_container_width=True, key="download_switch_to_english"):
                    st.session_state.language = 'English'
                    st.rerun()
            with btn_col2:
                if st.button(f"🇵🇰 {t('urdu')}", type="primary" if st.session_state.language == 'Urdu' else "secondary", use_container_width=True, key="download_switch_to_urdu"):
                    st.session_state.language = 'Urdu'
                    st.rerun()
    st.markdown("---")
    st.write(t('generate_download'))
    st.warning(t('bulk_note'))
    if not st.session_state.cards:
        st.warning("No flashcards available for download.")
        return

    download_options = [t('question_only'), t('answer_only'), t('question_then_answer')]
    selected_type = st.selectbox(
        t('select_type'),
        download_options
    )
    audio_lang = st.radio(
        t('voice_language'),
        ["English", "Urdu"],
        horizontal=True
    )
    max_cards = min(20, len(st.session_state.cards))
    if st.button(t('generate_package'), type="primary"):
        if len(st.session_state.cards) > 20:
            st.warning(f"Generating audio for first 20 cards only (out of {len(st.session_state.cards)}) for performance.")
        with st.spinner(f"Generating audio files (this may take a minute)..."):
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    zip_filename = f"llb_flashcards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                    zip_path = os.path.join(tmpdir, zip_filename)
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        processed = 0
                        progress_bar = st.progress(0)
                        for i, card in enumerate(st.session_state.cards[:max_cards]):
                            progress = (i + 1) / max_cards
                            progress_bar.progress(progress)
                            english_question, english_answer = card['english']
                            if 'urdu' in card:
                                urdu_question, urdu_answer = card['urdu']
                            else:
                                urdu_question, urdu_answer = f"سوال: {english_question}", english_answer

                            if selected_type == t('question_only'):
                                if audio_lang == "English":
                                    audio_bytes = text_to_speech(english_question, lang="en")
                                else:
                                    audio_bytes = text_to_speech(urdu_question, lang="ur")
                                if audio_bytes:
                                    lang_suffix = "_en" if audio_lang == "English" else "_ur"
                                    filename = f"question_{i+1:02d}{lang_suffix}.mp3"
                                    zipf.writestr(filename, audio_bytes)
                                    processed += 1
                            elif selected_type == t('answer_only'):
                                if audio_lang == "English":
                                    audio_bytes = text_to_speech(english_answer, lang="en")
                                else:
                                    audio_bytes = text_to_speech(urdu_answer, lang="ur")
                                if audio_bytes:
                                    lang_suffix = "_en" if audio_lang == "English" else "_ur"
                                    filename = f"answer_{i+1:02d}{lang_suffix}.mp3"
                                    zipf.writestr(filename, audio_bytes)
                                    processed += 1
                            elif selected_type == t('question_then_answer'):
                                if audio_lang == "English":
                                    audio_bytes = generate_combined_audio(english_question, english_answer, lang="en")
                                else:
                                    audio_bytes = generate_combined_audio(urdu_question, urdu_answer, lang="ur")
                                if audio_bytes:
                                    lang_suffix = "_en" if audio_lang == "English" else "_ur"
                                    filename = f"flashcard_{i+1:02d}_qa{lang_suffix}.mp3"
                                    zipf.writestr(filename, audio_bytes)
                                    processed += 1
                        progress_bar.empty()
                        with open(zip_path, 'rb') as f:
                            zip_data = f.read()
                        b64_zip = base64.b64encode(zip_data).decode()
                        href = f'<a href="application/zip;base64,{b64_zip}" download="{zip_filename}" style="text-decoration:none;">'
                        st.markdown(f'{href}<button style="background-color:#2196F3; color:white; padding:10px 20px; border:none; border-radius:5px; font-size:16px; cursor:pointer;">⬇️ {t("downloading")} ({processed} files)</button></a>', unsafe_allow_html=True)
                        st.success(f"✅ {t('generated_files')}")
                        st.info(t('zip_info'))
            except Exception as e:
                st.error(f"Error generating download package: {e}")
                st.info("This might be due to timeout or memory limits on Streamlit Cloud.")

def show_settings():
    st.subheader(t('settings'))
    with st.container():
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"### {t('current_language')}: **{t('english') if st.session_state.language == 'English' else t('urdu')}**")
        with col2:
            st.markdown("### 🌐")
        with col3:
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button(f"🇺🇸 {t('english')}", type="primary" if st.session_state.language == 'English' else "secondary", use_container_width=True, key="settings_switch_to_english"):
                    st.session_state.language = 'English'
                    st.rerun()
            with btn_col2:
                if st.button(f"🇵🇰 {t('urdu')}", type="primary" if st.session_state.language == 'Urdu' else "secondary", use_container_width=True, key="settings_switch_to_urdu"):
                    st.session_state.language = 'Urdu'
                    st.rerun()
    st.markdown("---")
    if st.session_state.cards:
        st.success(f"✅ {t('loaded_cards')} {len(st.session_state.cards)}")
    else:
        st.error(t('no_cards_loaded'))
    with st.expander(t('document_info')):
        st.write(f"**{t('document_path')}:** {DOC_PATH}")
        st.write(f"**{t('file_exists')}:** {'✅ Yes' if os.path.exists(DOC_PATH) else '❌ No'}")
        if st.session_state.cards:
            st.write(f"**{t('sample_cards')}:**")
            for i, card in enumerate(st.session_state.cards[:3]):
                english_q, english_a = card['english']
                if 'urdu' in card:
                    urdu_q, urdu_a = card['urdu']
                else:
                    urdu_q, urdu_a = f"سوال: {english_q}", english_a
                st.write(f"{i+1}. **English Q:** {english_q[:50]}...")
                st.write(f"   **English A:** {english_a[:50]}...")
                st.write(f"   **Urdu Q:** {urdu_q[:50]}...")
                st.write(f"   **Urdu A:** {urdu_a[:50]}...")
            st.write("---")
    with st.expander("🌐 Language Statistics"):
        st.write(f"**{t('current_language')}:** {st.session_state.language}")
        st.write(f"**Show translation:** {'✅ Yes' if st.session_state.show_urdu else '❌ No'}")
        st.write(f"**Total bilingual cards:** {len(st.session_state.cards) if st.session_state.cards else 0}")
        if st.session_state.cards:
            urdu_cards = sum(1 for card in st.session_state.cards if card.get('urdu'))
            st.write(f"**Cards with Urdu translations:** {urdu_cards}")
    if st.button(t('reset_state')):
        for key in list(st.session_state.keys()):
            if key not in ['language', 'show_urdu']:
                del st.session_state[key]
        st.rerun()
    with st.expander(t('about_app')):
        st.write("""
**LLB Preparation Flashcards with Voiceover (Bilingual)**
This bilingual app helps you study for LLB exams in both English and Urdu:
- Interactive flashcards with voice support in both languages
- Quiz mode for self-testing
- Audio generation for auditory learning in English and Urdu
- Bulk download of study materials
- Easy language switching with top menu buttons
""")

def main():
    st.set_page_config(
        page_title="LLB Preparation Flashcards (Bilingual)",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    with st.sidebar:
        st.title(t('sidebar_title'))
        st.markdown("---")
        st.info(t('sidebar_info'))
        if st.session_state.cards:
            st.success(f"**{len(st.session_state.cards)} {t('cards_loaded')}**")
        else:
            st.warning("No cards loaded")
        st.markdown("---")
        st.markdown(f"**{t('current_language')}:**")
        if st.session_state.language == 'English':
            st.markdown("🇺🇸 **English**")
        else:
            st.markdown("🇵🇰 **اردو**")
        st.markdown("---")
        st.caption(t('made_with'))

    tab1, tab2, tab3, tab4 = st.tabs([f"🎴 {t('flashcards')}", f"📝 {t('quiz')}", f"📥 {t('download')}", f"⚙️ {t('settings_tab')}"])
    with tab1:
        show_flashcards()
    with tab2:
        show_quiz()
    with tab3:
        show_bulk_download()
    with tab4:
        show_settings()

if __name__ == "__main__":
    main()