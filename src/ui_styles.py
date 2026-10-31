"""Design tokens and responsive styles for the AI_DR screening dashboard."""

CUSTOM_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root {
  --ai-teal: #087F8C;
  --ai-navy: #102A43;
  --ai-bg: #F5F8FA;
  --ai-card: #FFFFFF;
  --ai-text: #172B4D;
  --ai-muted: #62748A;
  --ai-success: #16865C;
  --ai-warning: #D99116;
  --ai-error: #C0392B;
  --ai-border: #E2E8F0;
}
/* Override Gradio's system-dependent defaults so light cards never inherit
   pale text from a dark-mode theme. */
.gradio-container {
  color-scheme: light !important;
  --body-background-fill: #F5F8FA !important;
  --body-text-color: #172B4D !important;
  --body-text-color-subdued: #62748A !important;
  --block-background-fill: #FFFFFF !important;
  --block-label-text-color: #172B4D !important;
  --block-title-text-color: #102A43 !important;
  --block-info-text-color: #62748A !important;
  --input-background-fill: #FFFFFF !important;
  --input-text-color: #172B4D !important;
  --input-placeholder-color: #62748A !important;
  --button-secondary-background-fill: #FFFFFF !important;
  --button-secondary-text-color: #172B4D !important;
  --color-accent: #087F8C !important;
  background: var(--ai-bg) !important;
  color: var(--ai-text) !important;
}
body { background: #F5F8FA !important; color: #172B4D !important; color-scheme: light !important; }
.gradio-container { max-width: 1440px !important; font-family: Inter, Manrope, ui-sans-serif, system-ui, sans-serif !important; }
.gradio-container * { font-family: Inter, Manrope, ui-sans-serif, system-ui, sans-serif; }
.gradio-container [data-testid="markdown"] :is(h1,h2,h3,h4,p,li,strong,em,a) { color: #172B4D !important; }
.gradio-container label, .gradio-container summary { color: #172B4D !important; }
.gradio-container input, .gradio-container textarea, .gradio-container select { color: #172B4D !important; background:#FFFFFF !important; }
.gradio-container input::placeholder, .gradio-container textarea::placeholder { color:#62748A !important; opacity:1 !important; }
.gradio-container .secondary { color:#172B4D !important; }
.app-shell { gap: 18px !important; }
.topbar { display:flex; align-items:center; justify-content:space-between; gap:18px; padding:12px 18px; background:#fff; border:1px solid var(--ai-border); border-radius:14px; box-shadow:0 2px 8px rgba(16,42,67,.04); }
.brand { display:flex; align-items:center; gap:11px; color:var(--ai-navy); }
.brand-mark { width:40px; height:40px; display:grid; place-items:center; background:#E8F4F5; border-radius:12px; color:var(--ai-teal); }
.brand-name { font-size:17px; font-weight:700; letter-spacing:.02em; }
.brand-subtitle { color:var(--ai-muted); font-size:12px; margin-top:2px; }
.topbar-right { display:flex; align-items:center; gap:22px; }
.nav-links { display:flex; gap:20px; }
.nav-links a { text-decoration:none; color:#42566D; font-size:13px; font-weight:600; }
.nav-links a:hover { color:var(--ai-teal); }
.prototype-badge, .model-badge { display:inline-flex; align-items:center; gap:7px; padding:7px 10px; border-radius:999px; background:#EAF5F5; color:#086C75; font-size:11px; font-weight:700; white-space:nowrap; }
.upload-panel .row { gap:10px !important; }
.hero-card { padding:15px 19px; border:1px solid var(--ai-border); border-radius:14px; background:#fff; }
.hero-title { color:var(--ai-navy); font-size:24px; line-height:1.2; font-weight:700; margin:0 0 6px; }
.hero-description { color:var(--ai-muted); font-size:14px; line-height:1.55; margin:0 0 11px; }
.section-card { background:var(--ai-card); border:1px solid var(--ai-border); border-radius:14px; padding:17px; box-shadow:0 3px 12px rgba(16,42,67,.035); }
.section-heading { color:var(--ai-navy) !important; margin:0 0 2px !important; }
.section-caption { color:var(--ai-muted) !important; font-size:13px !important; margin:0 0 12px !important; }
.upload-hint { color:var(--ai-muted); font-size:12px; margin-top:5px; }
.upload-panel .image-container, .upload-panel [data-testid="image"] { border-radius:10px !important; border-color:var(--ai-border) !important; background:#FBFCFD !important; }
.analyze-button { background:var(--ai-teal) !important; border:1px solid var(--ai-teal) !important; color:#fff !important; font-weight:700 !important; }
.analyze-button:hover { background:#066B76 !important; }
.clear-button { color:#42566D !important; border-color:#CBD5E1 !important; background:#fff !important; }
.quality-card { border:1px solid var(--ai-border); border-radius:11px; padding:12px; background:#FBFCFD; color:var(--ai-text); }
.quality-title { display:flex; align-items:center; gap:8px; font-size:14px; font-weight:700; margin:0 0 9px; }
.quality-title.pass { color:var(--ai-success); }
.quality-title.fail { color:var(--ai-error); }
.quality-metrics { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:7px; margin:8px 0; }
.quality-metric { padding:7px 8px; border:1px solid #E8EDF2; border-radius:8px; background:#fff; }
.quality-metric span { display:block; color:var(--ai-muted); font-size:10px; }
.quality-metric b { display:block; color:var(--ai-text); font-size:12px; margin-top:2px; }
.quality-message { color:#42566D; font-size:12px; line-height:1.45; margin-top:7px; }
.screening-card { border:1px solid var(--ai-border); border-left:4px solid var(--ai-teal); border-radius:12px; padding:14px 15px; background:#fff; }
.screening-card.referable { border-left-color:var(--ai-warning); }
.screening-card.nonreferable { border-left-color:var(--ai-success); }
.screening-card.failed { border-left-color:var(--ai-error); background:#FFFAFA; }
.screening-eyebrow { color:var(--ai-muted); font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.08em; }
.screening-title { color:var(--ai-navy); font-size:23px; line-height:1.25; margin:5px 0 8px; font-weight:700; }
.screening-card.referable .screening-title { color:#8A5700; }
.screening-card.nonreferable .screening-title { color:#126847; }
.screening-meta { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; margin:10px 0; }
.screening-meta div { padding:8px 9px; background:#F5F8FA; border-radius:8px; }
.screening-meta span { display:block; color:var(--ai-muted); font-size:10px; }
.screening-meta b { display:block; color:var(--ai-text); font-size:13px; margin-top:3px; }
.screening-note { color:#52667D; font-size:12px; line-height:1.5; margin:8px 0 0; }
.probability-card { border:1px solid var(--ai-border); background:#fff; border-radius:11px; padding:13px 14px; margin-top:12px; }
.probability-heading { display:flex; align-items:baseline; justify-content:space-between; gap:10px; margin-bottom:12px; }
.probability-heading strong { color:var(--ai-navy); font-size:14px; }
.probability-heading span { color:var(--ai-muted); font-size:11px; }
.probability-row { display:grid; grid-template-columns:minmax(118px,1.15fr) 3fr 48px; gap:10px; align-items:center; margin:9px 0; }
.probability-label { color:#42566D; font-size:12px; }
.probability-row.predicted .probability-label { color:var(--ai-teal); font-weight:700; }
.probability-track { height:8px; overflow:hidden; border-radius:99px; background:#EAF0F4; }
.probability-fill { height:100%; border-radius:99px; background:#93C9CE; }
.probability-row.predicted .probability-fill { background:var(--ai-teal); }
.probability-value { text-align:right; color:var(--ai-text); font-size:12px; font-weight:700; }
.probability-total { padding-top:9px; margin-top:10px; border-top:1px solid var(--ai-border); color:var(--ai-muted); text-align:right; font-size:11px; }
.viewer-panel { overflow:hidden; border:1px solid #243B53; border-radius:11px; background:var(--ai-navy); }
.viewer-panel .image-container, .viewer-panel [data-testid="image"] { background:var(--ai-navy) !important; border:0 !important; }
.viewer-panel img { object-fit:contain !important; }
.viewer-caption { color:var(--ai-muted); font-size:12px; line-height:1.5; margin:0 0 12px; }
.method-panel { border:1px solid var(--ai-border) !important; border-radius:12px !important; background:#fff !important; color:#172B4D !important; overflow:hidden; }
/* Gradio 6 renders Accordion labels as .label-wrap buttons, not <summary>. */
.gradio-container .method-panel .label-wrap {
  display:flex !important;
  align-items:center !important;
  min-height:48px !important;
  padding:12px 15px !important;
  border:0 !important;
  border-radius:11px !important;
  background:#FFFFFF !important;
  color:#102A43 !important;
  font-size:14px !important;
  font-weight:700 !important;
  opacity:1 !important;
}
.gradio-container .method-panel .label-wrap span,
.gradio-container .method-panel .label-wrap .icon { color:#102A43 !important; opacity:1 !important; }
.gradio-container .method-panel .label-wrap:hover,
.gradio-container .method-panel .label-wrap.open { background:#F0F7F8 !important; color:#102A43 !important; }
.gradio-container .method-panel [data-testid="accordion-content"] { background:#FFFFFF !important; color:#172B4D !important; padding:0 15px 14px !important; }
.method-copy { color:#42566D; font-size:13px; line-height:1.65; }
.method-copy strong { color:var(--ai-navy); }
.research-footer { padding:13px 15px; border:1px solid #F0D8A7; border-left:4px solid var(--ai-warning); border-radius:10px; background:#FFF9EC; color:#59451F; font-size:12px; line-height:1.55; }
.research-footer strong { color:#6F4B00; }
.error-banner { border:1px solid #F2C5C1; background:#FFF5F4; border-radius:10px; padding:12px 14px; color:#8E2B24; }
button:focus-visible, a:focus-visible, input:focus-visible { outline:3px solid #75C8D0 !important; outline-offset:2px !important; }
@media (max-width: 850px) {
  .topbar { align-items:flex-start; }
  .topbar-right { flex-direction:column-reverse; align-items:flex-end; gap:10px; }
  .nav-links { gap:12px; }
  .hero-title { font-size:21px; }
}
@media (max-width: 600px) {
  .topbar { padding:10px; }
  .brand-subtitle { max-width:180px; }
  .nav-links { display:none; }
  .prototype-badge { font-size:10px; padding:6px 8px; }
  .section-card { padding:12px; }
  .probability-row { grid-template-columns:100px 1fr 42px; gap:7px; }
  .probability-label { font-size:11px; }
  .screening-title { font-size:20px; }
}
"""

