import streamlit as st
import streamlit.components.v1 as components
import math

# =========================================================
# Configuração da página
# =========================================================
st.set_page_config(page_title="Simulador Força Eletrostática", layout="wide")

# CSS: melhora espaçamento geral e no celular
st.markdown(
    """
<style>
/* diminui padding padrão do Streamlit */
.block-container { padding-top: 1.3rem; padding-bottom: 1.3rem; }

/* cartões (opcional, só para consistência visual) */
.card {
  border-left: 8px solid #999;
  background: #fafafa;
  padding: 14px 16px;
  border-radius: 14px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.06);
  margin-bottom: 10px;
}

/* ajustes específicos no mobile */
@media (max-width: 768px){
  .block-container { padding-left: 1rem; padding-right: 1rem; }
  h1 { font-size: 1.6rem; }
  h2 { font-size: 1.25rem; }
  h3 { font-size: 1.05rem; }
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# Helpers
# =========================================================
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
    mant_s = fmt_uC_br(q_uC)
    exp = -6
    return f"{mant_s}×10{str(exp).translate(_sup_map)} C"

# =========================================================
# Cabeçalho
# =========================================================
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
        "**Desafio: tente encontrar uma situação onde a partícula 3 está em equilíbrio ou quase em equilíbrio (Fᵣ ~ 0).**"
    )

# =========================================================
# Controles (Mobile-friendly: sidebar)
# =========================================================
st.header("Definições das Partículas")

# Sliders de carga (µC)
qmin_uC, qmax_uC, qstep_uC = -5.0, 5.0, 0.05

# Sliders de posição -10 a 10
xmin_slider, xmax_slider = -10.0, 10.0

with st.sidebar:
    st.header("Controles")
    st.caption("No celular, esta barra fica recolhível (menu ☰).")

    st.subheader("Partícula 1")
    x1 = st.slider("Posição x₁ (m)", xmin_slider, xmax_slider, -4.0, 0.1, format="%.1f")
    q1_uC = st.slider("Carga q₁ (µC)", qmin_uC, qmax_uC, 2.0, qstep_uC, format="%.2f")
    q1 = q1_uC * 1e-6

    st.subheader("Partícula 2")
    x2 = st.slider("Posição x₂ (m)", xmin_slider, xmax_slider, 4.0, 0.1, format="%.1f")
    q2_uC = st.slider("Carga q₂ (µC)", qmin_uC, qmax_uC, -2.0, qstep_uC, format="%.2f")
    q2 = q2_uC * 1e-6

    st.subheader("Partícula 3")
    x3 = st.slider("Posição x₃ (m)", xmin_slider, xmax_slider, 0.0, 0.1, format="%.1f")
    q3_uC = st.slider("Carga q₃ (µC)", qmin_uC, qmax_uC, 1.0, qstep_uC, format="%.2f")
    q3 = q3_uC * 1e-6

# Bloqueio de posições iguais
if len({x1, x2, x3}) < 3:
    st.error("❌ As partículas **não podem** estar na mesma posição. Ajuste x₁, x₂ e x₃.")
    st.stop()

# =========================================================
# Física
# =========================================================
K = 9.0e9

# forças "reais" (sem arredondar q nem r)
F13_raw, r13 = coulomb_force_1d(q3, q1, x3, x1, K=K)
F23_raw, r23 = coulomb_force_1d(q3, q2, x3, x2, K=K)

# Apenas forças finais exibidas arredondadas para 2 AS
F13_disp = sig(F13_raw, 2)
F23_disp = sig(F23_raw, 2)

# Equilíbrio didático: soma usando forças exibidas (já em 2 AS)
Fr_disp = sig(F13_disp + F23_disp, 2)
equilibrio = (Fr_disp == 0.0)

# =========================================================
# Eixo e ticks (1 em 1, inclui 0)
# =========================================================
xMin = -15.0
xMax = 15.0
ticks = list(range(-15, 16, 1))

# =========================================================
# Escala dos vetores (com forças exibidas)
# =========================================================
maxF = max(abs(F13_disp), abs(F23_disp), abs(Fr_disp), 1e-30)
L13 = 120 * abs(F13_disp) / maxF
L23 = 120 * abs(F23_disp) / maxF
Lr  = 140 * abs(Fr_disp)  / maxF

d13 = 0 if math.isclose(F13_disp, 0.0, abs_tol=0.0) else (1 if F13_disp > 0 else -1)
d23 = 0 if math.isclose(F23_disp, 0.0, abs_tol=0.0) else (1 if F23_disp > 0 else -1)
dr  = 0 if math.isclose(Fr_disp,  0.0, abs_tol=0.0) else (1 if Fr_disp  > 0 else -1)

# =========================================================
# Figura (Canvas responsivo - não corta no celular)
# =========================================================
st.header("Figura – Sistema Unidimensional")

q1_str = br_charge_canvas_from_uC(q1_uC)
q2_str = br_charge_canvas_from_uC(q2_uC)
q3_str = br_charge_canvas_from_uC(q3_uC)

canvas_base_w = 1000
canvas_base_h = 410

html = f"""
<div id="wrap" style="width:100%; max-width:{canvas_base_w}px; margin:0 auto;">
  <canvas id="canvas" style="width:100%; border:1px solid #eee; background:white; display:block;"></canvas>
</div>

<script>
const BASE_W = {canvas_base_w};
const BASE_H = {canvas_base_h};

const wrap = document.getElementById("wrap");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

function resizeCanvas(){{
  const cssW = wrap.clientWidth;
  const scale = cssW / BASE_W;
  const cssH = Math.round(BASE_H * scale);

  canvas.style.width = cssW + "px";
  canvas.style.height = cssH + "px";

  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.floor(cssW * dpr);
  canvas.height = Math.floor(cssH * dpr);

  // desenhar usando coordenadas em CSS pixels
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  draw(cssW, cssH, scale);
}}

function draw(W, H, s){{
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = "white";
  ctx.fillRect(0, 0, W, H);

  const xMin = {xMin};
  const xMax = {xMax};

  const padL = 50*s;
  const padR = 50*s;

  function X(x) {{
    return padL + (x - xMin) * ((W - padL - padR) / (xMax - xMin));
  }}

  const yAxis = 235*s;

  function drawAxis() {{
    ctx.strokeStyle = "#111";
    ctx.lineWidth = 2*s;
    ctx.beginPath();
    ctx.moveTo(padL, yAxis);
    ctx.lineTo(W - padR, yAxis);
    ctx.stroke();

    const ticks = {ticks};
    ctx.fillStyle = "#111";
    ctx.font = `${{Math.max(11, 13*s)}}px Arial`;
    ctx.textAlign = "center";
    ctx.textBaseline = "top";

    ticks.forEach(t => {{
      const px = X(t);
      ctx.beginPath();
      ctx.moveTo(px, yAxis - 7*s);
      ctx.lineTo(px, yAxis + 7*s);
      ctx.stroke();

      ctx.fillText(t.toString().replace(".", ","), px, yAxis + 10*s);
    }});

    ctx.textAlign = "right";
    ctx.textBaseline = "bottom";
    ctx.fillText("x (m)", W - padR, yAxis - 10*s);
  }}

  function borderColorByCharge(q) {{
    const eps = 1e-15;
    if (q > eps) return "#d62728";
    if (q < -eps) return "#1f77b4";
    return "#111";
  }}

  function drawParticle(x, n, qText, qValue) {{
    const px = X(x);
    const py = yAxis;

    ctx.fillStyle = "#f7f7f7";
    ctx.strokeStyle = borderColorByCharge(qValue);
    ctx.lineWidth = 3*s;

    const r = Math.max(11, 16*s);

    ctx.beginPath();
    ctx.arc(px, py, r, 0, 2*Math.PI);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#111";
    ctx.font = `bold ${{Math.max(12, 16*s)}}px Arial`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(n.toString(), px, py);

    return {{px, py, n, qText}};
  }}

  function drawChargeLabelsBelow(particles) {{
    particles.sort((a,b) => a.px - b.px);

    const baseY = yAxis + 62*s;
    const dy = 16*s;
    const minDx = 140*s;
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
    ctx.font = `${{Math.max(11, 14*s)}}px Arial`;
    ctx.textAlign = "center";
    ctx.textBaseline = "top";

    for (let i=0; i<particles.length; i++) {{
      const p = particles[i];
      const level = levels[i];
      const y = baseY + level*dy;

      if (level > 0) {{
        ctx.strokeStyle = "#999";
        ctx.lineWidth = 1*s;
        ctx.beginPath();
        ctx.moveTo(p.px, yAxis + 18*s);
        ctx.lineTo(p.px, y - 2*s);
        ctx.stroke();
      }}

      ctx.fillText(`${{qSub[p.n]}} = ${{p.qText}}`, p.px, y);
    }}
  }}

  function drawVectorOverLabel(text, xAnchor, yBaseline, align, color) {{
    ctx.save();
    ctx.font = `${{Math.max(11, 14*s)}}px Arial`;
    ctx.fillStyle = color;
    ctx.strokeStyle = color;
    ctx.lineWidth = 2*s;

    const w = ctx.measureText(text).width;
    let xLeft = xAnchor;
    if (align === "right") xLeft = xAnchor - w;
    if (align === "center") xLeft = xAnchor - w/2;

    const yArrow = yBaseline - 16*s;
    ctx.beginPath();
    ctx.moveTo(xLeft, yArrow);
    ctx.lineTo(xLeft + w, yArrow);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(xLeft + w, yArrow);
    ctx.lineTo(xLeft + w - 6*s, yArrow - 4*s);
    ctx.lineTo(xLeft + w - 6*s, yArrow + 4*s);
    ctx.closePath();
    ctx.fill();

    ctx.restore();
  }}

  function drawArrow(x0, y0, dx, color, label) {{
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = 3*s;

    if (dx === 0) {{
      ctx.beginPath();
      ctx.moveTo(x0 - 8*s, y0);
      ctx.lineTo(x0 + 8*s, y0);
      ctx.stroke();

      ctx.font = `${{Math.max(11, 14*s)}}px Arial`;
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.fillText(label + " ≈ 0", x0 + 12*s, y0);

      drawVectorOverLabel(label, x0 + 12*s, y0, "left", color);
      return;
    }}

    const x1 = x0 + dx;

    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y0);
    ctx.stroke();

    const head = 10*s;
    const sign = (dx > 0) ? 1 : -1;

    ctx.beginPath();
    ctx.moveTo(x1, y0);
    ctx.lineTo(x1 - sign*head, y0 - head*0.6);
    ctx.lineTo(x1 - sign*head, y0 + head*0.6);
    ctx.closePath();
    ctx.fill();

    ctx.font = `${{Math.max(11, 14*s)}}px Arial`;
    const align = (dx > 0) ? "left" : "right";
    ctx.textAlign = align;
    ctx.textBaseline = "bottom";
    const xText = x1 + (dx > 0 ? 6*s : -6*s);
    const yText = y0 - 6*s;
    ctx.fillText(label, xText, yText);
    drawVectorOverLabel(label, xText, yText, align, color);
  }}

  drawAxis();

  const parts = [];
  parts.push(drawParticle({x1}, 1, "{q1_str}", {q1}));
  parts.push(drawParticle({x2}, 2, "{q2_str}", {q2}));
  parts.push(drawParticle({x3}, 3, "{q3_str}", {q3}));

  drawChargeLabelsBelow(parts);

  // setas: escalar comprimentos
  const px3 = X({x3});
  drawArrow(px3, yAxis - 95*s, {d13} * ({L13:.6f}*s), "#d62728", "F₁₃");
  drawArrow(px3, yAxis - 65*s, {d23} * ({L23:.6f}*s), "#1f77b4", "F₂₃");
  drawArrow(px3, yAxis - 35*s, {dr}  * ({Lr:.6f}*s),  "#2ca02c", "Fᵣ");
}}

resizeCanvas();
window.addEventListener("resize", resizeCanvas);
</script>
"""

# altura do iframe: deixamos folga para não cortar nada
components.html(html, height=560, scrolling=False)

# =========================================================
# Seção Forças
# =========================================================
st.header("Forças Eletrostáticas")

st.latex(r"F = K\frac{|q_a q_b|}{r^2}")
st.markdown(
    "onde $q_a$ e $q_b$ são as cargas das partículas interagindo, $r$ é a distância entre elas e "
    "**K é a constante de Coulomb igual a 9,0×10"
