import streamlit as st
import re
import math
import random
from collections import Counter

# ============================================================
# SIMPLE ML UTILITIES (no sklearn, no nltk, pure python)
# ============================================================

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize(text):
    return clean_text(text).split()

STOP_WORDS = set("""
a an the and or but in on at to for of is it this that was were be been being
have has had do does did will would shall should may might can could with from
by as are am not no nor so if then than too very just about above after again
all also any because before between both during each few more most other some
such through until while i me my we our you your he him his she her they them
their its own same which what when where who whom how up out into over under
""".split())

def remove_stopwords(tokens):
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 2]

# ============================================================
# TF-IDF Implementation
# ============================================================

class TfidfVectorizer:
    def __init__(self, max_features=500):
        self.max_features = max_features
        self.vocabulary_ = {}
        self.idf_ = {}

    def fit(self, documents):
        doc_freq = Counter()
        all_terms = Counter()
        n = len(documents)
        for doc in documents:
            tokens = remove_stopwords(tokenize(doc))
            unique = set(tokens)
            for t in unique:
                doc_freq[t] += 1
            for t in tokens:
                all_terms[t] += 1
        top_terms = [t for t, _ in all_terms.most_common(self.max_features)]
        self.vocabulary_ = {t: i for i, t in enumerate(top_terms)}
        self.idf_ = {}
        for term in self.vocabulary_:
            self.idf_[term] = math.log((1 + n) / (1 + doc_freq.get(term, 0))) + 1
        return self

    def transform(self, documents):
        vectors = []
        for doc in documents:
            tokens = remove_stopwords(tokenize(doc))
            tf = Counter(tokens)
            total = len(tokens) if tokens else 1
            vec = [0.0] * len(self.vocabulary_)
            for term, idx in self.vocabulary_.items():
                vec[idx] = (tf.get(term, 0) / total) * self.idf_.get(term, 1)
            norm = math.sqrt(sum(v * v for v in vec)) or 1
            vec = [v / norm for v in vec]
            vectors.append(vec)
        return vectors

    def fit_transform(self, documents):
        self.fit(documents)
        return self.transform(documents)

    def get_feature_names(self):
        return sorted(self.vocabulary_, key=self.vocabulary_.get)

def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return max(0.0, min(1.0, dot))

# ============================================================
# Naive Bayes Classifier
# ============================================================

class NaiveBayesClassifier:
    def __init__(self):
        self.class_probs = {}
        self.feature_probs = {}
        self.classes = []

    def fit(self, X, y):
        n = len(y)
        class_counts = Counter(y)
        self.classes = list(class_counts.keys())
        self.class_probs = {c: count / n for c, count in class_counts.items()}
        n_features = len(X[0])
        self.feature_probs = {}
        for c in self.classes:
            indices = [i for i, label in enumerate(y) if label == c]
            sums = [0.0] * n_features
            for i in indices:
                for j in range(n_features):
                    sums[j] += X[i][j]
            total = sum(sums) + n_features
            self.feature_probs[c] = [(s + 1) / total for s in sums]

    def predict(self, X):
        preds = []
        for vec in X:
            best_class = self.classes[0]
            best_score = -float('inf')
            for c in self.classes:
                score = math.log(self.class_probs[c])
                for j, v in enumerate(vec):
                    if v > 0:
                        score += v * math.log(self.feature_probs[c][j])
                if score > best_score:
                    best_score = score
                    best_class = c
            preds.append(best_class)
        return preds

# ============================================================
# Training Data Generator (300 samples)
# ============================================================

