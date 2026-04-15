import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Simulador Força Eletrostática", layout="wide")

# ================= Funções auxiliares =================

def sig(x, n=2):
    if x == 0:
        return 0.0
    return float(f"{x:.{n}g}")

def br_sci(x, n=2, unit=""):
    if x == 0:
        return f"0 {unit}"
    exp = int(math.floor(math.log10(abs(x))))
    mant = x / 10**exp
    mant = float(f"{mant:.{n}g}")
    return f"{str(mant).replace('.', ',')}×10^{exp} {unit}"

def arrow(F):
    if abs(F) < 1e-30:
        return "⟷"
    return "→" if F > 0 else "←"

def coulomb_1d(qi, qj, xi, xj, K=9e9):
    r = xi - xj
    d = abs(r)
    F = K * qi * qj * (r / d**3)
    return F, d

def cor_borda(q):
    if q > 0:
        return "#d62728"  # vermelho
    if q < 0:
        return "#1f77b4"  # azul
    return "#000000"      # preto

# ================= Cabeçalho =================

st.image("logo_maua.png", width=180)
st.title("Simulador Força Eletrostática Unidimensional")

st.write(
    "Veja as forças aplicadas na partícula carregada **3** "
    "quando posicionada próxima a outras duas partículas carregadas **1** e **2**."
)

# ================= Controles =================

st.header("Definições das Partículas")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Partícula 1")
    x1 = st.slider("Posição x₁ (m)", -15.0, 15.0, -4.0, 0.1)
    q1u = st.slider("Carga q₁ (µC)", -5.0, 5.0, 2.0, 0.05)
    q1 = q1u * 1e-6

with col2:
    st.subheader("Partícula 2")
    x2 = st.slider("Posição x₂ (m)", -15.0, 15.0, 4.0, 0.1)
    q2u = st.slider("Carga q₂ (µC)", -5.0, 5.0, -2.0, 0.05)
    q2 = q2u * 1e-6

with col3:
    st.subheader("Partícula 3")
    x3 = st.slider("Posição x₃ (m)", -15.0, 15.0, 0.0, 0.1)
    q3u = st.slider("Carga q₃ (µC)", -5.0, 5.0, 1.0, 0.05)
    q3 = q3u * 1e-6

if len({x1, x2, x3}) < 3:
    st.error("❌ As partículas não podem ocupar a mesma posição.")
    st.stop()

# ================= Física =================

F13, r13 = coulomb_1d(q3, q1, x3, x1)
F23, r23 = coulomb_1d(q3, q2, x3, x2)
Fr = F13 + F23

F13s = sig(F13)
F23s = sig(F23)
Frs = sig(Fr)

# ================= Figura =================

st.header("Figura – Sistema Unidimensional")

html = f"""
<canvas width="1000" height="330" id="cv"
style="background:white;border:1px solid #eee"></canvas>
<script>
const c = document.getElementById("cv");
const ctx = c.getContext("2d");
const W = c.width;
const H = c.height;
const y = H/2 + 30;
const xmin = -15, xmax = 15;

function X(x) {{
  return 60 + (x - xmin) * (W-120) / (xmax-xmin);
}}

ctx.font = "14px Arial";

// eixo
ctx.beginPath();
ctx.moveTo(60,y);
ctx.lineTo(W-60,y);
ctx.stroke();

// ticks
for(let t=-15;t<=15;t+=5){{
  const px = X(t);
  ctx.beginPath();
  ctx.moveTo(px,y-6);
  ctx.lineTo(px,y+6);
  ctx.stroke();
  ctx.fillText(t, px-8, y+18);
}}

function particula(x,n,q,dy){{
  const px=X(x);
  ctx.beginPath();
  ctx.arc(px,y,16,0,2*Math.PI);
  ctx.fillStyle="#f7f7f7";
  ctx.fill();
  ctx.strokeStyle="{cor_borda('{'}q{'}')}".replace("q", q>0?"pos":q<0?"neg":"neu");
}}

function drawP(x,n,q,color,dy){{
  const px=X(x);
  ctx.beginPath();
  ctx.arc(px,y,16,0,2*Math.PI);
  ctx.fillStyle="#f7f7f7";
  ctx.fill();
  ctx.strokeStyle=color;
  ctx.lineWidth=2;
  ctx.stroke();
  ctx.fillStyle="#111";
  ctx.font="bold 16px Arial";
  ctx.fillText(n,px-4,y+5);
  ctx.font="14px Arial";
  ctx.fillText(`q${n} = ${q}`,px-40,y-dy);
}}

drawP({x1},1,"{str(q1u).replace('.', ',')} µC","{cor_borda(q1)}",50);
drawP({x2},2,"{str(q2u).replace('.', ',')} µC","{cor_borda(q2)}",70);
drawP({x3},3,"{str(q3u).replace('.', ',')} µC","{cor_borda(q3)}",90);

function arrow(px,dy,len,color,label){{
  if(len===0) return;
  ctx.strokeStyle=color;
  ctx.beginPath();
  ctx.moveTo(px,y+dy);
  ctx.lineTo(px+len,y+dy);
  ctx.stroke();
  ctx.fillText(label,px+len+5,y+dy-5);
}}

const px3=X({x3});
arrow(px3,-40,{F13/abs(max(abs(F13),abs(F23),abs(Fr)))*120 if Fr!=0 else 0},"red","F₁₃");
arrow(px3,-20,{F23/abs(max(abs(F13),abs(F23),abs(Fr)))*120 if Fr!=0 else 0},"blue","F₂₃");
arrow(px3,0,{Fr/abs(max(abs(F13),abs(F23),abs(Fr)))*150 if Fr!=0 else 0},"green","Fᵣ");
</script>
"""

components.html(html, height=350)

# ================= Forças =================

st.header("Forças Eletrostáticas")

st.latex(r"F = K\frac{|q_a q_b|}{r^2}")
st.latex(r"\vec F_r = \vec F_{13} + \vec F_{23}")

c1,c2,c3 = st.columns(3)

with c1:
    st.markdown("### **F₁₃**")
    st.markdown(f"<div style='font-size:22px'><b>{br_sci(F13s,2,'N')}</b> {arrow(F13s)}</div>", unsafe_allow_html=True)

with c2:
    st.markdown("### **F₂₃**")
    st.markdown(f"<div style='font-size:22px'><b>{br_sci(F23s,2,'N')}</b> {arrow(F23s)}</div>", unsafe_allow_html=True)

with c3:
    st.markdown("### **Fᵣ (resultante)**")
    st.markdown(f"<div style='font-size:24px;color:green'><b>{br_sci(Frs,2,'N')}</b> {arrow(Frs)}</div>", unsafe_allow_html=True)

if Frs == 0:
    st.success("✅ A partícula 3 está na **posição de equilíbrio**.")
``
