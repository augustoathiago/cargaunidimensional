import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Simulador Força Eletrostática", layout="wide")

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
    F = K * qi * qj * (r / (dist**3))
    return F, dist

# ---------- Formatação "EXATA" como sliders ----------
# Aqui a ideia é preservar a resolução do slider:
# - cargas: 2 casas (µC)
# - posições: 1 casa (m)
# e evitar ruído binário (ex.: 3.999999999) usando round na mesma resolução.

def fmt_uC_br(q_uC: float) -> str:
    """Retorna a carga do slider em µC com 2 casas e vírgula."""
    return f"{round(q_uC, 2):.2f}".replace(".", ",")

def latex_charge_C_from_uC(q_uC: float) -> str:
    """
    Retorna LaTeX da carga em Coulomb, exibindo exatamente o valor do slider em µC (2 casas),
    convertido para (mantissa × 10^{-6}) C.
    Ex.: 2,35 µC -> 2{,}35\\times10^{-6}
    """
    if math.isclose(q_uC, 0.0, abs_tol=0.0):
        return r"0"
    mant = f"{round(q_uC, 2):.2f}".replace(".", "{,}")
    return rf"{mant}\times10^{{-6}}"

def fmt_pos_br(x: float) -> str:
    """Retorna posição do slider com 1 casa e vírgula."""
    return f"{round(x, 1):.1f}".replace(".", ",")

def latex_dist_from_positions(xa: float, xb: float) -> str:
    """Distância |xa-xb| exibida com 1 casa (mesma resolução do slider) em LaTeX."""
    d = abs(round(xa, 1) - round(xb, 1))
    return f"{d:.1f}".replace(".", "{,}")

def br_charge_canvas_from_uC(q_uC: float) -> str:
    """Texto para canvas: mostra q com 2 casas do slider em µC convertido para C em notação 10^-6."""
    if math.isclose(q_uC, 0.0, abs_tol=0.0):
        return "0 C"
    mant_s = fmt_uC_br(q_uC)  # já com vírgula e 2 casas
    exp = -6
    return f"{mant_s}×10{str(exp).translate(_sup_map)} C"

# ===================== Cabeçalho =====================

st.image("logo_maua.png", width=180)
st.title("Simulador Força Eletrostática Unidimensional")
st.write(
    "Veja as forças aplicadas na partícula carregada **3** quando posicionada próxima a "
    "outras duas partículas carregadas **1** e **2**."
)

st.markdown("**Desafio: tente encontrar uma situação onde a partícula 3 está em equilíbrio)**")

# ===================== Controles =====================

st.header("Definições das Partículas")

col1, col2, col3 = st.columns(3)

# Sliders de carga (µC)
qmin_uC, qmax_uC, qstep_uC = -5.0, 5.0, 0.05

# Sliders de posição -10 a 10
xmin_slider, xmax_slider = -10.0, 10.0

with col1:
    st.subheader("Partícula 1")
    x1 = st.slider("Posição x₁ (m)", xmin_slider, xmax_slider, -4.0, 0.1, format="%.1f")
    q1_uC = st.slider("Carga q₁ (µC)", qmin_uC, qmax_uC, 2.0, qstep_uC, format="%.2f")
    q1 = q1_uC * 1e-6

with col2:
    st.subheader("Partícula 2")
    x2 = st.slider("Posição x₂ (m)", xmin_slider, xmax_slider, 4.0, 0.1, format="%.1f")
    q2_uC = st.slider("Carga q₂ (µC)", qmin_uC, qmax_uC, -2.0, qstep_uC, format="%.2f")
    q2 = q2_uC * 1e-6

with col3:
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

# forças "reais" (sem arredondar q nem r)
F13_raw, r13 = coulomb_force_1d(q3, q1, x3, x1, K=K)
F23_raw, r23 = coulomb_force_1d(q3, q2, x3, x2, K=K)

# ✅ Apenas forças finais exibidas arredondadas para 2 AS
F13_disp = sig(F13_raw, 2)
F23_disp = sig(F23_raw, 2)

# ✅ Equilíbrio didático: soma usando forças exibidas (já em 2 AS)
Fr_disp = sig(F13_disp + F23_disp, 2)
equilibrio = (Fr_disp == 0.0)

