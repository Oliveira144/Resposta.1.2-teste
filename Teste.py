import streamlit as st

# =====================================================
# CONFIGURAÇÃO
# =====================================================
st.set_page_config(page_title="Football Studio PRO ULTIMATE", layout="centered")

# =====================================================
# ESTADOS
# =====================================================
if "history" not in st.session_state:
    st.session_state.history = []

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
    st.session_state.rounds_without_draw += 1

if c2.button("🔵 Away"):
    st.session_state.history.insert(0, "B")
    st.session_state.rounds_without_draw += 1

if c3.button("🟡 Empate"):
    st.session_state.history.insert(0, "D")
    st.session_state.rounds_without_draw = 0

st.markdown(f"### 💰 Banca: R$ {st.session_state.bank:.2f}")
st.markdown(f"### 📈 Lucro: R$ {st.session_state.profit:.2f}")

# =====================================================
# HISTÓRICO (RECENTE → ANTIGO)
# =====================================================
st.markdown("## 📊 Histórico (Recente → Antigo)")
st.write(" ".join(
    ["🔴" if x == "R" else "🔵" if x == "B" else "🟡"
     for x in st.session_state.history[:50]]
))

# =====================================================
# EXTRAÇÃO DE BLOCOS (EMPATE COMO EVENTO)
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
            blocks.append({
                "color": current,
                "size": size,
                "type": classify_block(current, size)
            })
            current = hist[i]
            size = 1

    blocks.append({
        "color": current,
        "size": size,
        "type": classify_block(current, size)
    })

    return blocks

def classify_block(color, size):
    if color == "D":
        return "EMPATE"
    if size == 1:
        return "CHOPPY"
    if size == 2:
        return "DUPLO CURTO"
    if size == 3:
        return "TRIPLO"
    if size >= 6:
        return "STREAK FORTE"
    if size >= 4:
        return "STREAK"
    return "DECAIMENTO"

# =====================================================
# MEMÓRIA DE 3 CICLOS
# =====================================================
def update_cycle_memory(blocks):
    if not blocks:
        return

    last = blocks[0]["type"]
    mem = st.session_state.cycle_memory

    if not mem or mem[-1] != last:
        mem.append(last)

    if len(mem) > 3:
        mem[:] = mem[-3:]

# =====================================================
# DETECÇÃO DE PADRÕES
# =====================================================
def detect_patterns(blocks):
    patterns = []
    sizes = [b["size"] for b in blocks]
    colors = [b["color"] for b in blocks]
    types = [b["type"] for b in blocks]

    # CURTOS
    if types[0] == "CHOPPY":
        patterns.append((colors[0], 55, "CURTO"))

    if len(types) >= 2 and types[0] == types[1] == "CHOPPY":
        patterns.append((colors[0], 58, "DUPLO CURTO"))

    if len(types) >= 3 and types[:3] == ["CHOPPY"] * 3:
        patterns.append((colors[0], 60, "1x1x1"))

    # STREAKS
    if types[0] == "STREAK":
        patterns.append((colors[0], 52, "STREAK"))

    if types[0] == "STREAK FORTE":
        patterns.append((colors[0], 55, "STREAK FORTE"))

    # DECAIMENTO
    if len(sizes) >= 3 and sizes[0] < sizes[1] < sizes[2]:
        patterns.append((colors[0], 57, "DECAIMENTO"))

    # PADRÃO COMPOSTO
    if len(sizes) >= 5:
        patterns.append((colors[0], 61, f"PADRÃO COMPOSTO {sizes[:8]}"))

    # EMPATE (DRAW HUNTING)
    if st.session_state.rounds_without_draw >= 35:
        patterns.append(("D", 64, "DRAW HUNTING"))

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

    if score >= 52:
        if color == "D":
            return "🎯 APOSTAR 🟡 (EMPATE)", score, f"{pattern} | CICLOS {mem}"
        return f"🎯 APOSTAR {'🔴' if color == 'R' else '🔵'}", score, f"{pattern} | CICLOS {mem}"

    return "⏳ AGUARDAR", score, f"{pattern} | CICLOS {mem}"

# =====================================================
# SAÍDA
# =====================================================
decision, score, context = ia_decision(st.session_state.history)

st.markdown("## 🎯 DECISÃO DA IA")
st.success(f"{decision} | Score {score}\n\n{context}")

with st.expander("🧠 Memória de 3 Ciclos"):
    st.write(st.session_state.cycle_memory)
