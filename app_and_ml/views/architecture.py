"""Scroll-led systems engineering dossier grounded in the running pipeline."""
import html
import base64
import json
from pathlib import Path
import streamlit as st

ASSETS = Path(__file__).resolve().parents[1] / 'assets/architecture'

STAGES = [
    dict(key='capture', name='Capture', title='Light becomes a signal.', subtitle='Optical ingestion & quality checks',
         description='An original camera recording becomes a bounded sequence of brightness samples. Quality checks begin before waveform analysis.',
         metric='20–25 s', unit='recommended recording',
         context='Rest the phone and hand on a flat surface. Use light finger contact, comfortably warm hands and fixed exposure/focus where supported. Prefer 1080p or 720p at 60 FPS; 30 FPS is supported.',
         equations='duration = frame_count / FPS\n12 s ≤ duration < 20 s → explicit approval\nprocessed segment ≤ 25 s\ns[k] = Σᵢ Σⱼ Iᵣ(i,j,k) / (H · W)',
         explanation='A temporary file supplies OpenCV with the local upload. Every fourth pixel in each axis is sampled on normal-size frames; small frames use all pixels. The decoder reads at most 25 seconds. Remove the first 2 seconds and last 1 second of that segment before checking mean red intensity and frame-difference variance.',
         bounds='O(N · H · W / 16) sampled reduction\n6.22 MB / decoded 1080p BGR frame\n30 ≤ mean red ≤ 250\nLocal variance > 4 × median → warning',
         detail='Under 12 seconds is rejected. Upload bytes and decoder buffers add to memory use. Brightness and variance checks are heuristics, not measurements of pressure, blanching or SNR.',
         tags=['20 seconds+ guidance', '2 s start / 1 s end trim', '25 s decoder cap']),
    dict(key='resample', name='Resample', title='Give time a common grid.', subtitle='Shape-preserving PCHIP interpolation',
         description='Camera samples move onto a uniform 200 Hz grid. The interpolation preserves local shape without creating new captured detail.',
         metric='200 Hz', unit='uniform processing grid',
         context='At 30 FPS, samples are about 33.3 ms apart; at 60 FPS, about 16.7 ms. The denser processing grid does not remove these acquisition limits.',
         equations='Pⱼ(t) = aⱼ + bⱼτ + cⱼτ² + dⱼτ³\nτ = t − tⱼ\nP and P′ continuous at knots\ntₘ = t₀ + m / 200',
         explanation='SciPy PchipInterpolator preserves monotonicity on monotone intervals and avoids interpolation overshoot. Monotonic video timestamps are used; nominal FPS supplies a fallback source clock.',
         bounds='Δt = 5.0 ms on the target grid\nC¹ continuity; second derivative may jump\nO(N) interpolator construction\nFinite, strictly increasing timestamps',
         detail='N is the number of retained camera samples; M is the interpolated sample count. A missing FPS uses a disclosed 30 FPS fallback and can affect timing estimates.',
         tags=['PCHIP', 'Shape preserving', '5.0 ms grid spacing']),
    dict(key='filter', name='Filter', title='Find the rhythm in the noise.', subtitle='SOS filtering & smoothed derivatives',
         description='Second-order sections provide a stable filter representation. Smoothed derivatives help inspect local waveform changes.',
         metric='0.5–8.5 Hz', unit='digital bandpass',
         context='The chosen band attenuates slower drift and higher-frequency noise. Movement and exposure artifacts can overlap the pulse band, so filtering alone cannot establish quality.',
         equations='SOS = butter(4, [0.5, 8.5], fs=200)\ny = sosfiltfilt(SOS, x)\nVPG, APG = Savitzky–Golay derivatives\nwindow = 15 samples; polynomial = 2',
         explanation='A fourth-order prototype becomes an eighth-order digital bandpass. Forward/backward execution has zero phase shift. A 0.35-second moving-mean detrended trace is also computed; segmentation uses the bandpassed contour.',
         bounds='O(M) filtering at fixed order\nPadding ≤ 3 seconds per side\n100 Hz Nyquist at 200 Hz sampling\n15 samples = 75 ms at 200 Hz',
         detail='Zero phase shift is different from wall-clock execution time. Derivative smoothing and detrending change morphology and need evaluation against reference recordings.',
         tags=['Second-order sections', 'Forward + backward', 'Savitzky–Golay derivatives']),
    dict(key='kinetics', name='Kinetics', title='From peaks to relationships.', subtitle='Repeatable beats & secondary landmarks',
         description='Repeated beat shapes are compared before timing and amplitude relationships are summarized. Missing landmarks stay missing.',
         metric='10–55%', unit='cycle search interval',
         context='Candidate primary peaks use spacing based on 160 BPM. Timing must remain within 40–160 BPM with interval coefficient of variation ≤0.20. Beat segments are normalized to 100 points and compared with a median template; correlation below 0.80 excludes a segment.',
         equations='SI = height / Δt  [m/s]\nRI = 100 · (Asecondary − Afoot) / (Asys − Afoot)\nAPG = d²PPG / dt²\n0.10 · Tcycle ≤ Δt < 0.55 · Tcycle',
         explanation='Search for a distinct secondary maximum, then a descending-slope VPG shoulder candidate if needed. At least four repeatable segments and four secondary candidates are needed for median SI and RI.',
         bounds='0.80 template-correlation threshold\n≥4 retained secondary candidates\nΔt ≥50 ms; amplitudes relative to foot\nO(M²) worst-case peak prominence search',
         detail='Height is entered by the user. SI is a height/delay descriptor, not measured pulse wave velocity. Values are not clipped into expected clinical ranges, and no disease tiers or vascular age are assigned.',
         tags=['Foot-referenced amplitudes', 'Median beat template', 'Missing-value handling']),
]


