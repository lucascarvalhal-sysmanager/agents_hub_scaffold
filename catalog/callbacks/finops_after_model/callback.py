import logging
import json
import os
import time
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from google.adk.models import LlmResponse
from google.adk.agents.callback_context import CallbackContext

from catalog.callbacks.finops_persistence import FinopsReport

logger = logging.getLogger(__name__)


def _get_base_context_data(callback_context: CallbackContext) -> Dict[str, Any]:
    """Extracts common context data used for all reports."""
    state_dict = callback_context.state.to_dict()
    end_time = time.time()
    start_time = callback_context.state.get("temp:finops_start_time", end_time)

    return {
        "execution_time_ms": (end_time - start_time) * 1000.0,
        "model_name": state_dict.get("temp:finops_model_name") or "unknown_model",
        "user_prompt": state_dict.get("temp:finops_user_prompt", "N/A"),
        "user_id": callback_context._invocation_context.session.user_id,
        "session_id": callback_context._invocation_context.session.id,
        "agent_app_name": os.getenv("AGENT_APP_NAME", "default_agent_app"),
        "agent_base_url": os.getenv("AGENT_BASE_URL", "http://localhost"),
        "invocation_id": callback_context.invocation_id,
        "interaction_timestamp": datetime.now(timezone.utc).isoformat()
    }


def _extract_usage_metrics(llm_response: LlmResponse) -> Dict[str, int]:
    """Extracts and normalizes usage metrics from the LLM response."""
    metrics = {
        "prompt": 0, "candidates": 0, "thoughts": 0,
        "total": 0, "cache": 0
    }

    if hasattr(llm_response, 'usage_metadata') and llm_response.usage_metadata:
        meta = llm_response.usage_metadata
        metrics["prompt"] = getattr(meta, 'prompt_token_count', 0) or 0
        metrics["candidates"] = getattr(meta, 'candidates_token_count', 0) or 0
        metrics["thoughts"] = getattr(meta, 'thoughts_token_count', 0) or 0
        metrics["total"] = getattr(meta, 'total_token_count', 0) or 0
        metrics["cache"] = getattr(meta, 'cached_content_token_count', 0) or 0

        # Auto-correct 'thoughts' logic
        calculated_sum = metrics["prompt"] + metrics["candidates"]
        if metrics["thoughts"] == 0 and metrics["total"] > calculated_sum:
            metrics["thoughts"] = metrics["total"] - calculated_sum

    return metrics


def _create_main_report(
    base_data: Dict[str, Any],
    usage: Dict[str, int],
    llm_response: LlmResponse
) -> FinopsReport:
    """Creates the primary report for the model interaction."""
    agent_response_text = "N/A"
    if hasattr(llm_response, 'content') and llm_response.content and llm_response.content.parts:
        agent_response_text = "".join([
            p.text for p in llm_response.content.parts
            if hasattr(p, 'text') and p.text
        ])

    return FinopsReport(
        user_id=base_data["user_id"],
        agent_base_url=base_data["agent_base_url"],
        agent_app_name=base_data["agent_app_name"],
        session_id=base_data["session_id"],
        invocation_id=base_data["invocation_id"],
        user_prompt=base_data["user_prompt"],
        agent_response=agent_response_text,
        thoughts_token_count=usage["thoughts"],
        prompt_token_count=usage["prompt"],
        candidates_token_count=usage["candidates"],
        cached_content_token_count=usage["cache"],
        total_token_count=usage["total"],
        interaction_timestamp=base_data["interaction_timestamp"],
        execution_time_ms=base_data["execution_time_ms"],
        model_name=base_data["model_name"],
        interaction_kind="agent"
    )


