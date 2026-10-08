import streamlit as st
import pandas as pd
import time

def inject_custom_css():
    """Injects CSS to match the FinLens wireframe color scheme and typography."""
    st.markdown("""
        <style>
        /* Dark Blue Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0a1128; 
        }
        [data-testid="stSidebar"] * {
            color: #e2e8f0;
        }
        /* Status Badges */
        .badge-high { background-color: #fee2e2; color: #991b1b; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 0.85em; }
        .badge-medium { background-color: #ffedd5; color: #9a3412; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 0.85em; }
        .badge-low { background-color: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 0.85em; }
        .badge-status { background-color: #f1f5f9; color: #334155; padding: 4px 8px; border-radius: 4px; font-weight: 500; font-size: 0.85em; }
        .badge-completed { color: #16a34a; font-weight: 600; }
        
        /* Metric Cards */
        .metric-card { border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; text-align: center; }
        .metric-high { border-top: 4px solid #ef4444; }
        .metric-medium { border-top: 4px solid #f97316; }
        .metric-low { border-top: 4px solid #22c55e; }
        .metric-total { border-top: 4px solid #3b82f6; }
        
        /* Document Highlights */
        .highlight-high { background-color: #fecaca; color: #991b1b; padding: 2px 4px; border-radius: 4px; border-bottom: 2px solid #ef4444; cursor: pointer;}
        .highlight-medium { background-color: #fed7aa; color: #9a3412; padding: 2px 4px; border-radius: 4px; border-bottom: 2px solid #f97316; cursor: pointer;}
        </style>
    """, unsafe_allow_html=True)


# --- ML API HOOKS ---

def run_compliance_pipeline(file_bytes, filename) -> dict:
    """
    HOOK FOR LEGAL-BERT:
    This is where your ML pipeline will ingest the PDF/TXT, extract clauses,
    run the inference, and return the structured JSON.
    """
    # Simulating ML processing time
    time.sleep(2) 
    
    return {
        "lender": filename.split('.')[0],
        "date": "Today",
        "status": "Completed",
        "risk_score": 85,
        "risk_level": "High Risk",
        "findings": {
            "high": 7, "medium": 5, "low": 2, "total": 14
        },
        "clauses": [
            {"id": 1, "text": "...you consent to us access your contacts, call logs...", "level": "High", "regulation": "KDPA Section 25", "confidence": 0.96},
            {"id": 2, "text": "...a daily rollover fee will be charged on all overdue...", "level": "High", "regulation": "CBK Regulations", "confidence": 0.93},
            {"id": 3, "text": "...we may share your data with third party service...", "level": "Medium", "regulation": "KDPA Section 31", "confidence": 0.78}
        ]
    }


# --- UI RENDERERS ---

def render_dashboard_list():
    """Renders the main table of digital lending applications."""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.text_input("🔍 Search Lender", placeholder="Search by lender name...")
        
    with col2:
        # File Upload Hook
        uploaded_file = st.file_uploader("Upload T&C Document", type=["pdf", "docx", "txt"])
        if uploaded_file:
            with st.spinner("Analyzing document with Legal-BERT..."):
                report = run_compliance_pipeline(uploaded_file.getvalue(), uploaded_file.name)
                st.session_state["current_report"] = report
                st.session_state["regulator_view"] = "audit"
                st.rerun()

    st.markdown("### Digital Lending Applications")
    
    # Simulating the table layout with columns for precise button control
    headers = st.columns([2, 2, 2, 2, 2])
    headers[0].markdown("**Lender Name**")
    headers[1].markdown("**Upload Date**")
    headers[2].markdown("**Status**")
    headers[3].markdown("**Compliance Risk Score**")
    headers[4].markdown("**Actions**")
    
    st.divider()
    
    # Mock Database Rows
    rows = [
        ("Lender A", "May 20, 2025", "Completed", 85, "High"),
        ("Lender B", "May 19, 2025", "Completed", 20, "Low"),
        ("Lender C", "May 18, 2025", "Completed", 62, "Medium")
    ]
    
    for lender, date, status, score, level in rows:
        cols = st.columns([2, 2, 2, 2, 2])
        cols[0].write(f"🏦 **{lender}**")
        cols[1].write(date)
        cols[2].markdown(f"🟢 <span class='badge-completed'>{status}</span>", unsafe_allow_html=True)
        
        badge_class = f"badge-{level.lower()}"
        cols[3].markdown(f"<span class='{badge_class}'>{score}% {level} Risk</span>", unsafe_allow_html=True)
        
        if cols[4].button("View Report", key=f"btn_{lender}"):
            st.session_state["current_report"] = {
                "lender": lender, "date": date, "status": status, 
                "risk_score": score, "risk_level": f"{level} Risk",
                "findings": {"high": 7, "medium": 5, "low": 2, "total": 14},
                "clauses": [
                    {"id": 1, "text": "...you consent to us access your contacts, call logs...", "level": "High", "regulation": "KDPA Section 25", "confidence": 0.96},
                    {"id": 2, "text": "...a daily rollover fee will be charged on all overdue...", "level": "High", "regulation": "CBK Regulations", "confidence": 0.93},
                    {"id": 3, "text": "...failure to repay may result in additional fees...", "level": "Medium", "regulation": "CBK Regulations", "confidence": 0.72}
                ]
            }
            st.session_state["regulator_view"] = "audit"
            st.rerun()


