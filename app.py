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

def br_float(x, nd=2):
    """Formata número em notação decimal com vírgula, com nd casas."""
    return br_decimal(f"{x:.{nd}f}")

_sup_map = str.maketrans("0123456789-+", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺")

def sci_parts(x, n=2):
    """Retorna (mantissa, expoente) com n algarismos significativos na mantissa."""
    if x == 0:
        return 0.0, 0
    exp = int(math.floor(math.log10(abs(x))))
    mant = x / (10 ** exp)
    mant = float(f"{mant:.{n}g}")
    # Ajuste se arredondamento virar 10
    if abs(mant) >= 10:
        mant /= 10
        exp += 1
    return mant, exp

def br_sci_text(x, n=2, unit=""):
    """Notação científica em texto com vírgula: 2,0×10⁻⁶ N"""
    if x == 0:
        out = "0"
    else:
        mant, exp = sci_parts(x, n)
        mant_s = br_decimal(f"{mant:.{n}g}")
        out = f"{mant_s}×10{str(exp).translate(_sup_map)}"
    return f"{out}{(' ' + unit) if unit else ''}"

def latex_sci(x, n=2):
    """Notação científica para LaTeX com vírgula decimal: 2{,}0\\times10^{-6}"""
    if x == 0:
        return "0"
    mant, exp = sci_parts(x, n)
    # mantissa em LaTeX com vírgula
    mant_s = f"{mant:.{n}g}".replace(".", "{,}")
    return rf"{mant_s}\times10^{{{exp}}}"

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

def nice_step(span):
    """
    Escolhe passo "bonito" para o eixo, baseado no span.
    Retorna um valor em [0.1, 0.2, 0.5, 1, 2, 5, 10, ...]
    """
    if span <= 0:
        return 1.0
    raw = span / 8  # queremos ~8 marcações
    p = 10 ** math.floor(math.log10(raw))
    m = raw / p
    if m < 1.5:
        step = 1 * p
    elif m < 3.5:
        step = 2 * p
    elif m < 7.5:
        step = 5 * p
    else:
        step = 10 * p
    # limite mínimo para evitar ticks "grudados"
    return max(step, 0.1)

# ===================== Cabeçalho =====================

st.image("logo_maua.png", width=180)
st.title("Simulador Força Eletrostática Unidimensional")
st.write(
    "Veja as forças aplicadas na partícula carregada **3** quando posicionada próxima a "
    "outras duas partículas carregadas **1** e **2**."
)

# ===================== Controles =====================

st.header("Definições das Partículas")

col1, col2, col3 = st.columns(3)

# Melhorando sliders de carga: trabalhar em µC (microcoulomb)
# Range típico escolar: -5 µC a +5 µC com passo fino (0,05 µC = 50 nC)
qmin_uC, qmax_uC, qstep_uC = -5.0, 5.0, 0.05

with col1:
    st.subheader("Partícula 1")
    x1 = st.slider("Posição x₁ (m)", -10.0, 10.0, -4.0, 0.1, format="%.1f")
    q1_uC = st.slider("Carga q₁ (µC)", qmin_uC, qmax_uC, 2.0, qstep_uC, format="%.2f")
    q1 = q1_uC * 1e-6

with col2:
    st.subheader("Partícula 2")
    x2 = st.slider("Posição x₂ (m)", -10.0, 10.0, 4.0, 0.1, format="%.1f")
    q2_uC = st.slider("Carga q₂ (µC)", qmin_uC, qmax_uC, -2.0, qstep_uC, format="%.2f")
    q2 = q2_uC * 1e-6

with col3:
    st.subheader("Partícula 3")
    x3 = st.slider("Posição x₃ (m)", -10.0, 10.0, 0.0, 0.1, format="%.1f")
    q3_uC = st.slider("Carga q₃ (µC)", qmin_uC, qmax_uC, 1.0, qstep_uC, format="%.2f")
    q3 = q3_uC * 1e-6

# Bloqueio de posições iguais
if len({x1, x2, x3}) < 3:
    st.error("❌ As partículas **não podem** estar na mesma posição. Ajuste x₁, x₂ e x₃.")
    st.stop()

# ===================== Física =====================

K = 9.0e9

F13, r13 = coulomb_force_1d(q3, q1, x3, x1, K=K)  # força em 3 devido a 1
F23, r23 = coulomb_force_1d(q3, q2, x3, x2, K=K)  # força em 3 devido a 2
Fr = F13 + F23

# Duas casas significativas (para exibição e equilíbrio)
F13s = sig(F13, 2)
F23s = sig(F23, 2)
Frs  = sig(Fr, 2)
r13s = sig(r13, 2)
r23s = sig(r23, 2)

# Critério de equilíbrio (coerente com 2 alg. sig.)
equilibrio = (Frs == 0.0)

# ===================== Zoom automático do eixo =====================

xmin = min(x1, x2, x3)
xmax = max(x1, x2, x3)
span = xmax - xmin

# margem proporcional + mínima
margin = max(1.0, 0.25 * span)
xMin = xmin - margin
xMax = xmax + margin

# Evita eixo degenerado
if math.isclose(xMin, xMax):
    xMin -= 1
    xMax += 1

step = nice_step(xMax - xMin)

# ticks bonitos
t0 = math.floor(xMin / step) * step
ticks = []
t = t0
# garante cobertura do intervalo
while t <= xMax + 1e-9:
    ticks.append(round(t, 10))
    t += step

# ===================== Escala dos vetores =====================

maxF = max(abs(F13), abs(F23), abs(Fr), 1e-30)
L13 = 120 * abs(F13) / maxF
L23 = 120 * abs(F23) / maxF
Lr  = 140 * abs(Fr)  / maxF

d13 = 0 if math.isclose(F13, 0.0, abs_tol=0.0) else (1 if F13 > 0 else -1)
d23 = 0 if math.isclose(F23, 0.0, abs_tol=0.0) else (1 if F23 > 0 else -1)
dr  = 0 if math.isclose(Fr,  0.0, abs_tol=0.0) else (1 if Fr  > 0 else -1)

# ===================== Figura (Canvas com fundo branco) =====================

st.header("Figura – Sistema Unidimensional (com zoom automático)")

# Para mostrar vírgula no canvas, enviaremos strings prontas para as legendas
q1_str = br_sci_text(q1, 2, "C")
q2_str = br_sci_text(q2, 2, "C")
q3_str = br_sci_text(q3, 2, "C")

html = f"""
<canvas id="canvas" width="1000" height="340" style="background: white; border: 1px solid #eee;"></canvas>

<script>
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const W = canvas.width;
const H = canvas.height;

// fundo branco (reforçado)
ctx.fillStyle = "white";
ctx.fillRect(0, 0, W, H);

// intervalo do eixo (zoom automático)
const xMin = {xMin};
const xMax = {xMax};

// margens em pixels
const padL = 50;
const padR = 50;

function X(x) {{
  return padL + (x - xMin) * ((W - padL - padR) / (xMax - xMin));
}}

const yAxis = H/2 + 40;

// ---------- Eixo ----------
function drawAxis() {{
  ctx.strokeStyle = "#111";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(padL, yAxis);
  ctx.lineTo(W - padR, yAxis);
  ctx.stroke();

  // ticks
  const ticks = {ticks};
  ctx.fillStyle = "#111";
  ctx.font = "14px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "top";

  ticks.forEach(t => {{
    const px = X(t);
    ctx.beginPath();
    ctx.moveTo(px, yAxis - 7);
    ctx.lineTo(px, yAxis + 7);
    ctx.stroke();

    // rótulo com vírgula decimal
    const label = (Math.round(t*10)/10).toString().replace(".", ",");
    ctx.fillText(label, px, yAxis + 10);
  }});

  // unidade
  ctx.textAlign = "right";
  ctx.textBaseline = "bottom";
  ctx.fillText("x (m)", W - padR, yAxis - 10);
}}

// ---------- Partícula como círculo numerado ----------
function drawParticle(x, n, qText) {{
  const px = X(x);
  const py = yAxis;

  // círculo
  ctx.fillStyle = "#f7f7f7";
  ctx.strokeStyle = "#111";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(px, py, 16, 0, 2*Math.PI);
  ctx.fill();
  ctx.stroke();

  // número dentro
  ctx.fillStyle = "#111";
  ctx.font = "bold 16px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(n.toString(), px, py);

  // legenda da carga acima
  ctx.fillStyle = "#111";
  ctx.font = "14px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "bottom";
  ctx.fillText("q" + n + " = " + qText, px, py - 22);
}}

// ---------- Seta ----------
function drawArrow(x0, y0, dx, color, label) {{
  // dx em pixels
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = 3;

  if (dx === 0) {{
    // marcador para ~0
    ctx.beginPath();
    ctx.moveTo(x0 - 8, y0);
    ctx.lineTo(x0 + 8, y0);
    ctx.stroke();

    ctx.font = "14px Arial";
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    ctx.fillText(label + " ≈ 0", x0 + 12, y0);
    return;
  }}

  const x1 = x0 + dx;

  // corpo
  ctx.beginPath();
  ctx.moveTo(x0, y0);
  ctx.lineTo(x1, y0);
  ctx.stroke();

  // cabeça
  const head = 10;
  const s = (dx > 0) ? 1 : -1;
  ctx.beginPath();
  ctx.moveTo(x1, y0);
  ctx.lineTo(x1 - s*head, y0 - head*0.6);
  ctx.lineTo(x1 - s*head, y0 + head*0.6);
  ctx.closePath();
  ctx.fill();

  // rótulo
  ctx.font = "14px Arial";
  ctx.textAlign = (dx > 0) ? "left" : "right";
  ctx.textBaseline = "bottom";
  ctx.fillText(label, x1 + (dx > 0 ? 6 : -6), y0 - 6);
}}

drawAxis();

// Partículas
drawParticle({x1}, 1, "{q1_str}");
drawParticle({x2}, 2, "{q2_str}");
drawParticle({x3}, 3, "{q3_str}");

// Vetores na partícula 3 (em linhas separadas)
const px3 = X({x3});
drawArrow(px3, yAxis - 55, {d13} * {L13:.6f}, "#d62728", "F₁₃");
drawArrow(px3, yAxis - 25, {d23} * {L23:.6f}, "#1f77b4", "F₂₃");
drawArrow(px3, yAxis +  5, {dr}  * {Lr:.6f},  "#2ca02c", "Fᵣ");
</script>
"""
components.html(html, height=360)

# ===================== Seção Forças =====================

st.header("Forças Eletrostáticas")

st.latex(r"F = K\frac{|q_a q_b|}{r^2}")
st.write(
    "onde **qₐ** e **q_b** são as cargas das partículas interagindo, **r** é a distância entre elas e "
    "**K = 9,0×10⁹ N·m²/C²**."
)

# Texto auxiliar com vírgula
st.caption(
    f"Constante de Coulomb: K = {br_sci_text(K, 2, 'N·m²/C²')}"
)

# --------- F13 ---------
st.subheader("Força na partícula 3 devido à partícula 1 (F₁₃)")

st.latex(r"F_{13} = K\frac{|q_1 q_3|}{r_{13}^2} \;\;\; \text{(módulo)}")
st.latex(
    rf"F_{{13}} = (9{{,}}0\times10^9)\cdot \frac{{\left|({latex_sci(q1,2)})({latex_sci(q3,2)})\right|}}{{({str(r13s).replace('.', '{,}')} )^2}}"
)
st.write(
    f"**F₁₃ = {br_sci_text(F13s, 2, 'N')}**  {arrow_symbol(F13s)}"
)

# --------- F23 ---------
st.subheader("Força na partícula 3 devido à partícula 2 (F₂₃)")

st.latex(r"F_{23} = K\frac{|q_2 q_3|}{r_{23}^2} \;\;\; \text{(módulo)}")
st.latex(
    rf"F_{{23}} = (9{{,}}0\times10^9)\cdot \frac{{\left|({latex_sci(q2,2)})({latex_sci(q3,2)})\right|}}{{({str(r23s).replace('.', '{,}')} )^2}}"
)
st.write(
    f"**F₂₃ = {br_sci_text(F23s, 2, 'N')}**  {arrow_symbol(F23s)}"
)

# --------- Resultante ---------
st.subheader("Força Resultante na partícula 3 (Fᵣ)")
st.latex(r"F_r = F_{13} + F_{23}")
st.write(
    f"**Fᵣ = {br_sci_text(Frs, 2, 'N')}**  {arrow_symbol(Frs)}"
)

if equilibrio:
    st.success("✅ A partícula 3 está na **posição de equilíbrio** (Fᵣ = 0, com 2 algarismos significativos).")
else:
    st.info("Ajuste **x₃** para buscar a condição de equilíbrio (Fᵣ ≈ 0).")