def _process_side_channels(
    callback_context: CallbackContext,
    base_data: Dict[str, Any],
    main_report: FinopsReport,
    buffer: List[FinopsReport]
) -> None:
    """Handles explicit side-channel reports and calculates generic deltas."""
    state_dict = callback_context.state.to_dict()
    reported_side_usage: Dict[str, int] = {}

    # 1. Handle Explicit Side Reports (e.g., Translations)
    side_reports: List[FinopsReport] = state_dict.get("temp:finops_side_reports", [])
    for report in side_reports:
        if not report.user_id:
            report.user_id = base_data["user_id"]
        if not report.session_id:
            report.session_id = base_data["session_id"]
        if not report.invocation_id:
            report.invocation_id = base_data["invocation_id"]
        if not report.agent_app_name:
            report.agent_app_name = base_data["agent_app_name"]
        if not report.agent_base_url:
            report.agent_base_url = base_data["agent_base_url"]

        if report.user_prompt == "N/A":
            report.user_prompt = base_data["user_prompt"]
        if report.agent_response == "N/A":
            report.agent_response = main_report.agent_response

        buffer.append(report)
        logger.debug(f"[FinOps] Buffered Side Report: {report.model_name} (Kind: {report.interaction_kind})")

        current_reported = reported_side_usage.get(report.model_name, 0)
        reported_side_usage[report.model_name] = current_reported + report.total_token_count

    # 2. Calculate Generic Delta (Unaccounted Usage)
    pre_usage_str = state_dict.get("temp:finops_pre_usage", "{}")
    pre_usage_snapshot = json.loads(pre_usage_str) if pre_usage_str else {}
    current_usage_stats = state_dict.get("model_usage_stats", {})

    for model_key, stats in current_usage_stats.items():
        pre_stats = pre_usage_snapshot.get(model_key, {"prompt": 0, "candidates": 0, "total": 0})

        delta_prompt = stats.get("prompt", 0) - pre_stats.get("prompt", 0)
        delta_candidates = stats.get("candidates", 0) - pre_stats.get("candidates", 0)
        delta_total = stats.get("total", 0) - pre_stats.get("total", 0)

        if delta_total > 0:
            remaining_delta = delta_total

            if (main_report.total_token_count > 0 and
                (base_data["model_name"] in model_key or model_key in base_data["model_name"])):
                remaining_delta -= main_report.total_token_count

            remaining_delta -= reported_side_usage.get(model_key, 0)

            if remaining_delta > 0:
                ratio = remaining_delta / delta_total

                buffer.append(FinopsReport(
                    user_id=base_data["user_id"],
                    agent_base_url=base_data["agent_base_url"],
                    agent_app_name=base_data["agent_app_name"],
                    session_id=base_data["session_id"],
                    invocation_id=base_data["invocation_id"],
                    user_prompt=base_data["user_prompt"],
                    agent_response=main_report.agent_response,
                    total_token_count=remaining_delta,
                    prompt_token_count=int(delta_prompt * ratio),
                    candidates_token_count=int(delta_candidates * ratio),
                    interaction_timestamp=datetime.now(timezone.utc).isoformat(),
                    model_name=model_key,
                    interaction_kind="unaccounted"
                ))
                logger.debug(f"[FinOps] Buffered Generic Report: {model_key} (Unaccounted)")


def collect_finops_metrics(
    callback_context: CallbackContext,
    llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    Aggregates usage and buffers FinOps reports for batch persistence.

    Registrar como: after_model_callback
    """
    try:
        # 1. Prepare Base Data
        base_data = _get_base_context_data(callback_context)
        usage_metrics = _extract_usage_metrics(llm_response)

        # 2. Main Report
        main_report = _create_main_report(base_data, usage_metrics, llm_response)

        # 3. Buffer Management
        state_dict = callback_context.state.to_dict()
        buffer: List[FinopsReport] = state_dict.get("finops_reports_buffer", [])
        buffer.append(main_report)
        logger.debug(f"[FinOps] Buffered Main Report: {base_data['model_name']}")

        # 4. Process Side Channels
        try:
            _process_side_channels(callback_context, base_data, main_report, buffer)
        except Exception as e:
            logger.warning(f"[FinOps] Side-channel processing failed: {e}", exc_info=True)

        # 5. Save State & Cleanup
        callback_context.state["finops_reports_buffer"] = buffer
        callback_context.state["temp:finops_pre_usage"] = ""
        callback_context.state["temp:finops_model_name"] = ""
        callback_context.state["temp:finops_user_prompt"] = ""
        callback_context.state["temp:finops_start_time"] = ""
        callback_context.state["temp:finops_side_reports"] = []

    except Exception as e:
        logger.error(f"[FinOps] Metric collection failed: {e}", exc_info=True)

    return None
