import streamlit as st

# =====================================================
# CONFIGURAÇÃO GERAL
# =====================================================
st.set_page_config(
    page_title="Football Studio PRO ULTIMATE",
    layout="centered"
)

# =====================================================
# ESTADOS GLOBAIS
# =====================================================
if "history" not in st.session_state:
    st.session_state.history = []

if "cycle_memory" not in st.session_state:
    st.session_state.cycle_memory = []

if "bank" not in st.session_state:
    st.session_state.bank = 1000.0

if "profit" not in st.session_state:
    st.session_state.profit = 0.0

# =====================================================
# INTERFACE
# =====================================================
st.title("⚽ Football Studio – PRO ULTIMATE")

c1, c2, c3 = st.columns(3)
if c1.button("🔴 Home"):
    st.session_state.history.insert(0, "R")
if c2.button("🔵 Away"):
    st.session_state.history.insert(0, "B")
if c3.button("⚪ Draw"):
    st.session_state.history.insert(0, "D")

st.markdown(f"### 💰 Banca: R$ {st.session_state.bank:.2f}")
st.markdown(f"### 📈 Lucro: R$ {st.session_state.profit:.2f}")

# =====================================================
# HISTÓRICO
# =====================================================
st.markdown("## 📊 Histórico (Recente → Antigo)")
st.write(" ".join(
    ["🔴" if h == "R" else "🔵" if h == "B" else "⚪"
     for h in st.session_state.history[:50]]
))

# =====================================================
# EXTRAÇÃO DE BLOCOS (CORE DO ALGORITMO)
# =====================================================
def extract_blocks(history):
    if not history:
        return []

    blocks = []
    current = history[0]
    size = 1

    for i in range(1, len(history)):
        if history[i] == current:
            size += 1
        else:
            blocks.append({"color": current, "size": size})
            current = history[i]
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
# MEMÓRIA DE CICLOS (IGUAL AO ORIGINAL)
# =====================================================
def update_cycle_memory(blocks):
    if not blocks:
        return

    mem = st.session_state.cycle_memory
    last_type = blocks[0]["type"]

    if not mem or mem[-1] != last_type:
        mem.append(last_type)

    if len(mem) > 3:
        mem[:] = mem[-3:]

# =====================================================
# DETECÇÃO DE PADRÕES (CORE ORIGINAL PRESERVADO)
# =====================================================
def detect_patterns(blocks):
    patterns = []
    if not blocks:
        return patterns

    sizes = [b["size"] for b in blocks]
    colors = [b["color"] for b in blocks]
    types = [b["type"] for b in blocks]

    # CHOPPY
    if types[0] == "CHOPPY":
        patterns.append((colors[0], 55, "CURTO"))

    if len(types) >= 2 and types[0] == types[1] == "CHOPPY":
        patterns.append((colors[0], 58, "DUPLO CURTO"))

    if len(types) >= 3 and types[0] == types[1] == types[2] == "CHOPPY":
        patterns.append((colors[0], 60, "1x1x1"))

    # STREAK
    if types[0] in ["STREAK", "STREAK FORTE"]:
        score = 52 if types[0] == "STREAK" else 54
        patterns.append((colors[0], score, types[0]))

    # DECAIMENTO
    if len(sizes) >= 3 and sizes[0] < sizes[1] < sizes[2]:
        patterns.append((colors[0], 57, "DECAIMENTO"))

    # PADRÃO COMPOSTO
    if len(sizes) >= 5:
        patterns.append((colors[0], 61, f"PADRÃO COMPOSTO {sizes[:8]}"))

    # DRAW BASE (como no original)
    if types[0] == "DRAW":
        base = 62 if all(b["type"] != "DRAW" for b in blocks[1:15]) else 50
        patterns.append((colors[0], base, "DRAW"))

    return patterns

# =====================================================
# LEITURA PROFISSIONAL DE EMPATES (NATIVA)
# NÃO MUDA SCORE, APENAS CONTEXTO
# =====================================================
def draw_context(blocks):
    if not blocks or blocks[0]["type"] != "DRAW":
        return None

    if len(blocks) > 1 and blocks[1]["type"] in ["STREAK", "STREAK FORTE"]:
        return "Empate após sequência (possível reversão)"

    if len(blocks) > 1 and blocks[1]["type"] == "DRAW":
        return "Empate duplo (manipulação ativa)"

    recent = [b["type"] for b in blocks[:6]]
    if recent.count("DRAW") >= 2:
        return "Empates intercalados (mercado confuso)"

    if len(blocks) > 2 and blocks[1]["color"] == blocks[2]["color"]:
        return "Empate absorvido (continuidade)"

    return "Empate isolado (atenção)"

# =====================================================
# IA – DECISÃO FINAL
# =====================================================
def ia_decision(history):
    blocks = extract_blocks(history)
    update_cycle_memory(blocks)

    patterns = detect_patterns(blocks)
    if not patterns:
        return "⏳ AGUARDAR", 0, "SEM PADRÃO"

    color, score, pattern = max(patterns, key=lambda x: x[1])
    mem = st.session_state.cycle_memory

    # CONTEXTO CHOPPY (ORIGINAL)
    if mem.count("CHOPPY") >= 2:
        if "CURTO" in pattern or "1x1x1" in pattern:
            score += 4
        elif "STREAK" in pattern:
            score -= 12
        else:
            score -= 3

    # REPETIÇÃO DE CICLO (ORIGINAL)
    if len(mem) == 3 and mem[0] == mem[2]:
        score += 4

    context = f"{pattern} | CICLOS {mem}"

    draw_info = draw_context(blocks)
    if draw_info:
        context += f" | {draw_info}"

    if score >= 52:
        if pattern == "DRAW":
            return "🎯 APOSTAR ⚪", score, context
        return f"🎯 APOSTAR {'🔴' if color == 'R' else '🔵'}", score, context

    return "⏳ AGUARDAR", score, context

# =====================================================
# SAÍDA FINAL
# =====================================================
decision, score, context = ia_decision(st.session_state.history)

st.markdown("## 🎯 DECISÃO DA IA")
st.success(f"{decision} | Score {score}\n\n{context}")

with st.expander("🧠 Memória de 3 Ciclos"):
    st.write(st.session_state.cycle_memory)
