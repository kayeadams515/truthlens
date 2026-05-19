"""Pydantic models for the TruthLens structured report."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# --- Primitive Evidence Types ---

class EvidenceItem(BaseModel):
    """A single piece of evidence with source tracing."""
    source: str = Field(..., description="来源名称，如 '新华社'、'微博用户@张三'")
    source_type: str = Field(..., description="来源类型: official / media / social / other")
    content: str = Field(..., description="证据内容原文摘要")
    reliability_score: float = Field(
        default=0.5, ge=0.0, le=1.0, description="信源可靠性评分 0-1"
    )
    url: Optional[str] = Field(default=None, description="原始链接")


class Claim(BaseModel):
    """A claim made by a party, backed by evidence items."""
    statement: str = Field(..., description="核心主张/说辞")
    speaker: str = Field(..., description="发言人/机构")
    speaker_type: str = Field(..., description="official / media / social")
    evidence_chain: list[EvidenceItem] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="置信度评分 0-1")
    emotional_tone: str = Field(default="neutral", description="情绪基调: positive/negative/neutral/angry/fearful")
    logical_flaws: list[str] = Field(default_factory=list, description="逻辑漏洞列表")
    interest_analysis: Optional[str] = Field(default=None, description="利益相关度分析")


class StanceAnalysis(BaseModel):
    """Aggregated stance from one perspective category."""
    category: str = Field(..., description="official / media / social")
    label: str = Field(..., description="显示标签，如 '🏛️ 官方/权威'")
    claims: list[Claim] = Field(default_factory=list)
    dominant_emotion: str = Field(default="neutral")
    emotion_distribution: dict[str, float] = Field(default_factory=dict)


# --- Composite Report ---

class FactAlignment(BaseModel):
    """Fact-chain alignment: confirmed vs disputed vs contradictory."""
    confirmed: list[str] = Field(default_factory=list, description="已确认事实")
    disputed: list[str] = Field(default_factory=list, description="存疑点")
    contradictory: list[str] = Field(default_factory=list, description="矛盾点")


class TruthReport(BaseModel):
    """The complete structured truth-perspective report."""
    # Metadata
    topic: str = Field(..., description="事件主题")
    generated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(), description="生成时间 ISO 格式"
    )
    model_used: str = Field(default="claude-sonnet-4-6")

    # 5W1H Summary
    summary_5w1h: str = Field(
        default="", description="📌 事件概述 — 5W1H 纯事实总结，不带主观修饰词"
    )

    # Truth Scoring
    truth_probability: float = Field(
        default=50.0, ge=0.0, le=100.0, description="真相可能概率 (%)"
    )
    truth_rationale: str = Field(default="", description="概率计算理由")
    missing_evidence: list[str] = Field(default_factory=list, description="缺失的关键证据")

    # Multi-Perspective Debate
    stances: list[StanceAnalysis] = Field(default_factory=list, description="各方观点对垒")

    # Fact Alignment
    fact_alignment: FactAlignment = Field(default_factory=FactAlignment)

    # Raw Markdown (for direct rendering)
    markdown_report: str = Field(default="", description="完整的 Markdown 格式报告")

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "某新能源车碰撞起火事件",
                "truth_probability": 67.0,
                "truth_rationale": "官方通报与行车记录仪视频相互印证，但电池供应商未出具第三方检测报告，故降低概率。",
            }
        }
