import os
import pandas as pd
import pytest

def test_raw_dataset_exists():
    assert os.path.exists("data/interim/documents.csv"), "documents.csv missing from data/interim/"

def test_processed_clauses_exist():
    assert os.path.exists("data/processed/annotation_dataset.csv"), "annotation_dataset.csv missing from data/processed/"

def test_clause_dataset_structure():
    df = pd.read_csv("data/processed/annotation_dataset.csv")
    required_cols = {"clause_id", "document_id", "clause_text", "violation_category", "risk_level"}
    assert required_cols.issubset(set(df.columns)), f"Missing required columns: {required_cols - set(df.columns)}"
    assert len(df) > 5000, f"Expected >5000 clauses, found {len(df)}"