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

# Sliders de carga (µC)
qmin_uC, qmax_uC, qstep_uC = -5.0, 5.0, 0.05

# Ajuste: eixo fixo -15 a 15 => sliders coerentes com o eixo
xmin_slider, xmax_slider = -15.0, 15.0

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

F13, r13 = coulomb_force_1d(q3, q1, x3, x1, K=K)  # força em 3 devido a 1
F23, r23 = coulomb_force_1d(q3, q2, x3, x2, K=K)  # força em 3 devido a 2
Fr = F13 + F23

# Duas casas significativas (para exibição e equilíbrio)
F13s = sig(F13, 2)
F23s = sig(F23, 2)
Frs  = sig(Fr, 2)
r13s = sig(r13, 2)
r23s = sig(r23, 2)

equilibrio = (Frs == 0.0)

# ===================== Eixo fixo (-15 a 15) =====================

xMin = -15.0
xMax =  15.0

step = nice_step(xMax - xMin)  # span=30 => step típico 5
t0 = math.floor(xMin / step) * step
ticks = []
t = t0
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

# ===================== Figura (Canvas) =====================

st.header("Figura – Sistema Unidimensional (eixo fixo de -15 a 15)")

q1_str = br_sci_text(q1, 2, "C")
q2_str = br_sci_text(q2, 2, "C")
q3_str = br_sci_text(q3, 2, "C")

html = f"""
<canvas id="canvas" width="1000" height="360" style="background: white; border: 1px solid #eee;"></canvas>

<script>
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const W = canvas.width;
const H = canvas.height;

// fundo branco
ctx.fillStyle = "white";
ctx.fillRect(0, 0, W, H);

// intervalo FIXO do eixo
const xMin = {xMin};
const xMax = {xMax};

// margens em pixels
const padL = 50;
const padR = 50;

function X(x) {{
  return padL + (x - xMin) * ((W - padL - padR) / (xMax - xMin));
}}

const yAxis = H/2 + 50;

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

    const label = (Math.round(t*10)/10).toString().replace(".", ",");
    ctx.fillText(label, px, yAxis + 10);
  }});

  // unidade
  ctx.textAlign = "right";
  ctx.textBaseline = "bottom";
  ctx.fillText("x (m)", W - padR, yAxis - 10);
}}

// ---------- Cor da borda pela carga ----------
function borderColorByCharge(q) {{
  const eps = 1e-15; // limiar para "neutro"
  if (q > eps) return "#d62728";  // vermelho (positivo)
  if (q < -eps) return "#1f77b4"; // azul (negativo)
  return "#111";                  // preto (neutro)
}}

// ---------- Partícula como círculo numerado ----------
function drawParticle(x, n, qText, qValue) {{
  const px = X(x);
  const py = yAxis;

  // círculo
  ctx.fillStyle = "#f7f7f7";
  ctx.strokeStyle = borderColorByCharge(qValue);
  ctx.lineWidth = 3;
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

  return {{px, py, n, qText}};
}}

// ---------- Desenha legendas das cargas SEM sobreposição ----------
function drawChargeLabels(particles) {{
  // Ordena por x (pixel)
  particles.sort((a,b) => a.px - b.px);

  const baseY = yAxis - 26;     // altura base (acima do círculo)
  const dy = 16;                // deslocamento vertical por nível
  const minDx = 120;            // distância mínima entre legendas para evitar sobreposição
  const levels = [];            // guarda (px, level) por partícula na ordem

  // Define níveis (0,1,2...) para "empilhar" quando estiverem próximas
  for (let i=0; i<particles.length; i++) {{
    let level = 0;
    for (let j=i-1; j>=0; j--) {{
      const prev = particles[j];
      const prevLevel = levels[j];
      const close = Math.abs(particles[i].px - prev.px) < minDx;
      if (close && prevLevel === level) {{
        level++;
        j = i; // reinicia busca (garante não colidir com outros níveis)
      }}
    }}
    levels.push(level);
  }}

  // Renderiza texto com subscrito unicode: q₁, q₂, q₃
  const qSub = {{1: "q₁", 2:"q₂", 3:"q₃"}};

  ctx.fillStyle = "#111";
  ctx.font = "14px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "bottom";

  for (let i=0; i<particles.length; i++) {{
    const p = particles[i];
    const level = levels[i];
    const y = baseY - level*dy;

    // pequena linha guia quando estiver muito alto (opcional, ajuda leitura)
    if (level > 0) {{
      ctx.strokeStyle = "#999";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(p.px, yAxis - 18);
      ctx.lineTo(p.px, y + 2);
      ctx.stroke();
    }}

    ctx.fillText(`${{qSub[p.n]}} = ${{p.qText}}`, p.px, y);
  }}
}}

// ---------- Seta ----------
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
  ctx.textAlign = (dx > 0) ? "left" : "right";
  ctx.textBaseline = "bottom";
  ctx.fillText(label, x1 + (dx > 0 ? 6 : -6), y0 - 6);
}}

drawAxis();

// Partículas
const parts = [];
parts.push(drawParticle({x1}, 1, "{q1_str}", {q1}));
parts.push(drawParticle({x2}, 2, "{q2_str}", {q2}));
parts.push(drawParticle({x3}, 3, "{q3_str}", {q3}));

// Legendas (sem sobreposição e com subíndice)
drawChargeLabels(parts);

// Vetores na partícula 3
const px3 = X({x3});
drawArrow(px3, yAxis - 70, {d13} * {L13:.6f}, "#d62728", "F₁₃");
drawArrow(px3, yAxis - 40, {d23} * {L23:.6f}, "#1f77b4", "F₂₃");
drawArrow(px3, yAxis - 10, {dr}  * {Lr:.6f},  "#2ca02c", "Fᵣ");
</script>
"""
components.html(html, height=390)

