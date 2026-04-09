# AI Resume Analyzer

---

## 1. Business Problem

Recruiters receive hundreds of resumes for a single job role, making it difficult to quickly identify the most relevant candidates. Manual screening is time-consuming, inconsistent, and inefficient.

---

## 2. Possible Solution

Use Machine Learning to automatically analyze resumes and compare them with job descriptions. The system can compute a match score, identify missing skills, and predict the most suitable job role.

---

## 3. Implemented Solution

This project is a Streamlit-based web application that:

* Extracts text from uploaded PDF resumes
* Cleans and processes text data
* Uses TF-IDF to convert text into numerical vectors
* Applies cosine similarity to compute match score
* Splits resume into chunks for better matching accuracy
* Uses a Naive Bayes classifier to predict job roles
* Identifies matched and missing keywords

---

## 4. Tech Stack Used

* Frontend: Streamlit (UI)
* Backend: Python
* Machine Learning:

  * Custom TF-IDF implementation
  * Cosine Similarity
  * Naive Bayes Classifier
* Libraries:

  * PyMuPDF (PDF extraction)
  * re, math, random (core processing)

---

## 5. Architecture Diagram

```
      +----------------------+
      |   Resume (PDF)       |
      +----------+-----------+
                 |
                 v
      +----------------------+
      | Text Extraction      |
      +----------------------+
                 |
                 v
      +----------------------+
      | Preprocessing        |
      +----------------------+
                 |
                 v
      +----------------------+
      | Resume Chunking      |
      +----------------------+
                 |
                 v
      +----------------------+
      | TF-IDF Vectorization |
      +----------------------+
                 |
                 v
      +----------------------+
      | Cosine Similarity    |
      +----------------------+
                 |
                 v
      +----------------------+
      | Match Score          |
      +----------------------+

                 +
                 |
                 v

      +----------------------+
      | Naive Bayes Model    |
      +----------------------+
                 |
                 v
      +----------------------+
      | Role Prediction      |
      +----------------------+

                 +
                 |
                 v

      +----------------------+
      | Keyword Analysis     |
      +----------------------+
```

---

## 6. How to Run in Local

Step 1: Clone Repository
git clone https://github.com/yourusername/ai-resume-analyzer.git
cd ai-resume-analyzer

Step 2: Install Dependencies
pip install streamlit pymupdf

Step 3: Run Application
python -m streamlit run rema1.py

Step 4: Open Browser
http://localhost:8501

---

## 7. References and Resources Used

* Streamlit Documentation – https://docs.streamlit.io
* PyMuPDF Documentation – https://pymupdf.readthedocs.io
* TF-IDF Concept – Information Retrieval Theory
* Naive Bayes Algorithm – Machine Learning Fundamentals
* Cosine Similarity – Vector Space Models

---

## Features

* Resume vs Job Description Matching
* Match Score (0–95%)
* Role Prediction (ML-based)
* Matched & Missing Keywords
* Fully Local (No APIs used)
* Clean, Premium UI

---

## Future Improvements

* Use advanced embeddings (BERT / Sentence Transformers)
* Add resume improvement suggestions
* Deploy online (Streamlit Cloud / Vercel)
