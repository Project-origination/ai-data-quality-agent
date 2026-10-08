import hashlib
import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


from report_export import build_quality_report
from data_quality import analyze_data_quality
from ai_advisor import generate_quality_advice, lm_studio_available

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Data Quality Agent",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DESIGN SYSTEM
# ============================================================

st.markdown(
    """
<style>

/* ---------- Global ---------- */

.stApp {
    background:
        radial-gradient(
            circle at 15% 5%,
            rgba(0, 174, 255, 0.08),
            transparent 25%
        ),
        radial-gradient(
            circle at 90% 10%,
            rgba(123, 92, 255, 0.07),
            transparent 25%
        ),
        #080c14;

    color: #f5f7fb;
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

[data-testid="stSidebar"] {
    background: #0d121d;
    border-right: 1px solid rgba(255,255,255,0.07);
}

[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0;
}


/* ---------- Typography ---------- */

h1,
h2,
h3 {
    letter-spacing: -0.03em;
}

.eyebrow {
    color: #55c7ff;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

.hero-title {
    font-size: 2.6rem;
    line-height: 1.05;
    font-weight: 700;
    letter-spacing: -0.05em;
    margin-bottom: 0.7rem;
}

.hero-subtitle {
    color: #8e9bae;
    font-size: 1.03rem;
    line-height: 1.6;
    max-width: 850px;
    margin-bottom: 1.7rem;
}


/* ---------- Pills ---------- */

.pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.55rem;
    margin-bottom: 1.8rem;
}

.pill {
    border: 1px solid rgba(255,255,255,0.09);
    background: rgba(255,255,255,0.035);
    color: #b9c4d4;
    padding: 0.38rem 0.72rem;
    border-radius: 999px;
    font-size: 0.78rem;
}

.pill-active {
    color: #6dd6ff;
    border-color: rgba(85,199,255,0.25);
    background: rgba(85,199,255,0.08);
}


/* ---------- Section headings ---------- */

.section-kicker {
    color: #6d7a8f;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}

.section-title {
    font-size: 1.35rem;
    font-weight: 650;
    margin-bottom: 1rem;
}


/* ---------- KPI cards ---------- */

.metric-card {
    min-height: 128px;
    border-radius: 18px;
    padding: 1.15rem 1.25rem;

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.055),
            rgba(255,255,255,0.025)
        );

    border: 1px solid rgba(255,255,255,0.075);

    box-shadow:
        0 10px 35px rgba(0,0,0,0.20),
        inset 0 1px 0 rgba(255,255,255,0.035);
}

.metric-label {
    color: #79879c;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.11em;
    text-transform: uppercase;
    margin-bottom: 0.65rem;
}

.metric-value {
    color: #f7f9fc;
    font-size: 2rem;
    font-weight: 650;
    letter-spacing: -0.05em;
    margin-bottom: 0.2rem;
}

.metric-sub {
    color: #8693a6;
    font-size: 0.78rem;
}

.metric-critical {
    color: #ff647c;
}


/* ---------- Dataset banner ---------- */

.dataset-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;

    border: 1px solid rgba(85,199,255,0.16);

    background:
        linear-gradient(
            90deg,
            rgba(85,199,255,0.08),
            rgba(123,92,255,0.035)
        );

    border-radius: 16px;
    padding: 0.9rem 1.1rem;
    margin-top: 0.3rem;
    margin-bottom: 1.5rem;
}

.dataset-name {
    font-weight: 650;
    color: #eaf6ff;
}

.dataset-meta {
    color: #8290a4;
    font-size: 0.8rem;
}


/* ---------- Issue cards ---------- */

.issue-card {
    border-radius: 15px;
    padding: 0.95rem 1rem;
    margin-bottom: 0.7rem;

    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.065);

    transition:
        transform 0.15s ease,
        border-color 0.15s ease,
        background 0.15s ease;
}

.issue-card:hover {
    transform: translateY(-1px);
    background: rgba(255,255,255,0.035);
    border-color: rgba(255,255,255,0.11);
}

.issue-critical {
    border-left: 3px solid #ff536d;
}

.issue-high {
    border-left: 3px solid #ff9655;
}

.issue-medium {
    border-left: 3px solid #f2cf5b;
}

.issue-low {
    border-left: 3px solid #57d6a2;
}

.issue-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.45rem;
}

.issue-title {
    font-weight: 650;
    color: #f4f7fb;
}

.issue-severity {
    font-size: 0.69rem;
    padding: 0.22rem 0.5rem;
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,0.09);
    color: #b9c4d4;
}

.issue-desc {
    color: #8f9caf;
    font-size: 0.82rem;
    line-height: 1.45;
}

.issue-meta {
    color: #66748a;
    margin-top: 0.45rem;
    font-size: 0.73rem;
}


/* ---------- Upload ---------- */

[data-testid="stFileUploader"] {
    border-radius: 18px;
}

[data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.025);
    border: 1px dashed rgba(85,199,255,0.25);
    border-radius: 16px;
}


/* ---------- Buttons ---------- */

.stButton > button {
    border-radius: 12px;
    min-height: 45px;
    font-weight: 600;

    border: 1px solid rgba(85,199,255,0.25);

    background:
        linear-gradient(
            135deg,
            rgba(29,127,201,0.85),
            rgba(80,81,210,0.85)
        );

    color: white;

    transition:
        transform 0.15s ease,
        border-color 0.15s ease,
        box-shadow 0.15s ease;
}

.stButton > button:hover {
    border-color: rgba(85,199,255,0.6);
    transform: translateY(-1px);
    box-shadow: 0 8px 25px rgba(30,120,220,0.16);
}


/* ---------- Dataframe ---------- */

[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 15px;
    overflow: hidden;
}

hr {
    border-color: rgba(255,255,255,0.06);
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# CONSTANTS
# ============================================================

PLOT_BG = "rgba(0,0,0,0)"
TEXT = "#9aa7b8"
GRID = "rgba(255,255,255,0.055)"

SEVERITY_COLORS = {
    "Critical": "#ff536d",
    "High": "#ff9655",
    "Medium": "#f0c84d",
    "Low": "#50d6a1",
}

SEVERITY_WEIGHTS = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
}


# ============================================================
# DATA LOADING
# ============================================================

def load_file(uploaded_file):

    name = uploaded_file.name.lower()

    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)

    if name.endswith(".xlsx"):
        return pd.read_excel(
            uploaded_file,
            engine="openpyxl",
        )

    raise ValueError(
        "Unsupported file format. Please upload CSV or XLSX."
    )


# ============================================================
# SCORE HELPERS
# ============================================================

def score_label(score):

    if score >= 90:
        return "Excellent"

    if score >= 75:
        return "Healthy"

    if score >= 50:
        return "Needs attention"

    return "Critical attention"


def score_color(score):

    if score >= 90:
        return "#50d6a1"

    if score >= 75:
        return "#55c7ff"

    if score >= 50:
        return "#f0c84d"

    return "#ff536d"


# ============================================================
# PLOTLY BASE
# ============================================================

def plot_layout(fig, height=None):

    fig.update_layout(
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,

        font=dict(
            family="Arial",
            color=TEXT,
        ),

        margin=dict(
            l=25,
            r=25,
            t=50,
            b=30,
        ),

        showlegend=False,
    )

    if height:
        fig.update_layout(
            height=height
        )

    return fig


# ============================================================
# QUALITY SCORE DONUT
# ============================================================

def build_score_donut(score):

    color = score_color(score)

    fig = go.Figure(
        go.Pie(
            values=[
                score,
                100 - score,
            ],

            hole=0.78,

            sort=False,

            direction="clockwise",

            marker=dict(
                colors=[
                    color,
                    "rgba(255,255,255,0.055)",
                ],

                line=dict(
                    width=0
                ),
            ),

            textinfo="none",
            hoverinfo="skip",
        )
    )

    fig.add_annotation(
        x=0.5,
        y=0.56,
        text=f"<b>{score}</b>",
        showarrow=False,

        font=dict(
            size=44,
            color="#f7f9fc",
        ),
    )

    fig.add_annotation(
        x=0.5,
        y=0.39,
        text="/ 100",
        showarrow=False,

        font=dict(
            size=13,
            color="#6f7d91",
        ),
    )

    fig.add_annotation(
        x=0.5,
        y=0.24,
        text=score_label(score).upper(),
        showarrow=False,

        font=dict(
            size=10,
            color=color,
        ),
    )

    plot_layout(
        fig,
        310,
    )

    fig.update_layout(
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10,
        )
    )

    return fig


# ============================================================
# SEVERITY CHART
# ============================================================

def build_severity_chart(severity_counts):

    labels = [
        "Critical",
        "High",
        "Medium",
        "Low",
    ]

    values = [
        severity_counts.get(label, 0)
        for label in labels
    ]

    colors = [
        SEVERITY_COLORS[label]
        for label in labels
    ]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",

            marker=dict(
                color=colors,
                line=dict(
                    width=0
                ),
            ),

            text=values,
            textposition="outside",
            cliponaxis=False,

            hovertemplate=(
                "<b>%{y}</b><br>"
                "%{x} issue(s)"
                "<extra></extra>"
            ),
        )
    )

    plot_layout(
        fig,
        300,
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
        showticklabels=False,
    )

    fig.update_yaxes(
        showgrid=False,
        autorange="reversed",
    )

    return fig


# ============================================================
# QUALITY DIMENSION RADAR
# ============================================================

def build_quality_radar(dimension_scores):

    dimensions = [
        "Completeness",
        "Uniqueness",
        "Validity",
        "Consistency",
        "Statistical Health",
    ]

    values = [
        dimension_scores.get(dimension)
        if dimension_scores.get(dimension) is not None
        else 0
        for dimension in dimensions
    ]

    radar_dimensions = (
        dimensions
        + [dimensions[0]]
    )

    radar_values = (
        values
        + [values[0]]
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=radar_values,
            theta=radar_dimensions,

            fill="toself",

            line=dict(
                color="#55c7ff",
                width=2,
            ),

            fillcolor="rgba(85,199,255,0.14)",

            marker=dict(
                size=7,
                color="#55c7ff",
            ),

            hovertemplate=(
                "<b>%{theta}</b><br>"
                "%{r}/100"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,

        height=380,

        margin=dict(
            l=55,
            r=55,
            t=35,
            b=35,
        ),

        showlegend=False,

        font=dict(
            family="Arial",
            color=TEXT,
        ),

        polar=dict(
            bgcolor="rgba(0,0,0,0)",

            radialaxis=dict(
                visible=True,
                range=[0, 100],

                tickvals=[
                    25,
                    50,
                    75,
                    100,
                ],

                tickfont=dict(
                    size=9,
                    color="#657287",
                ),

                gridcolor=GRID,

                linecolor="rgba(255,255,255,0.06)",
            ),

            angularaxis=dict(
                gridcolor=GRID,
                linecolor="rgba(255,255,255,0.06)",
            ),
        ),
    )

    return fig


# ============================================================
# QUALITY DIMENSION BARS
# ============================================================

def build_dimension_chart(dimension_scores):

    dimensions = [
        "Completeness",
        "Uniqueness",
        "Validity",
        "Consistency",
        "Statistical Health",
    ]

    scores = [
        dimension_scores.get(dimension)
        if dimension_scores.get(dimension) is not None
        else 0
        for dimension in dimensions
    ]

    colors = [
        score_color(score)
        for score in scores
    ]

    fig = go.Figure(
        go.Bar(
            x=scores,
            y=dimensions,

            orientation="h",

            marker=dict(
                color=colors,
            ),

            text=[
                f"{score}%"
                for score in scores
            ],

            textposition="inside",

            insidetextanchor="end",

            hovertemplate=(
                "<b>%{y}</b><br>"
                "%{x}/100"
                "<extra></extra>"
            ),
        )
    )

    plot_layout(
        fig,
        380,
    )

    fig.update_xaxes(
        range=[0, 100],

        showgrid=True,

        gridcolor=GRID,

        zeroline=False,

        tickvals=[
            0,
            25,
            50,
            75,
            100,
        ],

        ticksuffix="%",
    )

    fig.update_yaxes(
        showgrid=False,
        autorange="reversed",
    )

    return fig


# ============================================================
# COLUMN RISK
# ============================================================

def build_column_risk_chart(issues):

    if not issues:
        return None

    scores = {}

    for issue in issues:

        column = issue["column"]

        if column == "All columns":
            continue

        scores[column] = (
            scores.get(
                column,
                0,
            )
            + SEVERITY_WEIGHTS.get(
                issue["severity"],
                1,
            )
        )

    if not scores:
        return None

    risk_df = pd.DataFrame(
        {
            "Column": list(
                scores.keys()
            ),
            "Risk": list(
                scores.values()
            ),
        }
    )

    risk_df = risk_df.sort_values(
        "Risk",
        ascending=True,
    )

    max_risk = (
        risk_df["Risk"].max()
    )

    colors = []

    for value in risk_df["Risk"]:

        ratio = (
            value / max_risk
            if max_risk
            else 0
        )

        if ratio >= 0.75:
            colors.append(
                "#ff536d"
            )

        elif ratio >= 0.45:
            colors.append(
                "#ff9655"
            )

        else:
            colors.append(
                "#55c7ff"
            )

    fig = go.Figure(
        go.Bar(
            x=risk_df["Risk"],
            y=risk_df["Column"],

            orientation="h",

            marker=dict(
                color=colors,
            ),

            text=risk_df["Risk"],

            textposition="outside",

            cliponaxis=False,

            hovertemplate=(
                "<b>%{y}</b><br>"
                "Risk weight: %{x}"
                "<extra></extra>"
            ),
        )
    )

    plot_layout(
        fig,
        330,
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor=GRID,
        showticklabels=False,
        zeroline=False,
    )

    fig.update_yaxes(
        showgrid=False,
    )

    return fig


# ============================================================
# QUALITY HEATMAP
# ============================================================

def build_quality_heatmap(
    df,
    issues,
):

    categories = [
        "Missing values",
        "Uniqueness",
        "Format",
        "Business rule",
        "Consistency",
        "Outlier",
    ]

    columns = list(
        df.columns
    )

    matrix = pd.DataFrame(
        0,
        index=columns,
        columns=categories,
    )

    for issue in issues:

        column = issue["column"]
        category = issue["category"]

        if (
            column in matrix.index
            and category in matrix.columns
        ):

            matrix.loc[
                column,
                category,
            ] = max(
                matrix.loc[
                    column,
                    category,
                ],

                SEVERITY_WEIGHTS.get(
                    issue["severity"],
                    1,
                ),
            )

    labels = {
        0: "",
        1: "Low",
        2: "Medium",
        3: "High",
        4: "Critical",
    }

    text_matrix = matrix.map(
        lambda value: labels.get(
            value,
            "",
        )
    )

    fig = go.Figure(
        go.Heatmap(
            z=matrix.values,

            x=matrix.columns,

            y=matrix.index,

            text=text_matrix.values,

            texttemplate="%{text}",

            hovertemplate=(
                "<b>%{y}</b><br>"
                "%{x}<br>"
                "Risk level: %{text}"
                "<extra></extra>"
            ),

            zmin=0,
            zmax=4,

            colorscale=[
                [0.00, "#111722"],
                [0.24, "#111722"],

                [0.25, "#45c99a"],
                [0.49, "#45c99a"],

                [0.50, "#e8c348"],
                [0.74, "#e8c348"],

                [0.75, "#ff9655"],
                [0.89, "#ff9655"],

                [0.90, "#ff536d"],
                [1.00, "#ff536d"],
            ],

            showscale=False,

            xgap=3,
            ygap=3,
        )
    )

    plot_layout(
        fig,
        max(
            350,
            len(columns) * 42 + 100,
        ),
    )

    fig.update_xaxes(
        side="top",
        showgrid=False,
        tickangle=0,
    )

    fig.update_yaxes(
        showgrid=False,
        autorange="reversed",
    )

    return fig


# ============================================================
# HTML CARDS
# ============================================================

def metric_card(
    label,
    value,
    subtitle,
    critical=False,
):

    value_class = "metric-value"

    if critical:
        value_class += " metric-critical"

    return (
        '<div class="metric-card">'
        f'<div class="metric-label">{html.escape(str(label))}</div>'
        f'<div class="{value_class}">{html.escape(str(value))}</div>'
        f'<div class="metric-sub">{html.escape(str(subtitle))}</div>'
        '</div>'
    )


def issue_card(issue):

    severity = issue["severity"]

    css_class = {
        "Critical": "issue-critical",
        "High": "issue-high",
        "Medium": "issue-medium",
        "Low": "issue-low",
    }.get(
        severity,
        "issue-low",
    )

    category = html.escape(
        str(
            issue["category"]
        )
    )

    severity_text = html.escape(
        str(
            severity
        )
    )

    message = html.escape(
        str(
            issue["message"]
        )
    )

    column = html.escape(
        str(
            issue["column"]
        )
    )

    rows = issue[
        "affected_rows"
    ]

    return (
        f'<div class="issue-card {css_class}">'
        '<div class="issue-top">'
        f'<div class="issue-title">{category}</div>'
        f'<div class="issue-severity">{severity_text}</div>'
        '</div>'
        f'<div class="issue-desc">{message}</div>'
        '<div class="issue-meta">'
        f'Column: {column} · Affected rows: {rows}'
        '</div>'
        '</div>'
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
<div class="eyebrow">
DATA RELIABILITY
</div>

<h2 style="margin-top:0;">
◈ Quality Agent
</h2>
""",
        unsafe_allow_html=True,
    )

    st.caption(
        "Automated profiling, anomaly detection "
        "and AI-assisted remediation."
    )

    st.divider()

    st.markdown(
        "#### Control Framework"
    )

    st.caption(
        "COMPLETENESS"
    )

    st.write(
        "Missing values"
    )

    st.caption(
        "UNIQUENESS"
    )

    st.write(
        "Duplicate identifiers"
    )

    st.caption(
        "VALIDITY"
    )

    st.write(
        "Formats & business rules"
    )

    st.caption(
        "CONSISTENCY"
    )

    st.write(
        "Unexpected categories"
    )

    st.caption(
        "STATISTICAL HEALTH"
    )

    st.write(
        "Outlier detection"
    )

    st.divider()

    st.markdown(
        """
<div class="pill-row">
<span class="pill pill-active">
● Engine online
</span>
</div>
""",
        unsafe_allow_html=True,

    )

    st.caption(
        "Python · Pandas · Plotly"
    )

    st.caption(
        "Qwen3 4B · LM Studio · Local inference"
    )


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
<div class="eyebrow">
INTELLIGENT DATA QUALITY CONTROL
</div>

