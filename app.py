import streamlit as st
import streamlit.components.v1 as components
import math
import json

st.set_page_config(page_title="Simulador Força Eletrostática", layout="wide")

# ===================== CSS (Mobile First) =====================
st.markdown(
    """
    <style>
      /* reduz padding geral no mobile */
      @media (max-width: 640px) {
        .block-container { padding-left: 0.9rem !important; padding-right: 0.9rem !important; }
        h1 { font-size: 1.55rem !important; }
        h2 { font-size: 1.25rem !important; }
        h3 { font-size: 1.10rem !important; }
      }

      /* força colunas a empilharem no mobile (sliders/resultados) */
      @media (max-width: 640px) {
        div[data-testid="column"] {
          width: 100% !important;
          flex: 1 1 100% !important;
          min-width: 100% !important;
        }
      }

      /* melhora visual de cards no mobile */
      .result-card-title { font-size: 14px; color: #333; margin-bottom: 6px; }
      .result-card-value { font-size: 24px; color: #111; }
      .result-card-foot  { font-size: 12px; color: #555; margin-top: 6px; }

      @media (max-width: 640px) {
        .result-card-value { font-size: 20px !important; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===================== Helpers =====================
def sig(x, n=2):
    """Retorna x com n algarismos significativos (float)."""
    if x == 0 or math.isclose(x, 0.0, abs_tol=0.0):
        return 0.0
    return float(f"{x:.{n}g}")

def br_decimal(s: str) -> str:
    """Troca ponto por vírgula em uma string numérica."""
    return s.replace(".", ",")

_sup_map = str.maketrans("0123456789-+", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺")

def sci_parts(x, n=2):
    """Retorna (mantissa, expoente) com n algarismos significativos na mantissa."""
    if x == 0:
        return 0.0, 0
    exp = int(math.floor(math.log10(abs(x))))
    mant = x / (10 ** exp)
    mant = float(f"{mant:.{n}g}")
    if abs(mant) >= 10:
        mant /= 10
        exp += 1
    return mant, exp

def br_sci_force_text(x, n=2, unit="N"):
    """Forças em notação científica com vírgula e n algarismos significativos."""
    if x == 0:
        out = "0"
    else:
        mant, exp = sci_parts(x, n=n)
        mant_s = br_decimal(f"{mant:.{n}g}")
        out = f"{mant_s}×10{str(exp).translate(_sup_map)}"
    return f"{out} {unit}".strip()

def arrow_symbol(F, tol=0.0):
    """Seta indicando sentido no eixo x."""
    if abs(F) <= tol:
        return "⟷"
    return "→" if F > 0 else "←"

def coulomb_force_1d(qi, qj, xi, xj, K=9e9):
    """
    Força (1D) em i devido a j:
    F = k*qi*qj*(xi-xj)/|xi-xj|^3
    Retorna (F, r=|xi-xj|)
    """
    r = xi - xj
    dist = abs(r)
    if dist == 0:
        return float("nan"), 0.0
    F = K * qi * qj * (r / (dist**3))
    return F, dist

# ---------- Formatação "EXATA" como sliders ----------
def fmt_uC_br(q_uC: float) -> str:
    return f"{round(q_uC, 2):.2f}".replace(".", ",")

def latex_charge_C_from_uC(q_uC: float) -> str:
    if math.isclose(q_uC, 0.0, abs_tol=0.0):
        return r"0"
    mant = f"{round(q_uC, 2):.2f}".replace(".", "{,}")
    return rf"{mant}\times10^{{-6}}"

def latex_dist_from_positions(xa: float, xb: float) -> str:
    d = abs(round(xa, 1) - round(xb, 1))
    return f"{d:.1f}".replace(".", "{,}")

def br_charge_canvas_from_uC(q_uC: float) -> str:
    if math.isclose(q_uC, 0.0, abs_tol=0.0):
        return "0 C"
    mant_s = fmt_uC_br(q_uC)
    exp = -6
    return f"{mant_s}×10{str(exp).translate(_sup_map)} C"

# ===================== Cabeçalho =====================
col_logo, col_title = st.columns([1, 5], vertical_alignment="center")
with col_logo:
    try:
        st.image("logo_maua.png", use_container_width=True)
    except Exception:
        st.warning("Arquivo 'logo_maua.png' não encontrado na raiz do repositório.")

with col_title:
    st.title("Simulador Força Eletrostática Unidimensional")
    st.write(
        "Veja as forças aplicadas na partícula carregada **3** quando posicionada próxima a "
        "outras duas partículas carregadas **1** e **2**."
    )
    st.markdown(
        "**Desafio:** tente encontrar uma situação onde a partícula 3 está em equilíbrio ou quase em equilíbrio (**Fᵣ ~ 0**)."
    )

# ===================== Controles =====================
st.header("Definições das Partículas")

# Sliders de carga (µC)
qmin_uC, qmax_uC, qstep_uC = -5.0, 5.0, 0.05

# Sliders de posição -10 a 10
xmin_slider, xmax_slider = -10.0, 10.0

# ✅ Melhor para mobile: controles em abas (evita 3 colunas apertadas)
tab1, tab2, tab3 = st.tabs(["Partícula 1", "Partícula 2", "Partícula 3"])

with tab1:
    st.subheader("Partícula 1")
    x1 = st.slider("Posição x₁ (m)", xmin_slider, xmax_slider, -4.0, 0.1, format="%.1f")
    q1_uC = st.slider("Carga q₁ (µC)", qmin_uC, qmax_uC, 2.0, qstep_uC, format="%.2f")
    q1 = q1_uC * 1e-6

with tab2:
    st.subheader("Partícula 2")
    x2 = st.slider("Posição x₂ (m)", xmin_slider, xmax_slider, 4.0, 0.1, format="%.1f")
    q2_uC = st.slider("Carga q₂ (µC)", qmin_uC, qmax_uC, -2.0, qstep_uC, format="%.2f")
    q2 = q2_uC * 1e-6

with tab3:
    st.subheader("Partícula 3")
    x3 = st.slider("Posição x₃ (m)", xmin_slider, xmax_slider, 0.0, 0.1, format="%.1f")
    q3_uC = st.slider("Carga q₃ (µC)", qmin_uC, qmax_uC, 1.0, qstep_uC, format="%.2f")
    q3 = q3_uC * 1e-6

# Bloqueio de posições iguais
if len({x1, x2, x3}) < 3:
    st.error("❌ As partículas **não podem** estar na mesma posição. Ajuste x₁, x₂ e x₃.")
    st.stop()

# ===================== Física =====================
K = 9.0e9

F13_raw, r13 = coulomb_force_1d(q3, q1, x3, x1, K=K)
F23_raw, r23 = coulomb_force_1d(q3, q2, x3, x2, K=K)

# ✅ Apenas forças finais exibidas arredondadas para 2 AS
F13_disp = sig(F13_raw, 2)
F23_disp = sig(F23_raw, 2)

# ✅ Equilíbrio didático: soma usando forças exibidas (já em 2 AS)
Fr_disp = sig(F13_disp + F23_disp, 2)
equilibrio = (Fr_disp == 0.0)

# ===================== Escala dos vetores (normalizada) =====================
maxF = max(abs(F13_disp), abs(F23_disp), abs(Fr_disp), 1e-30)
a13 = abs(F13_disp) / maxF
a23 = abs(F23_disp) / maxF
ar  = abs(Fr_disp)  / maxF

d13 = 0 if math.isclose(F13_disp, 0.0, abs_tol=0.0) else (1 if F13_disp > 0 else -1)
d23 = 0 if math.isclose(F23_disp, 0.0, abs_tol=0.0) else (1 if F23_disp > 0 else -1)
dr  = 0 if math.isclose(Fr_disp,  0.0, abs_tol=0.0) else (1 if Fr_disp  > 0 else -1)

# ===================== Figura (Canvas responsivo) =====================
st.header("Figura – Sistema Unidimensional")

q1_str = br_charge_canvas_from_uC(q1_uC)
q2_str = br_charge_canvas_from_uC(q2_uC)
q3_str = br_charge_canvas_from_uC(q3_uC)

# Dados para JS (evita problemas de aspas/acentos)
payload = {
    "xMin": -15.0,
    "xMax":  15.0,
    "x1": x1, "x2": x2, "x3": x3,
    "q1": q1, "q2": q2, "q3": q3,
    "q1_str": q1_str, "q2_str": q2_str, "q3_str": q3_str,
    "d13": d13, "d23": d23, "dr": dr,
    "a13": a13, "a23": a23, "ar": ar,
}

html = f"""
<div id="wrap" style="width:100%; max-width:1100px; margin: 0 auto;">
  <canvas id="canvas" style="
      width:100%;
      display:block;
      background:white;
      border:1px solid #eee;
      border-radius: 14px;
      box-shadow: 0 1px 10px rgba(0,0,0,0.05);
  "></canvas>
  <div style="font-size:12px; color:#666; margin-top:8px;">
    Dica: no celular, a figura se adapta automaticamente à largura e redesenha ao girar a tela.
  </div>
</div>

<script>
const data = {json.dumps(payload, ensure_ascii=False)};

const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const BASE_W = 1000;
const BASE_H = 410;

function clamp(v, a, b) {{ return Math.max(a, Math.min(b, v)); }}

function Xmap(x, xMin, xMax, W, padL, padR) {{
  return padL + (x - xMin) * ((W - padL - padR) / (xMax - xMin));
}}

function borderColorByCharge(q) {{
  const eps = 1e-15;
  if (q > eps) return "#d62728";
  if (q < -eps) return "#1f77b4";
  return "#111";
}}

function drawVectorOverLabel(text, xAnchor, yBaseline, align, color, fontPx) {{
  ctx.save();
  ctx.font = `${{fontPx}}px Arial`;
  ctx.fillStyle = color;
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;

  const w = ctx.measureText(text).width;
  let xLeft = xAnchor;
  if (align === "right") xLeft = xAnchor - w;
  if (align === "center") xLeft = xAnchor - w/2;

  const yArrow = yBaseline - (fontPx + 2);
  ctx.beginPath();
  ctx.moveTo(xLeft, yArrow);
  ctx.lineTo(xLeft + w, yArrow);
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(xLeft + w, yArrow);
  ctx.lineTo(xLeft + w - 6, yArrow - 4);
  ctx.lineTo(xLeft + w - 6, yArrow + 4);
  ctx.closePath();
  ctx.fill();

  ctx.restore();
}}

function drawArrow(x0, y0, dx, color, label, fontPx) {{
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = 3;

  if (dx === 0) {{
    ctx.beginPath();
    ctx.moveTo(x0 - 8, y0);
    ctx.lineTo(x0 + 8, y0);
    ctx.stroke();

    ctx.font = `${{fontPx}}px Arial`;
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    ctx.fillText(label + " ≈ 0", x0 + 12, y0);

    drawVectorOverLabel(label, x0 + 12, y0, "left", color, fontPx);
    return;
  }}

  const x1 = x0 + dx;

  ctx.beginPath();
  ctx.moveTo(x0, y0);
  ctx.lineTo(x1, y0);
  ctx.stroke();

  const head = 10;
  const s = (dx > 0) ? 1 : -1;

  ctx.beginPath();
  ctx.moveTo(x1, y0);
  ctx.lineTo(x1 - s*head, y0 - head*0.6);
  ctx.lineTo(x1 - s*head, y0 + head*0.6);
  ctx.closePath();
  ctx.fill();

  ctx.font = `${{fontPx}}px Arial`;
  const align = (dx > 0) ? "left" : "right";
  ctx.textAlign = align;
  ctx.textBaseline = "bottom";
  const xText = x1 + (dx > 0 ? 6 : -6);
  const yText = y0 - 6;
  ctx.fillText(label, xText, yText);

  drawVectorOverLabel(label, xText, yText, align, color, fontPx);
}}

function drawParticle(px, py, n, qText, qValue, radiusPx, fontPx) {{
  ctx.fillStyle = "#f7f7f7";
  ctx.strokeStyle = borderColorByCharge(qValue);
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(px, py, radiusPx, 0, 2*Math.PI);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = "#111";
  ctx.font = `bold ${{Math.round(fontPx*1.15)}}px Arial`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(n.toString(), px, py);

  return {{px, py, n, qText}};
}}

function drawChargeLabelsBelow(particles, yAxis, W, scale) {{
  particles.sort((a,b) => a.px - b.px);

  const baseY = yAxis + Math.round(58*scale);
  const dy = Math.round(18*scale);
  const minDx = Math.round(140*scale);
  const levels = [];

  for (let i=0; i<particles.length; i++) {{
    let level = 0;
    for (let j=i-1; j>=0; j--) {{
      const close = Math.abs(particles[i].px - particles[j].px) < minDx;
      if (close && levels[j] === level) {{
        level++;
        j = i;
      }}
    }}
    levels.push(level);
  }}

  const qSub = {{1: "q₁", 2:"q₂", 3:"q₃"}};

  ctx.fillStyle = "#111";
  ctx.font = `${{Math.round(14*clamp(scale,0.85,1.15))}}px Arial`;
  ctx.textAlign = "center";
  ctx.textBaseline = "top";

  for (let i=0; i<particles.length; i++) {{
    const p = particles[i];
    const level = levels[i];
    const y = baseY + level*dy;

    if (level > 0) {{
      ctx.strokeStyle = "#999";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(p.px, yAxis + Math.round(18*scale));
      ctx.lineTo(p.px, y - 2);
      ctx.stroke();
    }}

    ctx.fillText(`${{qSub[p.n]}} = ${{p.qText}}`, p.px, y);
  }}
}}

function drawAxis(xMin, xMax, W, H, padL, padR, yAxis, scale) {{
  ctx.strokeStyle = "#111";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(padL, yAxis);
  ctx.lineTo(W - padR, yAxis);
  ctx.stroke();

  // ticks adaptativos p/ evitar sobreposição no mobile
  let step = 1;
  if (W < 520) step = 3;
  else if (W < 720) step = 2;

  const fontPx = Math.round(13*clamp(scale, 0.85, 1.2));
  ctx.fillStyle = "#111";
  ctx.font = `${{fontPx}}px Arial`;
  ctx.textAlign = "center";
  ctx.textBaseline = "top";

  for (let t = Math.ceil(xMin); t <= Math.floor(xMax); t += step) {{
    const px = Xmap(t, xMin, xMax, W, padL, padR);

    ctx.beginPath();
    ctx.moveTo(px, yAxis - Math.round(7*scale));
    ctx.lineTo(px, yAxis + Math.round(7*scale));
    ctx.stroke();

    ctx.fillText(t.toString().replace(".", ","), px, yAxis + Math.round(10*scale));
  }}

  ctx.textAlign = "right";
  ctx.textBaseline = "bottom";
  ctx.fillText("x (m)", W - padR, yAxis - Math.round(10*scale));
}}

function drawAll(W, H, scale) {{
  ctx.clearRect(0, 0, W, H);

  const xMin = data.xMin;
  const xMax = data.xMax;

  const padL = Math.round(50*clamp(scale, 0.85, 1.25));
  const padR = Math.round(50*clamp(scale, 0.85, 1.25));

  // posição vertical do eixo adaptativa
  const yAxis = Math.round(clamp(H*0.58, 190, H-130));

  drawAxis(xMin, xMax, W, H, padL, padR, yAxis, scale);

  const radiusPx = Math.round(16*clamp(scale, 0.85, 1.25));
  const fontPx = Math.round(14*clamp(scale, 0.85, 1.25));

  const parts = [];
  parts.push(drawParticle(Xmap(data.x1, xMin, xMax, W, padL, padR), yAxis, 1, data.q1_str, data.q1, radiusPx, fontPx));
  parts.push(drawParticle(Xmap(data.x2, xMin, xMax, W, padL, padR), yAxis, 2, data.q2_str, data.q2, radiusPx, fontPx));
  parts.push(drawParticle(Xmap(data.x3, xMin, xMax, W, padL, padR), yAxis, 3, data.q3_str, data.q3, radiusPx, fontPx));

  drawChargeLabelsBelow(parts, yAxis, W, clamp(scale, 0.85, 1.25));

  const px3 = Xmap(data.x3, xMin, xMax, W, padL, padR);

  const arrowBase = 120*clamp(scale, 0.85, 1.35);
  const arrowBaseR = 140*clamp(scale, 0.85, 1.35);

  // y das setas (adaptativo)
  const y1 = yAxis - Math.round(95*clamp(scale, 0.85, 1.25));
  const y2 = yAxis - Math.round(65*clamp(scale, 0.85, 1.25));
  const y3 = yAxis - Math.round(35*clamp(scale, 0.85, 1.25));

  drawArrow(px3, y1, data.d13 * arrowBase * data.a13, "#d62728", "F₁₃", fontPx);
  drawArrow(px3, y2, data.d23 * arrowBase * data.a23, "#1f77b4", "F₂₃", fontPx);
  drawArrow(px3, y3, data.dr  * arrowBaseR * data.ar, "#2ca02c", "Fᵣ",  fontPx);
}}

function resizeAndDraw() {{
  const wrap = document.getElementById("wrap");
  const cssW = wrap.clientWidth;

  // altura proporcional + margem p/ rótulos abaixo
  const scale = cssW / BASE_W;
  const cssH = Math.round(Math.max(320, BASE_H*scale + 70));

  canvas.style.width = "100%";
  canvas.style.height = cssH + "px";

  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.round(cssW * dpr);
  canvas.height = Math.round(cssH * dpr);

  // desenhar em "px CSS" (coord. naturais)
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  drawAll(cssW, cssH, scale);
}}

window.addEventListener("resize", resizeAndDraw);
window.addEventListener("orientationchange", resizeAndDraw);
setTimeout(resizeAndDraw, 80);
</script>
"""

# altura do iframe um pouco maior para evitar “corte” em alguns celulares
components.html(html, height=560, scrolling=False)

# ===================== Seção Forças =====================
st.header("Forças Eletrostáticas")

st.latex(r"F = K\frac{|q_a q_b|}{r^2}")
st.markdown(
    "onde $q_a$ e $q_b$ são as cargas das partículas interagindo, $r$ é a distância entre elas e "
    "**K é a constante de Coulomb igual a 9,0×10⁹ N·m²/C²**."
)

# ===================== Resultados destacados =====================
st.subheader("Resultados (sentido no eixo x)")

def result_card(title, value, direction, color):
    st.markdown(
        f"""
        <div style="
            border-left: 8px solid {color};
            background: #fafafa;
            padding: 14px 16px;
            border-radius: 14px;
            box-shadow: 0 1px 6px rgba(0,0,0,0.06);
            margin-bottom: 10px;">
          <div class="result-card-title"><b>{title}</b></div>
          <div class="result-card-value"><b>{value}</b> <span style="font-size: 22px;">{direction}</span></div>
          <div class="result-card-foot">
            Apenas os <b>resultados finais</b> são exibidos com <b>2 algarismos significativos</b>.
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# colunas no desktop, empilha no mobile via CSS acima
c1, c2, c3 = st.columns(3)
with c1:
    result_card("Força na partícula 3 devido à partícula 1 (F₁₃)",
                br_sci_force_text(F13_disp, 2, "N"),
                arrow_symbol(F13_disp),
                "#d62728")
with c2:
    result_card("Força na partícula 3 devido à partícula 2 (F₂₃)",
                br_sci_force_text(F23_disp, 2, "N"),
                arrow_symbol(F23_disp),
                "#1f77b4")
with c3:
    result_card("Força Resultante na partícula 3 (Fᵣ)",
                br_sci_force_text(Fr_disp, 2, "N"),
                arrow_symbol(Fr_disp),
                "#2ca02c")

# ===================== Cálculos =====================
st.subheader("Cálculos")

st.markdown("**Força na partícula 3 devido à partícula 1 (F₁₃)**")
st.latex(r"F_{13} = K\frac{|q_1 q_3|}{r_{13}^2}")
st.latex(
    rf"F_{{13}} = (9{{,}}0\times10^9)\cdot \frac{{\left|({latex_charge_C_from_uC(q1_uC)})({latex_charge_C_from_uC(q3_uC)})\right|}}{{({latex_dist_from_positions(x3, x1)})^2}}"
)

st.markdown("**Força na partícula 3 devido à partícula 2 (F₂₃)**")
st.latex(r"F_{23} = K\frac{|q_2 q_3|}{r_{23}^2}")
st.latex(
    rf"F_{{23}} = (9{{,}}0\times10^9)\cdot \frac{{\left|({latex_charge_C_from_uC(q2_uC)})({latex_charge_C_from_uC(q3_uC)})\right|}}{{({latex_dist_from_positions(x3, x2)})^2}}"
)

st.markdown("**Força Resultante na partícula 3**")
st.latex(r"\vec{F}_r = \vec{F}_{13} + \vec{F}_{23}")

if equilibrio:
    st.success("✅ A partícula 3 está na **posição de equilíbrio** (Fᵣ = 0, com 2 algarismos significativos).")
else:
    st.info("ℹ️ Ajuste posições/cargas para tentar obter **Fᵣ ≈ 0** (com 2 algarismos significativos).")
