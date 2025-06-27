import chainlit as cl
from agents import Agent, OpenAIChatCompletionsModel, RunConfig, Runner, function_tool
from openai import AsyncOpenAI
from dotenv import load_dotenv
from gmail_service import get_gmail_service, fetch_recent_emails, move_to_trash
import os

# Load .env variables
load_dotenv()

# Load Gemini API key
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Create OpenAI-compatible Gemini provider
provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Model wrapper
model = OpenAIChatCompletionsModel(
    openai_client=provider,
    model="gemini-2.0-flash",
)


config = RunConfig(model=model, model_provider=provider, tracing_disabled=True)


# ------------------- Agent Tools -------------------


@function_tool
def is_junk(subject: str, sender: str, body: str) -> bool:
    """Decides if an email is junk. Returns True if junk, False if important."""
    if "unsubscribe" in body.lower() or "offer" in subject.lower():
        return True
    return False


@function_tool
def is_easy_response(subject: str, body: str) -> bool:
    """Returns True if response can be auto-generated. False if it needs human input."""
    keywords = ["status", "update", "meeting", "availability"]
    return any(word in body.lower() for word in keywords)


@function_tool
def write_reply(subject: str, body: str) -> str:
    """Returns a short, professional reply based on the email."""
    return (
        f"Thank you for your message about '{subject}'. I'll get back to you shortly."
    )


# ------------------- Agent Setup -------------------


email_agent = Agent(
    name="Email Agent",
    instructions="Classify emails as junk or not, then decide whether to auto-reply or forward to human. Use tools only.",
    tools=[is_junk, is_easy_response, write_reply],
)


# ------------------- Chainlit Handler -------------------


@cl.on_message
async def on_message(message: cl.Message):
    service = get_gmail_service()
    emails = fetch_recent_emails(service)

    await cl.Message(content=f"📨 Fetched {len(emails)} emails. Processing...").send()

    for email in emails:
        await cl.Message(content=f"🔍 Analyzing: **{email['subject']}**").send()

        agent_input = {
            "subject": email["subject"],
            "sender": email["sender"],
            "body": email["snippet"],
        }

        result = await Runner.run(
            email_agent, run_config=config, input=agent_input
        )

        if (
            "is_junk" in result.tool_calls
            and result.tool_calls["is_junk"].output is True
        ):
            move_to_trash(service, email["id"])
            await cl.Message(content="🗑️ Marked as junk and moved to trash.").send()
        else:
            if (
                "is_easy_response" in result.tool_calls
                and result.tool_calls["is_easy_response"].output is True
            ):
                reply = result.tool_calls["write_reply"].output
                await cl.Message(content=f"✉️ Auto-reply: \n\n{reply}").send()
            else:
                await cl.Message(content="🧠 Complex email. Leaving for human.").send()