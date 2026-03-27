"""Normalized tool / function definitions for OpenAI (chat tools) and Anthropic (tools).

Use :class:`ToolDefinition` as the single in-app DTO, then convert at the provider boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(slots=True)
class ToolDefinition:
    """Provider-neutral tool: JSON Schema ``parameters`` matches OpenAI ``parameters``
    and Anthropic ``input_schema``.
    """

    name: str
    description: str
    parameters: Dict[str, Any]

    def to_openai_tool(self) -> Dict[str, Any]:
        """OpenAI Chat Completions ``tools[]`` entry (``type: function``)."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def to_anthropic_tool(self) -> Dict[str, Any]:
        """Anthropic ``tools`` entry (``input_schema``)."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }


def tool_definitions_to_openai_tools(tools: List[ToolDefinition]) -> List[Dict[str, Any]]:
    """Execute tool_definitions_to_openai_tools operation.

    Args:
        tools: The tools parameter.

    Returns:
        The result of the operation.
    """
    return [t.to_openai_tool() for t in tools]


def tool_definitions_to_anthropic_tools(tools: List[ToolDefinition]) -> List[Dict[str, Any]]:
    """Execute tool_definitions_to_anthropic_tools operation.

    Args:
        tools: The tools parameter.

    Returns:
        The result of the operation.
    """
    return [t.to_anthropic_tool() for t in tools]


def tool_definition_from_openai(tool: Dict[str, Any]) -> ToolDefinition:
    """Parse OpenAI ``tools[]`` or ``tool_calls`` tool spec."""
    if tool.get("type") == "function" and isinstance(tool.get("function"), dict):
        fn = tool["function"]
    else:
        fn = tool
    name = str(fn.get("name") or "")
    desc = str(fn.get("description") or "")
    params = fn.get("parameters")
    if not isinstance(params, dict):
        params = {"type": "object", "properties": {}}
    return ToolDefinition(name=name, description=desc, parameters=params)


def tool_definition_from_anthropic(tool: Dict[str, Any]) -> ToolDefinition:
    """Parse Anthropic ``tools`` entry."""
    name = str(tool.get("name") or "")
    desc = str(tool.get("description") or "")
    schema = tool.get("input_schema")
    if not isinstance(schema, dict):
        schema = {"type": "object", "properties": {}}
    return ToolDefinition(name=name, description=desc, parameters=schema)


def normalize_tools_to_openai(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Accept either OpenAI-shaped or Anthropic-shaped dicts; return OpenAI ``tools[]`` entries."""
    out: List[Dict[str, Any]] = []
    for t in tools:
        if t.get("type") == "function" or "function" in t:
            out.append(tool_definition_from_openai(t).to_openai_tool())
        elif "input_schema" in t:
            out.append(tool_definition_from_anthropic(t).to_openai_tool())
        else:
            out.append(tool_definition_from_openai(t).to_openai_tool())
    return out


def normalize_tools_to_anthropic(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Accept either shape; return Anthropic ``tools`` entries."""
    out: List[Dict[str, Any]] = []
    for t in tools:
        if "input_schema" in t and "name" in t:
            out.append(tool_definition_from_anthropic(t).to_anthropic_tool())
        else:
            out.append(tool_definition_from_openai(t).to_anthropic_tool())
    return out