CATEGORY_KEYWORDS = {
    "Data Science": [
        "python pandas numpy matplotlib seaborn scikit-learn data analysis statistics "
        "machine learning regression classification clustering visualization jupyter "
        "sql database tableau powerbi data wrangling exploratory analysis hypothesis "
        "testing statistical modeling feature engineering data pipeline etl big data "
        "spark hadoop data mining predictive modeling time series forecasting",
        "data scientist analytics python r statistics machine learning deep learning "
        "tensorflow keras neural networks natural language processing computer vision "
        "data engineering airflow kafka streaming batch processing data warehouse "
        "redshift snowflake bigquery data governance data quality metrics kpi dashboard",
        "probability distributions bayesian inference a/b testing experimentation "
        "causal inference dimensionality reduction pca svd recommendation systems "
        "collaborative filtering content based filtering anomaly detection outlier "
        "detection feature selection cross validation hyperparameter tuning grid search",
    ],
    "Web Development": [
        "html css javascript react angular vue nodejs express mongodb rest api "
        "frontend backend fullstack responsive design bootstrap tailwind webpack "
        "typescript graphql redux state management component lifecycle hooks routing "
        "authentication authorization jwt oauth session cookies middleware cors",
        "web developer frontend engineer react developer nextjs gatsby server side "
        "rendering static site generation progressive web app service worker caching "
        "performance optimization lazy loading code splitting bundle size accessibility "
        "wcag aria semantic html seo search engine optimization meta tags sitemap",
        "database mysql postgresql sqlite nosql firebase firestore realtime websocket "
        "socket.io deployment docker kubernetes ci cd github actions netlify vercel "
        "aws azure cloud hosting domain dns ssl tls https security xss csrf sanitization",
    ],
    "Cybersecurity": [
        "security vulnerability penetration testing ethical hacking network security "
        "firewall intrusion detection encryption cryptography malware analysis "
        "incident response threat intelligence siem splunk wireshark nmap metasploit "
        "kali linux owasp top ten sql injection cross site scripting buffer overflow",
        "cybersecurity analyst security engineer soc analyst threat hunting digital "
        "forensics reverse engineering binary analysis exploit development shellcode "
        "privilege escalation lateral movement persistence defense evasion red team "
        "blue team purple team security operations center monitoring alerting triage",
        "compliance gdpr hipaa pci dss iso 27001 nist framework risk assessment "
        "vulnerability management patch management endpoint security antivirus edr "
        "xdr zero trust architecture identity access management multi factor "
        "authentication single sign on certificate management pki public key",
    ],
    "AI/ML": [
        "artificial intelligence machine learning deep learning neural network "
        "tensorflow pytorch keras convolutional neural network recurrent neural network "
        "transformer attention mechanism bert gpt natural language processing computer "
        "vision object detection image segmentation generative adversarial network "
        "reinforcement learning q learning policy gradient actor critic reward",
        "ai engineer ml engineer research scientist deep learning engineer nlp engineer "
        "computer vision engineer model training inference optimization quantization "
        "pruning knowledge distillation transfer learning fine tuning pretrained model "
        "huggingface diffusion model stable diffusion large language model prompt "
        "engineering retrieval augmented generation vector database embedding",
        "mlops model deployment serving monitoring drift detection feature store "
        "experiment tracking mlflow wandb model registry versioning reproducibility "
        "gpu cuda distributed training data parallel model parallel pipeline parallel "
        "gradient accumulation mixed precision training automatic differentiation",
    ],
    "Software Engineering": [
        "software engineer developer programming coding java python c++ golang rust "
        "algorithms data structures design patterns solid principles clean code "
        "refactoring unit testing integration testing test driven development agile "
        "scrum kanban sprint retrospective code review pull request git version control",
        "software development lifecycle requirements gathering system design "
        "architecture microservices monolith event driven architecture message queue "
        "rabbitmq kafka distributed systems scalability availability reliability "
        "load balancing caching redis memcached api design rest grpc protobuf",
        "devops infrastructure as code terraform ansible puppet chef monitoring "
        "observability logging metrics tracing prometheus grafana elk stack "
        "containerization docker kubernetes orchestration service mesh istio "
        "continuous integration continuous deployment jenkins github actions gitlab ci",
    ],
}

