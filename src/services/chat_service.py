# src/services/chat_service.py

from agent.agent                        import agent
from utils.exceptions.custom_exceptions import BrewBaseException
from utils.exceptions.error_codes       import ErrorCodes


conversation_history = []




class ChatService:

    # handle_prompt 
    def handle_prompt(self, request) -> str:
        try:
            global conversation_history

            # Step 1 — append user message to conversation history
            conversation_history.append({
                "role"   : "user",
                "content": request.prompt
            })

            print("\n Brew Buddy: ", end="", flush=True)

            full_reply = ""

            # Step 2 — stream agent response token by token
            for chunk in agent.stream({
                "messages": conversation_history    # pass full history for multi-turn context
            }):
                if "agent" in chunk:
                    content = chunk["agent"]["messages"][-1].content

                    # content can be plain string
                    if isinstance(content, str):
                        if content:
                            print(content, end="", flush=True)  
                            full_reply += content               

                    # content can be list of blocks — extract only text blocks
                    elif isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                text = block.get("text", "")
                                if text:
                                    print(text, end="", flush=True)  
                                    full_reply += text               

            print("\n")     

            # Step 3 — append assistant reply to history for next turn context
            conversation_history.append({
                "role"   : "assistant",
                "content": full_reply
            })

            return full_reply   # return full reply as JSON to client

        except BrewBaseException:
            raise 
        except Exception as e:

            raise BrewBaseException(
                status_code = 500,
                error_code  = ErrorCodes.BB_AGENT_001,
                message     = f"Agent failed to process request: {str(e)}"
            )
