import os
import re

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, inspect, text

from agent import create_sql_agent


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="QueryPilot AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.8rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .subtitle {
            font-size: 1.1rem;
            color: #777;
            margin-bottom: 2rem;
        }

        .section-title {
            font-size: 1.4rem;
            font-weight: 600;
        }

        .feature-card {
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid rgba(128, 128, 128, 0.25);
            margin-bottom: 1rem;
        }

        .footer {
            text-align: center;
            padding: 25px 0 10px 0;
            color: #888;
            font-size: 0.9rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "query_history" not in st.session_state:
    st.session_state.query_history = []

if "selected_example" not in st.session_state:
    st.session_state.selected_example = ""


# ============================================================
# DATABASE PATH
# ============================================================

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "chinook.db"
)


# ============================================================
# SQL SAFETY
# ============================================================

FORBIDDEN_SQL_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "REPLACE",
    "TRUNCATE",
    "ATTACH",
    "DETACH",
    "VACUUM",
    "PRAGMA",
]


def is_safe_read_only_query(sql_query):
    """
    Check whether a generated SQL statement is safe
    for read-only execution.
    """

    if not sql_query:
        return False, "No SQL query was generated."

    query = sql_query.strip()

    if not query:
        return False, "The SQL query is empty."

    # Remove SQL comments before checking
    query_without_comments = re.sub(
        r"--.*?$|/\*.*?\*/",
        "",
        query,
        flags=re.MULTILINE | re.DOTALL
    ).strip()

    # Only SELECT or WITH queries are allowed
    if not re.match(
        r"^(SELECT|WITH)\b",
        query_without_comments,
        re.IGNORECASE
    ):
        return (
            False,
            "Only read-only SELECT or WITH queries are allowed."
        )

    # Check for dangerous SQL keywords
    for keyword in FORBIDDEN_SQL_KEYWORDS:

        if re.search(
            rf"\b{keyword}\b",
            query_without_comments,
            re.IGNORECASE
        ):
            return (
                False,
                f"Potentially unsafe SQL detected: {keyword}"
            )

    # Prevent multiple SQL statements
    statements = [
        statement.strip()
        for statement in query_without_comments.split(";")
        if statement.strip()
    ]

    if len(statements) > 1:
        return (
            False,
            "Multiple SQL statements are not allowed."
        )

    return True, "Safe read-only query."


# ============================================================
# LOAD AI AGENT
# ============================================================

@st.cache_resource
def load_agent():
    return create_sql_agent()


# ============================================================
# LOAD DATABASE
# ============================================================

@st.cache_resource
def load_database():
    if not os.path.exists(DB_PATH):
        return None

    engine = create_engine(
        f"sqlite:///{DB_PATH}"
    )

    return engine


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🤖 QueryPilot AI")

    st.caption(
        "Natural Language to SQL Analytics Assistant"
    )

    st.divider()

    # --------------------------------------------------------
    # ABOUT
    # --------------------------------------------------------

    st.subheader("📌 About")

    st.write(
        """
        **QueryPilot AI** is an AI-powered Text-to-SQL
        analytics assistant.

        It converts natural-language questions into SQL
        queries, executes read-only database operations,
        and presents the results through an interactive
        interface.
        """
    )

    st.divider()

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    st.subheader("🗄️ Database")

    st.write("**Database:** Chinook SQLite")
    st.write("**Engine:** SQLite")
    st.write("**Mode:** Read-only")

    st.divider()

    # --------------------------------------------------------
    # TECHNOLOGY
    # --------------------------------------------------------

    st.subheader("🛠️ Technology")

    st.markdown(
        """
        - **Python**
        - **LangChain**
        - **Groq LLM**
        - **SQLite**
        - **SQLAlchemy**
        - **Streamlit**
        - **Pandas**
        """
    )

    st.divider()

    # --------------------------------------------------------
    # SECURITY
    # --------------------------------------------------------

    st.subheader("🛡️ Security")

    st.success(
        "Read-only SQL mode enabled"
    )

    st.caption(
        "QueryPilot AI blocks INSERT, UPDATE, DELETE, "
        "DROP and other destructive SQL operations "
        "during result execution."
    )

    st.divider()

    # --------------------------------------------------------
    # DATABASE EXPLORER
    # --------------------------------------------------------

    st.subheader("🔎 Database Explorer")

    engine = load_database()

    if engine is not None:

        try:
            inspector = inspect(engine)

            tables = inspector.get_table_names()

            st.write(
                f"**{len(tables)} tables available**"
            )

            selected_table = st.selectbox(
                "Select a table",
                tables
            )

            if selected_table:

                columns = inspector.get_columns(
                    selected_table
                )

                column_names = [
                    column["name"]
                    for column in columns
                ]

                st.caption("Columns")

                for column in column_names:
                    st.write(f"• `{column}`")

        except Exception as e:

            st.warning(
                f"Unable to inspect database: {e}"
            )

    else:

        st.error(
            "chinook.db was not found."
        )


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🤖 QueryPilot AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Ask your database questions in plain English.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# FEATURE INTRO
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="feature-card">
        <b>💬 Natural Language</b><br>
        Ask questions without writing SQL.
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="feature-card">
        <b>⚡ AI-Powered SQL</b><br>
        QueryPilot generates SQL automatically.
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="feature-card">
        <b>📊 Instant Insights</b><br>
        View results and automatic visualizations.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# QUESTION SECTION
