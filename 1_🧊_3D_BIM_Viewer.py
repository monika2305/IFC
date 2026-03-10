import streamlit as st
import ifcopenshell
import pandas as pd
import json
import math
import time as _time

st.set_page_config(page_title="3D BIM Viewer", page_icon="🧊", layout="wide")

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


if not st.session_state.get("logged_in"):
    st.warning("Please log in from the Home page first.")
    st.stop()

try:
    model = ifcopenshell.open("temp.ifc")
except Exception:
    st.warning("No IFC file found. Please upload on the Home page first.")
    st.stop()

an = st.session_state.get("analysis", {})

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Analysis Summary")
    if an:
        sev = an.get("severity", "—")
        sev_color = {"LOW":"#238636","MEDIUM":"#1f6feb","HIGH":"#d29922","CRITICAL":"#da3633"}.get(sev,"#8b949e")
        q_score = an.get("quality_score", "—")
        q_grade = an.get("quality_grade", "—")
        q_col   = an.get("quality_color", "#8b949e")
        st.markdown(
            f'<div style="background:{sev_color}22;border:1px solid {sev_color};'
            f'border-radius:8px;padding:8px 14px;margin-bottom:6px;text-align:center;">'
            f'<div style="font-size:10px;color:#8b949e;letter-spacing:1px;">SEVERITY</div>'
            f'<span style="font-weight:700;color:{sev_color};font-size:15px">⚠ {sev}</span></div>',
            unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:{q_col}22;border:1px solid {q_col};'
            f'border-radius:8px;padding:8px 14px;margin-bottom:12px;text-align:center;">'
            f'<div style="font-size:10px;color:#8b949e;letter-spacing:1px;">QUALITY SCORE</div>'
            f'<span style="font-weight:700;color:{q_col};font-size:15px">⭐ {q_score}/100</span>'
            f'<div style="font-size:11px;color:{q_col}">{q_grade}</div></div>',
            unsafe_allow_html=True)
        st.markdown("**📈 Key Metrics**")
        c1, c2 = st.columns(2)
        c1.metric("Total",    an.get("total_elements","—"))
        c2.metric("Semantic", f"{an.get('semantic_pct',0):.1f}%")
        c1.metric("Proxy",    f"{an.get('proxy_pct',0):.1f}%")
        c2.metric("Other",    f"{an.get('other_pct',0):.1f}%")
        st.markdown("---")
        st.markdown("**🧱 Element Classification**")
        st.dataframe(pd.DataFrame({
            "Element Type": ["Walls","Doors","Windows","Proxies","Other"],
            "Count": [an.get("total_walls",0), an.get("doors",0), an.get("windows",0),
                      an.get("proxy_elements",0), an.get("other_semantic",0)],
        }), use_container_width=True, hide_index=True)
        st.markdown("---")
        proxy_list = an.get("proxy_list", [])
        st.markdown(f"**🔴 Proxy Elements ({len(proxy_list)})**")
        if proxy_list:
            with st.expander("View all proxy elements"):
                st.dataframe(pd.DataFrame(proxy_list), use_container_width=True, hide_index=True)
        else:
            st.success("✅ No proxy elements detected")
        pset_list = an.get("missing_pset_list", [])
        st.markdown(f"**🟠 Walls Missing Pset ({len(pset_list)})**")
        if pset_list:
            with st.expander("View walls missing Pset_WallCommon"):
                st.dataframe(pd.DataFrame(pset_list), use_container_width=True, hide_index=True)
        else:
            st.success("✅ All walls have Pset_WallCommon")
    else:
        st.info("No analysis data. Upload an IFC on the Home page.")

# ── Issue sets ─────────────────────────────────────────────────────────────────
proxies = model.by_type("IfcBuildingElementProxy")
proxy_ids = set(p.GlobalId for p in proxies)

walls_missing_pset = []
for wall in model.by_type("IfcWall"):
    has_pset = any(
        d.is_a("IfcRelDefinesByProperties") and
        getattr(d, "RelatingPropertyDefinition", None) and
        d.RelatingPropertyDefinition.is_a("IfcPropertySet") and
        d.RelatingPropertyDefinition.Name == "Pset_WallCommon"
        for d in getattr(wall, "IsDefinedBy", [])
    )
    if not has_pset:
        walls_missing_pset.append(wall)
missing_pset_ids = set(w.GlobalId for w in walls_missing_pset)

SKIP = {
    "IfcSpace","IfcOpeningElement","IfcVirtualElement","IfcAnnotation",
    "IfcGrid","IfcSite","IfcBuilding","IfcBuildingStorey","IfcProject",
    "IfcRelAggregates","IfcZone","IfcSpatialZone",
}

