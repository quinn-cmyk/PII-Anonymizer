# PII-Anonymizer: The Newsroom Air-Lock

A local-first, forensic utility for journalists to sanitize transcripts, source notes, and leaked documents before processing them in cloud-based AI tools.

## Installation

Run the following commands in your terminal to set up the sovereign environment:

```bash
pip install streamlit presidio-analyzer presidio-anonymizer detect-secrets spacy
python -m spacy download en_core_web_lg