def generate_training_data(n_per_category=60):
    texts, labels = [], []
    for category, templates in CATEGORY_KEYWORDS.items():
        for _ in range(n_per_category):
            template = random.choice(templates)
            words = template.split()
            sample_size = random.randint(len(words) // 2, len(words))
            sample = random.sample(words, min(sample_size, len(words)))
            random.shuffle(sample)
            texts.append(" ".join(sample))
            labels.append(category)
    return texts, labels

# ============================================================
# PDF Extraction
# ============================================================

def extract_text_from_pdf(pdf_file):
    try:
        import fitz
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except ImportError:
        st.error("PyMuPDF not installed. Run: pip install PyMuPDF")
        return ""

# ============================================================
# Resume Analysis Engine
# ============================================================

def chunk_text(text, chunk_size=100, overlap=30):
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def analyze_resume(resume_text, job_description):
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(job_description)
    chunks = chunk_text(resume_clean, chunk_size=80, overlap=20)
    all_docs = chunks + [jd_clean]
    tfidf = TfidfVectorizer(max_features=300)
    vectors = tfidf.fit_transform(all_docs)
    jd_vec = vectors[-1]
    chunk_scores = [cosine_similarity(vectors[i], jd_vec) for i in range(len(chunks))]
    raw_score = max(chunk_scores) if chunk_scores else 0.0
    match_score = min(95, max(15, raw_score * 100 * 1.8))

    if match_score >= 80:
        category = "Excellent Match"
        cat_icon = "✅"
        cat_color = "#10b981"
    elif match_score >= 60:
        category = "Good Match"
        cat_icon = "👍"
        cat_color = "#f59e0b"
    else:
        category = "Weak Match"
        cat_icon = "⚠️"
        cat_color = "#ef4444"

    feature_names = tfidf.get_feature_names()
    jd_tokens = set(remove_stopwords(tokenize(jd_clean)))
    resume_tokens = set(remove_stopwords(tokenize(resume_clean)))
    jd_keyword_scores = []
    for term in feature_names:
        if term in jd_tokens:
            idx = tfidf.vocabulary_[term]
            jd_keyword_scores.append((term, jd_vec[idx]))
    jd_keyword_scores.sort(key=lambda x: -x[1])
    top_jd_keywords = [t for t, _ in jd_keyword_scores[:30]]
    matched = [k for k in top_jd_keywords if k in resume_tokens]
    missing = [k for k in top_jd_keywords if k not in resume_tokens]

    random.seed(42)
    train_texts, train_labels = generate_training_data(60)
    clf_tfidf = TfidfVectorizer(max_features=400)
    X_train = clf_tfidf.fit_transform(train_texts)
    clf = NaiveBayesClassifier()
    clf.fit(X_train, train_labels)
    X_resume = clf_tfidf.transform([resume_clean])
    predicted_role = clf.predict(X_resume)[0]

    return {
        "score": round(match_score, 1),
        "category": category,
        "cat_icon": cat_icon,
        "cat_color": cat_color,
        "role": predicted_role,
        "matched_keywords": matched[:15],
        "missing_keywords": missing[:15],
    }

# ============================================================
# PREMIUM STREAMLIT UI
# ============================================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Global CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Reset & Base */
.stApp {
    background: #0a0f0d !important;
    font-family: 'Inter', sans-serif !important;
}

.block-container {
    max-width: 900px !important;
    padding: 2rem 1.5rem 4rem !important;
}

/* Hide default Streamlit elements */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}