def render_audit_view():
    """Renders the detailed two-column AI audit interface."""
    report = st.session_state["current_report"]
    
    # Header & Breadcrumbs
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"Documents > {report['lender']} > **Terms and Conditions Audit**")
        st.title("Terms and Conditions Audit")
    with col2:
        st.button("📥 Export Report", use_container_width=True)
        badge_class = f"badge-{report['risk_level'].split()[0].lower()}"
        st.markdown(f"<div style='text-align: right;'><span style='font-size: 1.2em; color: gray;'>Compliance Risk Score</span><br><span style='font-size: 1.5em; font-weight: bold; color: #ef4444;'>{report['risk_score']}%</span> <span class='{badge_class}'>{report['risk_level']}</span></div>", unsafe_allow_html=True)

    st.divider()

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.markdown("#### Original Document")
        st.markdown(f"📄 `{report['lender']}_T&Cs.pdf`")
        
        # Simulated Document Viewer with NLP Highlights
        st.markdown("""
        <div style="border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; height: 500px; overflow-y: auto; background-color: white; color: #334155;">
            <h4>TERMS AND CONDITIONS</h4>
            <p><strong>1. Introduction</strong><br>By using our digital lending platform, you agree to the terms and conditions outlined below.</p>
            <p><strong>2. User Consent and Permissions</strong><br>
            2.1 By using the Application, you consent to us <span class="highlight-high" title="Violates KDPA Section 25">access your contacts</span>, call logs, SMS, device information, and any other data stored on your device.</p>
            <p><strong>3. Fees and Charges</strong><br>
            3.1 A <span class="highlight-high" title="Violates CBK Regulations">daily rollover fee</span> will be charged on all overdue amounts until the loan is repaid in full.</p>
            <p><strong>4. Loan Repayment</strong><br>
            4.1 You agree to repay the loan amount along with processing fees on or before the due date.<br>
            4.2 <span class="highlight-medium" title="Requires additional clarity">Failure to repay may result in additional charges</span> and collection actions.</p>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown("#### AI Audit Results")
        
        # Metric Cards Array
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.markdown(f"<div class='metric-card metric-high'><div style='color:#ef4444'>High Risk</div><h2>{report['findings']['high']}</h2></div>", unsafe_allow_html=True)
        mc2.markdown(f"<div class='metric-card metric-medium'><div style='color:#f97316'>Medium Risk</div><h2>{report['findings']['medium']}</h2></div>", unsafe_allow_html=True)
        mc3.markdown(f"<div class='metric-card metric-low'><div style='color:#22c55e'>Low Risk</div><h2>{report['findings']['low']}</h2></div>", unsafe_allow_html=True)
        mc4.markdown(f"<div class='metric-card metric-total'><div style='color:#3b82f6'>Total Findings</div><h2>{report['findings']['total']}</h2></div>", unsafe_allow_html=True)
        
        st.write("")
        tabs = st.tabs(["Findings", "Risk Summary", "Law Mapping", "Explanations"])
        
        with tabs[0]:
            st.markdown("##### Detected Risky Clauses")
            for clause in report['clauses']:
                badge_class = f"badge-{clause['level'].lower()}"
                with st.expander(f"⚠️ **{clause['level']} Risk:** {clause['regulation']} (Conf: {clause['confidence']})"):
                    st.write(f"**Extracted Text:** `{clause['text']}`")
                    st.markdown(f"**Violation:** Matches strict parameters for non-compliance against {clause['regulation']}.")
                    st.button("Flag for Human Review", key=f"flag_{clause['id']}")

    if st.button("← Back to Dashboard"):
        st.session_state["regulator_view"] = "dashboard"
        st.session_state["current_report"] = None
        st.rerun()


# --- MAIN ROUTER ---

def render_regulator_dashboard():
    """Main entry point for the regulator workspace."""
    inject_custom_css()
    
    if "regulator_view" not in st.session_state:
        st.session_state["regulator_view"] = "dashboard"

    # Header section matching the wireframe
    st.title("Dashboard")
    st.markdown("Overview of digital lending applications and compliance risk.")

    # State Routing
    if st.session_state["regulator_view"] == "dashboard":
        render_dashboard_list()
    elif st.session_state["regulator_view"] == "audit":
        render_audit_view()