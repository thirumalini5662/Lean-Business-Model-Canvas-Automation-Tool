import os
import io
import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

# ============================================================
# OPTIONAL PDF LIBRARY
# ============================================================

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer
    )

    REPORTLAB_AVAILABLE = True

except ImportError:
    REPORTLAB_AVAILABLE = False


# ============================================================
# OPTIONAL OPENAI
# ============================================================

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True

except ImportError:
    OPENAI_AVAILABLE = False


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Lean Business Model Canvas",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# DATABASE
# ============================================================

DB_FILE = "lbmc_data.db"


def initialize_database():

    connection = sqlite3.connect(DB_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS canvas_data (

            id INTEGER PRIMARY KEY,

            business_name TEXT DEFAULT '',

            industry TEXT DEFAULT '',

            problem TEXT DEFAULT '',

            customer_segments TEXT DEFAULT '',

            unique_value_proposition TEXT DEFAULT '',

            solution TEXT DEFAULT '',

            channels TEXT DEFAULT '',

            revenue_streams TEXT DEFAULT '',

            cost_structure TEXT DEFAULT '',

            key_metrics TEXT DEFAULT '',

            unfair_advantage TEXT DEFAULT '',

            updated_at TEXT
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO canvas_data
        (id, updated_at)
        VALUES (1, ?)
    """, (
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    ))

    connection.commit()

    connection.close()


initialize_database()


# ============================================================
# CANVAS SECTIONS
# ============================================================

SECTIONS = [

    "Problem",

    "Customer Segments",

    "Unique Value Proposition",

    "Solution",

    "Channels",

    "Revenue Streams",

    "Cost Structure",

    "Key Metrics",

    "Unfair Advantage"
]


# ============================================================
# DATABASE LOAD
# ============================================================

def load_canvas():

    connection = sqlite3.connect(DB_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            business_name,
            industry,
            problem,
            customer_segments,
            unique_value_proposition,
            solution,
            channels,
            revenue_streams,
            cost_structure,
            key_metrics,
            unfair_advantage
        FROM canvas_data
        WHERE id = 1
    """)

    row = cursor.fetchone()

    connection.close()

    if not row:

        return {
            "business_name": "",
            "industry": "",
            "Problem": "",
            "Customer Segments": "",
            "Unique Value Proposition": "",
            "Solution": "",
            "Channels": "",
            "Revenue Streams": "",
            "Cost Structure": "",
            "Key Metrics": "",
            "Unfair Advantage": ""
        }

    return {

        "business_name": row[0] or "",

        "industry": row[1] or "",

        "Problem": row[2] or "",

        "Customer Segments": row[3] or "",

        "Unique Value Proposition": row[4] or "",

        "Solution": row[5] or "",

        "Channels": row[6] or "",

        "Revenue Streams": row[7] or "",

        "Cost Structure": row[8] or "",

        "Key Metrics": row[9] or "",

        "Unfair Advantage": row[10] or ""
    }


# ============================================================
# AUTO-SAVE ONE FIELD
# ============================================================

def autosave_field(
    database_column,
    value
):

    connection = sqlite3.connect(DB_FILE)

    cursor = connection.cursor()

    cursor.execute(
        f"""
        UPDATE canvas_data
        SET {database_column} = ?,
            updated_at = ?
        WHERE id = 1
        """,
        (
            value,

            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )

    connection.commit()

    connection.close()


# ============================================================
# AUTO-SAVE ENTIRE CANVAS
# ============================================================

def autosave_canvas(
    business_name,
    industry,
    canvas
):

    connection = sqlite3.connect(DB_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE canvas_data

        SET
            business_name = ?,
            industry = ?,
            problem = ?,
            customer_segments = ?,
            unique_value_proposition = ?,
            solution = ?,
            channels = ?,
            revenue_streams = ?,
            cost_structure = ?,
            key_metrics = ?,
            unfair_advantage = ?,
            updated_at = ?

        WHERE id = 1
    """,

    (
        business_name,

        industry,

        canvas["Problem"],

        canvas["Customer Segments"],

        canvas["Unique Value Proposition"],

        canvas["Solution"],

        canvas["Channels"],

        canvas["Revenue Streams"],

        canvas["Cost Structure"],

        canvas["Key Metrics"],

        canvas["Unfair Advantage"],

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    connection.commit()

    connection.close()


# ============================================================
# DELETE / CLEAR CANVAS
# ============================================================

def clear_database():

    connection = sqlite3.connect(DB_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE canvas_data

        SET
            business_name = '',
            industry = '',
            problem = '',
            customer_segments = '',
            unique_value_proposition = '',
            solution = '',
            channels = '',
            revenue_streams = '',
            cost_structure = '',
            key_metrics = '',
            unfair_advantage = '',
            updated_at = ?

        WHERE id = 1
    """,

    (
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    ))

    connection.commit()

    connection.close()


# ============================================================
# COMPLETENESS
# ============================================================

def calculate_completeness(canvas):

    completed = 0

    for section in SECTIONS:

        if canvas.get(
            section,
            ""
        ).strip():

            completed += 1

    return round(
        (completed / 9) * 100,
        1
    )


# ============================================================
# LOAD EXISTING DATA
# ============================================================

saved_data = load_canvas()


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "business_name" not in st.session_state:

    st.session_state.business_name = (
        saved_data["business_name"]
    )


if "industry" not in st.session_state:

    st.session_state.industry = (
        saved_data["industry"]
    )


for section in SECTIONS:

    key = f"canvas_{section}"

    if key not in st.session_state:

        st.session_state[key] = (
            saved_data[section]
        )


# ============================================================
# HELP TEXT
# ============================================================

SECTION_HELP = {

    "Problem":
        "What major problem does your target customer experience?",

    "Customer Segments":
        "Who are your main customers? Be specific.",

    "Unique Value Proposition":
        "Why should customers choose your product or service?",

    "Solution":
        "What product or service solves the identified problem?",

    "Channels":
        "How will customers discover, purchase, and receive your product?",

    "Revenue Streams":
        "How will the business generate revenue?",

    "Cost Structure":
        "What are the major costs involved in running the business?",

    "Key Metrics":
        "Which numbers will measure business performance?",

    "Unfair Advantage":
        "What advantage is difficult for competitors to copy?"
}


# ============================================================
# BUILT-IN AI GUIDANCE
# ============================================================

def built_in_suggestions(
    section,
    current_text,
    industry
):

    suggestions = {

        "Problem": [

            "Describe the customer's actual pain point.",

            "Mention the time, money, effort, or risk caused by the problem.",

            "Focus on the customer's problem rather than the product."
        ],

        "Customer Segments": [

            "Make the customer group specific.",

            "Identify your primary customer.",

            "Mention age, profession, location, or use case where relevant."
        ],

        "Unique Value Proposition": [

            "Clearly state the main customer benefit.",

            "Focus on the result customers receive.",

            "Explain what makes your idea different."
        ],

        "Solution": [

            "Connect each feature to a specific problem.",

            "Keep the MVP simple and focused.",

            "Mention the most important functionality."
        ],

        "Channels": [

            "Consider social media, websites, partnerships, referrals, and offline channels.",

            "Choose channels where your target customers already spend time.",

            "Separate marketing channels from delivery channels."
        ],

        "Revenue Streams": [

            "Consider subscriptions, one-time purchases, commissions, freemium models, or advertising.",

            "Explain exactly what customers pay for.",

            "Add pricing logic where possible."
        ],

        "Cost Structure": [

            "Include development, marketing, staff, technology, and operations.",

            "Identify major fixed and variable costs.",

            "Focus on costs that affect profitability."
        ],

        "Key Metrics": [

            "Consider users, revenue, conversion rate, retention, and repeat purchases.",

            "Choose metrics connected to business performance.",

            "Avoid metrics that do not support decisions."
        ],

        "Unfair Advantage": [

            "Consider proprietary data, partnerships, community, technology, or expertise.",

            "Avoid calling normal features an unfair advantage.",

            "Explain why competitors would find it difficult to copy."
        ]
    }

    result = suggestions.get(
        section,
        []
    )

    if not current_text.strip():

        result = [
            f"Start by adding 1–3 points for {section}."
        ] + result

    if industry.strip():

        result.append(
            f"Make the answer specific to the {industry} industry."
        )

    return result[:4]


# ============================================================
# OPTIONAL OPENAI
# ============================================================

def generate_ai_suggestions(
    section,
    current_text,
    industry
):

    api_key = os.getenv(
        "OPENAI_API_KEY",
        ""
    ).strip()

    if (
        not api_key
        or not OPENAI_AVAILABLE
    ):

        return (
            built_in_suggestions(
                section,
                current_text,
                industry
            ),

            "Built-in guidance"
        )


    try:

        client = OpenAI(
            api_key=api_key
        )

        prompt = f"""

You are a startup mentor.

Industry:
{industry}

Lean Canvas Section:
{section}

Current Content:
{current_text}

Give exactly 3 concise,
practical suggestions to improve
this section.

Do not invent facts.

Return only numbered suggestions.
"""


        response = client.responses.create(

            model=os.getenv(
                "OPENAI_MODEL",
                "gpt-5-mini"
            ),

            input=prompt
        )


        lines = [

            line.strip()

            for line in
            response.output_text.splitlines()

            if line.strip()
        ]


        if lines:

            return (
                lines[:3],
                "OpenAI"
            )


    except Exception:

        pass


    return (
        built_in_suggestions(
            section,
            current_text,
            industry
        ),

        "Built-in guidance"
    )


# ============================================================
# PDF GENERATOR
# ============================================================

def create_pdf(
    business_name,
    industry,
    canvas,
    completeness
):

    if not REPORTLAB_AVAILABLE:

        return None


    buffer = io.BytesIO()


    document = SimpleDocTemplate(

        buffer,

        pagesize=landscape(A4),

        rightMargin=25,

        leftMargin=25,

        topMargin=25,

        bottomMargin=25
    )


    styles = getSampleStyleSheet()


    title_style = ParagraphStyle(

        "TitleStyle",

        parent=styles["Title"],

        fontSize=18,

        leading=22,

        alignment=TA_CENTER
    )


    heading_style = ParagraphStyle(

        "HeadingStyle",

        parent=styles["Heading4"],

        fontSize=9,

        leading=11,

        alignment=TA_CENTER
    )


    body_style = ParagraphStyle(

        "BodyStyle",

        parent=styles["BodyText"],

        fontSize=7.5,

        leading=9,

        alignment=TA_LEFT
    )


    story = []


    story.append(

        Paragraph(
            "LEAN BUSINESS MODEL CANVAS",
            title_style
        )
    )


    story.append(

        Paragraph(

            f"<b>Business:</b> "
            f"{business_name or 'Untitled'}"
            f"&nbsp;&nbsp;&nbsp;"
            f"<b>Industry:</b> "
            f"{industry or 'Not specified'}"
            f"&nbsp;&nbsp;&nbsp;"
            f"<b>Completeness:</b> "
            f"{completeness}%",

            body_style
        )
    )


    story.append(
        Spacer(1, 10)
    )


    rows = []


    for start in range(
        0,
        9,
        3
    ):

        row = []


        for section in SECTIONS[
            start:start + 3
        ]:

            content = canvas.get(
                section,
                ""
            ).strip()


            if not content:

                content = "Not provided"


            content = (
                content
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\n", "<br/>")
            )


            cell = [

                Paragraph(
                    section,
                    heading_style
                ),

                Spacer(1, 4),

                Paragraph(
                    content,
                    body_style
                )
            ]


            row.append(cell)


        rows.append(row)


    table = Table(

        rows,

        colWidths=[
            250,
            250,
            250
        ],

        rowHeights=[
            150,
            150,
            150
        ]
    )


    table.setStyle(

        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.HexColor("#555555")
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )


    story.append(table)


    document.build(story)


    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# HEADER
# ============================================================

st.title(
    "📊 Lean Business Model Canvas Automation Tool"
)

st.caption(
    "Your work is automatically saved to the local database."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "⚙️ Business Information"
    )


    business_name = st.text_input(

        "Business / Startup Name",

        key="business_name",

        on_change=lambda:
            autosave_field(
                "business_name",
                st.session_state.business_name
            )
    )


    industry = st.text_input(

        "Industry",

        key="industry",

        on_change=lambda:
            autosave_field(
                "industry",
                st.session_state.industry
            )
    )


    st.divider()


    st.success(
        "💾 Auto-save is ON"
    )


    st.caption(
        "Changes are saved automatically when you leave a field."
    )


    if st.button(
        "🧹 Clear Everything",
        use_container_width=True
    ):

        clear_database()


        for section in SECTIONS:

            st.session_state[
                f"canvas_{section}"
            ] = ""


        st.session_state.business_name = ""

        st.session_state.industry = ""


        st.rerun()


# ============================================================
# BUILD CANVAS
# ============================================================

build_tab, preview_tab, ai_tab, saved_tab = st.tabs(

    [
        "✍️ Build Canvas",
        "📋 Preview",
        "🤖 AI Insights",
        "💾 Saved Data"
    ]
)


with build_tab:

    st.header(
        "1️⃣ Build Your Lean Canvas"
    )


    st.write(
        "Enter your business information. "
        "Every change is automatically saved."
    )


    canvas = {}


    columns = st.columns(3)


    for index, section in enumerate(
        SECTIONS
    ):

        with columns[index % 3]:

            key = f"canvas_{section}"


            canvas[section] = st.text_area(

                section,

                key=key,

                height=140,

                placeholder=SECTION_HELP[
                    section
                ],

                help=SECTION_HELP[
                    section
                ],

                on_change=autosave_canvas,

                args=(
                    st.session_state.business_name,
                    st.session_state.industry,
                    {
                        s: st.session_state.get(
                            f"canvas_{s}",
                            ""
                        )

                        for s in SECTIONS
                    }
                )
            )


    # --------------------------------------------------------
    # EXTRA AUTO-SAVE
    # --------------------------------------------------------

    # Save the complete current state
    # after every Streamlit interaction.

    autosave_canvas(

        st.session_state.business_name,

        st.session_state.industry,

        {
            s: st.session_state.get(
                f"canvas_{s}",
                ""
            )

            for s in SECTIONS
        }
    )


    # --------------------------------------------------------
    # COMPLETENESS
    # --------------------------------------------------------

    completeness = calculate_completeness(
        canvas
    )


    st.divider()


    col1, col2, col3 = st.columns(3)


    completed = sum(

        bool(
            canvas[s].strip()
        )

        for s in SECTIONS
    )


    col1.metric(
        "Completeness",
        f"{completeness}%"
    )


    col2.metric(
        "Completed Blocks",
        f"{completed}/9"
    )


    if completeness == 100:

        status = "Complete"

    elif completeness >= 60:

        status = "Almost Ready"

    else:

        status = "Needs Input"


    col3.metric(
        "Status",
        status
    )


    if completeness == 100:

        st.success(
            "🎉 All 9 sections are complete!"
        )

    else:

        st.warning(
            "Some sections are still incomplete."
        )


# ============================================================
# PREVIEW
# ============================================================

with preview_tab:

    st.header(
        "2️⃣ Canvas Preview"
    )


    completeness = calculate_completeness(
        canvas
    )


    st.subheader(
        st.session_state.business_name
        or "Untitled Business"
    )


    st.caption(

        f"{st.session_state.industry or 'Industry not specified'}"
        f" • Completeness: {completeness}%"
    )


    for start in range(
        0,
        9,
        3
    ):

        row = st.columns(3)


        for column, section in zip(

            row,

            SECTIONS[
                start:start + 3
            ]
        ):

            with column:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### {section}"
                    )


                    value = canvas.get(
                        section,
                        ""
                    ).strip()


                    if value:

                        st.write(value)

                    else:

                        st.warning(
                            "Not provided"
                        )


    st.divider()


    # --------------------------------------------------------
    # CSV
    # --------------------------------------------------------

    dataframe = pd.DataFrame(

        [
            {
                "Section": section,

                "Content": canvas.get(
                    section,
                    ""
                )
            }

            for section in SECTIONS
        ]
    )


    st.download_button(

        "⬇️ Download CSV",

        dataframe.to_csv(
            index=False
        ).encode("utf-8"),

        file_name=
        "lean_business_model_canvas.csv",

        mime="text/csv",

        use_container_width=True
    )


    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    pdf = create_pdf(

        st.session_state.business_name,

        st.session_state.industry,

        canvas,

        completeness
    )


    if pdf:

        st.download_button(

            "📄 Download Professional PDF",

            pdf,

            file_name=
            "lean_business_model_canvas.pdf",

            mime="application/pdf",

            use_container_width=True
        )


# ============================================================
# AI INSIGHTS
# ============================================================

with ai_tab:

    st.header(
        "3️⃣ AI / Improvement Suggestions"
    )


    selected_section = st.selectbox(

        "Choose a Canvas Section",

        SECTIONS
    )


    current_content = canvas.get(
        selected_section,
        ""
    )


    if current_content.strip():

        st.info(
            current_content
        )

    else:

        st.warning(
            "This section is currently empty."
        )


    if st.button(
        "✨ Generate Suggestions",
        type="primary"
    ):

        suggestions, source = (
            generate_ai_suggestions(

                selected_section,

                current_content,

                st.session_state.industry
            )
        )


        st.caption(
            f"Source: {source}"
        )


        for suggestion in suggestions:

            st.write(
                "• " + suggestion
            )


# ============================================================
# SAVED DATA
# ============================================================

with saved_tab:

    st.header(
        "4️⃣ Auto-Saved Data"
    )


    saved = load_canvas()


    st.success(
        "💾 Your latest canvas is stored automatically."
    )


    saved_dataframe = pd.DataFrame({

        "Field": [

            "Business Name",

            "Industry"

        ] + SECTIONS,

        "Saved Value": [

            saved["business_name"],

            saved["industry"]

        ] + [

            saved[section]

            for section in SECTIONS
        ]
    })


    st.dataframe(

        saved_dataframe,

        use_container_width=True,

        hide_index=True
    )


    st.download_button(

        "⬇️ Download Complete Canvas Data",

        saved_dataframe.to_csv(
            index=False
        ).encode("utf-8"),

        file_name=
        "auto_saved_canvas_data.csv",

        mime="text/csv",

        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()


st.caption(
    "Entrepreneurship Project 4 • "
    "Lean Business Model Canvas Automation Tool • "
    "Auto-save enabled"
)