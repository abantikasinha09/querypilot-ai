import os
import sys
import argparse

from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from rich.console import Console
from rich.panel import Panel

from download_database import download_database


# ---------------------------------------------------------
# Environment setup
# ---------------------------------------------------------

load_dotenv()

console = Console()


# ---------------------------------------------------------
# System prompt
# ---------------------------------------------------------

SYSTEM_PROMPT = """
You are an agent designed to interact with a SQL database.

Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer.

Unless the user specifies a specific number of examples they wish to obtain,
always limit your query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database.

Never query for all the columns from a specific table.
Only ask for the relevant columns given the question.

You MUST double check your query before executing it.

If you get an error while executing the query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you can query.

Do NOT skip this step.

Then you should query the schema of the most relevant tables.
"""


# ---------------------------------------------------------
# Create SQL Agent
# ---------------------------------------------------------

def create_sql_agent():

    # Make sure the database exists before creating the agent
    download_database()

    db_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "chinook.db"
    )

    db = SQLDatabase.from_uri(
        f"sqlite:///{db_path}",
        sample_rows_in_table_info=3
    )

    model = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0
    )

    toolkit = SQLDatabaseToolkit(
        db=db,
        llm=model
    )

    tools = toolkit.get_tools()

    agent = create_agent(
        model,
        tools,
        system_prompt=SYSTEM_PROMPT.format(
            dialect=db.dialect,
            top_k=5
        )
    )

    return agent


# ---------------------------------------------------------
# Main application
# ---------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="Text-to-SQL Agent powered by LangChain and Groq",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py "What are the top 5 best-selling artists?"
  python agent.py "Which employee generated the most revenue?"
  python agent.py "How many customers are from Canada?"
        """
    )

    parser.add_argument(
        "question",
        type=str,
        help="Natural language question to answer using the Chinook database"
    )

    args = parser.parse_args()

    # -----------------------------------------------------
    # Display question
    # -----------------------------------------------------

    console.print(
        Panel(
            f"[bold cyan]Question:[/bold cyan] {args.question}",
            border_style="cyan"
        )
    )

    console.print()

    # -----------------------------------------------------
    # Create agent
    # -----------------------------------------------------

    console.print("[dim]Creating SQL Agent...[/dim]")

    agent = create_sql_agent()

    console.print("[dim]Processing query...[/dim]\n")

    # -----------------------------------------------------
    # Execute question
    # -----------------------------------------------------

    try:

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": args.question
                    }
                ]
            }
        )

        # -------------------------------------------------
        # Display generated SQL
        # -------------------------------------------------

        console.print(
            "[bold yellow]Generated SQL:[/bold yellow]"
        )

        sql_found = False

        for message in result["messages"]:

            if hasattr(message, "tool_calls") and message.tool_calls:

                for tool_call in message.tool_calls:

                    if tool_call["name"] == "sql_db_query":

                        sql_found = True

                        query = tool_call["args"]["query"]

                        console.print(
                            Panel(
                                query,
                                border_style="yellow"
                            )
                        )

        if not sql_found:

            console.print(
                "[dim]No SQL query was directly exposed by the agent.[/dim]"
            )

        console.print()

        # -------------------------------------------------
        # Display final answer
        # -------------------------------------------------

        final_message = result["messages"][-1]

        answer = (
            final_message.content
            if hasattr(final_message, "content")
            else str(final_message)
        )

        console.print(
            Panel(
                f"[bold green]Answer:[/bold green]\n\n{answer}",
                border_style="green"
            )
        )

    # -----------------------------------------------------
    # Error handling
    # -----------------------------------------------------

    except Exception as e:

        console.print(
            Panel(
                f"[bold red]Error:[/bold red]\n\n{str(e)}",
                border_style="red"
            )
        )

        sys.exit(1)


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()