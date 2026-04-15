import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Simulador Força Eletrostática", layout="wide")

# Logo e título
st.image("logo_maua.png", width=180)
st.title("Simulador Força Eletrostática Unidimensional")
st.write(
    "Veja as forças aplicadas na partícula carregada 3 quando posicionada "
    "próxima a outras duas partículas carregadas 1 e 2."
)

# ---------------- CONTROLES ----------------
st.header("Definições das Partículas")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Partícula 1")
    x1 = st.slider("Posição x1 (m)", -10.0, 10.0, -4.0, 0.1)
    q1 = st.slider("Carga q1 (C)", -5e-6, 5e-6, 2e-6, 1e-7, format="%.2e")

with col2:
    st.subheader("Partícula 2")
    x2 = st.slider("Posição x2 (m)", -10.0, 10.0, 4.0, 0.1)
    q2 = st.slider("Carga q2 (C)", -5e-6, 5e-6, -2e-6, 1e-7, format="%.2e")

with col3:
    st.subheader("Partícula 3")
    x3 = st.slider("Posição x3 (m)", -10.0, 10.0, 0.0, 0.1)
    q3 = st.slider("Carga q3 (C)", -5e-6, 5e-6, 1e-6, 1e-7, format="%.2e")

# Verificação de posições coincidentes
if len({x1, x2, x3}) < 3:
    st.error("❌ As partículas não podem estar na mesma posição.")
    st.stop()

# ---------------- CONSTANTES ----------------
K = 9.0e9

# Cálculo das forças
def força(qi, qj, xi, xj):
    r = xi - xj
    F = K * qi * qj / (r ** 2)
    return F * (1 if r > 0 else -1), abs(r)

F13, r13 = força(q3, q1, x3, x1)
F23, r23 = força(q3, q2, x3, x2)
Fr = F13 + F23

# ---------------- FIGURA ----------------
st.header("Figura – Sistema Unidimensional")

html = f"""
<canvas id="canvas" width="900" height="250"></canvas>

<script>
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const xMin = -10;
const xMax = 10;
const scale = canvas.width / (xMax - xMin);

function X(x) {{
  return (x - xMin) * scale;
}}

ctx.clearRect(0,0,canvas.width,canvas.height);

// eixo
ctx.beginPath();
ctx.moveTo(0,125);
ctx.lineTo(canvas.width,125);
ctx.stroke();

// partículas
const particles = [
  {{x:{x1}, q:{q1}, label:"q1"}},
  {{x:{x2}, q:{q2}, label:"q2"}},
  {{x:{x3}, q:{q3}, label:"q3"}}
];

particles.forEach(p => {{
  ctx.beginPath();
  ctx.arc(X(p.x),125,6,0,2*Math.PI);
  ctx.fillStyle="black";
  ctx.fill();
  ctx.fillText(`${{p.label}} = ${{p.q.toExponential(2)}} C`, X(p.x)-30, 100);
}});

// vetores força
function drawArrow(x, y, fx, color, label) {{
  ctx.beginPath();
  ctx.moveTo(x, y);
  ctx.lineTo(x + fx, y);
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.stroke();
  ctx.fillText(label, x + fx + 5, y - 5);
}}

drawArrow(X({x3}), 125, {F13/Math.abs(F13+1e-12)}*60, "red", "F₁₃");
drawArrow(X({x3}), 125, {F23/Math.abs(F23+1e-12)}*60, "blue", "F₂₃");
drawArrow(X({x3}), 125, {Fr/Math.abs(Fr+1e-12)}*90, "green", "Fᵣ");
</script>
"""

components.html(html, height=270)

# ---------------- FORÇAS ----------------
st.header("Forças Eletrostáticas")

st.latex(r"F = K \frac{q_a q_b}{r^2}")
st.write(
    "onde $q_a$ e $q_b$ são as cargas das partículas que interagem, "
    "$r$ é a distância entre elas e "
    "$K = 9,0\\times10^9\\, \\mathrm{N·m^2/C^2}$."
)

st.subheader("Força F₁₃")
st.latex(
    rf"F_{{13}} = 9,0\times10^9 \cdot \frac{{({q3:.2e})({q1:.2e})}}{{({r13:.2f})^2}}"
)
st.write(f"**F₁₃ = {F13:.2e} N** {'→' if F13>0 else '←'}")

st.subheader("Força F₂₃")
st.latex(
    rf"F_{{23}} = 9,0\times10^9 \cdot \frac{{({q3:.2e})({q2:.2e})}}{{({r23:.2f})^2}}"
)
st.write(f"**F₂₃ = {F23:.2e} N** {'→' if F23>0 else '←'}")

st.subheader("Força Resultante")
st.write(f"**Fᵣ = {Fr:.2e} N** {'→' if Fr>0 else '←'}")

if abs(Fr) < 1e-12:
    st.success("✅ A partícula 3 está na **posição de equilíbrio** (Fᵣ = 0).")
