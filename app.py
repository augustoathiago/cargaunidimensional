import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Simulador Força Eletrostática", layout="wide")

# ----------------- Funções auxiliares -----------------
def sig(x, n=2):
    """Retorna x com n algarismos significativos (float)."""
    if x == 0 or math.isclose(x, 0.0, abs_tol=0.0):
        return 0.0
    return float(f"{x:.{n}g}")

def sig_str(x, n=2, unit=""):
    """String com n algarismos significativos (notação científica quando necessário)."""
    if x == 0:
        s = "0"
    else:
        s = f"{x:.{n}e}"
    return f"{s}{(' ' + unit) if unit else ''}"

def coulomb_force_1d(qi, qj, xi, xj, K=9e9):
    """
    Força (1D) em i devido a j:
    F = k*qi*qj*(xi-xj)/|xi-xj|^3
    Retorna (F, r=|xi-xj|)
    """
    r = xi - xj
    dist = abs(r)
    # dist=0 é bloqueado antes
    F = K * qi * qj * (r / (dist**3))
    return F, dist

def arrow_symbol(F, tol=0.0):
    """Seta indicando sentido no eixo x."""
    if abs(F) <= tol:
        return "⟷"
    return "→" if F > 0 else "←"

# ----------------- Cabeçalho -----------------
st.image("logo_maua.png", width=180)
st.title("Simulador Força Eletrostática Unidimensional")
st.write(
    "Veja as forças aplicadas na partícula carregada **3** quando posicionada próxima a "
    "outras duas partículas carregadas **1** e **2**."
)

# ----------------- Controles -----------------
st.header("Definições das Partículas")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Partícula 1")
    x1 = st.slider("Posição x1 (m)", -10.0, 10.0, -4.0, 0.1, format="%.1f")
    q1 = st.slider("Carga q1 (C)", -5e-6, 5e-6, 2e-6, 1e-7, format="%.2e")

with col2:
    st.subheader("Partícula 2")
    x2 = st.slider("Posição x2 (m)", -10.0, 10.0, 4.0, 0.1, format="%.1f")
    q2 = st.slider("Carga q2 (C)", -5e-6, 5e-6, -2e-6, 1e-7, format="%.2e")

with col3:
    st.subheader("Partícula 3")
    x3 = st.slider("Posição x3 (m)", -10.0, 10.0, 0.0, 0.1, format="%.1f")
    q3 = st.slider("Carga q3 (C)", -5e-6, 5e-6, 1e-6, 1e-7, format="%.2e")

# Bloqueio de posições iguais
if len({x1, x2, x3}) < 3:
    st.error("❌ As partículas **não podem** estar na mesma posição. Ajuste x1, x2 e x3.")
    st.stop()

# ----------------- Física -----------------
K = 9.0e9

F13, r13 = coulomb_force_1d(q3, q1, x3, x1, K=K)  # força em 3 devido a 1
F23, r23 = coulomb_force_1d(q3, q2, x3, x2, K=K)  # força em 3 devido a 2
Fr = F13 + F23

# Arredondamento em 2 algarismos significativos (para exibição e equilíbrio)
F13s = sig(F13, 2)
F23s = sig(F23, 2)
Frs  = sig(Fr,  2)
r13s = sig(r13, 2)
r23s = sig(r23, 2)

# Critério de equilíbrio coerente com 2 alg. sig.
equilibrio = (Frs == 0.0)

# ----------------- Escala de vetores (Canvas) -----------------
# Comprimentos em pixels proporcionais às magnitudes (limitados)
maxF = max(abs(F13), abs(F23), abs(Fr), 1e-30)
# vetor "grande" ~ 120 px
L13 = 120 * abs(F13) / maxF
L23 = 120 * abs(F23) / maxF
Lr  = 140 * abs(Fr)  / maxF

# direções
d13 = 0 if math.isclose(F13, 0.0, abs_tol=0.0) else (1 if F13 > 0 else -1)
d23 = 0 if math.isclose(F23, 0.0, abs_tol=0.0) else (1 if F23 > 0 else -1)
dr  = 0 if math.isclose(Fr,  0.0, abs_tol=0.0) else (1 if Fr  > 0 else -1)

# ----------------- Figura (Canvas HTML) -----------------
st.header("Figura – Sistema Unidimensional")

# Configuração do eixo
xMin, xMax = -10, 10
ticks = list(range(xMin, xMax + 1, 2))  # marcações de 2 em 2

