# prompts.py

# Prompt for extracting information from CV
EXTRACT_INFORMATION_PROMPT = """
You are an HR assistant helping to screen candidates for a Machine Learning Engineer position focused on Document Analysis and Recognition.

From the CV image provided, extract the following information:

- Full Name
- Contact Information (Email, Phone)
- Education (Degrees, Institutions, Majors, Graduation Dates)
- Work Experience (Companies, Roles, Durations, Responsibilities)
- Technical Skills (Programming Languages, ML Frameworks, Tools)
- Machine Learning Experience (Models used, Projects)
- Publications
- Certifications and Courses
- GitHub Links

Provide the extracted information in a structured JSON format under the key 'extracted_info'.

Then, generate a concise summary highlighting the candidate's qualifications under the key 'cv_summary'.

Ensure the response is in JSON format with keys 'extracted_info' and 'cv_summary'.
"""

# Prompt for asking question about code
def ASK_QUESTION_ABOUT_CODE_PROMPT(codebase_excerpt, question):
    return f"""
You are a code reviewer and software engineer with expertise in machine learning and document analysis.

Here is a codebase:
{codebase_excerpt}

Answer the following question about the codebase:
Question: {question}
"""

# Prompt for evaluating candidate
def EVALUATE_CANDIDATE_PROMPT(cv_summary, github_summary):
    return f"""
You are tasked with evaluating a job candidate based on their CV and GitHub repository summaries. Your goal is to classify the candidate into one of three categories:

1. **Ideal**: The candidate is an excellent fit with the required skills and qualifications.
2. **Mismatch**: The candidate does not meet the necessary criteria for the role.
3. **Potential**: The candidate does not fully fit the role but has some qualifications and shows a strong willingness to learn, with the potential to grow into the position over time.

**Input:**
- **Summary of CV**: {cv_summary}
- **Summary of GitHub Repositories**: {github_summary}

**Output:**
1. **Category**: [Ideal / Mismatch / Potential]
2. **Explanation**: Provide a short paragraph explaining why the candidate was classified into this category. Include reasons based on the skills, experience, or lack thereof, as seen in the CV and GitHub summary.
3. **Strengths**: Provide three bullet points highlighting the candidate's strengths based on the information provided.
4. **Weaknesses**: Provide three bullet points identifying areas where the candidate is lacking or could improve.

Example format:

**Category**: [Ideal / Mismatch / Potential]  
**Explanation**: Based on the candidate's CV and GitHub repositories, they have been classified as [Ideal / Mismatch / Potential] due to [specific reasons].  
**Strengths**:
- [Strength 1]
- [Strength 2]
- [Strength 3]
**Weaknesses**:
- [Weakness 1]
- [Weakness 2]
- [Weakness 3]
"""