# ============================================================

st.subheader("💬 Ask QueryPilot")

question = st.text_input(
    "Your question",
    value=st.session_state.selected_example,
    placeholder="Ask QueryPilot anything about your database..."
)


# ============================================================
# EXAMPLE QUESTIONS
# ============================================================

st.caption("Try an example:")

example_questions = [
    "Which country has the most customers?",
    "What are the top 5 best-selling tracks?",
    "How many customers are from Canada?",
    "Which employee generated the most revenue?",
]


example_columns = st.columns(4)

for index, example in enumerate(example_questions):

    with example_columns[index]:

        if st.button(
            example,
            key=f"example_{index}",
            width="stretch"
        ):

            st.session_state.selected_example = example

            st.rerun()


# ============================================================
# RUN QUERY
# ============================================================

st.write("")

run_query = st.button(
    "🚀 Ask QueryPilot",
    type="primary",
    width="stretch"
)


# ============================================================
# QUERY EXECUTION
# ============================================================

if run_query:

    if not question.strip():

        st.warning(
            "Please enter a question first."
        )

    else:

        st.session_state.selected_example = ""

        # ----------------------------------------------------
        # CREATE AGENT
        # ----------------------------------------------------

        with st.spinner(
            "🤖 QueryPilot is analyzing your question..."
        ):

            try:

                agent = load_agent()

                result = agent.invoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": question
                            }
                        ]
                    }
                )

            except Exception as e:

                st.error(
                    f"QueryPilot encountered an error: {e}"
                )

                st.stop()


        # ====================================================
        # EXTRACT SQL
        # ====================================================

        generated_sql = None

        for message in result["messages"]:

            if (
                hasattr(message, "tool_calls")
                and message.tool_calls
            ):

                for tool_call in message.tool_calls:

                    if tool_call["name"] == "sql_db_query":

                        generated_sql = (
                            tool_call["args"]
                            .get("query")
                        )

                        break

            if generated_sql:
                break


        # ====================================================
        # ANSWER
        # ====================================================

        final_message = result["messages"][-1]

        answer = (
            final_message.content
            if hasattr(final_message, "content")
            else str(final_message)
        )


        # ====================================================
        # DISPLAY ANSWER
        # ====================================================

        st.subheader("💡 QueryPilot's Answer")

        st.success(answer)


        # ====================================================
        # GENERATED SQL
        # ====================================================

        if generated_sql:

            st.subheader("🔍 Generated SQL")

            st.code(
                generated_sql,
                language="sql"
            )

        else:

            st.info(
                "No SQL query was directly exposed by the agent."
            )


        # ====================================================
        # SQL SAFETY CHECK
        # ====================================================

        query_results = None
        sql_is_safe = False
        safety_message = ""

        if generated_sql:

            sql_is_safe, safety_message = (
                is_safe_read_only_query(
                    generated_sql
                )
            )

            if sql_is_safe:

                st.success(
                    "🛡️ SQL Safety Check Passed — "
                    "read-only query."
                )

            else:

                st.error(
                    "🛡️ SQL Safety Check Failed"
                )

                st.warning(
                    safety_message
                )

                st.info(
                    "QueryPilot will not execute this "
                    "query through the result viewer."
                )


        # ====================================================
        # EXECUTE READ-ONLY QUERY
        # ====================================================

        if generated_sql and sql_is_safe:

            engine = load_database()

            if engine is not None:

                try:

                    with engine.connect() as connection:

                        query_results = pd.read_sql(
                            text(generated_sql),
                            connection
                        )

                    # ----------------------------------------
                    # QUERY RESULTS
                    # ----------------------------------------

                    st.subheader("📊 Query Results")

                    if query_results.empty:

                        st.info(
                            "The query returned no results."
                        )

                    else:

                        st.dataframe(
                            query_results,
                            width="stretch",
                            hide_index=True
                        )


                    # ========================================
                    # AUTOMATIC VISUALIZATION
                    # ========================================

                    if (
                        len(query_results) >= 2
                        and len(query_results.columns) >= 2
                    ):

                        numeric_columns = (
                            query_results.select_dtypes(
                                include="number"
                            ).columns.tolist()
                        )

                        non_numeric_columns = [
                            column
                            for column in query_results.columns
                            if column not in numeric_columns
                        ]

                        if (
                            numeric_columns
                            and non_numeric_columns
                        ):

                            category_column = (
                                non_numeric_columns[0]
                            )

                            value_column = (
                                numeric_columns[0]
                            )

                            chart_data = (
                                query_results[
                                    [
                                        category_column,
                                        value_column
                                    ]
                                ]
                                .set_index(
                                    category_column
                                )
                            )

                            st.subheader(
                                "📈 Visualization"
                            )

                            st.bar_chart(
                                chart_data,
                                width="stretch"
                            )

                except Exception as e:

                    st.error(
                        f"Unable to execute the generated "
                        f"SQL query: {e}"
                    )


        # ====================================================
        # QUERY HISTORY
        # ====================================================

        history_item = {
            "question": question,
            "sql": generated_sql,
            "answer": answer,
        }

        st.session_state.query_history.insert(
            0,
            history_item
        )

        # Keep only latest 10 queries
        st.session_state.query_history = (
            st.session_state.query_history[:10]
        )


        # ====================================================
        # TECHNICAL DETAILS
        # ====================================================

        with st.expander(
            "⚙️ Technical Details"
        ):

            st.write(
                "**Model:** Groq "
                "`openai/gpt-oss-120b`"
            )

            st.write(
                "**Framework:** LangChain"
            )

            st.write(
                "**Database:** SQLite / Chinook"
            )

            st.write(
                "**SQL Security:** "
                "Read-only query validation"
            )

            st.write(
                "**Query limit:** "
                "Maximum 5 results unless specified"
            )


# ============================================================
# QUERY HISTORY
# ============================================================

if st.session_state.query_history:

    st.divider()

    st.subheader("🕘 Query History")

    for index, item in enumerate(
        st.session_state.query_history
    ):

        with st.expander(
            f"{index + 1}. {item['question']}"
        ):

            st.markdown("**Answer**")

            st.write(
                item["answer"]
            )

            if item["sql"]:

                st.markdown(
                    "**Generated SQL**"
                )

                st.code(
                    item["sql"],
                    language="sql"
                )


    st.write("")

    if st.button(
        "🗑️ Clear Query History",
        width="content"
    ):

        st.session_state.query_history = []

        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        <b>QueryPilot AI</b> ·
        Natural Language to SQL Analytics Assistant
        <br><br>
        Built with Python · LangChain · Groq · SQLite · Streamlit
    </div>
    """,
    unsafe_allow_html=True
)