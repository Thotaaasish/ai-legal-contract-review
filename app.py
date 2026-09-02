import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from utils.document_utils import extract_text_from_file
from utils.s3_utils import upload_file_to_s3
from utils.logger import get_logger
from agents.extractor_agent import ExtractorAgent
from agents.template_agent import TemplateAgent
from agents.compare_agent import CompareAgent
from agents.risk_agent import RiskAgent
from agents.summary_agent import SummaryAgent

logger = get_logger("streamlit_app")

st.set_page_config(page_title="AI Legal Contract Review", page_icon="⚖️", layout="wide")
st.title("⚖️ Autonomous AI Legal Contract Review & Risk Assessment")
st.caption("Powered by AWS Bedrock (Claude 3), Amazon S3, CloudWatch & Multi-Agent Architecture")

# Sidebar Configuration
st.sidebar.header("⚙ Configuration & AWS Status")
contract_category = st.sidebar.selectbox("Select Contract Type", ["NDA", "MSA", "SOW", "Consulting", "Professional Services"])
baseline_source = st.sidebar.radio("Baseline Comparison Source", ["Use Standard S3 Template", "Upload Custom Existing Document"])
aws_s3_sync = st.sidebar.checkbox("Sync Reports & Baseline to Amazon S3", value=True)

# Main layout
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload Third-Party Contract (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"])
with col2:
    custom_baseline_file = None
    if baseline_source == "Upload Custom Existing Document":
        custom_baseline_file = st.file_uploader("Upload Existing Baseline Document (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"])

if uploaded_file is not None:
    raw_text = extract_text_from_file(uploaded_file)
    with st.expander("✉ View Uploaded Third-Party Document", expanded=False):
        st.text_area("Contract Text", raw_text, height=150)

    # State management for Human-In-The-Loop
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "deviations" not in st.session_state:
        st.session_state.deviations = []
    if "risks" not in st.session_state:
        st.session_state.risks = []

    if st.button("▶ Run AI Legal Analysis", type="primary"):
        with st.status("Executing Multi-Agent Workflow...", expanded=True) as status:
            st.write("🔍 **Extractor Agent**: Extracting and classifying clauses with confidence scoring...")
            extractor = ExtractorAgent()
            extracted_data = extractor.process(raw_text)
            
            st.write("📚 **Template Agent**: Resolving benchmark text...")
            if baseline_source == "Upload Custom Existing Document" and custom_baseline_file:
                baseline_template = extract_text_from_file(custom_baseline_file)
            else:
                template_agent = TemplateAgent()
                baseline_template = template_agent.get_template(contract_category)
            
            st.write("⚖️ **Compare Agent**: Executing sentence-level delta comparison...")
            compare_agent = CompareAgent()
            st.session_state.deviations = compare_agent.process(extracted_data.get("clauses", []), baseline_template)
            
            st.write("[!] **Risk Agent**: Classifying risk severity and calculating credibility metrics...")
            risk_agent = RiskAgent()
            st.session_state.risks = risk_agent.process(st.session_state.deviations)
            
            st.session_state.analysis_complete = True
            status.update(label="✔ Initial Analysis Complete. Ready for Human Review.", state="complete", expanded=False)

    if st.session_state.analysis_complete:
        st.divider()
        st.subheader("👤 Human-in-the-Loop (HITL) Review")
        st.info("Review and modify the AI-generated risk classifications and recommendations before generating the final executive summary.")
        
        # Convert to DataFrames for Streamlit Data Editor
        risk_df = pd.DataFrame(st.session_state.risks)
        
        if not risk_df.empty:
            edited_risk_df = st.data_editor(risk_df, num_rows="dynamic", use_container_width=True, key="risk_editor")
        else:
            st.write("No risks identified.")
            edited_risk_df = risk_df

        if st.button("Generate Final Executive Summary"):
            final_risks = edited_risk_df.to_dict('records')
            
            with st.spinner("📋 Summary Agent compiling final report..."):
                summary_agent = SummaryAgent()
                summary_report = summary_agent.process(contract_category, st.session_state.deviations, final_risks)

            tab1, tab2, tab3, tab4 = st.tabs(["📊 Executive Summary", "⚠️ Final Risk Matrix", "🔍 Clause Deviations", "↓ Export & Feedback"])
            
            with tab1:
                st.subheader("Executive Legal Brief")
                st.markdown(summary_report)
                
            with tab2:
                st.subheader("Clause Risk & Compliance Scorecard")
                for item in final_risks:
                    risk_lvl = str(item.get("risk_level", "LOW")).upper()
                    color = "red" if risk_lvl == "HIGH" else "orange" if risk_lvl == "MEDIUM" else "green"
                    st.markdown(f"#### :{color}[● {item.get('clause_name')} — {risk_lvl} RISK] (Credibility: {item.get('confidence_score', 'N/A')})")
                    st.markdown(f"**Impact:** {item.get('business_impact')}")
                    st.markdown(f"**Recommended Redline:** `{item.get('mitigation_recommendation')}`")
                    st.divider()
                    
            with tab3:
                st.subheader("Sentence-Level Baseline Deviations")
                for dev in st.session_state.deviations:
                    st.markdown(f"### Clause: `{dev.get('clause_name')}` ({dev.get('change_type')}) | Confidence: {dev.get('confidence_score')}")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.info(f"**Standard Baseline:**\n\n{dev.get('standard_clause_text')}")
                    with col_b:
                        st.warning(f"**Third-Party Clause:**\n\n{dev.get('contract_clause_text')}")
                    st.write(f"**Deviation Analysis:** {dev.get('deviation_details')}")
                    st.divider()
                    
            with tab4:
                st.subheader("System Feedback & Export")
                
                feedback_col, export_col = st.columns(2)
                with feedback_col:
                    st.write("**Rate this AI Assessment**")
                    feedback = st.feedback("thumbs")
                    user_comments = st.text_input("Additional comments for model fine-tuning:")
                    if st.button("Submit Feedback"):
                        logger.info(f"Model Feedback Received: Rating={feedback}, Comments={user_comments}")
                        st.success("Feedback securely logged to AWS CloudWatch for model evaluation.")

                with export_col:
                    text_report = f"LEGAL CONTRACT REVIEW\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{summary_report}"
                    report_filename = f"legal_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    
                    st.download_button("📥 Download TXT Audit Report", data=text_report, file_name=report_filename, mime="text/plain")
