import asyncio
import os
import sys
import gradio as gr
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI
from agents.mcp import MCPServerStdio
from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
    gen_trace_id,
    trace
)

# Set up environment variables for Azure OpenAI
AOAI_API_BASE = os.getenv("AZURE_OPENAI_API_BASE")
AOAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AOAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_API_DEPLOY")

# Disable debug tracing (OPTIONAL)
set_tracing_disabled(True)

# Initialise global variables to manage session state
agent = None
mcp_server = None
current_thread_id = None
previous_result = None

# Create event loop for Gradio app
event_loop = asyncio.new_event_loop()
asyncio.set_event_loop(event_loop)

# Helper function to process user input and run the agent
async def process_user_input(user_input, history):
    global agent, previous_result, current_thread_id
    
    if agent is None:
        return history + [
            {"role": "user", "content": user_input, "avatar": "👤"},
            {"role": "assistant", "content": "Agent not initialised. Please restart the application.", "avatar": "🤖"}
        ], ""
    
    # If this is a new conversation
    if previous_result is None:
        current_thread_id = gen_trace_id()
    
    # Process the input
    with trace(workflow_name="Conversation", group_id=current_thread_id):
        if previous_result:
            # Add new user message to the previous conversation
            input_messages = previous_result.to_input_list() + [{"role": "user", "content": user_input}]
            result = await Runner.run(starting_agent=agent, input=input_messages)
        else:
            # First message in the conversation
            result = await Runner.run(starting_agent=agent, input=user_input)
    
    # Update previous result for next turn
    previous_result = result
    
    history.append({"role": "user", "content": user_input, "avatar": "👤"})
    history.append({"role": "assistant", "content": result.final_output, "avatar": "🤖"})
    return history, ""  # Return empty string to clear the textbox

# Helper function to reset conversation
def reset_conversation():
    global previous_result, current_thread_id
    previous_result = None
    current_thread_id = gen_trace_id()
    return [], "Conversation has been reset. You can start a new chat."

# Helper function to initialise MCP client
async def initialise_agent():
    global agent, mcp_server
    
    # Get local credentials
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default"
    )
    
    # Initialise AOAI client
    aoai_client = AsyncAzureOpenAI(
        api_version=AOAI_API_VERSION,
        azure_endpoint=AOAI_API_BASE,
        azure_ad_token_provider=token_provider
    )
    
    # Create AI agent
    agent = Agent(
        name = "Assistant",
        instructions = "Use the tools to answer the questions. Maintain context from previous messages in the conversation.",
        model = OpenAIChatCompletionsModel(
            model = AOAI_DEPLOYMENT,
            openai_client = aoai_client,
        ),
        mcp_servers = [mcp_server],
    )
    
    return "AI Agent initialised successfully!"

# Helper function to start MCP server
async def start_mcp_server():
    global mcp_server
    
    # Path to MCP server script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(current_dir, "MCP_Server_GraphQL.py")
    
    mcp_server = MCPServerStdio(
        name = "FastMCP Local Server",
        params = {
            "command": sys.executable,  # Python interpreter
            "args": [server_script],    # Your MCP server script
        },
        cache_tools_list=True
    )
    
    await mcp_server.__aenter__()
    return "MCP server started successfully!"

# Wrapper for Gradio to handle asyncio without creating new event loops
def gradio_chat(user_input, history):
    # Use the global event loop instead of creating a new one
    return event_loop.run_until_complete(
        process_user_input(user_input, history)
    )

# Initialise MCP server and AI agent
def initialise_backend():
    server_status = event_loop.run_until_complete(start_mcp_server())
    agent_status = event_loop.run_until_complete(initialise_agent())
    return f"{server_status}\n{agent_status}\nSystem is ready to use!"

# Helper function for clean shutdown
def shutdown():
    if mcp_server is not None:
        event_loop.run_until_complete(mcp_server.__aexit__(None, None, None))
    event_loop.close()

# Create Gradio app
def create_gradio_app():
    with gr.Blocks(title="Demo MCP Connector for Fabric") as app:
        with gr.Row():
            with gr.Column(scale=3):
                gr.Markdown("# Demo MCP Connector for Microsoft Fabric")
                gr.Markdown("AI agent's two-way integration with your enterprise Data Warehouse.")
            
            with gr.Column(scale=1):
                init_button = gr.Button("Initialise System", variant="primary")
                status_text = gr.Textbox(label="System Status", value="System not initialised. Click 'Initialise System' to start.")
        
        # Chatbot area
        chatbot = gr.Chatbot(
            height = 300, 
            type = "messages", 
            show_label = False,
            avatar_images = ["avatars/Avatar_Human.png", "avatars/Avatar_Bot.png"]
        )
        
        with gr.Row():
            with gr.Column(scale=7):
                msg = gr.Textbox(
                    label = "Type your message here",
                    placeholder = "Ask me anything...",
                    lines = 2,
                    show_label = False
                )
            with gr.Column(scale=1):
                submit_btn = gr.Button("Submit", variant="primary")
            with gr.Column(scale=1):
                reset_btn = gr.Button("Reset Chat", variant="secondary")
        
        # Connect app components with their functions
        submit_btn.click(gradio_chat, [msg, chatbot], [chatbot, msg])
        msg.submit(gradio_chat, [msg, chatbot], [chatbot, msg])
        reset_btn.click(reset_conversation, None, [chatbot, status_text])
        init_button.click(initialise_backend, None, status_text)
        
        # Add a closing event handler
        app.load(lambda: None)  # This prevents automatic closing of the event loop
        
    return app

# Main function to launch the Gradio app
def main():
    try:
        app = create_gradio_app()
        app.launch(share=False)  # Set share=True if you want to create a public link
    finally:
        # Ensure proper shutdown
        shutdown()

if __name__ == "__main__":
    main()