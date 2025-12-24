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
        'app_title': "ایل ایل بی تیاری فلش کارڈز آواز کے ساتھ",
        'quiz_title': "ایل ایل بی تیاری کوئز",
        'bulk_download': "بلاک آڈیو ڈاؤن لوڈ",
        'settings': "اپلیکیشن ترتیبات",
        'flashcards': "فلش کارڈز",
        'quiz': "کوئز",
        'download': "بلاک ڈاؤن لوڈ",
        'settings_tab': "ترتیبات",
        'document_info': "دستاویز کی معلومات",
        'total_cards': "کل کارڈز",
        'sample_question': "نمونہ سوال",
        'currently_playing': "فی الحال آڈیو چل رہا ہے",
        'stop_all_audio': "تمام آڈیو روکیں",
        'no_audio': "فی الحال کوئی آڈیو نہیں چل رہا",
        'no_flashcards': "کوئی فلش کارڈ نہیں ملا۔ یقینی بنائیں کہ آپ کی دستاویز Q:/A: لائنز استعمال کرتی ہے۔",
        'expected_format': "متوقع فارمیٹ:",
        'format_example': "Q: قانون کی تعریف کیا ہے؟\nA: قانون اصولوں کا ایک نظام ہے...",
        'play_question': "🔊 سوال سنیں",
        'stop': "⏹️ روکیں",
        'question_audio': "⬇️ سوال آڈیو",
        'playing_loop': "🔁 سوال کی آڈیو لوپ پر چل رہی ہے...",
        'show_answer': "جواب دکھائیں",
        'next_card': "اگلا کارڈ",
        'play_answer': "🔊 جواب سنیں",
        'answer_audio': "⬇️ جواب آڈیو",
        'combined_qa': "⬇️ مشترکہ سوال اور جواب آڈیو",
        'card_settings': "کارڈ کی ترتیبات",
        'shuffle_deck': "کارڈ ملائیں",
        'quick_navigation': "فوری نیویگیشن",
        'first': "⏮️ پہلا",
        'previous': "⏪ پچھلا",
        'next': "⏩ اگلا",
        'test_knowledge': "اس انٹرایکٹو کوئز کے ساتھ اپنے علم کا امتحان لیں!",
        'cards_available': "کل دستیاب فلش کارڈز",
        'num_questions': "سوالات کی تعداد:",
        'start_quiz': "🚀 کوئز شروع کریں",
        'questions': "سوالات",
        'progress': "ترقی",
        'select_answer': "صحیح جواب منتخب کریں:",
        'correct_answer': "صحیح جواب:",
        'next_question': "➡️ اگلا سوال",
        'choose_answer': "اپنا جواب منتخب کریں:",
        'skip_question': "⏭️ سوال چھوڑیں",
        'quiz_completed': "🎉 کوئز مکمل ہوا!",
        'total_questions': "کل سوالات",
        'correct_answers': "صحیح جوابات",
        'score': "اسکور",
        'excellent': "🏆 شاندار! آپ مواد پر عبور حاصل کر رہے ہیں!",
        'good_job': "👍 اچھا کام! مضبوط سمجھ!",
        'keep_practicing': "📚 مشق جاری رکھیں! آپ قریب ہیں!",
        'review_material': "💪 مواد کا جائزہ لیں اور دوبارہ کوشش کریں!",
        'retry_quiz': "🔄 کوئز دوبارہ کوشش کریں",
        'new_quiz': "📝 نیا کوئز",
        'generate_download': "اپنے فلش کارڈز کے لیے آڈیو فائلیں تیار اور ڈاؤن لوڈ کریں",
        'bulk_note': "⚠️ نوٹ: بلاک ڈاؤن لوڈ آن ڈیمانڈ آڈیو تیار کرتا ہے اور بڑے سیٹ کے لیے وقت لے سکتا ہے۔",
        'select_type': "ڈاؤن لوڈ کی قسم منتخب کریں:",
        'question_only': "صرف سوال",
        'answer_only': "صرف جواب",
        'question_then_answer': "سوال پھر جواب",
        'generate_package': "🛠️ ڈاؤن لوڈ پیکیج تیار کریں",
        'downloading': "آڈیو فائلیں ڈاؤن لوڈ کریں",
        'generated_files': "آڈیو فائلیں تیار کی گئیں!",
        'zip_info': "زیپ فائل میں MP3 فارمیٹ میں آڈیو فائلیں ہیں۔",
        'loaded_cards': "فلش کارڈز لوڈ ہوئے",
        'no_cards_loaded': "کوئی کارڈ لوڈ نہیں ہوا",
        'document_path': "دستاویز کا راستہ",
        'file_exists': "فائل موجود ہے",
        'sample_cards': "نمونہ کارڈز",
        'reset_state': "🔄 ایپلیکیشن کی حالت ری سیٹ کریں",
        'about_app': "ℹ️ اس ایپ کے بارے میں",
        'sidebar_title': "📚 ایل ایل بی تیاری",
        'sidebar_info': "انٹرایکٹو فلش کارڈز اور آواز کی مدد کے ساتھ ایل ایل بی مواد کا مطالعہ کریں",
        'cards_loaded': "کارڈز لوڈ ہوئے",
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
        'combined_bilingual': "⬇️ مشترکہ دو لسانی آڈیو",
        'question_in_urdu': "سوال:",
        'answer_in_urdu': "جواب:",
        'translation_loading': "اردو میں ترجمہ ہو رہا ہے...",
        'translation_error': "ترجمہ دستیاب نہیں ہے",
        'enter_urdu': "اردو ترجمہ درج کریں",
        'manual_translation': "دستی ترجمہ",
        'save_translation': "💾 ترجمہ محفوظ کریں",
        'translation_saved': "✅ ترجمہ محفوظ ہو گیا!",
        'urdu_text_placeholder': "اردو ترجمہ یہاں ٹائپ کریں...",
        'switch_to_urdu': "اردو میں تبدیل کریں",
        'switch_to_english': "انگریزی میں تبدیل کریں",
        'current_language': "موجودہ زبان",
        'language_switch': "🌐 زبان تبدیل کریں",
        'quiz_not_available': "⚠️ کوئز دستیاب نہیں - کوئی فلش کارڈ لوڈ نہیں ہوئے",
        'load_cards_first': "براہ کرم پہلے فلش کارڈز ٹیب سے فلش کارڈز لوڈ کریں۔"
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
        current_question = None
        current_answer_english = None
        current_answer_urdu = None
        
        for para in document.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            
            # Check if this is a question
            if text.startswith("Q:"):
                # Save the previous card if it exists
                if current_question and current_answer_english:
                    cards.append({
                        'english': (current_question, current_answer_english),
                        'urdu': (f"سوال: {current_question}", current_answer_urdu if current_answer_urdu else current_answer_english)
                    })
                
                # Start a new card
                current_question = text[2:].strip()
                current_answer_english = None
                current_answer_urdu = None
            
            # Check if this is an English answer
            elif text.startswith("A (English):") and current_question:
                current_answer_english = text.replace("A (English):", "").strip()
            
            # Check if this is a Urdu answer
            elif text.startswith("A (Urdu):") and current_question:
                urdu_text = text.replace("A (Urdu):", "").strip()
                # Remove any directional tags if present
                urdu_text = urdu_text.replace("{dir=\"rtl\"}", "").strip()
                current_answer_urdu = urdu_text
        
        # Don't forget to add the last card
        if current_question and current_answer_english:
            cards.append({
                'english': (current_question, current_answer_english),
                'urdu': (f"سوال: {current_question}", current_answer_urdu if current_answer_urdu else current_answer_english)
            })
        
        return cards
        
    except Exception as e:
        st.error(f"Error reading document: {e}")
        return []