def resolve_placement(elem):
    x = y = z = 0.0
    try:
        pl = getattr(elem, "ObjectPlacement", None)
        while pl:
            rel = getattr(pl, "RelativePlacement", None)
            if rel:
                loc = getattr(rel, "Location", None)
                if loc:
                    c = loc.Coordinates
                    x += float(c[0]) if len(c)>0 else 0.0
                    y += float(c[1]) if len(c)>1 else 0.0
                    z += float(c[2]) if len(c)>2 else 0.0
            pl = getattr(pl, "PlacementRelTo", None)
    except Exception:
        pass
    return x, y, z

def get_dims(t):
    t = t.lower()
    if "curtainwall" in t: return ("wall",   6.0, 3.5, 0.08)
    if "wall"        in t: return ("wall",   6.0, 3.0, 0.25)
    if "door"        in t: return ("door",   1.0, 2.2, 0.12)
    if "window"      in t: return ("window", 1.4, 1.2, 0.10)
    if "slab"        in t: return ("slab",   8.0, 0.25,8.0)
    if "floor"       in t: return ("slab",   6.0, 0.20,6.0)
    if "roof"        in t: return ("roof",  10.0, 0.45,10.0)
    if "column"      in t: return ("column", 0.4, 3.5, 0.4)
    if "beam"        in t: return ("beam",   5.0, 0.4, 0.3)
    if "stair"       in t: return ("stair",  2.5, 2.8, 1.6)
    if "ramp"        in t: return ("slab",   4.0, 0.2, 3.0)
    if "railing"     in t: return ("beam",   3.0, 1.0, 0.1)
    if "proxy"       in t: return ("proxy",  1.2, 2.0, 1.2)
    return ("proxy", 1.0, 1.5, 1.0)

# ── Collect elements ───────────────────────────────────────────────────────────
raw = []
for elem in list(model.by_type("IfcProduct"))[:600]:
    if elem.is_a() in SKIP:
        continue
    try:
        gid  = elem.GlobalId
        name = getattr(elem, "Name", None) or "Unnamed"
        dims = get_dims(elem.is_a())
        if not dims: continue
        shape, w, h, d = dims
        x, y, z = resolve_placement(elem)
        if gid in proxy_ids:
            issue, label = "proxy",        "Semantic meaning lost (generic proxy)"
        elif gid in missing_pset_ids:
            issue, label = "missing_pset", "Missing Pset_WallCommon"
        else:
            issue, label = "ok",           "No issues detected"
        raw.append({"id":gid,"name":name,"type":elem.is_a(),
                    "shape":shape,"x":x,"y":y,"z":z,
                    "w":w,"h":h,"d":d,"issue":issue,"issue_label":label})
    except Exception:
        continue

# ── Scale mm → m ──────────────────────────────────────────────────────────────
if raw:
    xs = [r["x"] for r in raw]
    zs = [r["z"] for r in raw]
    spread = max(max(xs)-min(xs), max(zs)-min(zs)) if xs else 0
    if spread > 500:
        for r in raw:
            r["x"] /= 1000.0; r["y"] /= 1000.0; r["z"] /= 1000.0
        xs = [r["x"] for r in raw]
        zs = [r["z"] for r in raw]
        spread = max(max(xs)-min(xs), max(zs)-min(zs))
    has_spread = spread > 0.5
else:
    has_spread = False

