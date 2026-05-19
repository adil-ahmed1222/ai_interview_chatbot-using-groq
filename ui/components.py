"""Reusable premium UI injections for Streamlit."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"


def inject_premium_theme() -> None:
    css_path = ASSETS / "styles.css"
    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


def render_background_fx() -> None:
    js_path = ASSETS / "background.js"
    script = js_path.read_text(encoding="utf-8") if js_path.exists() else ""
    html = (
        '<div id="ai-bg-root" aria-hidden="true">'
        '<div class="orb orb-1"></div><div class="orb orb-2"></div>'
        '<div class="orb orb-3"></div><canvas id="particle-canvas"></canvas>'
        '<div id="mouse-glow"></div><div class="grid-overlay"></div></div>'
        f"<script>{script}</script>"
    )
    components.html(html, height=0, scrolling=False)


def render_futuristic_header(candidate_name: str, resume_loaded: bool) -> None:
    status = "indexed" if resume_loaded else "pending"
    status_label = "Resume indexed" if resume_loaded else "Awaiting resume"
    online = "online" if resume_loaded else "standby"
    name_chip = (
        f'<span class="chip chip-name">{candidate_name}</span>' if resume_loaded else ""
    )
    st.markdown(
        f"""
        <header class="ai-navbar fade-in">
          <div class="navbar-left">
            <div class="logo-ring">
              <span class="logo-core">AI</span>
              <span class="logo-pulse"></span>
            </div>
            <div class="navbar-titles">
              <h1 class="gradient-text">Interview<span>Coach</span></h1>
              <p class="navbar-sub">Resume-grounded AI · Groq powered</p>
            </div>
          </div>
          <div class="navbar-right">
            <span class="chip chip-{online}">
              <span class="dot pulse-dot"></span> AI {online}
            </span>
            <span class="chip chip-{status}">
              <span class="dot"></span> {status_label}
            </span>
            {name_chip}
          </div>
        </header>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand() -> None:
    st.markdown(
        """
        <div class="sidebar-brand fade-in">
          <div class="sidebar-logo">◆</div>
          <div>
            <p class="sidebar-title">Control Panel</p>
            <p class="sidebar-desc">Upload · Configure · Practice</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_upload_zone_hint() -> None:
    st.markdown(
        """
        <div class="upload-zone glass-panel fade-in">
          <div class="upload-icon-float">📄</div>
          <p class="upload-title">Drop your resume</p>
          <p class="upload-sub">PDF or DOCX · Secure local processing</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_upload_success_flash() -> None:
    st.markdown('<div class="upload-success-glow fade-in"></div>', unsafe_allow_html=True)


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="empty-state glass-panel fade-in-up">
          <div class="empty-icon">✦</div>
          <h3>Ready when you are</h3>
          <p>Your interview coach answers strictly from your CV — professional, confident, STAR-ready.</p>
          <div class="empty-tags">
            <span>HR Questions</span>
            <span>Technical</span>
            <span>Behavioral</span>
            <span>Career Coach</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_suggestions_header() -> None:
    st.markdown(
        """
        <div class="section-header fade-in">
          <h4 class="section-title">Suggested prompts</h4>
          <p class="section-sub">Click to start a conversation</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_typing_indicator(label: str = "AI is thinking") -> str:
    return f"""
    <div class="ai-thinking glass-panel">
      <div class="ai-avatar-pulse"><span>AI</span></div>
      <div>
        <p class="thinking-label">{label}</p>
        <div class="typing-indicator premium">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>
    """
