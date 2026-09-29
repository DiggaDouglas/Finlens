import os
import pandas as pd
import pytest

def test_raw_dataset_exists():
    assert os.path.exists("data/interim/documents.csv"), "documents.csv missing from data/interim/"

def test_processed_dataset_exists():
    assert os.path.exists("data/processed/Finlens_dataset.csv"), "Finlens_dataset.csv missing from data/processed/"

def test_clause_dataset_structure():
    df = pd.read_csv("data/processed/Finlens_dataset.csv")
    
    # Updated to match the new 12-column industry-standard schema
    required_cols = {
        "clause_id", "document_id", "provider_name", "document_type", 
        "source_type", "raw_text", "cleaned_clause_text", "violation_category", 
        "risk_level", "violating_span", "primary_law_reference", "annotator_notes"
    }
    
    missing_cols = required_cols - set(df.columns)
    assert not missing_cols, f"Missing required columns: {missing_cols}"
    
    # Asserting the exact finalized row count
    assert len(df) == 9467, f"Expected exactly 9467 clauses, found {len(df)}"

def test_no_missing_values():
    # keep_default_na=False stops pandas from turning the literal string "N/A" back into a missing value
    df = pd.read_csv("data/processed/Finlens_dataset.csv", keep_default_na=False)
    total_missing = df.isnull().sum().sum()
    assert total_missing == 0, f"Expected 0 missing values, found {total_missing}. Check 'violating_span' and 'annotator_notes'."