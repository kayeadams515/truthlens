"""Clean theme for Vision Lens — respects system light/dark mode."""

import streamlit as st


def apply_theme():
    """Apply minimal custom styling. Text colors follow Streamlit's native theme."""
    st.markdown("""
    <style>
    /* ========== Accent Colors ========== */
    :root {
        --cyan: #00bfa5;
        --magenta: #d63384;
        --gold: #f0a500;
        --red: #dc3545;
    }

    /* ========== Cards ========== */
    .cyber-card {
        border: 1px solid rgba(128,128,128,0.2);
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 16px;
        transition: all 0.2s ease;
    }

    .cyber-card:hover {
        border-color: var(--cyan);
        box-shadow: 0 4px 16px rgba(0,191,165,0.08);
    }

    /* ========== Badges ========== */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-official { background: rgba(0,191,165,0.12); color: var(--cyan); }
    .badge-media { background: rgba(214,51,132,0.12); color: var(--magenta); }
    .badge-social { background: rgba(240,165,0,0.12); color: var(--gold); }
    .badge-danger { background: rgba(220,53,69,0.12); color: var(--red); }

    /* ========== Report Container ========== */
    .report-container {
        border: 1px solid rgba(128,128,128,0.15);
        border-radius: 8px;
        padding: 28px 32px;
        font-size: 15px;
        line-height: 1.8;
    }

    .report-container h2 {
        border-bottom: 1px solid rgba(128,128,128,0.15);
        padding-bottom: 8px;
        margin-top: 28px;
    }

    .report-container table {
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
    }
    .report-container th, .report-container td {
        padding: 10px 12px;
        border: 1px solid rgba(128,128,128,0.15);
        text-align: left;
    }

    .report-container blockquote {
        border-left: 3px solid var(--magenta);
        padding-left: 16px;
        opacity: 0.8;
    }

    /* ========== Report Images ========== */
    .report-container img {
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        margin: 20px 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        display: block;
    }
    /* Captions (rendered as <em> after <img> when using ![]() ) */
    .report-container img + em {
        display: block;
        text-align: center;
        font-size: 0.85em;
        opacity: 0.7;
        margin-top: 4px;
        margin-bottom: 16px;
    }

    /* ========== Agent Thought Blocks ========== */
    .thought-block {
        border-left: 3px solid var(--cyan);
        padding: 10px 14px;
        margin: 8px 0;
        font-size: 13px;
        font-family: monospace;
        border-radius: 0 4px 4px 0;
        opacity: 0.85;
    }
    .thought-block.scout { border-left-color: var(--cyan); }
    .thought-block.challenger { border-left-color: var(--red); }
    .thought-block.judge { border-left-color: var(--gold); }
    .thought-block.editor { border-left-color: var(--magenta); }

    /* ========== Sidebar fine-tuning ========== */
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128,128,128,0.1);
    }

    /* ========== Card title link ========== */
    .card-title {
        font-weight: 700;
        margin: 6px 0;
    }

    /* ========== Subtle Links ========== */
    .report-container a, .stMarkdown a {
        color: inherit;
        text-decoration: underline;
        text-decoration-color: rgba(0,191,165,0.3);
        text-underline-offset: 2px;
    }
    .report-container a:hover, .stMarkdown a:hover {
        text-decoration-color: rgba(0,191,165,0.8);
    }

    /* ========== Gauge text ========== */
    .gauge-big {
        font-family: monospace;
        font-size: 36px;
        font-weight: 700;
    }
    .gauge-label {
        font-size: 12px;
        opacity: 0.7;
    }
    </style>
    """, unsafe_allow_html=True)
