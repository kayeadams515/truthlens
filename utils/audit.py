"""Content compliance audit engine for zh-beta (mainland China) mode.

Provides a two-stage content safety pipeline:
  1. Pre-constraint injection: add compliance rules to generation prompts
  2. Post-generation audit: LLM reviews content before display

Architecture:
  - Audit happens at the DISPLAY layer, not generation layer
  - Works for both freshly-generated and cached/historical content
  - Fail-open: if the audit LLM call fails, content is allowed through
  - Uses st.session_state.audit_cache to avoid re-auditing on reruns
"""

import streamlit as st

from utils.logger import logger
from utils.i18n import t


def is_beta_mode() -> bool:
    """Check whether the app is running in zh-beta (Chinese compliance) mode."""
    try:
        return st.session_state.get("lang", "zh") == "zh-beta"
    except Exception:
        return False


def add_compliance_constraint(prompt: str) -> str:
    """Append mainland China compliance constraints to a generation prompt.

    Only appends constraints when running in zh-beta mode.
    Returns the original prompt unchanged otherwise.
    """
    if not is_beta_mode():
        return prompt

    constraint = t("prompt.beta.preconstraint")
    if not constraint:
        return prompt

    return prompt + "\n\n" + constraint


def audit_content(content: str, max_chars: int = 4000) -> tuple:
    """Send content to integration_llm for compliance review.

    Args:
        content: The generated text to audit.
        max_chars: Truncation limit for very long content.

    Returns:
        (passed: bool, reason: str)
        - passed=True, reason="" — content is compliant
        - passed=False, reason="..." — content was rejected with reason
    """
    # Skip audit for very short content
    if not content or len(content.strip()) < 20:
        return True, ""

    # Skip if not in beta mode (shouldn't be called, but safety guard)
    if not is_beta_mode():
        return True, ""

    try:
        from config import create_integration_llm
        llm = create_integration_llm(temperature=0.0)

        system_prompt = t("prompt.audit.system")
        truncated = content[:max_chars]

        user_prompt = f"{system_prompt}\n\n## 待审核内容\n\n{truncated}"

        response = llm.call(messages=[{"role": "user", "content": user_prompt}])
        response_stripped = response.strip() if response else ""

        if response_stripped.startswith("[PASS]"):
            logger.info("Audit: PASS")
            return True, ""
        elif response_stripped.startswith("[REJECT]"):
            reason = response_stripped[8:].strip()  # Remove "[REJECT]" prefix
            logger.info(f"Audit: REJECT — {reason[:100]}")
            return False, reason
        else:
            # Unexpected response format — extract PASS/REJECT anywhere
            if "[PASS]" in response_stripped and "[REJECT]" not in response_stripped:
                return True, ""
            elif "[REJECT]" in response_stripped:
                reason = response_stripped.split("[REJECT]", 1)[1].strip()
                logger.info(f"Audit: REJECT (fuzzy match) — {reason[:100]}")
                return False, reason
            else:
                # Can't determine — fail open
                logger.warning(f"Audit: unclear response, failing open: {response_stripped[:200]}")
                return True, ""

    except Exception as e:
        # Fail open — don't block content due to audit infrastructure issues
        logger.warning(f"Audit LLM call failed, failing open: {e}")
        return True, ""


def audit_and_display(content, display_func, cache_key=None, **kwargs):
    """Audit content in beta mode, then display or show fallback.

    In non-beta mode, calls display_func(content, **kwargs) directly.
    In beta mode, audits first — passes content if compliant, shows
    fallback message if rejected.

    Uses session state cache to avoid re-auditing on Streamlit reruns.

    Args:
        content: The markdown content to potentially display.
        display_func: Callable (e.g., st.markdown) for actual rendering.
        cache_key: Optional string key for caching the audit verdict.
        **kwargs: Passed through to display_func (e.g., unsafe_allow_html=True).
    """
    if not is_beta_mode():
        display_func(content, **kwargs)
        return

    # Check cache first
    st.session_state.setdefault("audit_cache", {})
    cache = st.session_state["audit_cache"]

    if cache_key and cache_key in cache:
        cached = cache[cache_key]
        if cached["passed"]:
            display_func(cached["result"], **kwargs)
        else:
            display_func(cached["result"], **kwargs)
        return

    # Audit the content
    passed, reason = audit_content(content)

    if passed:
        display_func(content, **kwargs)
        if cache_key:
            cache[cache_key] = {"passed": True, "result": content}
    else:
        if reason:
            fallback = t("⚠️ **内容审核未通过**")
            fallback += f"\n\n> {reason}\n\n"
            fallback += t("⚠️ 该内容未通过安全审核，请尝试重新提问。")
        else:
            fallback = t("⚠️ 该内容未通过安全审核，请尝试重新提问。")

        display_func(fallback, **kwargs)
        if cache_key:
            cache[cache_key] = {"passed": False, "result": fallback}
