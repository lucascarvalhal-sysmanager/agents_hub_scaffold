import logging
import json
import time
from typing import Optional
from google.adk.models import LlmRequest
from google.adk.agents.callback_context import CallbackContext

logger = logging.getLogger(__name__)


def finops_before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest
) -> Optional[LlmRequest]:
    """
    Captures initial metrics and snapshots usage state before the model call.

    Registrar como: before_model_callback
    """
    try:
        # 1. Capture Start Time for Latency Calculation
        callback_context.state["temp:finops_start_time"] = time.time()

        # 2. Snapshot current side-channel usage stats
        state_dict = callback_context.state.to_dict()
        current_stats = state_dict.get("model_usage_stats", {})

        snapshot_json = json.dumps(current_stats)
        callback_context.state["temp:finops_pre_usage"] = snapshot_json

        # 3. Capture basic request metadata
        model_name = "unknown_model"
        full_input = "N/A"

        if hasattr(llm_request, 'model') and llm_request.model:
            model_name = llm_request.model

        # Capture full input for 'user_prompt' field
        if hasattr(llm_request, 'contents') and llm_request.contents:
            last_content = llm_request.contents[-1]
            if hasattr(last_content, 'parts') and last_content.parts:
                full_input = "".join([
                    p.text for p in last_content.parts
                    if hasattr(p, 'text') and p.text
                ])

        callback_context.state["temp:finops_model_name"] = model_name
        callback_context.state["temp:finops_user_prompt"] = full_input

    except Exception as e:
        logger.error(f"[FinOps] Before-callback failed: {e}", exc_info=True)

    return None