# ── Procedural building layout if no real coords ───────────────────────────────
if not has_spread and raw:
    FH = 3.5
    layout = [
        # Ground floor
        ("slab",   0,    -0.13, 0,    12.0, 0.25, 8.0),
        ("wall",   0,    0,    -4.0,  12.0, FH,   0.25),
        ("wall",   0,    0,     4.0,  12.0, FH,   0.25),
        ("wall",  -6.0,  0,     0,    0.25, FH,   8.0),
        ("wall",   6.0,  0,     0,    0.25, FH,   8.0),
        ("wall",   0,    0,     0,    0.25, FH,   8.0),  # interior wall
        ("column",-5.5,  0,    -3.5,  0.4,  FH,   0.4),
        ("column", 5.5,  0,    -3.5,  0.4,  FH,   0.4),
        ("column",-5.5,  0,     3.5,  0.4,  FH,   0.4),
        ("column", 5.5,  0,     3.5,  0.4,  FH,   0.4),
        ("column", 0,    0,    -3.5,  0.4,  FH,   0.4),
        ("column", 0,    0,     3.5,  0.4,  FH,   0.4),
        ("beam",   0,    FH-0.35,-3.8, 12.0, 0.4,  0.3),
        ("beam",   0,    FH-0.35, 3.8, 12.0, 0.4,  0.3),
        ("beam",  -5.5,  FH-0.35, 0,   0.3,  0.4,  8.0),
        ("beam",   5.5,  FH-0.35, 0,   0.3,  0.4,  8.0),
        ("door",  -2.5,  0,    -4.0,  0.12, 2.2,  1.0),
        ("door",   2.5,  0,    -4.0,  0.12, 2.2,  1.0),
        ("window",-4.5,  1.1,  -4.0,  0.1,  1.2,  1.4),
        ("window", 4.5,  1.1,  -4.0,  0.1,  1.2,  1.4),
        ("window",-4.5,  1.1,   4.0,  0.1,  1.2,  1.4),
        ("window", 4.5,  1.1,   4.0,  0.1,  1.2,  1.4),
        ("window",-4.5,  1.1,  -6.0,  1.4,  1.2,  0.1),
        ("window", 4.5,  1.1,  -6.0,  1.4,  1.2,  0.1),
        ("stair",  7.5,  0,     0,    2.5,  FH,   1.8),
        # First floor
        ("slab",   0,    FH,    0,    12.0, 0.25, 8.0),
        ("wall",   0,    FH+0.25,-4.0, 12.0, FH,   0.25),
        ("wall",   0,    FH+0.25, 4.0, 12.0, FH,   0.25),
        ("wall",  -6.0,  FH+0.25, 0,   0.25, FH,   8.0),
        ("wall",   6.0,  FH+0.25, 0,   0.25, FH,   8.0),
        ("column",-5.5,  FH+0.25,-3.5, 0.4,  FH,   0.4),
        ("column", 5.5,  FH+0.25,-3.5, 0.4,  FH,   0.4),
        ("column",-5.5,  FH+0.25, 3.5, 0.4,  FH,   0.4),
        ("column", 5.5,  FH+0.25, 3.5, 0.4,  FH,   0.4),
        ("window",-4.5,  FH+1.4, -4.0, 0.1,  1.2,  1.4),
        ("window", 4.5,  FH+1.4, -4.0, 0.1,  1.2,  1.4),
        ("window",-4.5,  FH+1.4,  4.0, 0.1,  1.2,  1.4),
        ("window", 4.5,  FH+1.4,  4.0, 0.1,  1.2,  1.4),
        ("beam",   0,    FH*2-0.35,-3.8,12.0, 0.4,  0.3),
        ("beam",   0,    FH*2-0.35, 3.8,12.0, 0.4,  0.3),
        # Roof
        ("slab",   0,    FH*2,  0,    12.5, 0.25, 8.5),
        ("roof",   0,    FH*2+0.25,0, 12.5, 0.6,  8.5),
    ]
    for i, r in enumerate(raw):
        if i < len(layout):
            s,px,py,pz,pw,ph,pd = layout[i]
            r["shape"]=s; r["x"]=px; r["y"]=py; r["z"]=pz
            r["w"]=pw; r["h"]=ph; r["d"]=pd
        else:
            col=(i-len(layout))%8; row=(i-len(layout))//8
            r["x"]=col*2.0-7; r["y"]=0; r["z"]=5.5+row*2.0

elements_3d = [{
    "id":r["id"],"name":r["name"],"type":r["type"],
    "shape":r["shape"],"issue":r["issue"],"issue_label":r["issue_label"],
    "x":round(r["x"],3),"y":round(r["y"],3),"z":round(r["z"],3),
    "w":r["w"],"h":r["h"],"d":r["d"],
} for r in raw]

issue_counts = {
    "proxy":        sum(1 for e in elements_3d if e["issue"]=="proxy"),
    "missing_pset": sum(1 for e in elements_3d if e["issue"]=="missing_pset"),
    "ok":           sum(1 for e in elements_3d if e["issue"]=="ok"),
}
total_3d=len(elements_3d)
proxy_c=issue_counts["proxy"]; pset_c=issue_counts["missing_pset"]; ok_c=issue_counts["ok"]

st.title("🧊 3D BIM Building Viewer")
st.caption("🔴 Proxy · 🟠 Missing Pset · 🔵 Normal  |  Left-drag: rotate · Right-drag: pan · Scroll: zoom · Click: select")

m1,m2,m3,m4 = st.columns(4)
m1.metric("Total Elements", total_3d)
m2.metric("🔴 Proxy",       proxy_c)
m3.metric("🟠 Missing Pset",pset_c)
m4.metric("🔵 Normal",      ok_c)

if not has_spread:
    st.info("ℹ️ IFC has no spread geometry — showing procedural building with your elements.")