# ===================== Seção Forças =====================

st.header("Forças Eletrostáticas")

st.latex(r"F = K\frac{|q_a q_b|}{r^2}")
st.write(
    "onde **qₐ** e **q_b** são as cargas das partículas interagindo, **r** é a distância entre elas e "
    "**K = 9,0×10⁹ N·m²/C²**."
)

st.caption(f"Constante de Coulomb: K = {br_sci_text(K, 2, 'N·m²/C²')}")

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
          <div style="font-size: 22px; color: #111;"><b>{value}</b> <span style="font-size: 20px;">{direction}</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )

c1, c2, c3 = st.columns(3)
with c1:
    result_card("Força na partícula 3 devido à partícula 1 (F₁₃)", br_sci_text(F13s, 2, "N"), arrow_symbol(F13s), "#d62728")
with c2:
    result_card("Força na partícula 3 devido à partícula 2 (F₂₃)", br_sci_text(F23s, 2, "N"), arrow_symbol(F23s), "#1f77b4")
with c3:
    result_card("Força Resultante na partícula 3 (Fᵣ)", br_sci_text(Frs, 2, "N"), arrow_symbol(Frs), "#2ca02c")

# --------- F13 detalhes ---------
st.subheader("Cálculos")

st.markdown("**Força na partícula 3 devido à partícula 1 (F₁₃)**")
st.latex(r"F_{13} = K\frac{|q_1 q_3|}{r_{13}^2} \;\;\; \text{(módulo)}")
st.latex(
    rf"F_{{13}} = (9{{,}}0\times10^9)\cdot \frac{{\left|({latex_sci(q1,2)})({latex_sci(q3,2)})\right|}}{{({str(r13s).replace('.', '{,}')} )^2}}"
)

# --------- F23 detalhes ---------
st.markdown("**Força na partícula 3 devido à partícula 2 (F₂₃)**")
st.latex(r"F_{23} = K\frac{|q_2 q_3|}{r_{23}^2} \;\;\; \text{(módulo)}")
st.latex(
    rf"F_{{23}} = (9{{,}}0\times10^9)\cdot \frac{{\left|({latex_sci(q2,2)})({latex_sci(q3,2)})\right|}}{{({str(r23s).replace('.', '{,}')} )^2}}"
)

# --------- Resultante (vetores) ---------
st.markdown("**Força Resultante na partícula 3**")
st.latex(r"\vec{F}_r = \vec{F}_{13} + \vec{F}_{23}")

if equilibrio:
    st.success("✅ A partícula 3 está na **posição de equilíbrio** (Fᵣ = 0, com 2 algarismos significativos).")
