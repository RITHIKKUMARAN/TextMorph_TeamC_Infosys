import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import PyPDF2
import docx
from fpdf import FPDF
import io
import os
from dotenv import load_dotenv
from datetime import datetime
import json
import markdown
from difflib import SequenceMatcher
from streamlit_mic_recorder import speech_to_text
import tempfile

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize session state
if 'users' not in st.session_state:
    st.session_state.users = {'admin': 'admin123'}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_profiles' not in st.session_state:
    st.session_state.user_profiles = {}
if 'history' not in st.session_state:
    st.session_state.history = {}
# Voice input session states
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = ""
if 'voice_input_confirmed' not in st.session_state:
    st.session_state.voice_input_confirmed = False
if 'confirmed_voice_text' not in st.session_state:
    st.session_state.confirmed_voice_text = ""

# User Authentication Functions
def login_user(username, password):
    if username in st.session_state.users and st.session_state.users[username] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        # Initialize user profile if doesn't exist
        if username not in st.session_state.user_profiles:
            st.session_state.user_profiles[username] = {
                'preferred_tone': 'Neutral',
                'preferred_style': 'General',
                'preferred_language': 'English',
                'preferred_depth': 'Detailed'
            }
        if username not in st.session_state.history:
            st.session_state.history[username] = []
        return True
    return False

def register_user(username, password):
    if username not in st.session_state.users:
        st.session_state.users[username] = password
        return True
    return False

def logout_user():
    st.session_state.logged_in = False
    st.session_state.username = None

# File Processing Functions
def extract_text_from_pdf(pdf_file):
    """
    Robust PDF text extraction:
    - Handles encrypted PDFs (tries empty password)
    - Avoids None concatenation (PyPDF2 can return None)
    - Returns "" if nothing extractable
    """
    try:
        reader = PyPDF2.PdfReader(pdf_file)

        # Try decrypt if encrypted
        if getattr(reader, "is_encrypted", False):
            try:
                # PyPDF2 3.x may still allow decrypt(""); if not, this will be caught
                reader.decrypt("")  # attempt empty password
            except Exception:
                return ""

        parts = []
        for page in reader.pages:
            try:
                t = page.extract_text() or ""
            except Exception:
                t = ""
            parts.append(t)

        return "\n".join(parts).strip()
    except Exception:
        return ""

def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

<<<<<<< HEAD
# Detect content type
def detect_content_type(text):
    text_lower = text.lower()
    keywords = {
        'scientific': ['abstract', 'methodology', 'hypothesis', 'research', 'study', 'analysis', 'conclusion'],
        'news': ['reported', 'according to', 'press', 'announced', 'stated', 'breaking'],
        'blog': ['i think', 'in my opinion', 'personally', 'today we', "let's"],
        'legal': ['hereby', 'pursuant to', 'whereas', 'therefore', 'shall', 'clause'],
        'technical': ['function', 'algorithm', 'system', 'implementation', 'configuration']
    }
    
    scores = {content: sum(1 for kw in words if kw in text_lower) for content, words in keywords.items()}
    detected = max(scores, key=scores.get) if max(scores.values()) > 2 else 'general'
    return detected
