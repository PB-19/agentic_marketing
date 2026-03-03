import logging


def log_agent_event(event, logger: logging.Logger) -> None:
    """Log ADK tool calls and tool responses emitted during run_async."""
    if not event.content:
        return
    for part in event.content.parts:
        if hasattr(part, "function_call") and part.function_call:
            fc = part.function_call
            args_preview = str(fc.args)[:150].replace("\n", " ")
            logger.info(f"[tool call] {fc.name}({args_preview})")
        elif hasattr(part, "function_response") and part.function_response:
            fr = part.function_response
            resp_preview = str(fr.response)[:200].replace("\n", " ")
            logger.info(f"[tool result] {fr.name} → {resp_preview}")