<div class="hero-title">
Data Quality Observatory
</div>

<div class="hero-subtitle">
Detect structural defects, integrity risks and statistical
anomalies before unreliable data reaches dashboards,
models or business decisions.
</div>

<div class="pill-row">

<span class="pill pill-active">
● Deterministic Engine
</span>

<span class="pill">
CSV / XLSX
</span>

<span class="pill">
Statistical Detection
</span>

<span class="pill">
AI-Powered Recommendations
</span>

</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# DATA SOURCE
# ============================================================

st.markdown(
    """
<div class="section-kicker">
01 · DATA SOURCE
</div>

<div class="section-title">
Select a dataset
</div>
""",
    unsafe_allow_html=True,
)


upload_col, demo_col = st.columns(
    [
        3.5,
        1,
    ],
    gap="medium",
)


with upload_col:

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel",

        type=[
            "csv",
            "xlsx",
        ],

        label_visibility="collapsed",
    )


with demo_col:

    use_demo = st.button(
        "Load demo dataset",
        width="stretch",
    )


# ============================================================
# SESSION STATE
# ============================================================

if "use_demo" not in st.session_state:
    st.session_state.use_demo = False


if use_demo:
    st.session_state.use_demo = True


df = None
source_name = None


# ============================================================
# LOAD DATASET
# ============================================================

