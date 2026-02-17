import streamlit as st
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# 1. Page Configuration
st.set_page_config(page_title="Newsroom Air-Lock", layout="wide")
st.title("Newsroom Air-Lock")
st.markdown("Sanitize transcripts and notes locally before using external AI tools.")

# 2. Initialize Engines with Custom Newsroom Rules
@st.cache_resource
def load_engines():
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()
    
    # Custom Recognizer: Employee IDs (e.g., EMP-774392)
    emp_pattern = Pattern(name="emp_pattern", regex=r"EMP-\d{6}", score=0.9)
    emp_rec = PatternRecognizer(supported_entity="EMPLOYEE_ID", patterns=[emp_pattern])
    analyzer.registry.add_recognizer(emp_rec)
    
    # Custom Recognizer: Internal Account numbers (e.g., AC-45822109)
    acct_pattern = Pattern(name="acct_pattern", regex=r"AC-\d{8}", score=0.8)
    acct_rec = PatternRecognizer(supported_entity="ACCOUNT_NUMBER", patterns=[acct_pattern])
    analyzer.registry.add_recognizer(acct_rec)
    
    return analyzer, anonymizer

analyzer, anonymizer = load_engines()

# 3. Sidebar Configuration
st.sidebar.header("Scrubbing Parameters")

# GHOST TEXT IMPLEMENTATION: Using placeholder instead of value
allow_list_raw = st.sidebar.text_area(
    "Allow-list (comma separated):",
    placeholder="e.g. Jordan, Midwest Analytics, Springfield"
)
allow_list = [word.strip() for word in allow_list_raw.split(',') if word.strip()]

st_threshold = st.sidebar.slider("Sensitivity Threshold", 0.0, 1.0, 0.35)
all_entities = analyzer.get_supported_entities()
st_entities = st.sidebar.multiselect("Data Types to Detect:", all_entities, default=all_entities)

op_mode = st.sidebar.selectbox("Anonymization Mode:", ["replace", "redact", "mask", "hash"])

# 4. Main Workspace
col1, col2 = st.columns(2)

with col1:
    st.subheader("Raw Input")
    input_text = st.text_area("Paste text here:", height=500)

with col2:
    st.subheader("Sanitized Output")
    if st.button("Run Scrubber"):
        if input_text:
            # Stage A: Analysis
            results = analyzer.analyze(
                text=input_text,
                entities=st_entities,
                language="en",
                score_threshold=st_threshold,
                allow_list=allow_list
            )
            
            # Stage B: Operator Configuration (fixes Masking/Hashing errors)
            if op_mode == "mask":
                operator_params = {"masking_char": "*", "chars_to_mask": 15, "from_end": True}
            elif op_mode == "hash":
                operator_params = {"hash_type": "sha256"}
            else:
                operator_params = {}

            operators = {"DEFAULT": OperatorConfig(op_mode, operator_params)}
            
            # Stage C: Transformation
            anonymized_result = anonymizer.anonymize(
                text=input_text,
                analyzer_results=results,
                operators=operators
            )
            
            st.code(anonymized_result.text, language=None)
            
            # Detailed entity log for reporter audit
            with st.expander("Audit Trail: Detected Entities"):
                st.write(results)
        else:
            st.warning("Please enter text to process.")

st.divider()
st.caption("Privacy Note: This application runs entirely on your local machine. No data is sent to the cloud.")