=======
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            success, msg = dummy_login(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = msg
                st.success(f"Welcome, {msg}!")
                st.rerun()
            else:
                st.error(msg)
    with tab2:
        reg_user = st.text_input("New Username", key="reg_user")
        reg_pass = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register"):
            success, msg = dummy_register(reg_user, reg_pass)
            if success:
                st.success(msg)
                st.info("You can now login.")
            else:
                st.error(msg)
    st.stop()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.image("https://via.placeholder.com/150x50.png?text=Linguify.AI", use_column_width=True)
    st.markdown(f"**User:** {st.session_state.username}")
    if st.button("Home", use_container_width=True): st.session_state.current_page = "Home"
    if st.button("Analytics", use_container_width=True): st.session_state.current_page = "Analytics"
    if st.button("History", use_container_width=True): st.session_state.current_page = "History"
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# ==================== CSS ====================
st.markdown("""
<style>
div.stButton > button {background-color: #4CAF50; color: white; border-radius: 10px; padding: 10px 20px;}
.stTextArea textarea {border-radius: 10px; border: 1px solid #ccc; padding: 10px;}
.stMetric {box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 10px; padding: 10px;}
.history-card {background-color: #f9f9f9; border-left: 5px solid #4CAF50; padding: 15px; margin: 10px 0; border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

# ==================== MODELS (SAFE) ====================
@st.cache_resource
def load_summarizer():
    return pipeline(
        "summarization",
        model="facebook/bart-large-cnn",
        truncation=True,
        max_length=512,
        min_length=30,
        do_sample=False
    )

@st.cache_resource
def load_paraphraser():
    return pipeline("text2text-generation", model="t5-small")

@st.cache_resource
def load_embedder():
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_resource
def load_keyword_extractor():
    return KeyBERT()

@st.cache_resource
def load_sentiment_analyzer():
    return nltk.sentiment.vader.SentimentIntensityAnalyzer()

@st.cache_resource
def load_translator():
    return Translator()

# Lazy & Safe Grammar Tool
def load_grammar_tool():
    if not GRAMMAR_AVAILABLE:
        return None
    try:
        tool = LanguageTool('en-US', remote_server=None)
        return tool
    except Exception as e:
        st.warning("Grammar tool unavailable. Skipping grammar check.")
        return None

# ==================== CORE FUNCTIONS ====================
def extract_text(uploaded_file):
    if not uploaded_file:
        return None
    try:
        if uploaded_file.type == "text/plain":
            return str(uploaded_file.read(), "utf-8")
        elif uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
            return text.strip()
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return docx2txt.process(uploaded_file)
    except Exception as e:
        st.error(f"Failed to read file: {e}")
    return None

def generate_summary(text, ratio):
    summarizer = load_summarizer()
    words = text.split()
    if len(words) > 900:
        text = " ".join(words[:900])
        st.caption("Input truncated to 900 words for model compatibility.")
    max_len = max(30, int(len(text.split()) * ratio))
    try:
        result = summarizer(text, max_length=max_len, min_length=30, do_sample=False)
        return result[0]['summary_text']
    except Exception as e:
        st.error(f"Summarization failed: {e}")
        return "Summary generation failed."

def generate_paraphrase(text, tone):
    paraphraser = load_paraphraser()
    prompt = f"paraphrase in {tone} tone: {text}"
    try:
        result = paraphraser(prompt, max_length=200, truncation=True)
        return result[0]['generated_text']
    except Exception as e:
        st.error(f"Paraphrasing failed: {e}")
        return "Paraphrase failed."

def translate_text(text, lang):
    if lang == "English":
        return text
    try:
        return load_translator().translate(text, dest=lang.lower()[:2]).text
    except:
        return text
    
def generate_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

def grammar_check(text):
    tool = load_grammar_tool()
    if not tool:
        return text
    try:
        return tool.correct(text)
    except:
        return text

def keyword_extract(text):
    try:
        kw_model = load_keyword_extractor()
        return [kw[0] for kw in kw_model.extract_keywords(text, top_n=5)]
    except:
        return []

def plagiarism_score(orig, para):
    try:
        e1, e2 = load_embedder().encode([orig, para])
        return round(util.cos_sim(e1, e2).item() * 100, 2)
    except:
        return 0.0

def sentiment_analysis(text):
    return load_sentiment_analyzer().polarity_scores(text)

# ==================== PAGES ====================
if st.session_state.current_page == "Home":
    st.title("Linguify.AI — Smart Text Tool")

    with st.sidebar:
        mode = st.selectbox("Mode", ["Summarization", "Paraphrasing", "All-in-One"])
        if "Summarization" in mode:
            ratio = st.slider("Summary Ratio (%)", 10, 90, 30) / 100
        output_lang = st.selectbox("Output Language", ["English", "French", "Spanish"])
        tone_style = st.selectbox("Tone", ["Neutral", "Formal", "Casual"])

    input_text = st.text_area("Input Text", height=200)
    uploaded_file = st.file_uploader("Upload File", type=["txt", "pdf", "docx"])
    
    if uploaded_file:
        extracted = extract_text(uploaded_file)
        if extracted:
            input_text = extracted
            st.success(f"✅ {uploaded_file.name} uploaded successfully!")
            st.caption(f"File type: {uploaded_file.type}, Size: {uploaded_file.size/1024:.1f} KB")

        else:
            st.error("Could not extract text from file.")
>>>>>>> c3269da (Added PDF download feature)

# Gemini API Functions with Context-Aware Processing
def process_text_with_gemini(text, operation, language="English", tone="Neutral", adaptation="General", 
                             summary_type=None, depth_level="Detailed", readability_level="General public",
                             content_type="auto"):
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Auto-detect content type
    if content_type == "auto":
        content_type = detect_content_type(text)
    
    # Depth level instructions
    depth_instructions = {
        "Brief": "Provide a very concise summary in 1-2 sentences capturing only the core message.",
        "Detailed": "Provide a detailed summary in a full paragraph covering main points and key details.",
        "Comprehensive": "Provide a comprehensive multi-section summary with headings, covering all major aspects thoroughly."
    }
    
    # Readability level instructions
    readability_map = {
        "Kids (Age 8-12)": "Use very simple words, short sentences, and concrete examples. Avoid complex terms.",
        "Teens (Age 13-17)": "Use clear language with some complexity. Explain specialized terms when used.",
        "General public": "Use accessible language appropriate for general readers with varied backgrounds.",
        "Experts": "Use technical terminology and assume domain knowledge. Be precise and detailed."
    }
    
    if operation == "summarize":
        if summary_type == "Abstractive":
            prompt = f"""Create an abstractive summary of the following {content_type} text in {language}.
Tone: {tone}
Style: {adaptation}
Depth: {depth_instructions[depth_level]}
Readability: {readability_map[readability_level]}

Content Type Adaptation: This is a {content_type} text. Structure your summary accordingly:
- Scientific: Focus on hypothesis, methods, findings, implications
- News: Lead with key facts, who/what/when/where/why
- Blog: Maintain conversational tone while summarizing main points
- Legal: Preserve key terms and logical structure
- Technical: Emphasize process, requirements, and specifications

Instructions:
- Generate a new summary using your own words
- Capture the main ideas and key concepts
- Create coherent, fluent sentences
- Do not copy exact sentences from the original text

Text: {text}

Abstractive Summary:"""
        else:  # Extractive
            prompt = f"""Create an extractive summary of the following {content_type} text in {language}.
Tone: {tone}
Style: {adaptation}
Depth: {depth_instructions[depth_level]}
Readability: {readability_map[readability_level]}

Content Type: {content_type}

Instructions:
- Select the most important sentences from the original text
- Maintain the original wording of selected sentences
- Arrange sentences in a logical order based on {content_type} structure
- Focus on key facts and main points

Text: {text}

Extractive Summary:"""
    elif operation == "paraphrase":
        prompt = f"""Paraphrase the following text in {language}.
Tone: {tone}
Style: {adaptation}
Readability Level: {readability_map[readability_level]}

Instructions:
- Rewrite the text using different words and sentence structures
- Maintain the original meaning and intent
- Adjust complexity level for: {readability_level}
- Improve clarity and readability
- Make it sound natural and fluent

Text: {text}

Paraphrased text:"""
    elif operation == "translate_summarize":
        prompt = f"""Simultaneously summarize AND translate the following text to {language}.
Tone: {tone}
Depth: {depth_instructions[depth_level]}

Instructions:
1. First understand the content in its original language
2. Create a summary of the main points
3. Express that summary in {language}
4. Ensure natural flow in the target language

Text: {text}

Translated Summary:"""
    else:
        prompt = text
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Semantic Comparison Function
def compare_texts_semantic(text1, text2):
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = f"""Compare these two texts for semantic similarity, rephrasing accuracy, and potential plagiarism risk.

Text 1 (Original):
{text1}

Text 2 (Comparison):
{text2}

Provide analysis in this format:
1. Semantic Similarity Score: [0-100%]
2. Rephrasing Quality: [Excellent/Good/Fair/Poor]
3. Plagiarism Risk: [High/Medium/Low]
4. Key Differences: [List main differences]
5. Recommendations: [Suggestions for improvement]
"""
    
    try:
        response = model.generate_content(prompt)
        
        # Also calculate basic text similarity
        similarity_ratio = SequenceMatcher(None, text1.lower(), text2.lower()).ratio() * 100
        
        return {
            'ai_analysis': response.text,
            'basic_similarity': f"{similarity_ratio:.1f}%"
        }
    except Exception as e:
        return {'error': str(e)}

# Text-to-Speech Function
def text_to_speech(text, language='en'):
    try:
        lang_map = {
            'English': 'en', 'Spanish': 'es', 'French': 'fr', 'German': 'de',
            'Hindi': 'hi', 'Chinese': 'zh-CN', 'Japanese': 'ja', 'Korean': 'ko'
        }
        
        lang_code = lang_map.get(language, 'en')
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return None

# Export Functions
def generate_pdf(text, title="Document"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, text)
    pdf_output = pdf.output(dest='S').encode('latin-1')
    return pdf_output

def generate_word_doc(text, title="Document"):
    doc = docx.Document()
    doc.add_heading(title, 0)
    doc.add_paragraph(text)
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

def generate_markdown(text, title="Document"):
    md_content = f"# {title}\n\n{text}"
    return md_content.encode('utf-8')

def generate_html(text, title="Document"):
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #1E88E5; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div>{markdown.markdown(text)}</div>
</body>
</html>"""
    return html_content.encode('utf-8')

def generate_json(text, title="Document", metadata=None):
    json_data = {
        "title": title,
        "content": text,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    return json.dumps(json_data, indent=2).encode('utf-8')

# Add to history
def add_to_history(username, operation, params, output):
    if username not in st.session_state.history:
        st.session_state.history[username] = []
    
    entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'operation': operation,
        'parameters': params,
        'output_preview': output[:200] + '...' if len(output) > 200 else output,
        'full_output': output
    }
    
    st.session_state.history[username].insert(0, entry)
    
    # Keep only last 50 entries
    if len(st.session_state.history[username]) > 50:
        st.session_state.history[username] = st.session_state.history[username][:50]

# Purpose-based tone presets
PURPOSE_PRESETS = {
    "Email - Professional": {"tone": "Professional", "style": "General", "readability": "General public"},
    "Email - Friendly": {"tone": "Friendly", "style": "General", "readability": "General public"},
    "Executive Summary": {"tone": "Formal", "style": "Academic", "readability": "Experts"},
    "Social Media Caption": {"tone": "Casual", "style": "Blog Post", "readability": "Teens (Age 13-17)"},
    "Legal Brief": {"tone": "Formal", "style": "Technical", "readability": "Experts"},
    "Technical Documentation": {"tone": "Neutral", "style": "Technical", "readability": "Experts"},
    "Blog Post": {"tone": "Friendly", "style": "Blog Post", "readability": "General public"},
    "Academic Paper": {"tone": "Formal", "style": "Academic", "readability": "Experts"},
    "News Article": {"tone": "Informative", "style": "News Article", "readability": "General public"},
    "Kids Story": {"tone": "Friendly", "style": "Creative", "readability": "Kids (Age 8-12)"},
}

# Main App
def main():
    st.set_page_config(page_title="AI Text Processor-TextMorph", page_icon="📝", layout="wide")
    st.markdown("""
        <style>
        /* --- General App & Body --- */
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
        }
        
        /* --- MAIN BACKGROUND GRADIENT --- */
        [data-testid="stAppViewContainer"] > .main {
            /* Light, airy, colorful gradient */
            background-image: linear-gradient(135deg, #F3E8FF 0%, #E0F2FE 100%);
        }
        
        /* --- VIBRANT Main Header --- */
        h1.main-header {
            font-size: 3.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 2rem;
            /* Vibrant Gradient text effect */
            background: linear-gradient(90deg, #4F46E5 0%, #D946EF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            color: transparent;
        }
        
        /* --- Sidebar (Dark Gradient) --- */
        [data-testid="stSidebar"] {
            background-image: linear-gradient(180deg, #1F2937 0%, #111827 100%);
            border-right: 1px solid #1F2937;
        }
        [data-testid="stSidebar"] * {
            color: #D1D5DB; /* Light gray text */
        }
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 {
            color: #FFFFFF; /* White headers */
            /* Gradient underline */
            border-bottom: 2px solid;
            border-image-slice: 1;
            border-image-source: linear-gradient(90deg, #4F46E5, #D946EF);
            padding-bottom: 8px;
            margin-bottom: 16px;
        }
        [data-testid="stSidebar"] label {
            font-weight: 600;
            color: #E5E7EB; /* Lighter label text */
        }
        [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background-color: #1F2937;
            border: 1px solid #374151;
            border-radius: 6px;
            color: #F9FAFB;
        }
        [data-testid="stSidebar"] .stButton>button {
            background-color: #374151;
            color: #D1D5DB;
            border: 1px solid #4B5563;
        }
        
        /* --- JUICY GRADIENT BUTTONS --- */
        
        /* Default buttons (Login, Logout, Profile, etc.) */
        .stButton>button:not([kind="primary"]):not([kind="secondary"]) {
            background-image: linear-gradient(45deg, #3B82F6 0%, #6366F1 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            box-shadow: 0 4px 14px 0 rgba(59, 130, 246, 0.39);
            transition: all 0.3s ease;
        }
        .stButton>button:not([kind="primary"]):not([kind="secondary"]):hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px 0 rgba(59, 130, 246, 0.5);
        }
        
        /* Primary buttons (Process Text, Use This Text, etc.) */
        [data-testid="stButton"] button[kind="primary"] {
            background-image: linear-gradient(45deg, #34D399 0%, #22C55E 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            box-shadow: 0 4px 14px 0 rgba(34, 197, 94, 0.4);
            transition: all 0.3s ease;
        }
        [data-testid="stButton"] button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px 0 rgba(34, 197, 94, 0.55);
        }
        
        /* Secondary buttons (Clear History) */
        [data-testid="stButton"] button[kind="secondary"] {
            background: #FFFFFF;
            color: #4B5563;
            border: 1px solid #CBD5E0;
            box-shadow: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        [data-testid="stButton"] button[kind="secondary"]:hover {
            background-color: #F9FAFB;
            border-color: #9CA3AF;
        }

        /* --- GRADIENT TABS --- */
        [data-testid="stTabs"] [data-baseweb="tab-list"] {
            border-bottom-color: #CBD5E0;
        }
        [data-testid="stTabs"] [data-baseweb="tab"] {
            font-weight: 600;
            font-size: 1.05rem;
            color: #718096;
            padding: 12px 16px;
        }
        [data-testid="stTabs"] [aria-selected="true"] {
            color: #4F46E5;
            padding-bottom: 12px;
            /* Gradient underline for active tab */
            border-image: linear-gradient(90deg, #4F46E5, #D946EF) 1;
            border-bottom-width: 4px;
            border-top: 0;
            border-left: 0;
            border-right: 0;
        }

        /* --- MODERN "GRADIENT BORDER" CARDS --- */
        .output-section, [data-testid="stExpander"], [data-testid="stMetric"] {
            /* This is the gradient border magic */
            background: linear-gradient(white, white) padding-box,
                        linear-gradient(135deg, #4F46E5, #D946EF) border-box;
            border: 2px solid transparent;
            /* --- */
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.07), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            border-radius: 12px;
            padding: 24px;
            margin-top: 20px;
        }
        
        /* --- GRADIENT BACKGROUND CARDS --- */
        .profile-box {
            background-image: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
            border-left: 5px solid #1E88E5;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.07), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            border-radius: 12px;
            padding: 24px;
            margin-top: 20px;
        }
        .voice-input-box {
            background-image: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
            border: 2px solid #F59E0B;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.07), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            border-radius: 12px;
            padding: 24px;
            margin-top: 20px;
        }
        .transcription-box {
            background-image: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
            border-left: 5px solid #22C55E;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.07), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            border-radius: 12px;
            padding: 24px;
            margin-top: 10px;
        }
        
        /* --- Expanders (History & Profile) --- */
        [data-testid="stExpander"] > details > summary {
            font-weight: 600;
            font-size: 1.1rem;
            color: #2D3748;
        }
        
        /* --- GRADIENT Metrics (History Tab) --- */
        [data-testid="stMetric"] > div:first-child { /* Label */
            color: #718096;
            font-weight: 500;
        }
        [data-testid="stMetric"] > div:nth-child(2) { /* Value */
            font-size: 2.25rem;
            font-weight: 700;
            /* Gradient text */
            background: linear-gradient(90deg, #1E88E5, #673AB7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            color: transparent;
        }

        /* --- Inputs (Text Area, Text Input) --- */
        [data-testid="stTextArea"] textarea,
        [data-testid="stTextInput"] input {
            background-color: #FFFFFF;
            border: 1px solid #D1D5DB;
            border-radius: 8px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            transition: all 0.2s ease;
        }
        [data-testid="stTextArea"] textarea:focus,
        [data-testid="stTextInput"] input:focus {
            border-color: #4F46E5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
            outline: none;
        }
        
        /* --- GRADIENT Alerts --- */
        [data-testid="stAlert"] {
            border-radius: 8px;
            border: none;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
        [data-testid="stAlert"][data-baseweb="alert-info"] {
            background-image: linear-gradient(135deg, #EFF6FF 0%, #EBF3FF 100%);
            color: #2563EB;
            border-left: 5px solid #2563EB;
        }
        [data-testid="stAlert"][data-baseweb="alert-success"] {
            background-image: linear-gradient(135deg, #F0FDF4 0%, #EBFBF1 100%);
            color: #22C55E;
            border-left: 5px solid #22C55E;
        }
        [data-testid="stAlert"][data-baseweb="alert-warning"] {
            background-image: linear-gradient(135deg, #FFFBEB 0%, #FEF9E3 100%);
            color: #F59E0B;
            border-left: 5px solid #F59E0B;
        }
        [data-testid="stAlert"][data-baseweb="alert-error"] {
            background-image: linear-gradient(135deg, #FEF2F2 0%, #FEECEC 100%);
            color: #EF4444;
            border-left: 5px solid #EF4444;
        }
        
        </style>
    """, unsafe_allow_html=True)
    
    
    # Login/Register Page
    if not st.session_state.logged_in:
        st.markdown("<h1 class='main-header'>AI Text Processor-TextMorph</h1>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
<<<<<<< HEAD
            st.subheader("Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login"):
                if login_user(username, password):
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        with tab2:
            st.subheader("Register")
            new_username = st.text_input("Username", key="register_username")
            new_password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.button("Register"):
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif register_user(new_username, new_password):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username already exists")
        
        return
    
    # Main Application (After Login)
    col1, col2, col3 = st.columns([5, 2, 1])
    with col1:
        st.markdown("<h1 class='main-header'>AI Text Processor-TextMorph</h1>", unsafe_allow_html=True)
    with col2:
        if st.button("👤 My Profile"):
            st.session_state.show_profile = not st.session_state.get('show_profile', False)
    with col3:
        if st.button("Logout"):
            logout_user()
            st.rerun()
    
    st.write(f"Welcome, **{st.session_state.username}**!")
    
    # Profile Management
    if st.session_state.get('show_profile', False):
        with st.expander("👤 AI Style Profile", expanded=True):
            st.markdown("<div class='profile-box'>", unsafe_allow_html=True)
            st.subheader("Your AI Preferences")
            
            profile = st.session_state.user_profiles[st.session_state.username]
            
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                profile['preferred_tone'] = st.selectbox(
                    "Default Tone",
                    ["Neutral", "Formal", "Casual", "Professional", "Friendly", "Persuasive", "Informative"],
                    index=["Neutral", "Formal", "Casual", "Professional", "Friendly", "Persuasive", "Informative"].index(profile['preferred_tone'])
                )
                profile['preferred_language'] = st.selectbox(
                    "Default Language",
                    ["English", "Spanish", "French", "German", "Hindi", "Chinese", "Japanese", "Korean"],
                    index=["English", "Spanish", "French", "German", "Hindi", "Chinese", "Japanese", "Korean"].index(profile['preferred_language'])
                )
            
            with col_p2:
                profile['preferred_style'] = st.selectbox(
                    "Default Style",
                    ["General", "Academic", "News Article", "Blog Post", "Technical", "Creative"],
                    index=["General", "Academic", "News Article", "Blog Post", "Technical", "Creative"].index(profile['preferred_style'])
                )
                profile['preferred_depth'] = st.selectbox(
                    "Default Depth",
                    ["Brief", "Detailed", "Comprehensive"],
                    index=["Brief", "Detailed", "Comprehensive"].index(profile['preferred_depth'])
                )
            
            if st.button("💾 Save Profile"):
                st.success("Profile saved successfully!")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Main tabs
    tab_process, tab_compare, tab_history = st.tabs(["📝 Process Text", "🔍 Compare Texts", "📜 History"])
    
    with tab_process:
        # Sidebar Configuration
        st.sidebar.header("⚙️ Configuration")
        
        # Quick Preset Selection
        st.sidebar.subheader("🎯 Quick Presets")
        preset_choice = st.sidebar.selectbox(
            "Choose a preset (or customize below)",
            ["Custom"] + list(PURPOSE_PRESETS.keys())
        )
        
        # Load profile defaults
        profile = st.session_state.user_profiles[st.session_state.username]
        
        # Apply preset or use profile defaults
        if preset_choice != "Custom":
            preset = PURPOSE_PRESETS[preset_choice]
            default_tone = preset['tone']
            default_style = preset['style']
            default_readability = preset['readability']
        else:
            default_tone = profile['preferred_tone']
            default_style = profile['preferred_style']
            default_readability = "General public"
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ Custom Settings")
        
        operation = st.sidebar.selectbox(
            "Operation",
            ["Summarize", "Paraphrase", "Summarize & Translate"]
        )
        
        # Summary settings
        summary_type = None
        depth_level = profile['preferred_depth']
        
        if operation == "Summarize" or operation == "Summarize & Translate":
            col_summary, col_info = st.sidebar.columns([3, 1])
            with col_summary:
                summary_type = st.selectbox(
                    "Summary Type",
                    ["Abstractive", "Extractive"]
                )
            with col_info:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("ℹ️", key="summary_info"):
                    st.session_state.show_summary_info = not st.session_state.get('show_summary_info', False)
            
            if st.session_state.get('show_summary_info', False):
                st.sidebar.info(
                    """
                    **Abstractive Summary:**
                    AI generates new sentences in its own words.
                    
                    **Extractive Summary:**
                    AI selects key sentences from original text.
                    """
                )
            
            # Depth level
            col_depth, col_depth_info = st.sidebar.columns([3, 1])
            with col_depth:
                depth_level = st.selectbox(
                    "Summary Depth",
                    ["Brief", "Detailed", "Comprehensive"],
                    index=["Brief", "Detailed", "Comprehensive"].index(depth_level)
                )
            with col_depth_info:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("ℹ️", key="depth_info"):
                    st.session_state.show_depth_info = not st.session_state.get('show_depth_info', False)
            
            if st.session_state.get('show_depth_info', False):
                st.sidebar.info(
                    """
                    **Brief:** 1-2 sentences
                    **Detailed:** Full paragraph
                    **Comprehensive:** Multi-section
                    """
                )
        
        language = st.sidebar.selectbox(
            "Output Language",
            ["English", "Spanish", "French", "German", "Hindi", "Chinese", "Japanese", "Korean"],
            index=["English", "Spanish", "French", "German", "Hindi", "Chinese", "Japanese", "Korean"].index(profile['preferred_language'])
        )
        
        tone = st.sidebar.selectbox(
            "Tone",
            ["Neutral", "Formal", "Casual", "Professional", "Friendly", "Persuasive", "Informative"],
            index=["Neutral", "Formal", "Casual", "Professional", "Friendly", "Persuasive", "Informative"].index(default_tone)
        )
        
        adaptation = st.sidebar.selectbox(
            "Style",
            ["General", "Academic", "News Article", "Blog Post", "Technical", "Creative"],
            index=["General", "Academic", "News Article", "Blog Post", "Technical", "Creative"].index(default_style)
        )
        
        # Readability Level
        col_read, col_read_info = st.sidebar.columns([3, 1])
        with col_read:
            readability = st.selectbox(
                "Readability Level",
                ["Kids (Age 8-12)", "Teens (Age 13-17)", "General public", "Experts"],
                index=["Kids (Age 8-12)", "Teens (Age 13-17)", "General public", "Experts"].index(default_readability)
            )
        with col_read_info:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("ℹ️", key="readability_info"):
                st.session_state.show_readability_info = not st.session_state.get('show_readability_info', False)
        
        if st.session_state.get('show_readability_info', False):
            st.sidebar.info(
                """
                **Kids:** Simple words, short sentences
                **Teens:** Clear with some complexity
                **General:** Accessible for all
                **Experts:** Technical terminology
                """
            )
        
        # Main Content Area
        st.header("📄 Input")
        
        input_method = st.radio(
            "Choose input method:",
            ["Type/Paste Text", "Upload File", "🎤 Voice Input"]
        )
        
        input_text = ""

        # If we already extracted from a file earlier, prefer that as default
        if not input_text and "extracted_input" in st.session_state:
            input_text = st.session_state["extracted_input"]
        
        # If voice input was confirmed, use that text
        if not input_text and st.session_state.get('voice_input_confirmed', False) and st.session_state.get('confirmed_voice_text', ''):
            input_text = st.session_state.confirmed_voice_text

        
        if input_method == "Type/Paste Text":
            input_text = st.text_area("Enter your text here:", height=200, value=input_text)
        
        elif input_method == "Upload File":
            uploaded_file = st.file_uploader("Upload a file", type=['pdf', 'docx', 'txt'])
            
            if uploaded_file:
                file_type = uploaded_file.name.split('.')[-1].lower()
                
                try:
                    if file_type == 'pdf':
                        input_text = extract_text_from_pdf(uploaded_file)

                        if input_text:
                            st.success(f"✅ PDF uploaded! Extracted ~{len(input_text.split())} words.")
                            st.session_state["extracted_input"] = input_text

                            with st.expander("📄 View Extracted Text"):
                                st.text_area("Extracted Text:", input_text, height=200, key="extracted")
                        else:
                            st.warning("No extractable text found. The PDF may be scanned/protected or has non-text pages.")

                    elif file_type == 'docx':
                        input_text = extract_text_from_docx(uploaded_file)
                        st.success(f"✅ File uploaded! Extracted {len(input_text)} characters.")
                        st.session_state["extracted_input"] = input_text
                        with st.expander("📄 View Extracted Text"):
                            st.text_area("Extracted Text:", input_text, height=200, key="extracted_docx")

                    elif file_type == 'txt':
                        input_text = uploaded_file.read().decode('utf-8')
                        st.success(f"✅ File uploaded! Extracted {len(input_text)} characters.")
                        st.session_state["extracted_input"] = input_text
                        with st.expander("📄 View Extracted Text"):
                            st.text_area("Extracted Text:", input_text, height=200, key="extracted_txt")
                    
                    # Auto-detect content type
                    if input_text:
                        detected_type = detect_content_type(input_text)
                        st.info(f"🔍 Detected content type: **{detected_type.title()}**")

                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        
        elif input_method == "🎤 Voice Input":
            st.markdown("<div class='voice-input-box'>", unsafe_allow_html=True)
            st.subheader("🎙️ Voice Recording & Transcription")
            st.markdown("**Instructions:** Click the button to start recording, speak clearly into your microphone, and click again to stop. The audio will be automatically transcribed.")
            
            # Direct Speech-to-Text
            text_from_speech = speech_to_text(
                language='en',
                start_prompt="🎙️ Start Speaking",
                stop_prompt="⏹️ Stop & Transcribe",
                use_container_width=True,
                just_once=False,
                key='speech_to_text'
            )
            
            if text_from_speech:
                st.session_state.transcribed_text = text_from_speech
                st.session_state.voice_input_confirmed = False
                st.success(f"✅ Transcribed successfully!")
            
            # Show transcription result
            if st.session_state.transcribed_text:
                st.markdown("<div class='transcription-box'>", unsafe_allow_html=True)
                st.markdown("**📝 Transcribed Text:**")
                
                # Editable text area for transcription
                edited_text = st.text_area(
                    "Edit if needed:",
                    value=st.session_state.transcribed_text,
                    height=150,
                    key="transcription_edit"
                )
                
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
                
                with col_btn1:
                    if st.button("✅ Use This Text", type="primary", use_container_width=True):
                        st.session_state.confirmed_voice_text = edited_text
                        st.session_state.voice_input_confirmed = True
                        st.success("✅ Text ready for processing!")
                
                with col_btn2:
                    if st.button("🔄 Clear & Record Again", use_container_width=True):
                        st.session_state.transcribed_text = ""
                        st.session_state.voice_input_confirmed = False
                        st.session_state.confirmed_voice_text = ""
                        st.rerun()
                
                with col_btn3:
                    st.caption(f"📊 {len(edited_text.split())} words | {len(edited_text)} characters")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # If confirmed, use the text
                if input_method == "🎤 Voice Input" and st.session_state.voice_input_confirmed:
                    input_text = st.session_state.confirmed_voice_text
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Process Button
        if st.button("🚀 Process Text", type="primary"):
            if not input_text:
                st.warning("⚠️ Please provide some input text!")
            else:
                with st.spinner(f"Processing with AI..."):
                    operation_type = "summarize" if operation in ["Summarize", "Summarize & Translate"] else "paraphrase"
                    if operation == "Summarize & Translate":
                        operation_type = "translate_summarize"
                    
                    output_text = process_text_with_gemini(
                        input_text, 
                        operation_type, 
                        language, 
                        tone, 
                        adaptation,
                        summary_type=summary_type,
                        depth_level=depth_level,
                        readability_level=readability,
                        content_type="auto"
                    )
                    
                    st.session_state.output_text = output_text
                    st.session_state.output_language = language
                    st.session_state.operation = operation
                    st.session_state.summary_type = summary_type
                    
                    # Add to history
                    params = {
                        'operation': operation,
                        'language': language,
                        'tone': tone,
                        'style': adaptation,
                        'summary_type': summary_type,
                        'depth': depth_level,
                        'readability': readability,
                        'input_method': input_method
                    }
                    add_to_history(st.session_state.username, operation, params, output_text)
        
        # Output Section
        if 'output_text' in st.session_state:
            st.markdown("---")
            st.header("✨ Output")
            
            st.markdown("<div class='output-section'>", unsafe_allow_html=True)
            if st.session_state.operation == "Summarize" and st.session_state.summary_type:
                st.markdown(f"**{st.session_state.summary_type} Summary:**")
            else:
                st.markdown(f"**{st.session_state.operation}d Text:**")
            st.write(st.session_state.output_text)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Action Buttons
            st.subheader("📥 Export Options")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            title = f"{st.session_state.operation}_{timestamp}"
            
            with col1:
                st.markdown("**PDF**")
                pdf_bytes = generate_pdf(st.session_state.output_text, title)
                st.download_button("📄 PDF", pdf_bytes, f"{title}.pdf", "application/pdf", use_container_width=True)
            
            with col2:
                st.markdown("**Word**")
                word_bytes = generate_word_doc(st.session_state.output_text, title)
                st.download_button("📘 DOCX", word_bytes, f"{title}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            
            with col3:
                st.markdown("**Markdown**")
                md_bytes = generate_markdown(st.session_state.output_text, title)
                st.download_button("📝 MD", md_bytes, f"{title}.md", "text/markdown", use_container_width=True)
            
            with col4:
                st.markdown("**HTML**")
                html_bytes = generate_html(st.session_state.output_text, title)
                st.download_button("🌐 HTML", html_bytes, f"{title}.html", "text/html", use_container_width=True)
            
            with col5:
                st.markdown("**JSON**")
                metadata = {
                    'operation': st.session_state.operation,
                    'language': st.session_state.output_language,
                    'summary_type': st.session_state.summary_type
                }
                json_bytes = generate_json(st.session_state.output_text, title, metadata)
                st.download_button("🔧 JSON", json_bytes, f"{title}.json", "application/json", use_container_width=True)
            
            # Audio Section
            st.subheader("🔊 Audio Output")
            col_audio1, col_audio2 = st.columns([1, 1])
            
            with col_audio1:
                if st.button("🎵 Generate Audio File", use_container_width=True):
                    with st.spinner("🎧 Generating audio..."):
                        audio_fp = text_to_speech(st.session_state.output_text, st.session_state.output_language)
                        if audio_fp:
                            st.session_state.audio_data = audio_fp.read()
                            st.success("✅ Audio generated!")
            
            if 'audio_data' in st.session_state:
                with col_audio2:
                    st.audio(st.session_state.audio_data, format='audio/mp3')
                    st.download_button("⬇️ Download MP3", st.session_state.audio_data, f"{title}.mp3", "audio/mp3", use_container_width=True)
            
            # Statistics
            st.markdown("---")
            st.subheader("📊 Statistics")
            
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            
            with stat_col1:
                st.metric("Words", len(st.session_state.output_text.split()))
            with stat_col2:
                st.metric("Characters", len(st.session_state.output_text))
            with stat_col3:
                st.metric("Language", st.session_state.output_language)
            with stat_col4:
                if st.session_state.operation == "Summarize" and st.session_state.summary_type:
                    st.metric("Type", st.session_state.summary_type)
                else:
                    st.metric("Operation", st.session_state.operation)
    
    # Compare Texts Tab
    with tab_compare:
        st.header("🔍 Semantic Comparison Mode")
        st.markdown("Compare two texts to detect semantic similarity, rephrasing accuracy, and plagiarism risk.")
        
        col_compare1, col_compare2 = st.columns(2)
        
        with col_compare1:
            st.subheader("📄 Original Text")
            text1 = st.text_area("Enter original text:", height=200, key="compare_text1")
        
        with col_compare2:
            st.subheader("📝 Comparison Text")
            text2 = st.text_area("Enter text to compare:", height=200, key="compare_text2")
        
        if st.button("🔍 Compare Texts", type="primary"):
            if not text1 or not text2:
                st.warning("⚠️ Please provide both texts to compare!")
            else:
                with st.spinner("Analyzing texts..."):
                    comparison_result = compare_texts_semantic(text1, text2)
                    
                    if 'error' not in comparison_result:
                        st.markdown("---")
                        st.subheader("📊 Comparison Results")
                        
                        # Show basic similarity
                        st.metric("Basic Text Similarity", comparison_result['basic_similarity'])
                        
                        # Show AI analysis
                        st.markdown("### 🤖 AI Analysis")
                        st.markdown(comparison_result['ai_analysis'])
                        
                        # Visual comparison
                        st.markdown("---")
                        st.subheader("📝 Side-by-Side Comparison")
                        col_side1, col_side2 = st.columns(2)
                        
                        with col_side1:
                            st.markdown("**Original Text**")
                            st.info(text1)
                            st.caption(f"Words: {len(text1.split())} | Characters: {len(text1)}")
                        
                        with col_side2:
                            st.markdown("**Comparison Text**")
                            st.info(text2)
                            st.caption(f"Words: {len(text2.split())} | Characters: {len(text2)}")
                    else:
                        st.error(f"Error during comparison: {comparison_result['error']}")
    
    # History Tab
    with tab_history:
        st.header("📜 Smart History & Versioning")
        st.markdown("View all your previous text processing operations with timestamps and parameters.")
        
        if st.session_state.username in st.session_state.history and st.session_state.history[st.session_state.username]:
            history = st.session_state.history[st.session_state.username]
            
            # Summary statistics
            col_hist1, col_hist2, col_hist3 = st.columns(3)
            with col_hist1:
                st.metric("Total Operations", len(history))
            with col_hist2:
                summarize_count = sum(1 for h in history if h['operation'] == 'Summarize')
                st.metric("Summaries", summarize_count)
            with col_hist3:
                paraphrase_count = sum(1 for h in history if h['operation'] == 'Paraphrase')
                st.metric("Paraphrases", paraphrase_count)
            
            st.markdown("---")
            
            # Display history entries
            for idx, entry in enumerate(history):
                with st.expander(f"📌 {entry['operation']} - {entry['timestamp']}", expanded=(idx == 0)):
                    col_h1, col_h2 = st.columns([2, 1])
                    
                    with col_h1:
                        st.markdown("**Output Preview:**")
                        st.write(entry['output_preview'])
                        
                        if st.button(f"View Full Output", key=f"view_{idx}"):
                            st.session_state[f'show_full_{idx}'] = not st.session_state.get(f'show_full_{idx}', False)
                        
                        if st.session_state.get(f'show_full_{idx}', False):
                            st.markdown("**Full Output:**")
                            st.text_area("", entry['full_output'], height=200, key=f"full_output_{idx}")
                    
                    with col_h2:
                        st.markdown("**Parameters:**")
                        params = entry['parameters']
                        st.caption(f"**Operation:** {params['operation']}")
                        st.caption(f"**Language:** {params['language']}")
                        st.caption(f"**Tone:** {params['tone']}")
                        st.caption(f"**Style:** {params['style']}")
                        if params.get('summary_type'):
                            st.caption(f"**Summary Type:** {params['summary_type']}")
                            st.caption(f"**Depth:** {params['depth']}")
                        st.caption(f"**Readability:** {params['readability']}")
                        if params.get('input_method'):
                            st.caption(f"**Input Method:** {params['input_method']}")
                        
                        # Restore button
                        if st.button("♻️ Restore", key=f"restore_{idx}"):
                            st.session_state.output_text = entry['full_output']
                            st.session_state.output_language = params['language']
                            st.session_state.operation = params['operation']
                            st.session_state.summary_type = params.get('summary_type')
                            st.success("✅ Output restored! Go to 'Process Text' tab to view.")
            
            # Clear history option
            st.markdown("---")
            if st.button("🗑️ Clear History", type="secondary"):
                if st.button("⚠️ Confirm Clear History"):
                    st.session_state.history[st.session_state.username] = []
                    st.success("History cleared!")
                    st.rerun()
        else:
            st.info("📭 No history yet. Start processing some text!")
=======
            st.write(output_data.get("summary", "No summary generated."))
            
            if output_data.get("summary"):
                st.download_button(
                    label="📄 Download Summary as PDF",
                    data=generate_pdf(output_data["summary"]),
                    file_name="TextMorph_Summary.pdf",
                    mime="application/pdf"
                )

        with tab2:
            st.write(output_data.get("paraphrase", "No paraphrase generated."))
            if output_data.get("paraphrase"):
                st.download_button(
                    label="📄 Download Paraphrase as PDF",
                    data=generate_pdf(output_data["paraphrase"]),
                    file_name="TextMorph_Paraphrase.pdf",
                    mime="application/pdf"
                )

        with tab3:
            st.json({
                "Keywords": output_data["keywords"],
                "Readability Score": output_data["readability"],
                "Plagiarism %": output_data["plagiarism"],
                "Sentiment": output_data["sentiment"]
            })
>>>>>>> c3269da (Added PDF download feature)

if __name__ == "__main__":
    main()