# ===================== Eixo e ticks (1 em 1, inclui 0) =====================

xMin = -15.0
xMax =  15.0
ticks = list(range(-15, 16, 1))  # inclui 0

# ===================== Escala dos vetores (com forças exibidas) =====================

maxF = max(abs(F13_disp), abs(F23_disp), abs(Fr_disp), 1e-30)
L13 = 120 * abs(F13_disp) / maxF
L23 = 120 * abs(F23_disp) / maxF
Lr  = 140 * abs(Fr_disp)  / maxF

d13 = 0 if math.isclose(F13_disp, 0.0, abs_tol=0.0) else (1 if F13_disp > 0 else -1)
d23 = 0 if math.isclose(F23_disp, 0.0, abs_tol=0.0) else (1 if F23_disp > 0 else -1)
dr  = 0 if math.isclose(Fr_disp,  0.0, abs_tol=0.0) else (1 if Fr_disp  > 0 else -1)

# ===================== Figura (Canvas) =====================

st.header("Figura – Sistema Unidimensional")

q1_str = br_charge_canvas_from_uC(q1_uC)
q2_str = br_charge_canvas_from_uC(q2_uC)
q3_str = br_charge_canvas_from_uC(q3_uC)

html = f"""
<canvas id="canvas" width="1000" height="410" style="background: white; border: 1px solid #eee;"></canvas>

<script>
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const W = canvas.width;
const H = canvas.height;

ctx.fillStyle = "white";
ctx.fillRect(0, 0, W, H);

const xMin = {xMin};
const xMax = {xMax};

const padL = 50;
const padR = 50;

function X(x) {{
  return padL + (x - xMin) * ((W - padL - padR) / (xMax - xMin));
}}

const yAxis = 235;

// ---------- Eixo ----------
function drawAxis() {{
  ctx.strokeStyle = "#111";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(padL, yAxis);
  ctx.lineTo(W - padR, yAxis);
  ctx.stroke();

  const ticks = {ticks};
  ctx.fillStyle = "#111";
  ctx.font = "13px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "top";

  ticks.forEach(t => {{
    const px = X(t);
    ctx.beginPath();
    ctx.moveTo(px, yAxis - 7);
    ctx.lineTo(px, yAxis + 7);
    ctx.stroke();

    const label = t.toString().replace(".", ",");
    ctx.fillText(label, px, yAxis + 10);
  }});

  ctx.textAlign = "right";
  ctx.textBaseline = "bottom";
  ctx.fillText("x (m)", W - padR, yAxis - 10);
}}

// ---------- Cor da borda pela carga ----------
function borderColorByCharge(q) {{
  const eps = 1e-15;
  if (q > eps) return "#d62728";
  if (q < -eps) return "#1f77b4";
  return "#111";
}}

// ---------- Partícula ----------
function drawParticle(x, n, qText, qValue) {{
  const px = X(x);
  const py = yAxis;

  ctx.fillStyle = "#f7f7f7";
  ctx.strokeStyle = borderColorByCharge(qValue);
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(px, py, 16, 0, 2*Math.PI);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = "#111";
  ctx.font = "bold 16px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(n.toString(), px, py);

  return {{px, py, n, qText}};
}}

// Cargas abaixo do eixo
function drawChargeLabelsBelow(particles) {{
  particles.sort((a,b) => a.px - b.px);

  const baseY = yAxis + 62;
  const dy = 16;
  const minDx = 140;
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
  ctx.font = "14px Arial";
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
      ctx.moveTo(p.px, yAxis + 18);
      ctx.lineTo(p.px, y - 2);
      ctx.stroke();
    }}

    ctx.fillText(`${{qSub[p.n]}} = ${{p.qText}}`, p.px, y);
  }}
}}

// Seta "de vetor" acima do texto do rótulo
function drawVectorOverLabel(text, xAnchor, yBaseline, align, color) {{
  ctx.save();
  ctx.font = "14px Arial";
  ctx.fillStyle = color;
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;

  const w = ctx.measureText(text).width;
  let xLeft = xAnchor;
  if (align === "right") xLeft = xAnchor - w;
  if (align === "center") xLeft = xAnchor - w/2;

  const yArrow = yBaseline - 16;
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

// Vetor (seta)
function drawArrow(x0, y0, dx, color, label) {{
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = 3;

  if (dx === 0) {{
    ctx.beginPath();
    ctx.moveTo(x0 - 8, y0);
    ctx.lineTo(x0 + 8, y0);
    ctx.stroke();

    ctx.font = "14px Arial";
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    ctx.fillText(label + " ≈ 0", x0 + 12, y0);

    drawVectorOverLabel(label, x0 + 12, y0, "left", color);
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

  ctx.font = "14px Arial";
  const align = (dx > 0) ? "left" : "right";
  ctx.textAlign = align;
  ctx.textBaseline = "bottom";
  const xText = x1 + (dx > 0 ? 6 : -6);
  const yText = y0 - 6;
  ctx.fillText(label, xText, yText);

  drawVectorOverLabel(label, xText, yText, align, color);
}}

drawAxis();

const parts = [];
parts.push(drawParticle({x1}, 1, "{q1_str}", {q1}));
parts.push(drawParticle({x2}, 2, "{q2_str}", {q2}));
parts.push(drawParticle({x3}, 3, "{q3_str}", {q3}));

drawChargeLabelsBelow(parts);

const px3 = X({x3});
drawArrow(px3, yAxis - 95, {d13} * {L13:.6f}, "#d62728", "F₁₃");
drawArrow(px3, yAxis - 65, {d23} * {L23:.6f}, "#1f77b4", "F₂₃");
drawArrow(px3, yAxis - 35, {dr}  * {Lr:.6f},  "#2ca02c", "Fᵣ");
</script>
"""
components.html(html, height=430)