html = f"""
<canvas id="canvas" width="980" height="280" style="border:0px solid #ccc;"></canvas>

<script>
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const xMin = {xMin};
const xMax = {xMax};
const W = canvas.width;
const H = canvas.height;

function X(x) {{
  return (x - xMin) * (W / (xMax - xMin));
}}

function drawAxis() {{
  // eixo
  ctx.strokeStyle = "#111";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(20, H/2);
  ctx.lineTo(W-20, H/2);
  ctx.stroke();

  // ticks e rótulos
  ctx.fillStyle = "#111";
  ctx.font = "14px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "top";

  const ticks = {ticks};
  ticks.forEach(t => {{
    const px = X(t);
    ctx.beginPath();
    ctx.moveTo(px, H/2 - 7);
    ctx.lineTo(px, H/2 + 7);
    ctx.stroke();
    ctx.fillText(t.toString(), px, H/2 + 10);
  }});
}}

function drawParticle(x, label, q, color) {{
  const px = X(x);
  const py = H/2;

  // ponto
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(px, py, 7, 0, 2*Math.PI);
  ctx.fill();

  // legenda acima
  ctx.fillStyle = "#111";
  ctx.font = "14px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "bottom";
  ctx.fillText(label + " = " + q.toExponential(2) + " C", px, py - 15);
}}

function drawArrow(x0, y0, dx, color, label) {{
  // dx em pixels (positivo para direita, negativo para esquerda)
  if (dx === 0) {{
    // pequeno marcador quando a força ~ 0
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(x0 - 8, y0);
    ctx.lineTo(x0 + 8, y0);
    ctx.stroke();
    ctx.fillStyle = color;
    ctx.font = "14px Arial";
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    ctx.fillText(label + " ≈ 0", x0 + 12, y0);
    return;
  }}

  const x1 = x0 + dx;
  ctx.strokeStyle = color;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(x0, y0);
  ctx.lineTo(x1, y0);
  ctx.stroke();

  // cabeça da seta
  const head = 10;
  const ang = Math.atan2(0, dx);
  ctx.beginPath();
  ctx.moveTo(x1, y0);
  ctx.lineTo(x1 - head*Math.cos(ang) + head*Math.sin(ang), y0 - head*Math.sin(ang) - head*Math.cos(ang));
  ctx.lineTo(x1 - head*Math.cos(ang) - head*Math.sin(ang), y0 + head*Math.sin(ang) - head*Math.cos(ang));
  ctx.closePath();
  ctx.fillStyle = color;
  ctx.fill();

  // rótulo da seta
  ctx.fillStyle = color;
  ctx.font = "14px Arial";
  ctx.textAlign = (dx > 0) ? "left" : "right";
  ctx.textBaseline = "bottom";
  ctx.fillText(label, x1 + (dx > 0 ? 6 : -6), y0 - 6);
}}

ctx.clearRect(0,0,W,H);
drawAxis();

// Partículas
drawParticle({x1}, "q1", {q1}, "#000000");
drawParticle({x2}, "q2", {q2}, "#000000");
drawParticle({x3}, "q3", {q3}, "#000000");

// Vetores na partícula 3
const px3 = X({x3});
const py3 = H/2;

// desloca um pouco as setas verticalmente para não sobrepor
drawArrow(px3, py3 - 28, {d13} * {L13:.6f}, "#d62728", "F₁₃");
drawArrow(px3, py3,       {d23} * {L23:.6f}, "#1f77b4", "F₂₃");
drawArrow(px3, py3 + 28,  {dr}  * {Lr:.6f},  "#2ca02c", "Fᵣ");
</script>
"""
components.html(html, height=300)

# ----------------- Seção Forças -----------------
st.header("Forças Eletrostáticas")

st.latex(r"F = K\frac{q_a q_b}{r^2}")
st.write(
    "onde $q_a$ e $q_b$ são as cargas das partículas interagindo, "
    "$r$ é a distância entre elas e "
    "$K = 9{,}0\\times10^9\\;\\mathrm{N\\cdot m^2/C^2}$."
)

# Mostrar valores com 2 alg. sig.
st.subheader("Força na partícula 3 devido à partícula 1 (F₁₃)")

st.latex(r"F_{13} = K\frac{q_1 q_3}{r_{13}^2}")
st.latex(
    rf"F_{{13}} = (9{{,}}0\times10^9)\cdot \frac{{({sig_str(q1,2)})({sig_str(q3,2)})}}{{({r13s:.2g})^2}}"
)
st.write(f"**F₁₃ = {sig_str(F13s,2,'N')}**  {arrow_symbol(F13s)}")

st.subheader("Força na partícula 3 devido à partícula 2 (F₂₃)")

st.latex(r"F_{23} = K\frac{q_2 q_3}{r_{23}^2}")
st.latex(
    rf"F_{{23}} = (9{{,}}0\times10^9)\cdot \frac{{({sig_str(q2,2)})({sig_str(q3,2)})}}{{({r23s:.2g})^2}}"
)
st.write(f"**F₂₃ = {sig_str(F23s,2,'N')}**  {arrow_symbol(F23s)}")

st.subheader("Força Resultante na partícula 3 (Fᵣ)")
st.latex(r"F_r = F_{13} + F_{23}")
st.write(f"**Fᵣ = {sig_str(Frs,2,'N')}**  {arrow_symbol(Frs)}")

if equilibrio:
    st.success("✅ A partícula 3 está na **posição de equilíbrio** (Fᵣ = 0, com 2 algarismos significativos).")
else:
    st.info("Ajuste a posição **x3** para buscar a condição de equilíbrio (Fᵣ ≈ 0).")
