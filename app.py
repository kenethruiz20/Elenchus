import os
import chainlit as cl
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Load environment variables from .env file
load_dotenv()

# --- Configuration for Literal AI (Data Persistence) ---
# Chainlit automatically picks up LITERAL_API_KEY from environment variables
# when literalai is installed. No explicit code needed here.

# --- Configuration for Google Authentication ---
# Chainlit automatically picks up OAUTH_GOOGLE_CLIENT_ID and OAUTH_GOOGLE_CLIENT_SECRET
# from environment variables when configured.
# You will need to define the OAuth callback in your app using a custom auth provider.
# For simplicity, Chainlit handles the basic Google OAuth flow if the env vars are set.
# A custom callback in your app.py would look something like this for more advanced cases:
# @cl.oauth_callback
# def oauth_google_callback(
#     provider_id: str,
#     token: str,
#     raw_user_data: dict,
#     default_user: cl.User,
# ) -> cl.User:
#     if provider_id == "google":
#         # You can enrich default_user with data from raw_user_data
#         # For example, setting the user's email or name
#         if "email" in raw_user_data:
#             default_user.metadata["email"] = raw_user_data["email"]
#         if "name" in raw_user_data:
#             default_user.metadata["name"] = raw_user_data["name"]
#     return default_user

# --- Initialize Google Gemini LLM ---
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY environment variable not set.")

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # Updated to current model name
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# --- Define your conversational chain ---
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful AI assistant powered by Google Gemini. Respond concisely and accurately."),
        ("human", "{input}"),
    ]
)

# Create a simple chain: Prompt -> LLM -> OutputParser
chain = prompt | llm | StrOutputParser()

# Usa la instancia FastAPI de Chainlit si existe, si no, crea una nueva
try:
    app = cl.server.app  # Chainlit >= 0.7.0
except AttributeError:
    app = FastAPI()

@app.post("/api/chat")
async def chat_api(request: Request):
    data = await request.json()
    user_message = data.get("content", "")
    if not user_message:
        return JSONResponse({"content": "No message provided."}, status_code=400)

    # Crea el chain directamente (no uses user_session)
    chain = prompt | llm | StrOutputParser()
    response = await chain.ainvoke({"input": user_message})
    return {"content": response}

@cl.on_chat_start
async def start():
    """
    This function is called when a new chat session is started.
    It can be used to send a welcome message or initialize session-specific data.
    """
    await cl.Message(
        content="Hello! I am your AI assistant, powered by Google Gemini. How can I help you today?"
    ).send()

    # Store the chain in the user session for later use
    cl.user_session.set("chain", chain)

@cl.on_message
async def main(message: cl.Message):
    """
    This function is called every time a user sends a message.
    It retrieves the chain and processes the user's input.
    """
    # Retrieve the chain from the user session
    chain = cl.user_session.get("chain")

    # Create a message element to stream the response
    msg = cl.Message(content="")

    async for chunk in chain.astream(
        {"input": message.content},
        config={"callbacks": [cl.LangchainCallbackHandler()]}
    ):
        await msg.stream_token(chunk)

    await msg.send() 