/* ---- Hero Header ---- */
.hero-header {
    text-align: center;
    padding: 3rem 0 2rem;
    position: relative;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -60px; left: 50%; transform: translateX(-50%);
    width: 500px; height: 300px;
    background: radial-gradient(ellipse, rgba(94,210,156,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(94,210,156,0.08);
    border: 1px solid rgba(94,210,156,0.2);
    color: #5ed29c;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 2px;
    padding: 6px 16px; border-radius: 100px;
    margin-bottom: 1.2rem;
}
.hero-title {
    font-family: 'Inter', sans-serif;
    font-size: 2.8rem; font-weight: 900;
    color: #ffffff;
    letter-spacing: -1.5px; line-height: 1.05;
    margin: 0 0 1rem;
}
.hero-title span { color: #5ed29c; }
.hero-sub {
    font-size: 0.95rem; color: rgba(255,255,255,0.45);
    max-width: 520px; margin: 0 auto; line-height: 1.7;
}

/* ---- Glass Card ---- */
.glass-card {
    background: rgba(255,255,255,0.02);
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    transition: border-color 0.3s ease;
}
.glass-card:hover {
    border-color: rgba(94,210,156,0.15);
}
.glass-card-header {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 1rem;
}
.glass-card-icon {
    width: 36px; height: 36px; border-radius: 10px;
    background: rgba(94,210,156,0.1);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.glass-card-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.95rem; font-weight: 700;
    color: rgba(255,255,255,0.85);
    letter-spacing: -0.3px;
}

/* ---- Streamlit Overrides ---- */
.stFileUploader > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px dashed rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    transition: border-color 0.3s !important;
}
.stFileUploader > div:hover {
    border-color: rgba(94,210,156,0.3) !important;
}
.stTextArea textarea {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: rgba(255,255,255,0.85) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 1rem !important;
    transition: border-color 0.3s !important;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: rgba(94,210,156,0.4) !important;
    box-shadow: 0 0 0 3px rgba(94,210,156,0.08) !important;
}
.stTextArea textarea::placeholder {
    color: rgba(255,255,255,0.2) !important;
}

/* Primary Button */
.stButton > button {
    background: linear-gradient(135deg, #5ed29c 0%, #3bb87a 100%) !important;
    color: #070b0a !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    border: none !important;
    border-radius: 100px !important;
    padding: 0.85rem 2rem !important;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: 0 4px 20px rgba(94,210,156,0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(94,210,156,0.35) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* Divider */
.premium-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
    margin: 2rem 0;
}

/* ---- Results ---- */
.score-ring {
    text-align: center;
    padding: 2.5rem 0;
}
.score-circle {
    width: 180px; height: 180px;
    border-radius: 50%;
    margin: 0 auto 1.2rem;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    position: relative;
}
.score-circle::before {
    content: '';
    position: absolute; inset: 0;
    border-radius: 50%;
    padding: 3px;
    background: conic-gradient(var(--ring-color) var(--ring-pct), rgba(255,255,255,0.06) 0%);
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
}
.score-value {
    font-family: 'Inter', sans-serif;
    font-size: 3.2rem; font-weight: 900;
    color: #ffffff; letter-spacing: -2px;
    line-height: 1;
}
.score-pct {
    font-size: 1.2rem; font-weight: 600;
    color: rgba(255,255,255,0.4);
}
.score-category {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 8px 20px; border-radius: 100px;
    font-size: 0.85rem; font-weight: 700;
    letter-spacing: 0.5px;
}

/* Role Card */
.role-card {
    background: linear-gradient(135deg, rgba(94,210,156,0.06) 0%, rgba(94,210,156,0.02) 100%);
    border: 1px solid rgba(94,210,156,0.12);
    border-radius: 14px;
    padding: 1.5rem 2rem;
    display: flex; align-items: center; gap: 16px;
    margin: 1.5rem 0;
}
.role-icon {
    width: 48px; height: 48px;
    background: rgba(94,210,156,0.1);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; flex-shrink: 0;
}
.role-label {
    font-size: 0.7rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 2px;
    color: rgba(255,255,255,0.35); margin-bottom: 4px;
}
.role-value {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.3rem; font-weight: 800;
    color: #5ed29c; letter-spacing: -0.5px;
}

/* Keywords */
.kw-section-title {
    display: flex; align-items: center; gap: 8px;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.85rem; font-weight: 700;
    color: rgba(255,255,255,0.7);
    margin-bottom: 0.8rem;
}
.kw-dot {
    width: 8px; height: 8px; border-radius: 50%;
}
.kw-grid {
    display: flex; flex-wrap: wrap; gap: 6px;
}
.kw-tag {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem; font-weight: 500;
    transition: transform 0.2s ease;
}
.kw-tag:hover {
    transform: translateY(-1px);
}
.kw-matched {
    background: rgba(16,185,129,0.1);
    color: #34d399;
    border: 1px solid rgba(16,185,129,0.15);
}
.kw-missing {
    background: rgba(239,68,68,0.08);
    color: #f87171;
    border: 1px solid rgba(239,68,68,0.12);
}
.kw-empty {
    font-size: 0.85rem; color: rgba(255,255,255,0.3);
    padding: 1rem; text-align: center;
}

/* Pipeline */
.pipeline-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 1.8rem;
    margin-top: 1.5rem;
}
.pipeline-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.9rem; font-weight: 700;
    color: rgba(255,255,255,0.7);
    margin-bottom: 1.2rem;
    display: flex; align-items: center; gap: 8px;
}
.pipeline-step {
    display: flex; align-items: flex-start; gap: 14px;
    padding: 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.pipeline-step:last-child { border-bottom: none; }
.step-num {
    width: 28px; height: 28px;
    background: rgba(94,210,156,0.1);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 700;
    color: #5ed29c; flex-shrink: 0;
}
.step-text {
    font-size: 0.82rem; color: rgba(255,255,255,0.55);
    line-height: 1.5;
}
.step-text strong { color: rgba(255,255,255,0.8); }

/* Footer */
.app-footer {
    text-align: center;
    padding: 3rem 0 1rem;
    color: rgba(255,255,255,0.15);
    font-size: 0.72rem;
    letter-spacing: 1px;
}

/* Spinner override */
.stSpinner > div {
    border-top-color: #5ed29c !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 4px;
    border: 1px solid rgba(255,255,255,0.06);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: rgba(255,255,255,0.4) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(94,210,156,0.1) !important;
    color: #5ed29c !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }
.stTabs [data-baseweb="tab-border"] { display: none; }

/* Expander */
.streamlit-expanderHeader {
    background: transparent !important;
    color: rgba(255,255,255,0.5) !important;
    font-size: 0.85rem !important;
}

/* Animations */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.animate-in {
    animation: fadeInUp 0.6s cubic-bezier(0.16,1,0.3,1) forwards;
}
.delay-1 { animation-delay: 0.1s; opacity: 0; }
.delay-2 { animation-delay: 0.2s; opacity: 0; }
.delay-3 { animation-delay: 0.3s; opacity: 0; }
.delay-4 { animation-delay: 0.4s; opacity: 0; }
</style>
""", unsafe_allow_html=True)

# ---- Hero Header ----
st.markdown("""
<div class="hero-header">
    <div class="hero-badge">🧠 Machine Learning Powered</div>
    <h1 class="hero-title">AI Resume<br>Analyzer<span>.</span></h1>
    <p class="hero-sub">
        Upload your resume and paste a job description for an instant match score,
        role prediction, and smart keyword analysis — all running locally.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

# ---- Input Section ----
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("""
    <div class="glass-card-header">
        <div class="glass-card-icon">📎</div>
        <div class="glass-card-title">Upload Resume</div>
    </div>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")

with col2:
    st.markdown("""
    <div class="glass-card-header">
        <div class="glass-card-icon">📝</div>
        <div class="glass-card-title">Job Description</div>
    </div>
    """, unsafe_allow_html=True)
    job_description = st.text_area(
        "Paste JD",
        height=200,
        label_visibility="collapsed",
        placeholder="Paste the target job description here..."
    )

st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

# ---- Analyze Button ----
if st.button("⚡  Analyze Resume", use_container_width=True, type="primary"):
    if not uploaded_file:
        st.error("Please upload a PDF resume.")
    elif not job_description.strip():
        st.error("Please enter a job description.")
    else:
        with st.spinner("Running ML pipeline..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            if not resume_text.strip():
                st.error("Could not extract text from PDF.")
            else:
                results = analyze_resume(resume_text, job_description)

                st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

                # ---- Score Ring ----
                score = results["score"]
                cat_color = results["cat_color"]
                pct = score / 100

                st.markdown(f"""
                <div class="score-ring animate-in">
                    <div class="score-circle" style="--ring-color: {cat_color}; --ring-pct: {pct*100}%;">
                        <div class="score-value">{score}</div>
                        <div class="score-pct">%</div>
                    </div>
                    <div class="score-category" style="background: {cat_color}15; color: {cat_color}; border: 1px solid {cat_color}30;">
                        {results['cat_icon']} {results['category']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ---- Role Prediction ----
                role_icons = {
                    "Data Science": "📊",
                    "Web Development": "🌐",
                    "Cybersecurity": "🔒",
                    "AI/ML": "🤖",
                    "Software Engineering": "⚙️",
                }
                r_icon = role_icons.get(results["role"], "🎯")

                st.markdown(f"""
                <div class="role-card animate-in delay-1">
                    <div class="role-icon">{r_icon}</div>
                    <div>
                        <div class="role-label">Predicted Job Role</div>
                        <div class="role-value">{results['role']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ---- Keywords ----
                kw_col1, kw_col2 = st.columns(2, gap="medium")

                with kw_col1:
                    matched_tags = "".join(
                        f'<span class="kw-tag kw-matched">{k}</span>'
                        for k in results["matched_keywords"]
                    ) if results["matched_keywords"] else '<div class="kw-empty">No matches found</div>'

                    st.markdown(f"""
                    <div class="glass-card animate-in delay-2">
                        <div class="kw-section-title">
                            <div class="kw-dot" style="background: #10b981;"></div>
                            Matched Keywords
                        </div>
                        <div class="kw-grid">{matched_tags}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with kw_col2:
                    missing_tags = "".join(
                        f'<span class="kw-tag kw-missing">{k}</span>'
                        for k in results["missing_keywords"]
                    ) if results["missing_keywords"] else '<div class="kw-empty">All key terms present ✓</div>'

                    st.markdown(f"""
                    <div class="glass-card animate-in delay-3">
                        <div class="kw-section-title">
                            <div class="kw-dot" style="background: #ef4444;"></div>
                            Missing Keywords
                        </div>
                        <div class="kw-grid">{missing_tags}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # ---- Pipeline Info ----
                steps = [
                    ("PDF Extraction", "Text extracted locally using PyMuPDF"),
                    ("Preprocessing", "Lowercase, remove special chars, stopword removal"),
                    ("Chunking", "Resume split into 80-word overlapping chunks"),
                    ("TF-IDF Vectorization", "Text converted to numerical feature vectors"),
                    ("Cosine Similarity", "Best chunk-to-JD similarity → match score"),
                    ("Naive Bayes", "Trained on 300 samples across 5 job categories"),
                    ("Keyword Analysis", "TF-IDF features identify matched & missing terms"),
                ]
                steps_html = "".join(
                    f'<div class="pipeline-step"><div class="step-num">{i+1}</div>'
                    f'<div class="step-text"><strong>{name}</strong> — {desc}</div></div>'
                    for i, (name, desc) in enumerate(steps)
                )

                st.markdown(f"""
                <div class="pipeline-card animate-in delay-4">
                    <div class="pipeline-title">⚙️ ML Pipeline</div>
                    {steps_html}
                </div>
                """, unsafe_allow_html=True)

# ---- Footer ----
st.markdown("""
<div class="app-footer">
    © 2025 AI RESUME ANALYZER · BUILT WITH MACHINE LEARNING · NO EXTERNAL APIS
</div>
""", unsafe_allow_html=True)