if uploaded_file is not None:

    try:

        df = load_file(
            uploaded_file
        )

        source_name = (
            uploaded_file.name
        )

        st.session_state.use_demo = False

    except Exception as error:

        st.error(
            f"Unable to load dataset: {error}"
        )


elif st.session_state.use_demo:

    try:

        df = pd.read_csv(
            "data/customers_dirty.csv"
        )

        source_name = (
            "customers_dirty.csv"
        )

    except FileNotFoundError:

        st.error(
            "Demo dataset not found. "
            "Run create_sample_data.py first."
        )


# ============================================================
# DASHBOARD
# ============================================================

if df is not None:

    result = analyze_data_quality(
        df
    )

    # Detect dataset changes
    dataset_fingerprint = hashlib.sha256(
        df.to_csv(index=False).encode("utf-8")
    ).hexdigest()

    # Clear previous AI analysis when dataset changes
    if st.session_state.get("ai_dataset_fingerprint") != dataset_fingerprint:
        st.session_state.ai_dataset_fingerprint = dataset_fingerprint
        st.session_state.ai_advice = None

   

    # ========================================================
    # DATASET BANNER
    # ========================================================

    dataset_html = (
        '<div class="dataset-banner">'
        '<div>'
        f'<div class="dataset-name">◈ {html.escape(str(source_name))}</div>'
        '<div class="dataset-meta">Dataset successfully profiled</div>'
        '</div>'
        '<div class="dataset-meta">'
        f'{result["total_rows"]:,} rows · '
        f'{result["total_columns"]} columns'
        '</div>'
        '</div>'
    )

    st.markdown(
        dataset_html,
        unsafe_allow_html=True,
    )


    # ========================================================
    # 02 OVERVIEW
    # ========================================================

    st.markdown(
        """
<div class="section-kicker">
02 · OVERVIEW
</div>

<div class="section-title">
Data health snapshot
</div>
""",
        unsafe_allow_html=True,
    )


    k1, k2, k3, k4 = st.columns(
        4
    )


    with k1:

        st.markdown(
            metric_card(
                "Quality Score",

                f'{result["quality_score"]}/100',

                score_label(
                    result[
                        "quality_score"
                    ]
                ),

                critical=(
                    result[
                        "quality_score"
                    ]
                    < 50
                ),
            ),

            unsafe_allow_html=True,
        )


    with k2:

        st.markdown(
            metric_card(
                "Rows analyzed",

                f'{result["total_rows"]:,}',

                "Records evaluated",
            ),

            unsafe_allow_html=True,
        )


    with k3:

        st.markdown(
            metric_card(
                "Columns",

                result[
                    "total_columns"
                ],

                "Fields inspected",
            ),

            unsafe_allow_html=True,
        )


    with k4:

        st.markdown(
            metric_card(
                "Issues detected",

                result[
                    "total_issues"
                ],

                "Quality signals",

                critical=(
                    result[
                        "total_issues"
                    ]
                    > 0
                ),
            ),

            unsafe_allow_html=True,
        )


    st.write("")


    # ========================================================
    # QUALITY SCORE + SEVERITY
    # ========================================================

    score_col, severity_col = st.columns(
        [
            0.85,
            1.4,
        ],

        gap="large",
    )


    with score_col:

        st.markdown(
            """
<div class="section-kicker">
QUALITY INDEX
</div>

<div class="section-title">
Overall reliability
</div>
""",
            unsafe_allow_html=True,
        )

        st.plotly_chart(
            build_score_donut(
                result[
                    "quality_score"
                ]
            ),

            width="stretch",

            config={
                "displayModeBar": False
            },
        )


    with severity_col:

        st.markdown(
            """
<div class="section-kicker">
RISK DISTRIBUTION
</div>

<div class="section-title">
Issues by severity
</div>
""",
            unsafe_allow_html=True,
        )

        st.plotly_chart(
            build_severity_chart(
                result[
                    "severity_counts"
                ]
            ),

            width="stretch",

            config={
                "displayModeBar": False
            },
        )


    # ========================================================
    # 03 QUALITY DIMENSIONS
    # ========================================================

    st.markdown(
        """
<div class="section-kicker">
03 · QUALITY DIMENSIONS
</div>

<div class="section-title">
Multidimensional data health
</div>
""",
        unsafe_allow_html=True,
    )


    st.caption(
        "The overall quality score combines completeness, "
        "uniqueness, validity, consistency and statistical health."
    )


    radar_col, dimensions_col = st.columns(
        [
            1,
            1.35,
        ],

        gap="large",
    )


    with radar_col:

        st.plotly_chart(
            build_quality_radar(
                result[
                    "quality_dimensions"
                ]
            ),

            width="stretch",

            config={
                "displayModeBar": False
            },
        )


    with dimensions_col:

        st.plotly_chart(
            build_dimension_chart(
                result[
                    "quality_dimensions"
                ]
            ),

            width="stretch",

            config={
                "displayModeBar": False
            },
        )


    # ========================================================
    # 04 RISK MAP
    # ========================================================

    st.markdown(
        """
<div class="section-kicker">
04 · RISK MAP
</div>

<div class="section-title">
Data quality control matrix
</div>
""",
        unsafe_allow_html=True,
    )


    st.caption(
        "Each cell highlights the strongest detected "
        "risk for a column and control dimension."
    )


    st.plotly_chart(
        build_quality_heatmap(
            df,

            result[
                "issues"
            ],
        ),

        width="stretch",

        config={
            "displayModeBar": False
        },
    )


    # ========================================================
    # PRIORITIZATION + REMEDIATION
    # ========================================================

    left, right = st.columns(
        [
            1,
            1.15,
        ],

        gap="large",
    )


    with left:

        st.markdown(
            """
<div class="section-kicker">
PRIORITIZATION
</div>

<div class="section-title">
Column risk ranking
</div>
""",
            unsafe_allow_html=True,
        )


        risk_chart = (
            build_column_risk_chart(
                result[
                    "issues"
                ]
            )
        )


        if risk_chart is not None:

            st.plotly_chart(
                risk_chart,

                width="stretch",

                config={
                    "displayModeBar": False
                },
            )

        else:

            st.success(
                "No column-level risks detected."
            )


    with right:

        st.markdown(
            """
<div class="section-kicker">
REMEDIATION QUEUE
</div>

<div class="section-title">
Priority issues
</div>
""",
            unsafe_allow_html=True,
        )


        ordered_issues = sorted(
            result[
                "issues"
            ],

            key=lambda item: {
                "Critical": 0,
                "High": 1,
                "Medium": 2,
                "Low": 3,
            }.get(
                item[
                    "severity"
                ],
                4,
            ),
        )


        if ordered_issues:

            for issue in ordered_issues:

                st.markdown(
                    issue_card(
                        issue
                    ),

                    unsafe_allow_html=True,
                )

        else:

            st.success(
                "No quality issues detected."
            )


    # ========================================================
    # 05 AUDIT DETAIL
    # ========================================================

    st.markdown(
        """
<div class="section-kicker">
05 · AUDIT DETAIL
</div>

<div class="section-title">
Quality findings
</div>
""",
        unsafe_allow_html=True,
    )


    if result[
        "issues"
    ]:

        issues_df = pd.DataFrame(
            result[
                "issues"
            ]
        )


        issues_df = issues_df.rename(
            columns={
                "category": "Control",
                "severity": "Severity",
                "column": "Column",
                "affected_rows": "Affected Rows",
                "message": "Finding",
            }
        )


        severity_order = {
            "Critical": 0,
            "High": 1,
            "Medium": 2,
            "Low": 3,
        }


        issues_df[
            "_order"
        ] = (
            issues_df[
                "Severity"
            ]
            .map(
                severity_order
            )
        )


        issues_df = (
            issues_df
            .sort_values(
                "_order"
            )
            .drop(
                columns="_order"
            )
        )


        st.dataframe(
            issues_df,
            width="stretch",
            hide_index=True,
        )


    # ========================================================
    # 06 AI ADVISOR
    # ========================================================

    st.markdown(
        """
<div class="section-kicker">
06 · AI ADVISOR
</div>

<div class="section-title">
AI-powered remediation guidance
</div>
""",
        unsafe_allow_html=True,
    )

    st.caption(
        "The AI advisor interprets the deterministic quality findings "
        "and recommends remediation actions. It does not detect issues itself."
    )

    if "ai_advice" not in st.session_state:
        st.session_state.ai_advice = None

    if lm_studio_available():

        if st.button(
            "✦ Generate AI Analysis",
            width="stretch",
            key="generate_ai_analysis",
        ):

            with st.spinner(
                "Qwen is reviewing the quality findings..."
            ):

                try:

                    st.session_state.ai_advice = generate_quality_advice(
                        result
                    )

                except Exception as error:

                    st.error(
                        f"AI analysis failed: {error}"
                    )

        if st.session_state.ai_advice:

            st.markdown(
                st.session_state.ai_advice
            )

    else:

        st.warning(
            "Local AI is unavailable. "
            "Start the LM Studio server and load the Qwen model."
        )
            # ========================================================
    # DOWNLOAD QUALITY REPORT
    # ========================================================

    st.markdown(
        """
<div class="section-kicker">
REPORT EXPORT
</div>

<div class="section-title">
Export quality assessment
</div>
""",
        unsafe_allow_html=True,
    )

    st.caption(
        "Download the quality scores, detected issues "
        "and AI recommendations in a Markdown report."
    )

    report_text = build_quality_report(
        result=result,
        dataset_name=source_name,
        status=score_label(result["quality_score"]),
        ai_advice=st.session_state.get("ai_advice"),
    )

    st.download_button(
        label="↓ Download Quality Report",
        data=report_text,
        file_name="data_quality_report.md",
        mime="text/markdown",
        width="stretch",
        key="download_quality_report",
    )

    # ========================================================
    # SOURCE DATASET
    # ========================================================

    st.write("")


    with st.expander(
        "Explore source dataset"
    ):

        st.dataframe(
            df,
            width="stretch",
            hide_index=True,
        )


    # ========================================================
    # ARCHITECTURE
    # ========================================================

    with st.expander(
        "View control architecture"
    ):

        st.markdown(
            """
**Dataset**

→ ingestion and profiling

**Deterministic controls**

→ completeness, uniqueness, validity and consistency

**Statistical detection**

→ numerical anomaly identification

**Multidimensional scoring**

→ completeness, uniqueness, validity, consistency and statistical health

**Risk prioritization**

→ severity-weighted findings

**AI interpretation**

→ business explanation and remediation recommendations *(next layer)*
"""
        )


# ============================================================
# EMPTY STATE
# ============================================================

else:

    st.markdown(
        """
<div style="
    margin-top: 2rem;
    padding: 3rem;
    text-align: center;
    border-radius: 20px;
    border: 1px dashed rgba(85,199,255,0.20);
    background: rgba(255,255,255,0.018);
">

<div style="
    font-size: 2.2rem;
    margin-bottom: 0.7rem;
">
◈
</div>

<div style="
    font-size: 1.05rem;
    font-weight: 600;
    margin-bottom: 0.3rem;
">
No dataset selected
</div>

<div style="
    color: #77859a;
    font-size: 0.85rem;
">
Upload a CSV or XLSX file,
or load the demonstration dataset.
</div>

</div>
""",
        unsafe_allow_html=True,
    )