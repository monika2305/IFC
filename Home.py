import streamlit as st
import ifcopenshell
import pandas as pd
from fpdf import FPDF
import json

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IFC Semantic Analyzer",
    page_icon="🏗️",
    layout="wide",
)

# ── Session state ──────────────────────────────────────────────────────────────
if "logged_in"    not in st.session_state: st.session_state.logged_in    = False
if "user_context" not in st.session_state: st.session_state.user_context = {}
if "model_loaded" not in st.session_state: st.session_state.model_loaded = False
if "analysis"     not in st.session_state: st.session_state.analysis     = {}

st.markdown("""
<style>
/* ══ 1. PAGE SHELL ══════════════════════════════════════════════════════════ */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main, .block-container,
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
}

/* ══ 2. SIDEBAR ══════════════════════════════════════════════════════════════*/
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {
    background-color: #161b22 !important;
    border-right: 1px solid #30363d !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] a {
    color: #e6edf3 !important;
}

/* ══ 3. TYPOGRAPHY ══════════════════════════════════════════════════════════ */
h1, h2, h3, h4, h5, h6 {
    color: #e6edf3 !important;
}
p, li, a {
    color: #e6edf3 !important;
}
/* Labels above widgets */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
label { color: #e6edf3 !important; }

/* ══ 4. INPUTS & SELECTBOX ══════════════════════════════════════════════════ */
input, textarea {
    background-color: #161b22 !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
}
/* Base-web select control */
[data-baseweb="select"] > div:first-child {
    background-color: #161b22 !important;
    border-color: #30363d !important;
}
[data-baseweb="select"] span,
[data-baseweb="select"] div {
    color: #e6edf3 !important;
    background-color: transparent !important;
}
/* Dropdown list */
[data-baseweb="popover"],
[data-baseweb="popover"] ul,
[data-baseweb="popover"] li,
[data-baseweb="menu"],
[data-baseweb="menu"] li {
    background-color: #161b22 !important;
    color: #e6edf3 !important;
    border-color: #30363d !important;
}
[data-baseweb="menu"] li:hover {
    background-color: #21262d !important;
}

/* ══ 5. FILE UPLOADER ════════════════════════════════════════════════════════ */
[data-testid="stFileUploader"],
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] section > div,
[data-testid="stFileUploader"] > div {
    background-color: #161b22 !important;
    border-color: #30363d !important;
    color: #e6edf3 !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small,
[data-testid="stFileUploaderDropzoneInstructions"] div {
    color: #8b949e !important;
    background-color: transparent !important;
}

/* ══ 6. DATAFRAME / TABLE ════════════════════════════════════════════════════ */
/* Outer wrapper */
[data-testid="stDataFrame"],
[data-testid="stDataFrame"] > div,
[data-testid="stDataFrameResizable"] {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
}
/* Header row */
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] [role="columnheader"] *,
.dvn-scroller .header-cell,
.dvn-scroller .header-cell * {
    background-color: #21262d !important;
    color: #e6edf3 !important;
    border-color: #30363d !important;
}
/* Data cells */
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataFrame"] [role="gridcell"] *,
[data-testid="stDataFrame"] [role="row"],
[data-testid="stDataFrame"] [role="row"] * {
    background-color: #161b22 !important;
    color: #e6edf3 !important;
    border-color: #30363d !important;
}
/* glide-data-grid canvas fallback: inject color vars via CSS custom props */
[data-testid="stDataFrame"] canvas {
    filter: none;
}

/* ══ 7. METRICS ══════════════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    color: #e6edf3 !important;
}
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {
    color: #8b949e !important;
}
[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] * {
    color: #8b949e !important;
}

/* ══ 8. EXPANDER ═════════════════════════════════════════════════════════════ */
[data-testid="stExpander"] {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary * {
    color: #e6edf3 !important;
    background-color: #161b22 !important;
}
[data-testid="stExpander"] [data-testid="stExpanderDetails"],
[data-testid="stExpander"] [data-testid="stExpanderDetails"] * {
    background-color: #161b22 !important;
    color: #e6edf3 !important;
}

/* ══ 9. ALERT BOXES (keep semantic colours, fix text) ════════════════════════ */
[data-testid="stAlert"] {
    border-radius: 8px !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] span {
    color: inherit !important;
}

/* ══ 10. BUTTONS ═════════════════════════════════════════════════════════════ */
div[data-testid="stButton"] > button {
    width: 100%;
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 14px !important;
    padding: 22px 20px !important;
    color: #e6edf3 !important;
    text-align: left;
    font-size: 13px;
    line-height: 1.6;
    height: auto;
    white-space: pre-wrap;
    transition: border-color .18s, background .18s, transform .15s, box-shadow .18s;
    cursor: pointer;
}
div[data-testid="stButton"] > button:hover {
    border-color: #58a6ff !important;
    background: #1c2333 !important;
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(88,166,255,0.15);
    color: #e6edf3 !important;
}
div[data-testid="stButton"] > button:focus {
    box-shadow: 0 0 0 2px #58a6ff44 !important;
    outline: none !important;
}

/* ══ 11. TABS ════════════════════════════════════════════════════════════════ */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background-color: #161b22 !important;
    border-bottom: 2px solid #30363d !important;
    border-radius: 8px 8px 0 0 !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #8b949e !important;
}
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
    color: #58a6ff !important;
    border-bottom: 2px solid #58a6ff !important;
}
[data-testid="stTabs"] [data-baseweb="tab-panel"] {
    background-color: #0d1117 !important;
}

/* ══ 12. CAPTIONS & HELPERS ══════════════════════════════════════════════════ */
[data-testid="stCaptionContainer"] p,
.stCaption, small {
    color: #8b949e !important;
}
hr {
    border: none !important;
    border-top: 1px solid #30363d !important;
    margin: 16px 0 !important;
}
/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.title("Login")
    name = st.text_input("Your name (optional)")
    role = st.selectbox("Your role", [
        "Select an option", "Architect", "Structural Engineer",
        "BIM Manager", "Contractor", "Facility Manager", "Student / Researcher"
    ])
    domain = st.selectbox("Project domain", [
        "Select an option", "Architecture", "Structural",
        "MEP", "Infrastructure", "Facility Management"
    ])
    purpose = st.selectbox("Purpose of IFC", [
        "Select an option", "Design coordination", "Compliance",
        "Construction", "Handover / FM", "Academic / Research"
    ])
    if st.button("Continue"):
        if "Select" in (role, domain, purpose):
            st.error("Please select all fields.")
        else:
            st.session_state.user_context = {
                "name": name, "role": role,
                "domain": domain, "purpose": purpose
            }
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
context = st.session_state.user_context

st.title("🏗️ IFC Semantic Data-Loss Analyzer")
c1, c2, c3 = st.columns(3)
c1.write(f"**Role:** {context['role']}")
c2.write(f"**Domain:** {context['domain']}")
c3.write(f"**Purpose:** {context['purpose']}")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗂️ Dashboards")
    st.markdown(
        "After uploading your IFC file, visit the dedicated dashboards:\n\n"
        "- **🧊 3D BIM Viewer** — interactive 3D model with issue highlights\n"
        "- **🔥 Issue Heatmap** — 2D floor plan density map"
    )
    st.markdown("---")
    if st.session_state.model_loaded:
        st.success("✅ Model loaded — dashboards ready")
    else:
        st.info("Upload an IFC file to enable dashboards")

# ── File upload ────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Upload IFC file", type=["ifc"])

# ── On fresh upload: parse IFC and store ALL results in session_state ──────────
if uploaded_file:
    with open("temp.ifc", "wb") as f:
        f.write(uploaded_file.getbuffer())
    model = ifcopenshell.open("temp.ifc")

    walls          = model.by_type("IfcWall")
    standard_walls = model.by_type("IfcWallStandardCase")
    doors          = model.by_type("IfcDoor")
    windows        = model.by_type("IfcWindow")
    proxies        = model.by_type("IfcBuildingElementProxy")
    all_elements   = model.by_type("IfcProduct")

    total_elements    = len(all_elements)
    total_walls       = len(walls) + len(standard_walls)
    semantic_elements = total_walls + len(doors) + len(windows)
    proxy_elements    = len(proxies)
    other_semantic    = max(total_elements - semantic_elements - proxy_elements, 0)
    semantic_pct = (semantic_elements / total_elements) * 100 if total_elements else 0
    proxy_pct    = (proxy_elements    / total_elements) * 100 if total_elements else 0
    other_pct    = (other_semantic    / total_elements) * 100 if total_elements else 0

    if proxy_pct <= 10:  severity = "LOW"
    elif proxy_pct < 20: severity = "MEDIUM"
    elif proxy_pct < 50: severity = "HIGH"
    else:                severity = "CRITICAL"

    # ── Model Quality Score (0–100) ────────────────────────────────────────────
    # 50 pts: semantic richness | 30 pts: proxy penalty | 20 pts: Pset completeness
    _total_walls_q = len(model.by_type("IfcWall")) + len(model.by_type("IfcWallStandardCase"))
    _walls_with_pset = 0
    for _w in model.by_type("IfcWall"):
        for _d in getattr(_w, "IsDefinedBy", []):
            if _d.is_a("IfcRelDefinesByProperties"):
                _ps = _d.RelatingPropertyDefinition
                if _ps and _ps.is_a("IfcPropertySet") and _ps.Name == "Pset_WallCommon":
                    _walls_with_pset += 1
                    break
    _pset_score  = (_walls_with_pset / _total_walls_q * 20) if _total_walls_q else 20
    _sem_score   = semantic_pct / 100 * 50
    _proxy_score = (1 - proxy_pct / 100) * 30
    quality_score = round(min(100, _sem_score + _proxy_score + _pset_score), 1)
    if   quality_score >= 85: quality_grade, quality_color = "Excellent", "#238636"
    elif quality_score >= 70: quality_grade, quality_color = "Good",      "#1f6feb"
    elif quality_score >= 50: quality_grade, quality_color = "Fair",      "#d29922"
    else:                     quality_grade, quality_color = "Poor",      "#da3633"

    walls_missing_pset = []
    for wall in model.by_type("IfcWall"):
        has_pset = False
        if hasattr(wall, "IsDefinedBy"):
            for defn in wall.IsDefinedBy:
                if defn.is_a("IfcRelDefinesByProperties"):
                    ps = defn.RelatingPropertyDefinition
                    if ps and ps.is_a("IfcPropertySet") and ps.Name == "Pset_WallCommon":
                        has_pset = True
        if not has_pset:
            walls_missing_pset.append(wall)

    # Store everything — persists across page switches
    st.session_state.model_loaded = True
    st.session_state.analysis = {
        "total_elements":    total_elements,
        "total_walls":       total_walls,
        "doors":             len(doors),
        "windows":           len(windows),
        "proxy_elements":    proxy_elements,
        "other_semantic":    other_semantic,
        "semantic_elements": semantic_elements,
        "semantic_pct":      semantic_pct,
        "proxy_pct":         proxy_pct,
        "other_pct":         other_pct,
        "severity":          severity,
        "quality_score":     quality_score,
        "quality_grade":     quality_grade,
        "quality_color":     quality_color,
        "proxy_list": [{
            "Name":     p.Name or "Unnamed",
            "GlobalId": p.GlobalId,
            "IFC Type": p.is_a(),
            "Issue":    "Semantic meaning lost (generic proxy)",
        } for p in proxies],
        "missing_pset_list": [{
            "Wall Name": w.Name or "Unnamed",
            "GlobalId":  w.GlobalId,
            "Issue":     "Pset_WallCommon missing",
        } for w in walls_missing_pset],
        "missing_pset_count": len(walls_missing_pset),
    }
    st.success("IFC file uploaded and analyzed successfully!")

# ══════════════════════════════════════════════════════════════════════════════
# RENDER ANALYSIS
# Reads from session_state → works on fresh upload AND when returning from
# another page (3D Viewer / Heatmap) without re-uploading the file.
# ══════════════════════════════════════════════════════════════════════════════
an = st.session_state.analysis

if an:
    # ── Summary metrics ────────────────────────────────────────────────────────
    st.header("📊 Summary Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Elements",     an["total_elements"])
    m2.metric("Semantic (%)",       f"{an['semantic_pct']:.2f}%")
    m3.metric("Proxy (%)",          f"{an['proxy_pct']:.2f}%")
    m4.metric("Other Semantic (%)", f"{an['other_pct']:.2f}%")

    # ── Element-wise classification ────────────────────────────────────────────
    st.subheader("🧱 Element-wise Classification")
    st.markdown(f'<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:4px;margin-bottom:8px;">', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({
        "Element Type": ["Walls", "Doors", "Windows", "Proxy Elements", "Other Semantic Elements"],
        "Count":        [
            an["total_walls"], an["doors"], an["windows"],
            an["proxy_elements"], an["other_semantic"],
        ],
    }), use_container_width=True)

    # ── Automated conclusion ───────────────────────────────────────────────────
    st.subheader("🧠 Automated Conclusion")
    if an["proxy_pct"] <= 10:
        st.success("The IFC model preserves semantic representation across all analyzed elements. No semantic degradation detected.")
    elif an["proxy_pct"] < 20:
        st.info("The IFC model largely preserves semantic meaning, with minor semantic degradation observed in a small subset of elements.")
    elif an["proxy_pct"] < 50:
        st.warning("The IFC model exhibits mixed semantic representation. Several building components are represented as proxy elements.")
    else:
        st.error("The IFC model shows significant semantic degradation. A large portion of elements are represented as generic proxy objects.")
    sev_color_map = {"LOW":"#238636","MEDIUM":"#1f6feb","HIGH":"#d29922","CRITICAL":"#da3633"}
    sev_col  = sev_color_map.get(an["severity"], "#8b949e")
    q_col    = an.get("quality_color", "#8b949e")
    q_score  = an.get("quality_score", "—")
    q_grade  = an.get("quality_grade", "—")
    q_sev    = an["severity"]
    st.markdown(
        f'<div style="display:flex;gap:16px;margin-top:10px;flex-wrap:wrap;">'
        f'<div style="flex:1;min-width:180px;background:{sev_col}18;border:1.5px solid {sev_col};'
        f'border-radius:10px;padding:14px 20px;text-align:center;">'
        f'<div style="font-size:11px;color:#8b949e;font-weight:600;letter-spacing:1px;margin-bottom:4px;">SEVERITY LEVEL</div>'
        f'<div style="font-size:22px;font-weight:800;color:{sev_col};">⚠ {q_sev}</div>'
        f'</div>'
        f'<div style="flex:1;min-width:180px;background:{q_col}18;border:1.5px solid {q_col};'
        f'border-radius:10px;padding:14px 20px;text-align:center;">'
        f'<div style="font-size:11px;color:#8b949e;font-weight:600;letter-spacing:1px;margin-bottom:4px;">MODEL QUALITY SCORE</div>'
        f'<div style="font-size:22px;font-weight:800;color:{q_col};">{q_score} / 100</div>'
        f'<div style="font-size:12px;color:{q_col};font-weight:600;margin-top:2px;">{q_grade}</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Proxy element tracing ──────────────────────────────────────────────────
    st.subheader("🔍 Element‑Level Tracing (Proxy Elements)")
    if an["proxy_list"]:
        st.dataframe(pd.DataFrame(an["proxy_list"]), use_container_width=True)
    else:
        st.markdown(f'<p style="color:#8b949e">No proxy elements detected.</p>', unsafe_allow_html=True)

    # ── Walls missing Pset_WallCommon ──────────────────────────────────────────
    st.subheader("🧱 Walls Missing Pset_WallCommon")
    st.markdown(f'<p style="color:#8b949e">Count: <strong style="color:#e6edf3">{an["missing_pset_count"]}</strong></p>', unsafe_allow_html=True)
    if an["missing_pset_count"] == 0:
        st.success("✅ All walls contain Pset_WallCommon.")
    else:
        st.dataframe(pd.DataFrame(an["missing_pset_list"]), use_container_width=True)

    # ── Dashboard navigation cards ─────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📐 Visual Dashboards")
    st.caption("Click a card to open the dashboard instantly.")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button(
            "🧊\n\n**3D BIM Viewer**\n\nInteractive 3D building model with issues highlighted. Rotate, zoom and click any element to inspect.\n\n→ Open Viewer",
            key="nav_3d",
            use_container_width=True,
        ):
            st.switch_page("pages/1_🧊_3D_BIM_Viewer.py")

    with c2:
        if st.button(
            "🔥\n\n**Issue Heatmap**\n\n2D floor plan showing issue density per zone. Hover over zones to drill into element details.\n\n→ Open Heatmap",
            key="nav_heat",
            use_container_width=True,
        ):
            st.switch_page("pages/2_🔥_Issue_Heatmap.py")

    with c3:
        if st.button(
            "📏\n\n**Rule Validation**\n\nValidate your model against 15+ BIM rules. Add custom rules and export a full compliance report.\n\n→ Open Validator",
            key="nav_rules",
            use_container_width=True,
        ):
            st.switch_page("pages/3_📏_Rule_Validation.py")

    with c4:
        if st.button(
            "🛠️\n\n**Correction Suggestions**\n\nAI-powered fix recommendations for every proxy and missing-Pset element found.\n\n→ Open Suggestions",
            key="nav_fix",
            use_container_width=True,
        ):
            st.switch_page("pages/4_🛠️_Correction_Suggestions.py")

    # ── PDF report ─────────────────────────────────────────────────────────────
    st.markdown("---")
    def generate_pdf(file_path="IFC_Analysis_Report.pdf"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "IFC Semantic Analysis Report", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 8, f"User Name: {context.get('name', 'N/A')}")
        pdf.multi_cell(0, 8, f"Role: {context.get('role', 'N/A')}")
        pdf.multi_cell(0, 8, f"Domain: {context.get('domain', 'N/A')}")
        pdf.multi_cell(0, 8, f"Purpose: {context.get('purpose', 'N/A')}")
        pdf.ln(5)
        pdf.multi_cell(0, 8, "Summary Metrics:")
        pdf.multi_cell(0, 8, f"Total Elements: {an['total_elements']}")
        pdf.multi_cell(0, 8, f"Semantic Elements: {an['semantic_elements']}")
        pdf.multi_cell(0, 8, f"Proxy Elements: {an['proxy_elements']}")
        pdf.multi_cell(0, 8, f"Other Semantic Elements: {an['other_semantic']}")
        pdf.multi_cell(0, 8, f"Semantic %: {an['semantic_pct']:.2f}%")
        pdf.multi_cell(0, 8, f"Proxy %: {an['proxy_pct']:.2f}%")
        pdf.multi_cell(0, 8, f"Other %: {an['other_pct']:.2f}%")
        pdf.multi_cell(0, 8, f"Severity Level: {an['severity']}")
        pdf.multi_cell(0, 8, f"Model Quality Score: {an.get('quality_score', 'N/A')} / 100  ({an.get('quality_grade', '')})")
        pdf.ln(5)
        if an["proxy_list"]:
            pdf.multi_cell(0, 8, "Proxy Elements Detail:")
            for i, p in enumerate(an["proxy_list"], 1):
                pdf.multi_cell(0, 8,
                    f"{i}. Name: {p['Name']} | Type: {p['IFC Type']} "
                    f"| GlobalId: {p['GlobalId']} | Issue: {p['Issue']}")
        pdf.ln(5)
        if an["missing_pset_count"] > 0:
            pdf.multi_cell(0, 8, "Walls Missing Pset_WallCommon:")
            for i, w in enumerate(an["missing_pset_list"], 1):
                pdf.multi_cell(0, 8,
                    f"{i}. Wall Name: {w['Wall Name']} "
                    f"| GlobalId: {w['GlobalId']} | Issue: {w['Issue']}")
        pdf.output(file_path)
        return file_path

    if st.button("📄 Download PDF Report"):
        pdf_path = generate_pdf()
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇️ Click to download PDF",
                data=f,
                file_name="IFC_Analysis_Report.pdf",
                mime="application/pdf",
            )