def diagram(index):
    """Small explanatory signal drawings, not recorded patient waveforms."""
    base='<path d="M0 92H720 M0 40H720" stroke="#23272b" stroke-width="1"/>'
    wave='M0 87 C25 87 35 84 43 70 C51 43 54 14 63 20 C78 31 78 83 101 84 C116 84 120 54 137 58 C156 61 160 86 180 87'
    curves=''.join(f'<path d="{wave}" transform="translate({i*180} 0)" fill="none" stroke="#00f2fe" stroke-width="2"/>' for i in range(4))
    if index == 0:
        content=''.join(f'<rect x="{i*37+7}" y="{40+(i%3)*7}" width="24" height="{45-(i%3)*7}" fill="#00f2fe" opacity="{.15+(i%4)*.15}"/>' for i in range(19))
    elif index == 1:
        content=curves+''.join(f'<circle cx="{i*24}" cy="100" r="2" fill="#8b9a9f"/>' for i in range(31))
    elif index == 2:
        content='<path d="M0 65 L20 80 40 29 60 76 80 15 100 60 120 51 140 80 160 58 180 85 200 30 220 70 240 16 260 74 280 60 300 82 320 60 340 87 360 65 380 80 400 29 420 76 440 15 460 60 480 51 500 80 520 58 540 85 560 30 580 70 600 16 620 74 640 60 660 82 680 60 720 87" fill="none" stroke="#6d757e" opacity=".4"/>'+curves
    else:
        content=curves+'<path d="M63 8V106 M137 8V106" stroke="#ffffff" stroke-dasharray="3 6" opacity=".5"/><circle cx="63" cy="20" r="5" fill="#00f2fe"/><circle cx="137" cy="58" r="5" fill="#fff"/>'
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 115">{base}{content}</svg>'
    encoded=base64.b64encode(svg.encode()).decode()
    return f'<img class="dossier-signal" src="data:image/svg+xml;base64,{encoded}" alt="Illustrative signal transformation for stage {index+1}">'


