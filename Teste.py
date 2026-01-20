import streamlit as st

# =====================================================
# CONFIGURAÇÃO
# =====================================================
st.set_page_config(
    page_title="Football Studio PRO ULTIMATE",
    layout="centered"
)

# =====================================================
# ESTADOS
# =====================================================
if "history" not in st.session_state:
    st.session_state.history = []  # R, B, D (recente -> antigo)

if "cycle_memory" not in st.session_state:
    st.session_state.cycle_memory = []

if "bank" not in st.session_state:
    st.session_state.bank = 1000.0

if "profit" not in st.session_state:
    st.session_state.profit = 0.0

if "rounds_without_draw" not in st.session_state:
    st.session_state.rounds_without_draw = 0

# =====================================================
# UI
# =====================================================
st.title("⚽ Football Studio – PRO ULTIMATE")

c1, c2, c3 = st.columns(3)
if c1.button("🔴 Home"):
    st.session_state.history.insert(0, "R")
if c2.button("🔵 Away"):
    st.session_state.history.insert(0, "B")
if c3.button("🟡 Draw"):
    st.session_state.history.insert(0, "D")

st.markdown(f"### 💰 Banca: R$ {st.session_state.bank:.2f}")
st.markdown(f"### 📈 Lucro: R$ {st.session_state.profit:.2f}")

# =====================================================
# CONTADOR DE DRAW
# =====================================================
if st.session_state.history:
    if st.session_state.history[0] == "D":
        st.session_state.rounds_without_draw = 0
    else:
        st.session_state.rounds_without_draw += 1

# =====================================================
# HISTÓRICO (RECENTE → ANTIGO, ESQ → DIR)
# =====================================================
st.markdown("## 📊 Histórico (Recente → Antigo)")

def icon(x):
    if x == "R":
        return "🔴"
    if x == "B":
        return "🔵"
    return "🟡"

st.write(" ".join(icon(x) for x in st.session_state.history[:30]))

# =====================================================
# EXTRAÇÃO DE BLOCOS (INCLUINDO DRAW)
# =====================================================
def extract_blocks(hist):
    if not hist:
        return []

    blocks = []
    current = hist[0]
    size = 1

    for i in range(1, len(hist)):
        if hist[i] == current:
            size += 1
        else:
            blocks.append({"color": current, "size": size})
            current = hist[i]
            size = 1

    blocks.append({"color": current, "size": size})

    for b in blocks:
        if b["color"] == "D":
            b["type"] = "DRAW"
        elif b["size"] == 1:
            b["type"] = "CHOPPY"
        elif b["size"] == 2:
            b["type"] = "DUPLO CURTO"
        elif b["size"] == 3:
            b["type"] = "TRIPLO"
        elif b["size"] >= 6:
            b["type"] = "STREAK FORTE"
        elif b["size"] >= 4:
            b["type"] = "STREAK"
        else:
            b["type"] = "DECAIMENTO"

    return blocks

# =====================================================
# MEMÓRIA DE 3 CICLOS
# =====================================================
def update_cycle_memory(blocks):
    if not blocks:
        return

    last_type = blocks[0]["type"]
    mem = st.session_state.cycle_memory

    if not mem or mem[-1] != last_type:
        mem.append(last_type)

    if len(mem) > 3:
        mem[:] = mem[-3:]

# =====================================================
# DETECTOR DE PADRÕES (BLINDADO)
# =====================================================
def detect_patterns(blocks):
    patterns = []

    if not blocks:
        return patterns

    sizes = [b["size"] for b in blocks]
    colors = [b["color"] for b in blocks]
    types = [b["type"] for b in blocks]

    if not types:
        return patterns

    # ===============================
    # CURTOS / ALTERNÂNCIA
    # ===============================
    if types[0] == "CHOPPY":
        patterns.append((colors[0], 55, "CURTO"))

    if len(types) >= 2 and types[0] == types[1] == "CHOPPY":
        patterns.append((colors[0], 58, "DUPLO CURTO"))

    if len(types) >= 3 and types[:3] == ["CHOPPY"] * 3:
        patterns.append((colors[0], 60, "1x1x1"))

    # ===============================
    # STREAKS
    # ===============================
    if types[0] == "STREAK":
        patterns.append((colors[0], 52, "STREAK"))

    if types[0] == "STREAK FORTE":
        patterns.append((colors[0], 55, "STREAK FORTE"))

    # ===============================
    # DECAIMENTO
    # ===============================
    if len(sizes) >= 3 and sizes[0] < sizes[1] < sizes[2]:
        patterns.append((colors[0], 57, "DECAIMENTO"))

    # ===============================
    # PADRÕES COMPOSTOS (4x4x3x2x...)
    # ===============================
    if len(sizes) >= 5:
        patterns.append((colors[0], 61, f"PADRÃO COMPOSTO {sizes[:8]}"))

    # ===============================
    # DRAW HUNTING (EMPATE)
    # ===============================
    if st.session_state.rounds_without_draw >= 30:
        patterns.append(("D", 65, "DRAW HUNTING"))

    return patterns

# =====================================================
# IA – DECISÃO FINAL
# =====================================================
def ia_decision(hist):
    blocks = extract_blocks(hist)
    update_cycle_memory(blocks)

    patterns = detect_patterns(blocks)

    if not patterns:
        return "⏳ AGUARDAR", 0, "SEM PADRÃO"

    color, score, pattern = max(patterns, key=lambda x: x[1])
    mem = st.session_state.cycle_memory

    # Ajuste por contexto
    if mem.count("CHOPPY") >= 2 and "STREAK" in pattern:
        score -= 8

    if len(mem) == 3 and mem[0] == mem[2]:
        score += 4

    # DECISÃO FINAL
    if score >= 55:
        if color == "R":
            return "🎯 APOSTAR 🔴 HOME", score, f"{pattern} | CICLOS {mem}"
        if color == "B":
            return "🎯 APOSTAR 🔵 AWAY", score, f"{pattern} | CICLOS {mem}"
        return "🎯 APOSTAR 🟡 DRAW", score, f"{pattern} | {st.session_state.rounds_without_draw} rodadas sem empate"

    return "⏳ AGUARDAR", score, f"{pattern} | CICLOS {mem}"

# =====================================================
# SAÍDA FINAL
# =====================================================
decision, score, context = ia_decision(st.session_state.history)

st.markdown("## 🎯 DECISÃO DA IA")
st.success(f"{decision}\n\nScore: {score}\n\n{context}")

with st.expander("🧠 Memória de 3 Ciclos"):
    st.write(st.session_state.cycle_memory)

with st.expander("🟡 Estatística de Empate"):
    st.write(f"Rodadas sem Draw: {st.session_state.rounds_without_draw}")
