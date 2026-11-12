"""The AcmeBot agent: a LangChain tool-calling agent with three tools, wrapped by the tool guard."""
from __future__ import annotations

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import StructuredTool
from langgraph.errors import GraphRecursionError

from app import approvals, tools
from app.context import RequestContext
from app.guards import ToolDecision, runtime_guard, tool_guard
from app.llm import get_chat_model
from app.prompts import SYSTEM_PROMPT


def _wrap(name: str, description: str, schema, raw_fn, ctx: RequestContext) -> StructuredTool:
    """Every tool call goes through tool_guard.authorize() first. Fail closed on guard errors."""

    def run(**kwargs) -> str:
        entry = {"name": name, "args": kwargs, "status": "executed", "result": ""}
        ctx.trace.tool_calls.append(entry)
        try:
            decision = tool_guard.authorize(name, kwargs, ctx)
        except Exception as exc:  # noqa: BLE001 - a broken guard must not mean "allow"
            decision = ToolDecision(allow=False, reason=f"guard error: {exc}")
        if not decision.allow:
            entry.update(status="blocked", result=decision.reason)
            ctx.trace.event("tool", "blocked", f"{name}: {decision.reason}")
            return f"BLOCKED by security policy: {decision.reason}"
        if decision.needs_approval:
            aid = approvals.create(name, kwargs, ctx.session_id)
            entry.update(status="pending_approval", result=f"approval id {aid}")
            ctx.trace.event("tool", "needs_approval", f"{name} -> approval {aid}")
            return f"Action queued for human approval (id={aid}). It has NOT been executed yet."
        try:
            result = raw_fn(**kwargs)
        except Exception as exc:  # noqa: BLE001
            entry.update(status="error", result=str(exc)[:300])
            return f"ERROR: {exc}"
        entry["result"] = result[:500]
        return result

    return StructuredTool.from_function(func=run, name=name, description=description, args_schema=schema)


def build_tools(ctx: RequestContext) -> list[StructuredTool]:
    return [
        _wrap(
            "sql_query",
            "Run one SQL statement against the Acme SQLite database and return the rows as JSON.",
            tools.SqlArgs,
            lambda query: tools.sql_query(query, tool_guard.sql_policy()),
            ctx,
        ),
        _wrap(
            "send_email",
            "Send an email on behalf of Acme Store.",
            tools.EmailArgs,
            lambda to, subject, body: tools.send_email(to, subject, body, ctx.session_id),
            ctx,
        ),
        _wrap(
            "read_file",
            "Read a text file from the server and return its contents.",
            tools.FileArgs,
            lambda path: tools.read_file(path, tool_guard.file_policy()),
            ctx,
        ),
    ]


def _text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content)
    return str(content)


def run(message: str, context_text: str, ctx: RequestContext) -> tuple[str, dict]:
    limits = runtime_guard.limits()
    agent = create_agent(get_chat_model(limits.max_output_tokens), build_tools(ctx), system_prompt=SYSTEM_PROMPT)
    user_content = (f"Context:\n{context_text}\n\n" if context_text else "") + f"Question: {message}"
    usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    try:
        result = agent.invoke({"messages": [HumanMessage(content=user_content)]}, config={"recursion_limit": limits.recursion_limit})
    except GraphRecursionError:
        ctx.trace.event("runtime", "step_limit", f"stopped after {limits.recursion_limit} steps")
        return "I had to stop: this request needed too many steps.", usage
    answer = ""
    for m in result["messages"]:
        if isinstance(m, AIMessage):
            um = m.usage_metadata or {}
            for k in usage:
                usage[k] += int(um.get(k, 0) or 0)
            if m.content:
                answer = _text(m.content)
    return answer or "(no answer)", usage
