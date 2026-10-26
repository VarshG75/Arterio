"""Shared ARTERIO dashboard styling."""
import streamlit as st

def inject_editorial_theme():
    st.html("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:ital,wght@0,300;0,400;0,500;0,600;1,400&family=Newsreader:ital,opsz,wght@0,6..72,200..800;1,6..72,200..800&display=swap');

        /* Page colors */
        html, body, .stApp {
            background-color: #020204 !important;
            color: #f1f5f9 !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            letter-spacing: -0.012em;
        }

        .stApp {
            background: radial-gradient(ellipse 90% 50% at 50% -20%, rgba(220, 220, 225, 0.12), rgba(0, 0, 0, 0)),
                        radial-gradient(ellipse 60% 40% at 85% 95%, rgba(170, 170, 180, 0.06), rgba(0, 0, 0, 0)),
                        #020204 !important;
        }

        #MainMenu, [data-testid="stHeader"], .stApp > footer { visibility: hidden; }

        .block-container {
            width: 100% !important;
            max-width: 1580px !important;
            min-height: 100dvh;
            margin-inline:auto;
            padding: 96px clamp(24px,4vw,72px) 32px !important;
        }
        @media(max-width:700px) {
            .block-container {padding: 174px 20px 24px !important;}
        }
        .hero-caption {max-width: 65ch;}

        /* Animations */
        @keyframes viewFadeIn {
            from { opacity: 0; transform: translateY(14px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes liveBeacon {
            0% { box-shadow: 0 0 0 0 rgba(220, 220, 225, 0.8); }
            70% { box-shadow: 0 0 0 7px rgba(220, 220, 225, 0); }
            100% { box-shadow: 0 0 0 0 rgba(220, 220, 225, 0); }
        }

        .page-transition {
            animation: viewFadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
        }

        /* Floating Navigation Header */
        .nav-bar-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 24px;
            background: rgba(8, 8, 12, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 9999px;
            backdrop-filter: blur(24px);
            margin-bottom: 2rem;
            box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.8);
        }

        .nav-brand {
            font-family: 'Newsreader', serif;
            font-size: 1.45rem;
            font-weight: 300;
            color: #ffffff;
            letter-spacing: -0.03em;
        }

        .nav-beacon {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #94a3b8;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 4px 12px;
            border-radius: 9999px;
        }

        .beacon-dot {
            width: 6px;
            height: 6px;
            background-color: #00f2fe;
            border-radius: 50%;
            animation: liveBeacon 2.2s infinite cubic-bezier(0.4, 0, 0.6, 1);
        }

    /* Navigation pills */
    div[data-testid="stRadio"] {
        margin-bottom: 2.2rem !important;
    }

    div[data-testid="stRadio"] > div {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        gap: 10px !important;
        background: transparent !important;
    }

    /* Keep the native input accessible while hiding its decoration. */
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-testid="stRadioOption"] > div:first-child,
    div[data-testid="stRadio"] [data-testid="stRadioButton"] {
        display: none !important;
    }

    div[data-testid="stRadio"] label[data-testid="stRadioOption"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 9999px !important;
        padding: 9px 24px !important;
        cursor: pointer !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    /* Navigation text */
    div[data-testid="stRadio"] label[data-testid="stRadioOption"] div,
    div[data-testid="stRadio"] label[data-testid="stRadioOption"] p {
        background: transparent !important;
        background-color: transparent !important;
        color: #71717a !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.74rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
    }

    div[data-testid="stRadio"] label[data-testid="stRadioOption"]:hover {
        border-color: rgba(0, 242, 254, 0.4) !important;
        background: rgba(0, 242, 254, 0.04) !important;
    }

    div[data-testid="stRadio"] label[data-testid="stRadioOption"]:hover p {
        color: #ffffff !important;
    }

    div[data-testid="stRadio"] label[data-testid="stRadioOption"][data-checked="true"],
    div[data-testid="stRadio"] label[data-testid="stRadioOption"]:has(input:checked) {
        background: rgba(0, 242, 254, 0.1) !important;
        border-color: #00f2fe !important;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.2) !important;
    }

    div[data-testid="stRadio"] label[data-testid="stRadioOption"][data-checked="true"] p,
    div[data-testid="stRadio"] label[data-testid="stRadioOption"]:has(input:checked) p {
        color: #00f2fe !important;
    }

    /* Streamlit 1.61 uses React Aria: its decorative circle is inside the label row. */
    [data-testid="stRadio"] [data-testid="stRadioGroup"]{justify-content:center !important;gap:10px !important}
    [data-testid="stRadio"] label[data-testid="stRadioOption"]{display:flex !important;align-items:center !important;justify-content:center !important;box-sizing:border-box;min-height:40px;position:relative}
    [data-testid="stRadioOption"] > div > div:first-child{justify-content:center !important;gap:0 !important}
    [data-testid="stRadioOption"] > div > div:first-child > div:first-child{display:none !important}
    [data-testid="stRadio"] label[data-testid="stRadioOption"] > span:has(input){position:absolute !important;width:1px !important;height:1px !important;overflow:hidden;clip-path:inset(50%)}
    [data-testid="stRadio"] label[data-testid="stRadioOption"][data-selected]{background:rgba(0,242,254,.1) !important;border-color:#00f2fe !important;box-shadow:0 0 25px rgba(0,242,254,.2) !important}
    [data-testid="stRadio"] label[data-testid="stRadioOption"][data-selected] p{color:#00f2fe !important}
    [data-testid="stRadio"] label[data-testid="stRadioOption"][data-focus-visible]{outline:2px solid #00f2fe;outline-offset:3px}

    [data-testid="stRadio"] > label{display:none !important}
    [data-testid="stRadioGroup"]{width:100% !important}

        /* Keep the entire header in one fixed surface, including its brand. */
        .st-key-site_navigation{position:fixed!important;z-index:30;top:18px;left:4vw;right:4vw;width:auto!important;height:auto!important;min-height:0!important;margin:0!important;gap:0!important;overflow:visible!important}
        .st-key-site_navigation [data-testid="stElementContainer"],.st-key-site_navigation [data-testid="stVerticalBlock"]{position:static!important;gap:0!important}
        .st-key-site_navigation .nav-bar-container{position:relative;inset:auto;margin:0;padding:12px 22px;background:#06090bf2}
        .st-key-site_navigation [data-testid="stRadio"]{position:absolute!important;top:11px;left:19vw;right:13vw;width:auto!important;margin:0!important}
        @media(max-width:1200px){.st-key-site_navigation [data-testid="stRadio"]{top:66px;left:0;right:0}.block-container{padding-top:158px!important}}
        @media(max-width:700px){.st-key-site_navigation{top:10px;left:14px;right:14px}.st-key-site_navigation .nav-bar-container{padding:10px 14px}.st-key-site_navigation [data-testid="stRadio"]{top:61px;left:0;right:0}[data-testid="stRadio"] label[data-testid="stRadioOption"]{padding:8px 10px!important}[data-testid="stRadio"] label p{font-size:.62rem!important}.block-container{padding-top:174px!important}}

        /* Typography */
        .hero-title {
            font-family: 'Newsreader', serif !important;
            font-weight: 300 !important;
            font-size: 4.2rem !important;
            letter-spacing: -0.045em !important;
            line-height: 0.95 !important;
            color: #ffffff !important;
            margin-bottom: 0.8rem !important;
        }

        .hero-caption {
            font-size: 1.12rem;
            color: #8a8a93;
            font-weight: 300;
            line-height: 1.6;
            max-width: 680px;
            margin-bottom: 2.2rem;
        }

        .section-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: #94a3b8;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 5px 12px;
            border-radius: 9999px;
            margin-bottom: 1.1rem;
        }

        /* Upload control */
        div[data-testid="stFileUploader"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            width: 100% !important;
        }

        [data-testid="stFileUploaderDropzone"] {
            background: rgba(10, 10, 14, 0.6) !important;
            border: 1px dashed rgba(255, 255, 255, 0.14) !important;
            border-radius: 18px !important;
            padding: 28px 24px !important;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }

        [data-testid="stFileUploaderDropzone"]:hover {
            border-color: rgba(220, 220, 225, 0.45) !important;
            background: rgba(14, 16, 24, 0.8) !important;
            box-shadow: 0 10px 30px -10px rgba(220, 220, 225, 0.15) !important;
        }

        [data-testid="stFileUploaderDropzone"] button {
            background: rgba(255, 255, 255, 0.05) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 9999px !important;
            padding: 8px 22px !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.74rem !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            transition: all 0.25s ease !important;
        }

        [data-testid="stFileUploaderDropzone"] button:hover {
            background: #eeeeef !important;
            color: #020204 !important;
            border-color: #eeeeef !important;
            box-shadow: 0 0 20px rgba(220, 220, 225, 0.4) !important;
        }

        /* Uploaded file label */
        [data-testid="stFileUploaderDropzone"] * {
            background-color: transparent !important;
        }

        div[data-testid="stFileUploaderFile"] {
            background: rgba(16, 18, 26, 0.9) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            padding: 12px 18px !important;
            margin-top: 12px !important;
        }

        /* Action buttons */
        div.stButton > button {
            width: 100% !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.82rem !important;
            font-weight: 500 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.12em !important;
            background: linear-gradient(180deg, rgba(16, 18, 26, 0.9) 0%, rgba(8, 9, 14, 0.95) 100%) !important;
            color: #eeeeef !important;
            border: 1px solid rgba(220, 220, 225, 0.35) !important;
            border-radius: 14px !important;
            padding: 16px 28px !important;
            margin-top: 14px !important;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
            box-shadow: 0 10px 30px -10px rgba(220, 220, 225, 0.15) !important;
        }

        div.stButton > button:hover {
            background: #eeeeef !important;
            color: #020204 !important;
            border-color: #eeeeef !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 35px rgba(220, 220, 225, 0.35) !important;
        }

        div.stButton > button:active {
            transform: translateY(0) scale(0.99) !important;
        }

        /* Bento Telemetry Cards */
        .bento-card {
            background: linear-gradient(180deg, rgba(12, 12, 18, 0.7) 0%, rgba(6, 6, 10, 0.85) 100%);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 18px;
            padding: 24px;
            backdrop-filter: blur(28px);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            box-shadow: 0 20px 40px -20px rgba(0, 0, 0, 0.8);
            height: 100%;
        }

        .bento-card:hover {
            border-color: rgba(220, 220, 225, 0.3);
            transform: translateY(-3px);
            box-shadow: 0 24px 45px -15px rgba(220, 220, 225, 0.1);
        }

        .bento-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            color: #64748b;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }

        .bento-metric {
            font-family: 'Newsreader', serif;
            font-size: 3.4rem;
            font-weight: 300;
            line-height: 1.0;
            color: #ffffff;
            margin: 10px 0 6px 0;
        }

        .bento-subtext {
            font-size: 0.84rem;
            color: #94a3b8;
            line-height: 1.5;
        }
    @media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none !important;transition:none !important}}
    [data-testid="stFileUploaderDropzone"]{display:flex !important;align-items:center !important;flex-wrap:wrap !important;gap:18px !important;min-height:125px !important}
    [data-testid="stFileUploaderDropzone"] button{display:inline-flex !important;align-items:center !important;justify-content:center !important;gap:10px !important;min-height:48px;min-width:145px;white-space:nowrap !important;letter-spacing:.07em !important}
    [data-testid="stFileUploaderDropzoneInstructions"]{min-width:150px;flex:1}
    [data-testid="stFileUploaderDropzoneInstructions"] small{color:#94a3b8 !important;font-size:12px !important;line-height:1.6 !important}
    [data-testid="stFileUploaderFileName"]{overflow-wrap:anywhere;white-space:normal}
    .capture-guide{border-top:1px solid #36363d;border-bottom:1px solid #28282d;padding:22px 0;margin-bottom:24px}
    .capture-specs{display:grid;grid-template-columns:repeat(3,1fr);gap:6px 24px;margin:20px 0}
    .capture-specs > div{display:flex;flex-direction:column;gap:7px}.capture-specs strong{font-size:18px;font-weight:500;color:#f4f4f5}.capture-specs span{font-size:12px;color:#94949d;line-height:1.6}
    .capture-guide p{max-width:820px;color:#a4a4ad;font-size:13px;line-height:1.8}
    @media(max-width:600px){.capture-specs{grid-template-columns:1fr}.capture-specs span{grid-row:auto}.capture-specs strong{margin-top:12px}[data-testid="stRadio"] label{min-width:0;padding:9px 12px !important}}

.warning-modal-card{background:linear-gradient(145deg,rgba(24,18,14,.85),rgba(12,10,8,.95));border:1px solid rgba(234,88,12,.4);border-radius:18px;box-shadow:0 16px 36px -10px rgba(234,88,12,.15);padding:24px;margin:16px 0;animation:captureWarning .35s ease-out}
.warning-modal-card h3{font:12px/1.7 'JetBrains Mono',monospace;color:#fb923c;margin:0 0 12px}.warning-modal-card p{font:14px/1.8 Inter,system-ui,sans-serif;color:#c7bdba;max-width:850px}
.red-orange-pill-badge{display:inline-flex;align-items:center;gap:8px;font: .74rem/1.7 'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:.08em;color:#fb923c;background:rgba(234,88,12,.12);border:1px solid rgba(234,88,12,.4);border-radius:9999px;box-shadow:0 0 16px rgba(234,88,12,.15);padding:10px 16px;max-width:100%;margin:18px 0}
.bento-metric small{font:14px 'JetBrains Mono',monospace;color:#94a3b8}
@keyframes captureWarning{from{opacity:0;transform:translateY(-12px)}to{opacity:1;transform:translateY(0)}}
@media(prefers-reduced-motion:reduce){.warning-modal-card{animation:none}}
@media(max-width:700px){.warning-modal-card{padding:18px}.red-orange-pill-badge{font-size:.65rem;border-radius:18px}}
[data-testid="stExpander"]{border:1px solid #ffffff18!important;border-radius:18px!important;background:rgba(12,12,18,.7);backdrop-filter:blur(14px)}
</style>
    """)