# Initialize session states
if 'language' not in st.session_state:
    st.session_state.language = 'English'
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

# ✅ NEW: Improved audio player function
def play_audio_in_browser(audio_bytes, audio_id):
    """Play audio directly in the browser with proper HTML5 audio element"""
    if audio_bytes:
        # Create a unique player ID
        player_id = f"audio_player_{audio_id}"
        
        # Create base64 encoded audio
        audio_base64 = base64.b64encode(audio_bytes).decode()
        
        # Create HTML audio element
        audio_html = f"""
        <audio id="{player_id}" autoplay style="display:none;">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        <script>
            var audio = document.getElementById('{player_id}');
            audio.play().catch(function(error) {{
                console.log('Audio play failed:', error);
            }});
        </script>
        """
        return audio_html
    return ""

# ✅ NEW: Function to create audio player
def create_audio_player(audio_bytes, label="Audio"):
    """Create an audio player that works in Streamlit"""
    if audio_bytes:
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
        <audio controls style="width: 100%; margin-top: 10px;">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """
        return audio_html
    return ""

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
    
    # Debug: Show loaded cards count
    with st.expander("🔧 Debug Info", expanded=False):
        st.write(f"Number of cards loaded: {len(st.session_state.cards) if st.session_state.cards else 0}")
        if st.session_state.cards:
            st.write("First card preview:")
            card = st.session_state.cards[0]
            st.write(f"English Q: {card['english'][0]}")
            st.write(f"English A: {card['english'][1]}")
            st.write(f"Urdu A: {card['urdu'][1]}")
    
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
    
    if not st.session_state.cards:
        st.warning(t('no_flashcards'))
        st.info(f"**{t('expected_format')}:**\n```\n{t('format_example')}\n```")
        return
    
    # Main flashcard display
    idx = st.session_state.order[st.session_state.index] if st.session_state.order else 0
    card = st.session_state.cards[idx]
    english_question, english_answer = card['english']
    urdu_question, urdu_answer = card['urdu']
    
    # ✅ Display question
    if st.session_state.language == 'Urdu':
        st.subheader(f"{urdu_question}")
        if st.session_state.show_urdu:
            st.markdown(f"*{t('original_text')}: {english_question}*")
    else:
        st.subheader(f"Q: {english_question}")
        if st.session_state.show_urdu:
            st.markdown(f"*{t('urdu_translation')}: {urdu_question}*")
    
    # ✅ Audio section for question
    st.markdown("### 🔊 Audio for Question")
    
    # Create columns for audio buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"🎵 {t('listen_english')}", key=f"play_q_en_{idx}", use_container_width=True):
            with st.spinner("Generating English audio..."):
                audio_bytes = text_to_speech(english_question, lang="en")
                if audio_bytes:
                    st.session_state[f"audio_q_en_{idx}"] = audio_bytes
                    st.success("✅ English audio ready!")
    
    with col2:
        if st.button(f"🎵 {t('listen_urdu')}", key=f"play_q_ur_{idx}", use_container_width=True):
            with st.spinner("Generating Urdu audio..."):
                audio_bytes = text_to_speech(urdu_question, lang="ur")
                if audio_bytes:
                    st.session_state[f"audio_q_ur_{idx}"] = audio_bytes
                    st.success("✅ Urdu audio ready!")
    
    # Display audio players if available
    if f"audio_q_en_{idx}" in st.session_state:
        st.markdown("**English Audio Player:**")
        st.markdown(create_audio_player(st.session_state[f"audio_q_en_{idx}"], "English Question"), unsafe_allow_html=True)
    
    if f"audio_q_ur_{idx}" in st.session_state:
        st.markdown("**Urdu Audio Player:**")
        st.markdown(create_audio_player(st.session_state[f"audio_q_ur_{idx}"], "Urdu Question"), unsafe_allow_html=True)
    
    # ✅ Download buttons for question
    st.markdown("---")
    st.markdown("### 📥 Download Question Audio")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"⬇️ {t('download_english')}", key=f"dl_q_en_{idx}", use_container_width=True):
            with st.spinner("Generating download..."):
                audio_bytes = text_to_speech(english_question, lang="en")
                if audio_bytes:
                    filename = f"question_{idx+1}_en.mp3"
                    b64 = base64.b64encode(audio_bytes).decode()
                    href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}" style="text-decoration:none;">'
                    st.markdown(f'{href}<button style="display:none;" id="download_q_en_{idx}">Download</button></a>', unsafe_allow_html=True)
                    st.markdown(f'<script>document.getElementById("download_q_en_{idx}").click();</script>', unsafe_allow_html=True)
                    st.success(f"✅ Download started: {filename}")
    
    with col2:
        if st.button(f"⬇️ {t('download_urdu')}", key=f"dl_q_ur_{idx}", use_container_width=True):
            with st.spinner("Generating download..."):
                audio_bytes = text_to_speech(urdu_question, lang="ur")
                if audio_bytes:
                    filename = f"question_{idx+1}_ur.mp3"
                    b64 = base64.b64encode(audio_bytes).decode()
                    href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}" style="text-decoration:none;">'
                    st.markdown(f'{href}<button style="display:none;" id="download_q_ur_{idx}">Download</button></a>', unsafe_allow_html=True)
                    st.markdown(f'<script>document.getElementById("download_q_ur_{idx}").click();</script>', unsafe_allow_html=True)
                    st.success(f"✅ Download started: {filename}")
    
    # ✅ Show answer button
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t('show_answer'), key=f"show_ans_{idx}", use_container_width=True):
            st.session_state.show_answer = True
            st.rerun()
    
    # Display answer if show_answer is True
    if st.session_state.show_answer:
        st.markdown("---")
        st.markdown("## 📝 Answer")
        
        if st.session_state.language == 'Urdu':
            st.markdown(f"""<div style='color:green; font-size:24px; padding:15px; border-left:5px solid #4CAF50; background-color:#f9f9f9; border-radius:5px; margin:10px 0;'><strong>{t('answer_in_urdu')}</strong><br>{urdu_answer}</div>""", unsafe_allow_html=True)
            if st.session_state.show_urdu:
                st.markdown(f"*{t('original_text')}: {english_answer}*")
        else:
            st.markdown(f"""<div style='color:green; font-size:24px; padding:15px; border-left:5px solid #4CAF50; background-color:#f9f9f9; border-radius:5px; margin:10px 0;'><strong>A:</strong><br>{english_answer}</div>""", unsafe_allow_html=True)
            if st.session_state.show_urdu:
                st.markdown(f"*{t('urdu_translation')}: {urdu_answer}*")
        
        # ✅ Audio section for answer
        st.markdown("### 🔊 Audio for Answer")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"🎵 {t('listen_english')} (Answer)", key=f"play_a_en_{idx}", use_container_width=True):
                with st.spinner("Generating English audio..."):
                    audio_bytes = text_to_speech(english_answer, lang="en")
                    if audio_bytes:
                        st.session_state[f"audio_a_en_{idx}"] = audio_bytes
                        st.success("✅ English audio ready!")
        
        with col2:
            if st.button(f"🎵 {t('listen_urdu')} (Answer)", key=f"play_a_ur_{idx}", use_container_width=True):
                with st.spinner("Generating Urdu audio..."):
                    audio_bytes = text_to_speech(urdu_answer, lang="ur")
                    if audio_bytes:
                        st.session_state[f"audio_a_ur_{idx}"] = audio_bytes
                        st.success("✅ Urdu audio ready!")
        
        # Display audio players for answer if available
        if f"audio_a_en_{idx}" in st.session_state:
            st.markdown("**English Answer Audio Player:**")
            st.markdown(create_audio_player(st.session_state[f"audio_a_en_{idx}"], "English Answer"), unsafe_allow_html=True)
        
        if f"audio_a_ur_{idx}" in st.session_state:
            st.markdown("**Urdu Answer Audio Player:**")
            st.markdown(create_audio_player(st.session_state[f"audio_a_ur_{idx}"], "Urdu Answer"), unsafe_allow_html=True)
        
        # ✅ Download buttons for answer
        st.markdown("---")
        st.markdown("### 📥 Download Answer Audio")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"⬇️ {t('download_english')} (Answer)", key=f"dl_a_en_{idx}", use_container_width=True):
                with st.spinner("Generating download..."):
                    audio_bytes = text_to_speech(english_answer, lang="en")
                    if audio_bytes:
                        filename = f"answer_{idx+1}_en.mp3"
                        b64 = base64.b64encode(audio_bytes).decode()
                        href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}" style="text-decoration:none;">'
                        st.markdown(f'{href}<button style="display:none;" id="download_a_en_{idx}">Download</button></a>', unsafe_allow_html=True)
                        st.markdown(f'<script>document.getElementById("download_a_en_{idx}").click();</script>', unsafe_allow_html=True)
                        st.success(f"✅ Download started: {filename}")
        
        with col2:
            if st.button(f"⬇️ {t('download_urdu')} (Answer)", key=f"dl_a_ur_{idx}", use_container_width=True):
                with st.spinner("Generating download..."):
                    audio_bytes = text_to_speech(urdu_answer, lang="ur")
                    if audio_bytes:
                        filename = f"answer_{idx+1}_ur.mp3"
                        b64 = base64.b64encode(audio_bytes).decode()
                        href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}" style="text-decoration:none;">'
                        st.markdown(f'{href}<button style="display:none;" id="download_a_ur_{idx}">Download</button></a>', unsafe_allow_html=True)
                        st.markdown(f'<script>document.getElementById("download_a_ur_{idx}").click();</script>', unsafe_allow_html=True)
                        st.success(f"✅ Download started: {filename}")
        
        # ✅ Combined audio buttons
        st.markdown("---")
        st.markdown("### 🎧 Combined Audio")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🎵 {t('combined_qa')} (English)", key=f"combined_en_{idx}", use_container_width=True):
                with st.spinner("Generating combined English audio..."):
                    combined_text = f"Question: {english_question}. Answer: {english_answer}"
                    audio_bytes = text_to_speech(combined_text, lang="en")
                    if audio_bytes:
                        st.session_state[f"combined_en_{idx}"] = audio_bytes
                        st.success("✅ Combined English audio ready!")
        
        with col2:
            if st.button(f"🎵 {t('combined_bilingual')}", key=f"bilingual_{idx}", use_container_width=True):
                with st.spinner("Generating bilingual audio..."):
                    english_content = f"Question: {english_question} Answer: {english_answer}"
                    urdu_content = f"سوال: {english_question} جواب: {urdu_answer}"
                    bilingual_audio = generate_bilingual_audio(english_content, urdu_content)
                    if bilingual_audio:
                        st.session_state[f"bilingual_{idx}"] = bilingual_audio
                        st.success("✅ Bilingual audio ready!")
        
        # Display combined audio players if available
        if f"combined_en_{idx}" in st.session_state:
            st.markdown("**Combined English Q&A Audio Player:**")
            st.markdown(create_audio_player(st.session_state[f"combined_en_{idx}"], "Combined English"), unsafe_allow_html=True)
        
        if f"bilingual_{idx}" in st.session_state:
            st.markdown("**Bilingual Audio Player:**")
            st.markdown(create_audio_player(st.session_state[f"bilingual_{idx}"], "Bilingual"), unsafe_allow_html=True)
    
    # Navigation buttons
    st.markdown("---")
    st.markdown("### 🔄 Navigation")
    
    # Next card button
    if col2.button(t('next_card'), key=f"next_{idx}", use_container_width=True):
        st.session_state.index = (st.session_state.index + 1) % len(st.session_state.order)
        st.session_state.show_answer = False
        st.session_state.audio_playing = None
        st.session_state.stop_requested = False
        st.rerun()
    
    # Card settings
    with st.expander(f"⚙️ {t('card_settings')}"):
        if st.button(t('shuffle_deck'), key=f"shuffle_{idx}"):
            random.shuffle(st.session_state.order)
            st.session_state.index = 0
            st.session_state.show_answer = False
            st.session_state.audio_playing = None
            st.session_state.stop_requested = False
            st.success("Deck shuffled!")
            st.rerun()
        
        st.write(f"**Card {st.session_state.index + 1} of {len(st.session_state.order)}**")
    
    # Quick navigation
    st.markdown("---")
    st.write(f"**{t('quick_navigation')}:**")
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    
    with nav_col1:
        if st.button(t('first'), key=f"first_{idx}"):
            st.session_state.index = 0
            st.session_state.show_answer = False
            st.session_state.audio_playing = None
            st.rerun()
    
    with nav_col2:
        if st.button(t('previous'), key=f"prev_{idx}"):
            st.session_state.index = (st.session_state.index - 1) % len(st.session_state.order)
            st.session_state.show_answer = False
            st.session_state.audio_playing = None
            st.rerun()
    
    with nav_col3:
        if st.button(t('next'), key=f"nav_next_{idx}"):
            st.session_state.index = (st.session_state.index + 1) % len(st.session_state.order)
            st.session_state.show_answer = False
            st.session_state.audio_playing = None
            st.rerun()

# [Rest of the functions remain the same - show_quiz(), show_bulk_download(), show_settings(), main()]
# Due to character limit, I'm showing the key changes. The rest of the functions are the same as before.

def show_quiz():
    st.title(t('quiz_title'))
    # ... (same as before)

def show_bulk_download():
    st.title(t('bulk_download'))
    # ... (same as before)

def show_settings():
    st.subheader(t('settings'))
    # ... (same as before)

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
    
    tab1, tab2, tab3, tab4 = st.tabs([
        f"🎴 {t('flashcards')}", 
        f"📝 {t('quiz')}", 
        f"📥 {t('download')}", 
        f"⚙️ {t('settings_tab')}"
    ])
    
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