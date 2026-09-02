# Autonomous AI Legal Contract Review & Risk Assessment

An enterprise-grade multi-agent AI system that automates the review of third-party legal contracts against internal organizational baselines, calculates risk scores, and generates executive legal briefs.

## 🚀 Key Features
* **Multi-Agent Architecture:** Sequential autonomous agents (`Extractor`, `Template`, `Compare`, `Risk`, and `Summary`) built using Python and AWS Bedrock.
* **Deterministic Delta Analysis:** Performs sentence-level comparisons against standard baselines (NDA, MSA, SOW) to classify deviations.
* **Human-in-the-Loop (HITL):** Interactive Streamlit data editor allowing legal professionals to review and override AI risk assessments.
* **Cloud Integration & Auditing:** Securely archives reports to Amazon S3 and streams execution metrics to AWS CloudWatch.

## 🛠️ Tech Stack
* **Frontend:** Streamlit, Pandas
* **AI & Cloud:** AWS Bedrock, Amazon S3, AWS CloudWatch, Boto3/Botocore
* **Document Processing:** PyPDF, python-docx

## 📋 How to Run Locally

1. Clone the repository:
```bash
git clone [https://github.com/YOUR_USERNAME/ai-legal-contract-review.git](https://github.com/YOUR_USERNAME/ai-legal-contract-review.git)
cd ai-legal-contract-review
