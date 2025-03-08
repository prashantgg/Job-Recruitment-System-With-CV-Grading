import re
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import spacy  # type: ignore
import fitz  # type: ignore  # PyMuPDF for PDF extraction
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Job, JobApplication
from .models import CvGrading  # Assuming CvGrading model exists for storing grades

# Load SpaCy model for word vectors
nlp = spacy.load("en_core_web_md")  # Using medium model for better word embeddings

# Extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = " ".join([page.get_text("text") for page in doc])
    return text.strip()

# Preprocess CV text by removing unwanted content like page numbers and headers
def preprocess_cv_text(cv_text):
    """Preprocess the CV text by removing unwanted content like page numbers and headers."""
    # Remove page numbers and unwanted metadata (e.g., "Page 1", "Page 2", "Confidential", etc.)
    cv_text = re.sub(r"Page \d+", "", cv_text)
    cv_text = re.sub(r"\bConfidential\b", "", cv_text)
    cv_text = re.sub(r"\bPersonal\b", "", cv_text)
    
    # Remove extra spaces and punctuation
    cv_text = re.sub(r"[^\w\s]", " ", cv_text)  # Remove punctuation
    cv_text = re.sub(r"\s+", " ", cv_text).strip()  # Remove extra spaces
    
    return cv_text.strip()

# Extract all keywords (e.g., nouns, verbs, and other significant words)
def extract_all_keywords(text):
    """Extract keywords from the CV text."""
    # Using spaCy to extract the most significant words (e.g., nouns, verbs)
    doc = nlp(text)
    
    # Extracting nouns and proper nouns as keywords
    keywords = [token.text.lower() for token in doc if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 2]
    return keywords

# Compute similarity between extracted CV data and job post using weighted TF-IDF + Word Embeddings
def compute_similarity(application):
    """Compute similarity between extracted CV data and job post using weighted TF-IDF + Word Embeddings."""
    
    # Get job details from the database using the Job model
    job = application.job
    job_skills = job.skill_list()  # Skills list from the job post
    job_experience = job.experience  # Experience required for the job
    job_education = job.education  # Education required for the job
    
    # Extract CV text
    resume_path = application.resume.path
    cv_text = extract_text_from_pdf(resume_path)
    
    # Preprocess the CV text (remove page numbers, headers, and other irrelevant content)
    cv_text = preprocess_cv_text(cv_text)
    
    # Extract keywords from the CV
    extracted_keywords_cv = extract_all_keywords(cv_text)
    cv_combined_text = " ".join(extracted_keywords_cv)

    # Combine job post details (skills, experience, education)
    job_combined_text = f"{' '.join(job_skills)} {job_experience} {job_education}"

    # Directly compare skills in job description with CV keywords
    skill_matches = [skill for skill in job_skills if skill.lower() in cv_combined_text]

    # If job skills are present in CV, boost the cosine similarity score
    if skill_matches:
        skill_boost = len(skill_matches) * 10  # Boost for each skill match (weight can be adjusted)
    else:
        skill_boost = 0

    # Preprocess CV and job text before feeding into the vectorizer
    documents = [cv_combined_text, job_combined_text]
    
    # Initialize TF-IDF Vectorizer with stop words removal (only unigrams)
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 1))  # Unigrams only
    
    # Fit and transform both documents
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Compute cosine similarity between job and CV
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    
    # Get the similarity score
    similarity_score = cosine_sim[0][0] * 100  # Scale it to 100 for percentage

    # Add the skill boost to the similarity score
    final_similarity_score = min(similarity_score + skill_boost, 100)  # Cap at 100%

    # Return the similarity score
    return round(final_similarity_score, 2)

# Grade all CVs for a specific job using cosine similarity
def grade_all_cvs(request, job_id):
    """Grades all CVs for a specific job using cosine similarity."""
    
    job = get_object_or_404(Job, pk=job_id)
    applications = JobApplication.objects.filter(job=job)
    grading_results = {}

    for application in applications:
        if application.resume:
            # Compute cosine similarity score for the CV
            similarity_score = compute_similarity(application)

            # Determine recommendation based on similarity score
            if similarity_score >= 80:
                recommendation = "Highly Recommended"
            elif 60 <= similarity_score < 80:
                recommendation = "Moderately Recommended"
            else:
                recommendation = "Not Recommended"

            # Store results in CvGrading model (to track scores and recommendations)
            grading, created = CvGrading.objects.update_or_create(
                application=application,
                defaults={"score": similarity_score, "recommendation": recommendation}
            )

            # Update the grading status for the JobApplication model
            application.is_graded = True  # Mark the application as graded
            application.save()

            # Add grading result for this application to the results dictionary
            grading_results[application.id] = f"{recommendation} ({similarity_score}%)"

    return JsonResponse({"success": True, "results": grading_results})