# ══════════════════════════════════════════════════════════════════════════════
# PURE CANVAS 2D RENDERER — no CDN, no external libs, works everywhere
# Isometric-perspective 3D with per-face lighting, depth sorting, glow effects
# ══════════════════════════════════════════════════════════════════════════════
HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
html,body { width:100%; height:100%; background:#0a0e17; overflow:hidden; }
#app { width:100vw; height:100vh; display:flex; flex-direction:column; }

#toolbar {
  flex-shrink:0;
  display:flex; align-items:center; gap:8px; flex-wrap:wrap;
  padding:7px 12px;
  background:rgba(10,14,23,0.95);
  border-bottom:1px solid #1e2733;
  font-family:'Segoe UI',system-ui,sans-serif; font-size:12px; color:#e6edf3;
}
.leg {
  display:flex; align-items:center; gap:5px;
  padding:3px 10px; border-radius:18px; cursor:pointer;
  border:1px solid transparent; user-select:none; transition:border-color .15s;
}
.leg.on  { border-color:currentColor; }
.leg:hover { border-color:#58a6ff; }
.dot { width:9px; height:9px; border-radius:2px; flex-shrink:0; }
.dp  { background:#ff4444; box-shadow:0 0 5px #ff4444; }
.dm  { background:#ff9500; box-shadow:0 0 5px #ff9500; }
.dok { background:#4fc3f7; box-shadow:0 0 5px #4fc3f7; }
.badge { background:#161b22; padding:1px 7px; border-radius:8px; font-size:11px; font-weight:700; }
#ctrls { margin-left:auto; display:flex; gap:6px; }
.btn {
  background:#161b22; border:1px solid #30363d; color:#e6edf3;
  padding:4px 11px; border-radius:6px; cursor:pointer; font-size:11px;
  transition:all .15s; font-family:inherit;
}
.btn:hover  { background:#21262d; border-color:#58a6ff; }
.btn.on { background:#1f3a6e; border-color:#58a6ff; color:#79c0ff; }

#cvs-wrap { flex:1; position:relative; }
canvas { display:block; cursor:grab; }
canvas:active { cursor:grabbing; }

#tip {
  position:absolute; pointer-events:none; display:none;
  background:#0d1117f5; border:1px solid #30363d;
  border-radius:9px; padding:10px 14px; font-size:12px;
  font-family:'Segoe UI',system-ui,sans-serif; color:#e6edf3;
  max-width:260px; box-shadow:0 6px 24px #000a; z-index:10;
}
.tt { color:#8b949e; font-size:11px; margin-bottom:2px; }
.tn { font-weight:700; font-size:13px; margin-bottom:4px; }
.ti { color:#8b949e; font-size:10px; margin-bottom:5px; font-family:monospace; }
.tb { display:inline-block; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700; }
.bp { background:#ff444422; color:#ff6b6b; border:1px solid #ff4444; }
.bm { background:#ff950022; color:#ffb347; border:1px solid #ff9500; }
.bo { background:#4fc3f722; color:#7dd3fc; border:1px solid #4fc3f7; }

#stats {
  position:absolute; bottom:12px; right:12px;
  background:#0d1117ee; border:1px solid #30363d;
  border-radius:9px; padding:10px 14px;
  font-family:'Segoe UI',system-ui,sans-serif; font-size:12px; color:#e6edf3;
  min-width:150px;
}
#stats h4 { font-size:11px; color:#8b949e; margin-bottom:7px; text-transform:uppercase; letter-spacing:.6px; }
.sr { display:flex; justify-content:space-between; margin-bottom:4px; }
.sl { color:#8b949e; }
.sv { font-weight:700; }

#hint {
  position:absolute; bottom:12px; left:50%; transform:translateX(-50%);
  background:#0d1117cc; border:1px solid #30363d44;
  border-radius:6px; padding:4px 12px;
  font-family:'Segoe UI',system-ui,sans-serif; font-size:11px; color:#8b949e;
  pointer-events:none; white-space:nowrap;
}
</style>
</head>
<body>
<div id="app">
<div id="toolbar">
  <div class="leg on" id="lp" onclick="toggleF('proxy')">
    <div class="dot dp"></div><span style="color:#ff6b6b">Proxy</span>
    <span class="badge" style="color:#ff6b6b" id="bp-c">0</span>
  </div>
  <div class="leg on" id="lm" onclick="toggleF('missing_pset')">
    <div class="dot dm"></div><span style="color:#ffb347">Missing Pset</span>
    <span class="badge" style="color:#ffb347" id="bm-c">0</span>
  </div>
  <div class="leg on" id="lo" onclick="toggleF('ok')">
    <div class="dot dok"></div><span style="color:#7dd3fc">Normal</span>
    <span class="badge" style="color:#7dd3fc" id="bo-c">0</span>
  </div>
  <div id="ctrls">
    <button class="btn" onclick="fitAll()">⛶ Fit All</button>
    <button class="btn" onclick="focusIssues()">🎯 Issues</button>
    <button class="btn" id="wb" onclick="toggleWire()">⬡ Wire</button>
    <button class="btn" id="xb" onclick="toggleXray()">👁 X-Ray</button>
    <button class="btn" id="eb" onclick="toggleExplode()">💥 Explode</button>
  </div>
</div>

<div id="cvs-wrap">
  <canvas id="c"></canvas>

  <div id="tip">
    <div class="tt" id="t-tp"></div>
    <div class="tn"  id="t-nm"></div>
    <div class="ti"  id="t-id"></div>
    <div class="tb"  id="t-bg"></div>
  </div>

  <div id="stats">
    <h4>🏗 Scene</h4>
    <div class="sr"><span class="sl">Total</span>  <span class="sv" id="s-tot">0</span></div>
    <div class="sr"><span class="sl">Visible</span><span class="sv" id="s-vis">0</span></div>
    <div class="sr"><span class="sl">Issues</span> <span class="sv" style="color:#ff6b6b" id="s-iss">0</span></div>
    <div class="sr"><span class="sl">Selected</span><span class="sv" style="color:#ffe066;font-size:11px" id="s-sel">—</span></div>
  </div>

  <div id="hint">Left-drag: rotate &nbsp;·&nbsp; Right-drag: pan &nbsp;·&nbsp; Scroll: zoom &nbsp;·&nbsp; Click: select</div>
</div>
</div>

<script>
// ── DATA ──────────────────────────────────────────────────────────────────────
const ELEMS = ELEMENTS_JSON_PLACEHOLDER;

// ── Canvas setup ──────────────────────────────────────────────────────────────
const wrap = document.getElementById('cvs-wrap');
const cv   = document.getElementById('c');
const ctx  = cv.getContext('2d');

function resize() {
  const w = wrap.offsetWidth  || window.innerWidth;
  const h = wrap.offsetHeight || (window.innerHeight - 50);
  cv.width  = w;
  cv.height = h;
  draw();
}
window.addEventListener('resize', resize);

// ── Camera ────────────────────────────────────────────────────────────────────
let cam = { rotX: 0.52, rotY: 0.60, zoom: 1.0, panX: 0, panY: 0 };

// Compute scene centre & radius
let sceneC = {x:0,y:0,z:0};
if (ELEMS.length) {
  ELEMS.forEach(e => { sceneC.x+=e.x; sceneC.y+=e.y+e.h/2; sceneC.z+=e.z; });
  sceneC.x/=ELEMS.length; sceneC.y/=ELEMS.length; sceneC.z/=ELEMS.length;
}
let sceneR = 1;
ELEMS.forEach(e => {
  const dx=e.x-sceneC.x, dy=(e.y+e.h/2)-sceneC.y, dz=e.z-sceneC.z;
  sceneR = Math.max(sceneR, Math.sqrt(dx*dx+dy*dy+dz*dz) + Math.max(e.w,e.h,e.d)/2);
});

// ── 3D → 2D projection (centred on scene) ─────────────────────────────────────
function project(wx, wy, wz) {
  // translate to scene centre
  const x = wx - sceneC.x;
  const y = wy - sceneC.y;
  const z = wz - sceneC.z;
  // Rotate Y
  const cY = Math.cos(cam.rotY), sY = Math.sin(cam.rotY);
  const rx =  x*cY - z*sY;
  const rz =  x*sY + z*cY;
  // Rotate X
  const cX = Math.cos(cam.rotX), sX = Math.sin(cam.rotX);
  const ry =  y*cX - rz*sX;
  const rzz= y*sX + rz*cX;
  // Perspective
  const fov  = Math.min(cv.width, cv.height) * 0.82 * cam.zoom;
  const dist = rzz + sceneR * 2.8 + 0.001;
  return {
    sx: rx/dist*fov + cv.width/2  + cam.panX,
    sy:-ry/dist*fov + cv.height/2 + cam.panY,
    depth: rzz
  };
}

// ── Colours ───────────────────────────────────────────────────────────────────
const BASE_COLORS = {
  wall:   '#4a8fc0',  slab:   '#8a7050',
  column: '#3d8a4a',  beam:   '#2d7a3a',
  door:   '#804060',  window: '#1a7888',
  stair:  '#7a5535',  roof:   '#6a5030',
  ramp:   '#557755',  proxy:  '#446688',
};
const ISSUE_COLORS = { proxy:'#cc2222', missing_pset:'#bb5500' };

function faceColor(base, lightFactor, alpha=1) {
  const r = parseInt(base.slice(1,3),16);
  const g = parseInt(base.slice(3,5),16);
  const b = parseInt(base.slice(5,7),16);
  const ri = Math.min(255, (r*lightFactor)|0);
  const gi = Math.min(255, (g*lightFactor)|0);
  const bi = Math.min(255, (b*lightFactor)|0);
  return alpha<1 ? `rgba(${ri},${gi},${bi},${alpha})` : `rgb(${ri},${gi},${bi})`;
}

// ── State ─────────────────────────────────────────────────────────────────────
let filters  = { proxy:true, missing_pset:true, ok:true };
let wireMode = false;
let xrayMode = false;
let explodeAmt= 0, explodeTgt=0;
let selId    = null;
let hovId    = null;
let tick     = 0;

// ── Draw one building element ─────────────────────────────────────────────────
function drawElem(e, explodeExtra) {
  const { x, y, z, w, h, d, shape, issue } = e;
  const hw = w/2, hd = d/2;

  const ey = y + explodeExtra;           // explode offset

  // 8 corners of the box
  const C = [
    [x-hw, ey,   z-hd], [x+hw, ey,   z-hd],
    [x+hw, ey,   z+hd], [x-hw, ey,   z+hd],
    [x-hw, ey+h, z-hd], [x+hw, ey+h, z-hd],
    [x+hw, ey+h, z+hd], [x-hw, ey+h, z+hd],
  ];
  const P = C.map(([a,b,c]) => project(a,b,c));

  // 6 faces: {indices, normal light, isTop}
  const FACES = [
    { v:[4,5,6,7], li:1.00 },   // top
    { v:[0,1,2,3], li:0.18 },   // bottom
    { v:[0,1,5,4], li:0.55 },   // front (z-)
    { v:[2,3,7,6], li:0.40 },   // back  (z+)
    { v:[1,2,6,5], li:0.80 },   // right (x+)
    { v:[0,3,7,4], li:0.35 },   // left  (x-)
  ];

  // depth = centre z of each face
  const sorted = FACES.map(f => {
    const depthSum = f.v.reduce((s,i)=>s+P[i].depth,0)/4;
    return { ...f, depth: depthSum };
  }).sort((a,b) => b.depth-a.depth);   // back to front

  const baseHex = ISSUE_COLORS[issue] || BASE_COLORS[shape] || '#446688';
  const isIssue = issue !== 'ok';
  const isSel   = selId === e.id;
  const isHov   = hovId === e.id;

  // X-ray: reduce normal elements' opacity
  const alpha = xrayMode && !isIssue ? 0.12 : 1.0;
  // Window is always semi-transparent
  const winAlpha = shape==='window' ? (xrayMode ? 0.12 : 0.45) : alpha;
  const elemAlpha = shape==='window' ? winAlpha : alpha;

  for (const f of sorted) {
    const pts = f.v.map(i => P[i]);
    ctx.beginPath();
    ctx.moveTo(pts[0].sx, pts[0].sy);
    for (let i=1;i<pts.length;i++) ctx.lineTo(pts[i].sx, pts[i].sy);
    ctx.closePath();

    if (!wireMode) {
      ctx.fillStyle = faceColor(baseHex, f.li, elemAlpha);
      ctx.fill();
    }

    // Edge style
    if (isSel) {
      ctx.strokeStyle = '#ffe066'; ctx.lineWidth = 1.8;
    } else if (isHov) {
      ctx.strokeStyle = '#ffffff99'; ctx.lineWidth = 1.2;
    } else if (wireMode) {
      ctx.strokeStyle = baseHex + 'cc'; ctx.lineWidth = 0.8;
    } else {
      ctx.strokeStyle = '#ffffff0d'; ctx.lineWidth = 0.4;
    }
    ctx.stroke();
  }

  // Glow ring for issue elements
  if (isIssue && !xrayMode) {
    const glowColor = issue==='proxy' ? '#ff3333' : '#ff8800';
    const pulse = 0.25 + 0.15*Math.sin(tick*0.07*(e.id.charCodeAt(0)||1));
    ctx.strokeStyle = glowColor;
    ctx.lineWidth   = 1.5;
    ctx.globalAlpha = pulse;
    // draw outline of top face
    const pts = FACES[0].v.map(i => P[i]);
    ctx.beginPath();
    ctx.moveTo(pts[0].sx, pts[0].sy);
    pts.forEach(p => ctx.lineTo(p.sx, p.sy));
    ctx.closePath();
    ctx.stroke();
    ctx.globalAlpha = 1.0;
  }

  // Selected highlight flash
  if (isSel) {
    ctx.globalAlpha = 0.15;
    ctx.fillStyle = '#ffe066';
    const pts = FACES[0].v.map(i => P[i]);
    ctx.beginPath(); ctx.moveTo(pts[0].sx, pts[0].sy);
    pts.forEach(p=>ctx.lineTo(p.sx,p.sy)); ctx.closePath(); ctx.fill();
    ctx.globalAlpha = 1.0;
  }
}

// ── Draw grid floor ───────────────────────────────────────────────────────────
function drawGrid() {
  const gs   = sceneR * 1.6;
  const step = Math.max(0.5, (gs/10));
  ctx.strokeStyle = '#1e2a1e';
  ctx.lineWidth   = 0.5;
  for (let i=-gs; i<=gs; i+=step) {
    const a = project(sceneC.x+i, 0, sceneC.z-gs);
    const b = project(sceneC.x+i, 0, sceneC.z+gs);
    const c = project(sceneC.x-gs,0, sceneC.z+i);
    const d = project(sceneC.x+gs,0, sceneC.z+i);
    ctx.beginPath(); ctx.moveTo(a.sx,a.sy); ctx.lineTo(b.sx,b.sy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(c.sx,c.sy); ctx.lineTo(d.sx,d.sy); ctx.stroke();
  }
  // XYZ axes
  const o  = project(sceneC.x, 0, sceneC.z);
  const ax = project(sceneC.x+3, 0, sceneC.z);
  const ay = project(sceneC.x, 3, sceneC.z);
  const az = project(sceneC.x, 0, sceneC.z+3);
  [['#ff4444',ax],['#44cc66',ay],['#4488ff',az]].forEach(([col,p])=>{
    ctx.strokeStyle=col; ctx.lineWidth=1.5;
    ctx.beginPath(); ctx.moveTo(o.sx,o.sy); ctx.lineTo(p.sx,p.sy); ctx.stroke();
  });
}

// ── Explode offset per element ────────────────────────────────────────────────
function explodeOffset(e) {
  return e.y * explodeAmt * 0.55;
}

// ── Main draw loop ────────────────────────────────────────────────────────────
function draw() {
  ctx.clearRect(0, 0, cv.width, cv.height);

  // Background gradient
  const bg = ctx.createLinearGradient(0,0,0,cv.height);
  bg.addColorStop(0,'#0a0e17'); bg.addColorStop(1,'#0d1520');
  ctx.fillStyle=bg; ctx.fillRect(0,0,cv.width,cv.height);

  drawGrid();

  // Filter & depth-sort elements
  const visible = ELEMS.filter(e => filters[e.issue]);
  visible
    .map(e => ({ e, depth: project(e.x, e.y+e.h/2, e.z+explodeOffset(e)).depth }))
    .sort((a,b) => b.depth - a.depth)
    .forEach(({e}) => drawElem(e, explodeOffset(e)));

  // Stats
  const issCount = visible.filter(e=>e.issue!=='ok').length;
  document.getElementById('s-vis').textContent = visible.length;
  document.getElementById('s-iss').textContent = issCount;
}

// ── Animation loop ────────────────────────────────────────────────────────────
function animate() {
  tick++;
  // Smooth explode
  if (Math.abs(explodeAmt-explodeTgt) > 0.005) {
    explodeAmt += (explodeTgt-explodeAmt)*0.1;
    draw();
  } else if (tick%3===0) {
    // Redraw occasionally for glow pulse
    draw();
  }
  requestAnimationFrame(animate);
}

// ── Hit test ──────────────────────────────────────────────────────────────────
function pip(px,py,poly) {
  let ins=false;
  for(let i=0,j=poly.length-1;i<poly.length;j=i++){
    const xi=poly[i].sx,yi=poly[i].sy,xj=poly[j].sx,yj=poly[j].sy;
    if(((yi>py)!==(yj>py))&&(px<(xj-xi)*(py-yi)/(yj-yi)+xi)) ins=!ins;
  }
  return ins;
}

function hitTest(mx,my) {
  const visible = ELEMS.filter(e=>filters[e.issue]);
  const sorted  = visible
    .map(e=>({e,depth:project(e.x,e.y+e.h/2,e.z+explodeOffset(e)).depth}))
    .sort((a,b)=>a.depth-b.depth);

  for (const {e} of sorted) {
    const {x,y,z,w,h,d} = e;
    const ey = y+explodeOffset(e);
    const hw=w/2, hd=d/2;
    const C = [
      [x-hw,ey,  z-hd],[x+hw,ey,  z-hd],[x+hw,ey,  z+hd],[x-hw,ey,  z+hd],
      [x-hw,ey+h,z-hd],[x+hw,ey+h,z-hd],[x+hw,ey+h,z+hd],[x-hw,ey+h,z+hd],
    ];
    const P = C.map(([a,b,c])=>project(a,b,c));
    const faces = [[0,1,5,4],[0,1,2,3],[4,5,6,7],[1,2,6,5],[0,3,7,4],[2,3,7,6]];
    if (faces.some(f => pip(mx,my,f.map(i=>P[i])))) return e;
  }
  return null;
}

// ── Mouse events ──────────────────────────────────────────────────────────────
let isDrag=false, isPan=false, lm={x:0,y:0};

cv.addEventListener('mousedown', e=>{
  if(e.button===0) isDrag=true;
  if(e.button===2) isPan =true;
  lm={x:e.clientX,y:e.clientY};
});
cv.addEventListener('contextmenu',e=>e.preventDefault());

cv.addEventListener('mousemove', e=>{
  const dx=e.clientX-lm.x, dy=e.clientY-lm.y;
  if(isDrag){
    cam.rotY += dx*0.006;
    cam.rotX  = Math.max(-Math.PI/2+0.05, Math.min(Math.PI/2-0.05, cam.rotX+dy*0.006));
    draw();
  } else if(isPan){
    cam.panX+=dx; cam.panY+=dy; draw();
  } else {
    doHover(e);
  }
  lm={x:e.clientX,y:e.clientY};
});
cv.addEventListener('mouseup',   ()=>{ isDrag=false; isPan=false; });
cv.addEventListener('mouseleave',()=>{ isDrag=false; isPan=false; clearTip(); });

cv.addEventListener('wheel', e=>{
  e.preventDefault();
  cam.zoom = Math.max(0.05, Math.min(15, cam.zoom*(e.deltaY>0?0.92:1.09)));
  draw();
},{passive:false});

cv.addEventListener('click', e=>{
  const rect = cv.getBoundingClientRect();
  const hit  = hitTest(e.clientX-rect.left, e.clientY-rect.top);
  selId = hit ? (selId===hit.id?null:hit.id) : null;
  document.getElementById('s-sel').textContent = selId
    ? (ELEMS.find(el=>el.id===selId)?.name||selId.slice(0,10)) : '—';
  draw();
});

// ── Hover tooltip ─────────────────────────────────────────────────────────────
function doHover(e) {
  const rect = cv.getBoundingClientRect();
  const hit  = hitTest(e.clientX-rect.left, e.clientY-rect.top);
  if(hit){
    hovId = hit.id;
    const tip = document.getElementById('tip');
    tip.style.display='block';
    tip.style.left=(e.clientX+14)+'px';
    tip.style.top =(e.clientY-8)+'px';
    document.getElementById('t-tp').textContent=hit.type;
    document.getElementById('t-nm').textContent=hit.name;
    document.getElementById('t-id').textContent=hit.id?hit.id.slice(0,22)+'…':'';
    const b=document.getElementById('t-bg');
    b.textContent=hit.issue_label;
    b.className='tb '+(hit.issue==='proxy'?'bp':hit.issue==='missing_pset'?'bm':'bo');
    cv.style.cursor='pointer';
  } else {
    clearTip();
  }
}
function clearTip(){
  hovId=null;
  document.getElementById('tip').style.display='none';
  cv.style.cursor='grab';
}

// ── Toolbar controls ──────────────────────────────────────────────────────────
function toggleF(type){
  filters[type]=!filters[type];
  document.getElementById(type==='proxy'?'lp':type==='missing_pset'?'lm':'lo')
    .classList.toggle('on',filters[type]);
  draw();
}

function toggleWire(){
  wireMode=!wireMode;
  document.getElementById('wb').classList.toggle('on',wireMode);
  draw();
}

function toggleXray(){
  xrayMode=!xrayMode;
  document.getElementById('xb').classList.toggle('on',xrayMode);
  draw();
}

function toggleExplode(){
  explodeTgt = explodeTgt>0 ? 0 : 1;
  document.getElementById('eb').classList.toggle('on',explodeTgt>0);
}

function fitAll(){
  cam = { rotX:0.52, rotY:0.60, zoom:1.0, panX:0, panY:0 };
  filters={proxy:true,missing_pset:true,ok:true};
  ['lp','lm','lo'].forEach(id=>document.getElementById(id).classList.add('on'));
  draw();
}

function focusIssues(){
  filters.ok=false;
  document.getElementById('lo').classList.remove('on');
  cam.zoom=1.4;
  draw();
}

// ── Init ──────────────────────────────────────────────────────────────────────
window.addEventListener('load', function() {
  // Set badge counts
  document.getElementById('bp-c').textContent = ELEMS.filter(e=>e.issue==='proxy').length;
  document.getElementById('bm-c').textContent = ELEMS.filter(e=>e.issue==='missing_pset').length;
  document.getElementById('bo-c').textContent = ELEMS.filter(e=>e.issue==='ok').length;
  document.getElementById('s-tot').textContent= ELEMS.length;

  // Auto-fit zoom based on scene size
  cam.zoom = Math.min(3.0, Math.max(0.1, 9 / Math.max(sceneR*2, 1)));

  resize();   // sets canvas width/height from DOM, then draws
  animate();  // starts animation loop
});
</script>
</body>
</html>
"""

# Inject data + unique timestamp so Streamlit never serves a stale cached iframe
viewer_html = (HTML
    .replace("ELEMENTS_JSON_PLACEHOLDER", json.dumps(elements_3d))
    .replace("</html>", f"<!-- ts={int(_time.time())} --></html>")
)

st.components.v1.html(viewer_html, height=730, scrolling=False)
