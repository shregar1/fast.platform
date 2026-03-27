"""AI Agent framework for FastMVC."""

from typing import List, Dict, Any, Callable, Optional, AsyncIterator
from dataclasses import dataclass, field
from functools import wraps
import json
import asyncio


@dataclass
class Tool:
    """A tool that an agent can use."""

    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable

    def to_schema(self) -> Dict[str, Any]:
        """Convert to function schema for LLM."""
        return {"name": self.name, "description": self.description, "parameters": self.parameters}


@dataclass
class AgentContext:
    """Context for agent execution."""

    agent_id: str
    conversation_id: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Execution tracking
    step_count: int = 0
    max_steps: int = 10
    tools_used: List[str] = field(default_factory=list)

    def should_continue(self) -> bool:
        """Check if agent should continue executing."""
        return self.step_count < self.max_steps


def tool(name: Optional[str] = None, description: Optional[str] = None):
    """Decorator to mark a function as an agent tool.

    Args:
        name: Tool name (defaults to function name)
        description: Tool description (defaults to docstring)

    """

    def decorator(func: Callable) -> Tool:
        """Execute decorator operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """
        tool_name = name or func.__name__
        tool_description = description or (func.__doc__ or "")

        # Extract parameters from function signature
        import inspect

        sig = inspect.signature(func)
        parameters = {"type": "object", "properties": {}, "required": []}

        for param_name, param in sig.parameters.items():
            param_type = "string"  # Default
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == str:
                    param_type = "string"
                elif param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"

            parameters["properties"][param_name] = {"type": param_type}

            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)

        return Tool(
            name=tool_name, description=tool_description, parameters=parameters, handler=func
        )

    return decorator


class Agent:
    """AI Agent with tool use and memory."""

    def __init__(
        self,
        name: str,
        model: str = "gpt-4",
        tools: Optional[List[Tool]] = None,
        system_prompt: Optional[str] = None,
        memory: Optional[Any] = None,
        max_steps: int = 10,
        provider: Optional[Any] = None,
    ):
        """Execute __init__ operation.

        Args:
            name: The name parameter.
            model: The model parameter.
            tools: The tools parameter.
            system_prompt: The system_prompt parameter.
            memory: The memory parameter.
            max_steps: The max_steps parameter.
            provider: The provider parameter.
        """
        self.name = name
        self.model = model
        self.tools = tools or []
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.memory = memory
        self.max_steps = max_steps
        self.provider = provider

    async def run(
        self, query: str, context: Optional[AgentContext] = None, stream: bool = False
    ) -> str:
        """Run the agent with a query.

        Args:
            query: User query
            context: Optional execution context
            stream: Whether to stream the response

        Returns:
            Agent response

        """
        ctx = context or AgentContext(agent_id=self.name, conversation_id="default")
        ctx.max_steps = self.max_steps

        # Load conversation history
        history = []
        if self.memory:
            history = await self.memory.get_messages(ctx.conversation_id)

        # Add user query
        messages = [
            {"role": "system", "content": self.system_prompt},
            *history,
            {"role": "user", "content": query},
        ]

        # Execute with tool loop
        final_response = ""
        while ctx.should_continue():
            response = await self._call_llm(messages, tools=self.tools)

            if response.get("tool_calls"):
                # Execute tools
                for tool_call in response["tool_calls"]:
                    result = await self._execute_tool(tool_call, ctx)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(result),
                        }
                    )
                ctx.step_count += 1
            else:
                # Final response
                final_response = response.get("content", "")
                break

        # Save to memory
        if self.memory:
            await self.memory.add_message(ctx.conversation_id, "user", query)
            await self.memory.add_message(ctx.conversation_id, "assistant", final_response)

        return final_response

    async def _call_llm(
        self, messages: List[Dict[str, str]], tools: Optional[List[Tool]] = None
    ) -> Dict[str, Any]:
        """Call the LLM provider."""
        if self.provider:
            return await self.provider.complete(messages, tools)

        # Default mock implementation
        return {"content": "Mock LLM response"}

    async def _execute_tool(self, tool_call: Dict[str, Any], context: AgentContext) -> Any:
        """Execute a tool call."""
        tool_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])

        # Find tool
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            return {"error": f"Tool {tool_name} not found"}

        # Track usage
        context.tools_used.append(tool_name)

        # Execute
        try:
            if asyncio.iscoroutinefunction(tool.handler):
                result = await tool.handler(**arguments)
            else:
                result = tool.handler(**arguments)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


def agent(
    model: str = "gpt-4",
    tools: Optional[List[Tool]] = None,
    memory: bool = False,
    system_prompt: Optional[str] = None,
    max_steps: int = 10,
):
    """Decorator to create an AI agent.

    Args:
        model: LLM model to use
        tools: List of tools available to the agent
        memory: Whether to enable conversation memory
        system_prompt: System prompt for the agent
        max_steps: Maximum number of tool execution steps

    """

    def decorator(func: Callable) -> Agent:
        """Execute decorator operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """
        # Extract tools from function attributes
        agent_tools = tools or []

        # Create agent
        agent_instance = Agent(
            name=func.__name__,
            model=model,
            tools=agent_tools,
            system_prompt=system_prompt or func.__doc__,
            max_steps=max_steps,
        )

        # Bind the function as the run method
        @wraps(func)
        async def wrapper(query: str, **kwargs):
            """Execute wrapper operation.

            Args:
                query: The query parameter.

            Returns:
                The result of the operation.
            """
            return await agent_instance.run(query, **kwargs)

        wrapper._agent = agent_instance
        return wrapper

    return decorator
