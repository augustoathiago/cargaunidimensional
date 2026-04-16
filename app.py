import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Simulador Força Eletrostática", layout="wide")

# =========================================================
# ✅ MELHORIA (mobile): CSS para reduzir margens e melhorar tipografia
# =========================================================
st.markdown(
    """
<style>
.block-container { padding-top: 1.3rem; padding-bottom: 1.3rem; }
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
    st.markdown("**Desafio: tente encontrar uma situação onde a partícula 3 está em equilíbrio ou quase em equilíbrio (Fr ~ 0).**")

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

# =========================================================
# ✅ MELHORIA PRINCIPAL: canvas responsivo (sem cortar no celular)
# - Não muda seu desenho; só faz o canvas "encaixar" na largura disponível
# - Mantém nitidez com devicePixelRatio
# =========================================================
BASE_W = 1000
BASE_H = 410

html = f"""
<div id="wrap" style="width:100%; max-width:{BASE_W}px; margin:0 auto;">
  <canvas id="canvas" style="width:100%; background:white; border:1px solid #eee; display:block;"></canvas>
</div>

<script>
const BASE_W = {BASE_W};
const BASE_H = {BASE_H};

const canvas = document.getElementById("canvas");
const wrap = document.getElementById("wrap");
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

  // desenhar em "CSS pixels"
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  draw(cssW, cssH, scale);
}}

function draw(W, H, s) {{
  // Limpa
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = "white";
  ctx.fillRect(0, 0, W,
