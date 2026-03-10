import streamlit as st
import ifcopenshell
import pandas as pd
from fpdf import FPDF

st.set_page_config(
    page_title="Correction Suggestions — IFC Analyzer",
    page_icon="🛠️",
    layout="wide",
)

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
.main, .block-container {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
}
[data-testid="stSidebar"], [data-testid="stSidebar"] > div {
    background-color: #161b22 !important;
    border-right: 1px solid #30363d !important;
}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span,
[data-testid="stSidebar"] label, [data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #e6edf3 !important;
}
h1, h2, h3, h4, h5, h6, p, span, label { color: #e6edf3 !important; }
input, textarea {
    background-color: #161b22 !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
}
[data-baseweb="select"] > div:first-child {
    background-color: #161b22 !important;
    border-color: #30363d !important;
}
[data-baseweb="select"] span, [data-baseweb="select"] div {
    color: #e6edf3 !important;
    background-color: transparent !important;
}
[data-baseweb="popover"], [data-baseweb="popover"] ul,
[data-baseweb="popover"] li, [data-baseweb="menu"], [data-baseweb="menu"] li {
    background-color: #161b22 !important;
    color: #e6edf3 !important;
    border-color: #30363d !important;
}
[data-testid="stFileUploader"], [data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploader"] section, [data-testid="stFileUploader"] > div {
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
[data-testid="stDataFrame"], [data-testid="stDataFrame"] > div {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
}
[data-testid="stDataFrame"] th, [data-testid="stDataFrame"] [role="columnheader"] {
    background-color: #21262d !important;
    color: #e6edf3 !important;
}
[data-testid="stDataFrame"] td, [data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataFrame"] [role="gridcell"] * {
    background-color: #161b22 !important;
    color: #e6edf3 !important;
}
[data-testid="stMetric"] {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * { color: #e6edf3 !important; }
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * { color: #8b949e !important; }
[data-testid="stExpander"] {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {
    color: #e6edf3 !important;
    background-color: #161b22 !important;
}
[data-testid="stAlert"] { border-radius: 8px !important; }
[data-testid="stAlert"] p, [data-testid="stAlert"] span { color: inherit !important; }
div[data-testid="stButton"] > button {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
}
div[data-testid="stButton"] > button:hover {
    background: #1c2333 !important;
    border-color: #58a6ff !important;
    color: #e6edf3 !important;
}
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background-color: #161b22 !important;
    border-bottom: 2px solid #30363d !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #8b949e !important;
}
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
    color: #58a6ff !important;
    border-bottom: 2px solid #58a6ff !important;
}
[data-testid="stTabs"] [data-baseweb="tab-panel"] { background-color: #0d1117 !important; }
[data-testid="stCaptionContainer"] p, .stCaption, small { color: #8b949e !important; }
hr { border: none !important; border-top: 1px solid #30363d !important; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── Guards ─────────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.warning("Please log in from the Home page first.")
    st.stop()

try:
    model = ifcopenshell.open("temp.ifc")
except Exception:
    st.warning("⚠️ No IFC file found. Please upload a file on the **Home** page first.")
    st.stop()

an = st.session_state.get("analysis", {})
if not an:
    st.warning("⚠️ No analysis data found. Please upload and analyze an IFC file on the **Home** page first.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# CORRECTION ENGINE
# For each detected issue, generate a specific, actionable suggestion
# ══════════════════════════════════════════════════════════════════════════════

def get_suggested_type(name: str, current_type: str) -> str:
    """Guess the correct IFC type from the element name."""
    n = (name or "").lower()
    if any(k in n for k in ["wall", "wand", "mur", "muur"]):        return "IfcWall"
    if any(k in n for k in ["door", "tur", "porte", "deur"]):       return "IfcDoor"
    if any(k in n for k in ["window", "fenster", "fenêtre", "raam"]): return "IfcWindow"
    if any(k in n for k in ["slab", "floor", "dalle", "platte"]):   return "IfcSlab"
    if any(k in n for k in ["column", "col", "stütze", "pilier"]):  return "IfcColumn"
    if any(k in n for k in ["beam", "träger", "poutre", "balk"]):   return "IfcBeam"
    if any(k in n for k in ["stair", "treppe", "escalier"]):        return "IfcStair"
    if any(k in n for k in ["roof", "dach", "toit", "dak"]):        return "IfcRoof"
    if any(k in n for k in ["ramp", "rampe"]):                      return "IfcRamp"
    if any(k in n for k in ["rail", "geländer", "garde"]):          return "IfcRailing"
    if any(k in n for k in ["pipe", "rohr", "tuyau"]):              return "IfcPipeSegment"
    if any(k in n for k in ["duct", "kanal", "gaine"]):             return "IfcDuctSegment"
    if any(k in n for k in ["furn", "möbel", "meuble", "meubilair"]): return "IfcFurnishingElement"
    return "IfcBuildingElement"  # generic fallback — better than proxy

def confidence_score(name: str, suggested: str) -> int:
    """Return 0-100 confidence that the suggestion is correct."""
    n = (name or "").lower()
    exact_map = {
        "IfcWall":    ["wall","wand","mur"],
        "IfcDoor":    ["door","tur","porte"],
        "IfcWindow":  ["window","fenster"],
        "IfcSlab":    ["slab","floor","dalle"],
        "IfcColumn":  ["column","col","stütze"],
        "IfcBeam":    ["beam","träger","poutre"],
        "IfcStair":   ["stair","treppe"],
        "IfcRoof":    ["roof","dach"],
    }
    keywords = exact_map.get(suggested, [])
    if any(k in n for k in keywords): return 92
    if n and n != "unnamed":          return 55
    return 20

def pset_suggestions(ifc_type: str) -> list:
    """Return recommended Psets for a given IFC type."""
    pset_map = {
        "IfcWall":    ["Pset_WallCommon",    "Pset_ConcreteElementGeneral"],
        "IfcDoor":    ["Pset_DoorCommon",    "Pset_DoorWindowGlazingType"],
        "IfcWindow":  ["Pset_WindowCommon",  "Pset_DoorWindowGlazingType"],
        "IfcSlab":    ["Pset_SlabCommon",    "Pset_ConcreteElementGeneral"],
        "IfcColumn":  ["Pset_ColumnCommon",  "Pset_ConcreteElementGeneral"],
        "IfcBeam":    ["Pset_BeamCommon",    "Pset_ConcreteElementGeneral"],
        "IfcStair":   ["Pset_StairCommon"],
        "IfcRoof":    ["Pset_RoofCommon"],
        "IfcRailing": ["Pset_RailingCommon"],
    }
    return pset_map.get(ifc_type, ["Pset_BuildingElementCommon"])

def ifc_correction_steps(current: str, suggested: str) -> str:
    """Return IFC file edit instruction."""
    return (
        f"In the IFC file, locate the entity `#{current}` and change "
        f"`{current}` → `{suggested}`. "
        f"Ensure the ObjectType and PredefinedType attributes are updated accordingly."
    )

# ── Build correction list ──────────────────────────────────────────────────────
corrections = []

# 1. Proxy element corrections
for item in an.get("proxy_list", []):
    name      = item["Name"]
    gid       = item["GlobalId"]
    suggested = get_suggested_type(name, "IfcBuildingElementProxy")
    conf      = confidence_score(name, suggested)
    psets     = pset_suggestions(suggested)
    corrections.append({
        "GlobalId":        gid,
        "Element Name":    name,
        "Current Type":    "IfcBuildingElementProxy",
        "Suggested Type":  suggested,
        "Confidence":      conf,
        "Issue":           "Generic proxy — semantic meaning lost",
        "Action":          f"Reclassify to {suggested}",
        "Add Psets":       ", ".join(psets),
        "IFC Edit":        ifc_correction_steps("IfcBuildingElementProxy", suggested),
        "category":        "proxy",
    })

# 2. Walls missing Pset corrections
for item in an.get("missing_pset_list", []):
    name = item["Wall Name"]
    gid  = item["GlobalId"]
    corrections.append({
        "GlobalId":       gid,
        "Element Name":   name,
        "Current Type":   "IfcWall",
        "Suggested Type": "IfcWall",
        "Confidence":     100,
        "Issue":          "Missing Pset_WallCommon property set",
        "Action":         "Add Pset_WallCommon with required properties",
        "Add Psets":      "Pset_WallCommon",
        "IFC Edit":       (
            "Add a new IfcPropertySet named 'Pset_WallCommon' and link it to this wall "
            "via IfcRelDefinesByProperties. Required properties: IsExternal, LoadBearing, "
            "FireRating, AcousticRating, ThermalTransmittance."
        ),
        "category":       "missing_pset",
    })

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛠️ Correction Summary")
    proxy_fixes = sum(1 for c in corrections if c["category"] == "proxy")
    pset_fixes  = sum(1 for c in corrections if c["category"] == "missing_pset")
    high_conf   = sum(1 for c in corrections if c["Confidence"] >= 80)
    med_conf    = sum(1 for c in corrections if 50 <= c["Confidence"] < 80)
    low_conf    = sum(1 for c in corrections if c["Confidence"] < 50)

    st.metric("Total Suggestions", len(corrections))
    st.metric("🔴 Proxy Reclassifications", proxy_fixes)
    st.metric("🟠 Pset Additions",          pset_fixes)
    st.markdown("---")
    st.markdown("**Confidence Breakdown**")
    st.markdown(f"🟢 High (≥80%)  : **{high_conf}**")
    st.markdown(f"🟡 Medium (50–79%): **{med_conf}**")
    st.markdown(f"🔴 Low (<50%)    : **{low_conf}**")
    st.markdown("---")
    st.markdown("**How to apply fixes:**")
    st.markdown(
        "1. Review each suggestion below\n"
        "2. Open your IFC file in a BIM tool (Revit, ArchiCAD, BlenderBIM)\n"
        "3. Apply the suggested type change or add the missing Pset\n"
        "4. Re-export and re-upload to verify"
    )

# ── Page header ────────────────────────────────────────────────────────────────
st.title("🛠️ Automated Correction Suggestions")
st.caption(
    "For every detected semantic issue, the system recommends the correct IFC classification "
    "and missing property sets — with confidence scores and step-by-step fix instructions."
)

if not corrections:
    st.success("✅ No issues detected — your IFC model is semantically clean!")
    st.stop()

# ── Top summary cards ──────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Issues",          len(corrections))
col2.metric("Proxy Reclassifications", proxy_fixes)
col3.metric("Missing Pset Fixes",    pset_fixes)
col4.metric("High Confidence Fixes", high_conf)

st.markdown("---")

# ── Filter bar ─────────────────────────────────────────────────────────────────
st.subheader("🔍 Filter & Explore Suggestions")
fcol1, fcol2, fcol3 = st.columns(3)
with fcol1:
    filter_type = st.selectbox("Issue Type", ["All", "Proxy Reclassification", "Missing Pset"])
with fcol2:
    filter_conf = st.selectbox("Confidence", ["All", "High (≥80%)", "Medium (50–79%)", "Low (<50%)"])
with fcol3:
    search_term = st.text_input("Search by name or GlobalId", placeholder="e.g. Wall_001 or 0A3...")

# Apply filters
filtered = corrections[:]
if filter_type == "Proxy Reclassification":
    filtered = [c for c in filtered if c["category"] == "proxy"]
elif filter_type == "Missing Pset":
    filtered = [c for c in filtered if c["category"] == "missing_pset"]

if filter_conf == "High (≥80%)":
    filtered = [c for c in filtered if c["Confidence"] >= 80]
elif filter_conf == "Medium (50–79%)":
    filtered = [c for c in filtered if 50 <= c["Confidence"] < 80]
elif filter_conf == "Low (<50%)":
    filtered = [c for c in filtered if c["Confidence"] < 50]

if search_term:
    s = search_term.lower()
    filtered = [c for c in filtered if s in c["Element Name"].lower() or s in c["GlobalId"].lower()]

st.caption(f"Showing **{len(filtered)}** of **{len(corrections)}** suggestions")

# ── Main table ─────────────────────────────────────────────────────────────────
st.subheader("📋 Correction Table")

if filtered:
    display_df = pd.DataFrame([{
        "Element Name":   c["Element Name"],
        "GlobalId":       c["GlobalId"],
        "Current Type":   c["Current Type"],
        "Suggested Type": c["Suggested Type"],
        "Confidence %":   c["Confidence"],
        "Issue":          c["Issue"],
        "Action":         c["Action"],
        "Add Psets":      c["Add Psets"],
    } for c in filtered])

    # Colour-code confidence with pandas Styler
    def colour_conf(val):
        if val >= 80:   return "background-color:#1a3a1a;color:#66cc66"
        elif val >= 50: return "background-color:#3a3a1a;color:#cccc66"
        else:           return "background-color:#3a1a1a;color:#cc6666"

    styled = display_df.style.applymap(colour_conf, subset=["Confidence %"])
    st.dataframe(styled, use_container_width=True, hide_index=True)
else:
    st.info("No suggestions match the current filters.")

st.markdown("---")

# ── Detailed cards per suggestion ─────────────────────────────────────────────
st.subheader("🔎 Detailed Fix Instructions")
st.caption("Expand each card to see exactly what to change in your IFC file.")

for i, c in enumerate(filtered[:50]):   # cap at 50 for performance
    conf = c["Confidence"]
    badge_color = "#238636" if conf >= 80 else "#d29922" if conf >= 50 else "#da3633"
    badge_label = "HIGH" if conf >= 80 else "MEDIUM" if conf >= 50 else "LOW"

    with st.expander(
        f"{'🔴' if c['category']=='proxy' else '🟠'}  "
        f"{c['Element Name']}  —  {c['Action']}  "
        f"[{badge_label} confidence: {conf}%]",
        expanded=False,
    ):
        d1, d2, d3 = st.columns(3)
        d1.markdown(f"**Element Name**\n\n`{c['Element Name']}`")
        d2.markdown(f"**GlobalId**\n\n`{c['GlobalId']}`")
        d3.markdown(
            f"**Confidence**\n\n"
            f"<span style='background:{badge_color}33;color:{badge_color};"
            f"padding:2px 10px;border-radius:4px;font-weight:700;"
            f"border:1px solid {badge_color}'>{badge_label} — {conf}%</span>",
            unsafe_allow_html=True,
        )

        st.markdown("---")
        e1, e2 = st.columns(2)
        with e1:
            st.markdown("**❌ Current (Problematic)**")
            st.code(c["Current Type"], language="text")
            st.markdown(f"*Issue:* {c['Issue']}")
        with e2:
            st.markdown("**✅ Suggested Fix**")
            st.code(c["Suggested Type"], language="text")
            st.markdown(f"*Action:* {c['Action']}")

        st.markdown("**📦 Recommended Property Sets to Add**")
        for pset in c["Add Psets"].split(", "):
            st.markdown(
                f"<span style='background:#1f6feb22;border:1px solid #1f6feb;"
                f"border-radius:4px;padding:2px 10px;font-size:13px;'>{pset}</span>&nbsp;",
                unsafe_allow_html=True,
            )

        st.markdown("**🔧 IFC File Edit Instruction**")
        st.info(c["IFC Edit"])

        # Pset_WallCommon property list
        if c["category"] == "missing_pset":
            st.markdown("**📝 Required Properties for Pset_WallCommon**")
            pset_props = pd.DataFrame({
                "Property":    ["IsExternal", "LoadBearing", "FireRating",
                                "AcousticRating", "ThermalTransmittance",
                                "Combustible", "SurfaceSpreadOfFlame"],
                "Type":        ["IfcBoolean", "IfcBoolean", "IfcLabel",
                                "IfcLabel", "IfcThermalTransmittanceMeasure",
                                "IfcBoolean", "IfcLabel"],
                "Description": [
                    "Is the wall an external (outer) wall?",
                    "Does the wall bear structural load?",
                    "Fire resistance rating (e.g. REI 60)",
                    "Sound insulation rating in dB",
                    "U-value in W/(m²·K)",
                    "Is the wall material combustible?",
                    "Surface spread of flame classification",
                ],
            })
            st.dataframe(pset_props, use_container_width=True, hide_index=True)

if len(filtered) > 50:
    st.caption(f"ℹ️ Showing first 50 of {len(filtered)} detailed cards. Use filters above to narrow down.")

st.markdown("---")

# ── Correction Statistics Chart ────────────────────────────────────────────────
st.subheader("📊 Suggested Type Distribution")

if proxy_fixes > 0:
    type_counts = {}
    for c in corrections:
        if c["category"] == "proxy":
            t = c["Suggested Type"]
            type_counts[t] = type_counts.get(t, 0) + 1

    if type_counts:
        chart_df = pd.DataFrame({
            "Suggested IFC Type": list(type_counts.keys()),
            "Count":              list(type_counts.values()),
        }).sort_values("Count", ascending=False)
        st.bar_chart(chart_df.set_index("Suggested IFC Type"))
else:
    st.info("No proxy reclassification data to chart.")

st.markdown("---")

# ── Export corrections as CSV ──────────────────────────────────────────────────
st.subheader("⬇️ Export Correction Report")

ecol1, ecol2 = st.columns(2)

with ecol1:
    if st.button("📥 Download CSV"):
        export_df = pd.DataFrame([{
            "Element Name":   c["Element Name"],
            "GlobalId":       c["GlobalId"],
            "Current Type":   c["Current Type"],
            "Suggested Type": c["Suggested Type"],
            "Confidence %":   c["Confidence"],
            "Issue":          c["Issue"],
            "Action":         c["Action"],
            "Add Psets":      c["Add Psets"],
            "IFC Edit":       c["IFC Edit"],
        } for c in corrections])
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="⬇️ Click to download CSV",
            data=csv,
            file_name="IFC_Correction_Suggestions.csv",
            mime="text/csv",
        )

with ecol2:
    if st.button("📄 Download PDF Report"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "IFC Correction Suggestions Report", ln=True, align="C")
        pdf.ln(6)
        pdf.set_font("Arial", size=11)
        ctx = st.session_state.get("user_context", {})
        pdf.multi_cell(0, 7, f"Role: {ctx.get('role','N/A')}  |  Domain: {ctx.get('domain','N/A')}  |  Purpose: {ctx.get('purpose','N/A')}")
        pdf.ln(4)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Total Suggestions: {len(corrections)}  |  Proxy: {proxy_fixes}  |  Missing Pset: {pset_fixes}", ln=True)
        pdf.ln(4)
        for i, c in enumerate(corrections, 1):
            pdf.set_font("Arial", "B", 11)
            pdf.multi_cell(0, 7, f"{i}. {c['Element Name']} ({c['Current Type']})")
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 6, f"   GlobalId   : {c['GlobalId']}")
            pdf.multi_cell(0, 6, f"   Issue      : {c['Issue']}")
            pdf.multi_cell(0, 6, f"   Suggestion : {c['Suggested Type']}")
            pdf.multi_cell(0, 6, f"   Confidence : {c['Confidence']}%")
            pdf.multi_cell(0, 6, f"   Add Psets  : {c['Add Psets']}")
            pdf.multi_cell(0, 6, f"   Fix        : {c['IFC Edit']}")
            pdf.ln(3)
        path = "IFC_Correction_Suggestions.pdf"
        pdf.output(path)
        with open(path, "rb") as f:
            st.download_button(
                label="⬇️ Click to download PDF",
                data=f,
                file_name="IFC_Correction_Suggestions.pdf",
                mime="application/pdf",
            )