# ===================== Seção Forças =====================

st.header("Forças Eletrostáticas")

st.latex(r"F = K\frac{|q_a q_b|}{r^2}")
st.markdown(
    "onde $q_a$ e $q_b$ são as cargas das partículas interagindo, $r$ é a distância entre elas e "
    "**K = 9,0×10⁹ N·m²/C²**."
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
          <div style="font-size: 14px; color: #333; margin-bottom: 6px;"><b>{title}</b></div>
          <div style="font-size: 24px; color: #111;"><b>{value}</b> <span style="font-size: 22px;">{direction}</span></div>
          <div style="font-size: 12px; color: #555; margin-top: 6px;">
            Apenas os <b>resultados finais</b> são exibidos com <b>2 algarismos significativos</b>.
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

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

# Equações: mostrar q e r com os valores EXATOS dos sliders (resolução do slider),
# sem "sig()" aqui. Somente o valor final da força exibida é 2 AS.

st.markdown("**Força na partícula 3 devido à partícula 1 (F₁₃)**")
st.latex(r"F_{13} = K\frac{|q_1 q_3|}{r_{13}^2}")
st.latex(
    rf"F_{{13}} = (9{{,}}0\times10^9)\cdot \frac{{\left|({latex_charge_C_from_uC(q1_uC)})({latex_charge_C_from_uC(q3_uC)})\right|}}{{({latex_dist_from_positions(x3, x1)})^2}}"
)
st.markdown(f"**Valor exibido:** {br_sci_force_text(F13_disp, 2, 'N')}  {arrow_symbol(F13_disp)}")

st.markdown("**Força na partícula 3 devido à partícula 2 (F₂₃)**")
st.latex(r"F_{23} = K\frac{|q_2 q_3|}{r_{23}^2}")
st.latex(
    rf"F_{{23}} = (9{{,}}0\times10^9)\cdot \frac{{\left|({latex_charge_C_from_uC(q2_uC)})({latex_charge_C_from_uC(q3_uC)})\right|}}{{({latex_dist_from_positions(x3, x2)})^2}}"
)
st.markdown(f"**Valor exibido:** {br_sci_force_text(F23_disp, 2, 'N')}  {arrow_symbol(F23_disp)}")

st.markdown("**Força Resultante na partícula 3**")
st.latex(r"\vec{F}_r = \vec{F}_{13} + \vec{F}_{23}")
st.markdown(f"**Valor exibido:** {br_sci_force_text(Fr_disp, 2, 'N')}  {arrow_symbol(Fr_disp)}")

if equilibrio:
    st.success("✅ A partícula 3 está na **posição de equilíbrio** (Fᵣ = 0, com 2 algarismos significativos).")
