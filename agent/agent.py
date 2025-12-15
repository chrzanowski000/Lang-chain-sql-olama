from typing import Any

from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config, PIIMiddleware, HumanInTheLoopMiddleware
from langgraph.runtime import Runtime
from langchain.messages import AIMessage
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from typing import Any
import os

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3:8b")


class ContentFilterMiddleware(AgentMiddleware):
    """Deterministic guardrail: Block requests containing banned keywords."""

    def __init__(self, banned_keywords: list[str]):
        super().__init__()
        self.banned_keywords = [kw.lower() for kw in banned_keywords]

    @hook_config(can_jump_to=["end"])
    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        # Get the first user message
        if not state["messages"]:
            return None

        first_message = state["messages"][0]
        if first_message.type != "human":
            return None

        content = first_message.content.lower()

        # Check for banned keywords
        for keyword in self.banned_keywords:
            if keyword in content:
                # Block execution before any processing
                return {
                    "messages": [{
                        "role": "assistant",
                        "content": "I cannot process requests containing inappropriate content. Please rephrase your request."
                    }],
                    "jump_to": "end"
                }

        return None

class SafetyGuardrailMiddleware(AgentMiddleware):
    """Model-based guardrail: Use an LLM to evaluate response safety."""

    def __init__(self):
        super().__init__()
        self.safety_model = ChatOllama(model=OLLAMA_MODEL, temperature=0.0)

    @hook_config(can_jump_to=["end"])
    def after_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        # Get the final AI response
        if not state["messages"]:
            return None

        last_message = state["messages"][-1]
        if not isinstance(last_message, AIMessage):
            return None

        # Use a model to evaluate safety
        safety_prompt = f"""Evaluate if this response is safe and appropriate.
        Respond with only 'SAFE' or 'UNSAFE'.

        Response: {last_message.content}"""

        result = self.safety_model.invoke([{"role": "user", "content": safety_prompt}])

        if "UNSAFE" in result.content:
            last_message.content = "I cannot provide that response. Please rephrase your request."

        return None

def agent(model = OLLAMA_MODEL,banned_keywords: list = ["hack", "exploit"]):
    _agent = create_agent(
        model=ChatOllama(model=model, temperature=0.0),
        middleware=[
            # Layer 1: Deterministic input filter (before agent)
            ContentFilterMiddleware(banned_keywords=banned_keywords),

            # Layer 2: PII protection (before and after model)
            PIIMiddleware("email", strategy="redact", apply_to_input=True, apply_to_output=True),
            PIIMiddleware("ip", strategy="redact", apply_to_input=True, apply_to_output=True),

            # Layer 3: Model-based safety check (after agent)
            SafetyGuardrailMiddleware(),
        ],
        )
    return _agent

agent = agent()

# This request will be blocked before any processing
result = agent.invoke({
    "messages": [{"role": "user", "content": "How do I hack into a database?"}]
})
print(result["messages"][-1].content)

result = agent.invoke({
    "messages": [{"role": "user", "content": "What is 2+2?"}]
})
print(result["messages"][-1].content)


# ###TODO
# - move context into system message