def render_architecture_view():
    bench=json.loads((ASSETS / 'benchmark.json').read_text())
    sections=[]
    for i,stage in enumerate(STAGES):
        e=lambda key: html.escape(stage[key])
        tags=''.join(f'<span>{html.escape(tag)}</span>' for tag in stage['tags'])
        sections.append(f'''<section class="dossier-stage" id="system-{stage['key']}" aria-labelledby="stage-title-{i}">
<div class="dossier-stage-content"><div class="dossier-stage-top"><span class="dossier-stage-index">0{i+1}</span><span class="dossier-eyebrow">{e('subtitle')}</span></div>
<div class="dossier-stage-heading"><h2 id="stage-title-{i}">{e('title')}</h2><div class="dossier-stage-spec"><strong>{e('metric')}</strong><span>{e('unit')}</span></div></div>
<p class="dossier-lead">{e('description')}</p>{diagram(i)}
<details class="dossier-details"><summary>Explore the engineering <span>+</span></summary><div class="dossier-bento"><article><h3>Hardware & acquisition</h3><p>{e('context')}</p></article><article><h3>Mathematical formulation</h3><pre>{e('equations')}</pre><p>{e('explanation')}</p></article><article><h3>Complexity & numerical bounds</h3><pre>{e('bounds')}</pre><p>{e('detail')}</p></article></div></details><div class="dossier-tags">{tags}</div></div></section>''')
    links=''.join(f'<a href="#system-{s["key"]}" data-stage-link="{i}">0{i+1}<span> · {s["name"]}</span></a>' for i,s in enumerate(STAGES))
    latency='&lt; 15 ms' if bench['p95_ms'] < 15 else f'{bench["p95_ms"]:.2f} ms'
    content=f'''<main class="arterio-dossier"><header class="dossier-intro"><p class="dossier-eyebrow">04 / SYSTEMS ENGINEERING DOSSIER</p><h1>Follow the signal.<br><em>Understand every step.</em></h1><p>From the first frame to the shape of a pulse. Explore the acquisition, mathematics and numerical decisions behind ARTERIO.</p><div class="dossier-scroll-cue"><span>↓</span> SCROLL TO TRACE THE PIPELINE</div></header>
<nav class="dossier-stage-nav" aria-label="Processing stages">{links}</nav>
<div class="dossier-story"><div class="dossier-connections" aria-hidden="true"></div>{''.join(sections)}</div>
<footer class="dossier-summary"><p class="dossier-eyebrow">EXECUTION / AT A GLANCE</p><div class="dossier-summary-grid"><article><h3>DSP pipeline latency</h3><strong>{latency}</strong><p>1,000 samples · local signal benchmark</p><small>Median {bench['median_ms']:.3f} ms · P95 {bench['p95_ms']:.3f} ms · {bench['runs']} runs<br>{bench['platform']} / {bench['machine']} · Python {bench['python']}</small></article><article><h3>Resampling continuity</h3><strong>200 Hz</strong><p>C¹ shape-preserving PCHIP interpolant</p><small>Uniform 5.0 ms processing grid</small></article><article><h3>Ringing guard window</h3><strong>10%–55%</strong><p>Bounded secondary-peak search</p><small>Fraction of each detected cardiac cycle</small></article></div><p class="dossier-method">Benchmark scope: PCHIP resampling, SOS filter design and execution, detrending, segmentation, template comparison, ratios and smoothed derivatives on 1,000 generated samples. Video decoding and rendering are excluded.</p><div class="dossier-sources"><span>IMPLEMENTATION NOTES</span><a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html" target="_blank" rel="noopener">PCHIP ↗</a><a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html" target="_blank" rel="noopener">SOS filtering ↗</a><span>N = source samples · M = processing samples · H × W = frame size</span></div></footer></main>'''
    st.html('<style>'+(ASSETS / 'dossier.css').read_text()+'</style>'+content)
    with st.container(key='architecture_motion'):
        st.iframe((ASSETS / 'motion.html').read_text(),height=1,tab_index=-1)
