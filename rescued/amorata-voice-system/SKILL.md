---
name: amorata-voice-system
description: >
  Loads Amorata's complete dual-voice architecture for the Carta natal OS project.
  Use this skill whenever working on combinator.py, VOICE_LOCK constants, prompt builders,
  or any session that generates or evaluates natal chart text for Amorata.
  Trigger on: "voice lock", "voz experta", "expert voice", "interpreter voice", "INTERPRETER_VOICE",
  "EXPERT_VOICE", "word ranges", "amorata voice", "dual voice", "voz técnica", "combinator",
  "section weight", "capa de sección", "astro commentary", "carta text quality",
  or any request to write, audit, or improve astrological text generation in this project.
  Contains INTERPRETER_VOICE_LOCK, EXPERT_VOICE_LOCK, WORD_RANGES, and implementation guide.
---

# Amorata Voice System

Amorata genera **dos textos complementarios** por sección: una voz literaria (INTERPRETER) y
una voz técnica (EXPERT). Nunca se reemplazan — siempre coexisten. La literaria abre; la
técnica valida.

**Origen del split:** Giulina (usuaria real, Phase 0, 2026-06-18): "el lenguaje es demasiado
abstracto nada se entiende se siente fantasía nada serio ni técnico."

---

## 1. WORD_RANGES — Extensión por capa

La extensión no es fija por voz — es función de la **capa de la sección**. Ambas voces
escalan proporcionalmente.

```python
WORD_RANGES = {
    "TRUNK":    {"literary": (80, 120),  "expert": (60, 80)},   # Sol, Luna, ASC
    "PILLAR":   {"literary": (60, 80),   "expert": (40, 60)},   # Casas 1, 4, 7, 10
    "PERSONAL": {"literary": (40, 60),   "expert": (30, 45)},   # Mercurio, Venus, Marte
    "SOCIAL":   {"literary": (30, 50),   "expert": (20, 35)},   # Júpiter, Saturno
    "OUTER":    {"literary": (15, 25),   "expert": (10, 18)},   # Urano, Neptuno, Plutón
    "MODIFIER": {"literary": (15, 20),   "expert": (10, 15)},   # Quirón, Lílith, Nodos
    "ASPECT":   {"literary": (25, 40),   "expert": (15, 25)},   # Aspectos mayores
    "TRANSIT":  {"literary": (12, 20),   "expert": (8, 12)},    # Tránsitos activos
}
```

**Layer mapping** — añadir `layer` como 6º campo en `SECCIONES_DEF`:

```python
# (num, titulo, cuerpo, signo_key, casa_key, layer)
(1,  "Tu Sol...",    "sol",     "sol",     "sol",     "TRUNK"),
(2,  "Tu Luna...",   "luna",    "luna",    "luna",    "TRUNK"),
(3,  "Tu ASC...",    "asc",     "asc",     None,      "TRUNK"),
(4,  "Mercurio...",  "mercurio","mercurio","mercurio","PERSONAL"),
(5,  "Venus...",     "venus",   "venus",   "venus",   "PERSONAL"),
(6,  "Marte...",     "marte",   "marte",   "marte",   "PERSONAL"),
(7,  "Júpiter...",   "jupiter", "jupiter", "jupiter", "SOCIAL"),
(8,  "Saturno...",   "saturno", "saturno", "saturno", "SOCIAL"),
(9,  "Urano...",     "urano",   "urano",   "urano",   "OUTER"),
(10, "Neptuno...",   "neptuno", "neptuno", "neptuno", "OUTER"),
(11, "Plutón...",    "pluton",  "pluton",  "pluton",  "OUTER"),
(12, "Nodo Norte..","nodo_norte","nodo_norte","nodo_norte","MODIFIER"),
(13, "Nodo Sur...", "nodo_sur","nodo_sur","nodo_sur", "MODIFIER"),
(14, "Casa 1...",    None,      None,      "casa_1",  "PILLAR"),
(15, "Casa 2...",    None,      None,      "casa_2",  "PERSONAL"),
(16, "Casa 4...",    None,      None,      "casa_4",  "PILLAR"),
(17, "Casa 5...",    None,      None,      "casa_5",  "PERSONAL"),
(18, "Casa 7...",    None,      None,      "casa_7",  "PILLAR"),
(19, "Casa 8...",    None,      None,      "casa_8",  "PERSONAL"),
(20, "Casa 10...",   None,      None,      "casa_10", "PILLAR"),
(21, "Casa 12...",   None,      None,      "casa_12", "PERSONAL"),
(29, "Casa 3...",    None,      None,      "casa_3",  "PERSONAL"),
(30, "Casa 6...",    None,      None,      "casa_6",  "PERSONAL"),
(31, "Casa 9...",    None,      None,      "casa_9",  "PERSONAL"),
(32, "Casa 11...",   None,      None,      "casa_11", "PERSONAL"),
(22, "Aspectos...",  None,      None,      None,      "ASPECT"),
(23, "Elemental...", None,      None,      None,      "MODIFIER"),
(24, "Modalidades..",None,      None,      None,      "MODIFIER"),
(25, "Stellium...",  None,      None,      None,      "MODIFIER"),
(26, "Config esp..", None,      None,      None,      "MODIFIER"),
(27, "Tránsitos...", None,      None,      None,      "TRANSIT"),
(28, "Síntesis...",  None,      None,      None,      "TRUNK"),
```

---

## 2. INTERPRETER_VOICE_LOCK

Ver archivo completo → `references/interpreter-voice.md`

Resumen de identidad:
- Registro: literario, imagen viva, emocional, español LATAM
- Referencia: Rowling × Martha Stewart
- Función: abre cada sección, habla al corazón
- Nunca: "manifestar", "vibra", "energía cósmica", "despertar espiritual"
- Sujeto gramatical: siempre la persona, nunca el planeta

---

## 3. EXPERT_VOICE_LOCK

Ver archivo completo → `references/expert-voice.md`

Resumen de identidad:
- Registro: técnico, posicional, diagnóstico
- Referencia: Rob Hand × Susan Miller
- Función: cierra cada sección, habla a la cabeza
- Reglas: sin metáfora, sin hedge ("puede ser que"), sin preguntas retóricas
- Formato: signo + casa + dignidad + consecuencia práctica
- Palabras técnicas permitidas y esperadas: dignidad, domicilio, exaltación, caída, detrimento, angular, sucedente, cadente, orbe, aplicante, separante, rx

---

## 4. Implementación en combinator.py

```python
def assemble_section(
    seccion_num, titulo, cuerpo, signo, casa,
    template_a, template_b, modifiers,
    perfil_nombre, chart=None, chart_brief="",
    layer="PERSONAL"   # ← nuevo parámetro
) -> tuple[str, str, str]:
    """Retorna (texto_literario, texto_experto, estado)"""

    ranges = WORD_RANGES.get(layer, WORD_RANGES["PERSONAL"])
    lit_min, lit_max = ranges["literary"]
    exp_min, exp_max = ranges["expert"]

    # Voz A: literaria
    literary_prompt = _build_prompt(
        titulo, perfil_nombre, template_a, template_b, modifiers,
        chart_brief, word_min=lit_min, word_max=lit_max
    )
    texto_literario = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=600,
        system=INTERPRETER_VOICE_LOCK,
        messages=[{"role": "user", "content": literary_prompt}]
    ).content[0].text.strip()

    # Voz B: experta
    expert_prompt = _build_expert_prompt(
        titulo, perfil_nombre, signo, casa, chart,
        chart_brief, word_min=exp_min, word_max=exp_max
    )
    texto_experto = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=300,
        system=EXPERT_VOICE_LOCK,
        messages=[{"role": "user", "content": expert_prompt}]
    ).content[0].text.strip()

    return texto_literario, texto_experto, estado
```

**Firestore schema** — cada sección almacena:
```json
{
  "numero": 1,
  "titulo": "Tu Sol: esencia e identidad central",
  "texto": "<literario>",
  "analisis": "<experto>",
  "estado": "generado",
  "casa": null,
  "layer": "TRUNK"
}
```

**Viewer** expone ambos campos:
- `resumen` → texto literario
- `analisis` → texto experto

---

## 5. Reglas de calidad por voz

### INTERPRETER (voz A)
- No copia frases de modificadores textualmente — reescribe la idea
- Nunca usa nombre propio como sujeto gramatical ("Fernando siente")
- No abre con planeta como sujeto ("Mercurio en Piscis...")
- No define por negación ("X no es Y — es Z")
- Cierra con segunda persona directa y específica para el placement

### EXPERT (voz B)
- Siempre menciona signo + casa + dignidad si aplica
- Consecuencia práctica obligatoria ("Resultado:", "En práctica:", o implícito)
- Menciona aspectos relevantes si están en contexto
- Rx siempre señalado cuando aplica
- No más palabras de las que el rango permite — densidad sobre extensión

---

## 6. Banderas de violación (_check_voice_lock)

El sistema actualmente valida voz A. Extender para voz B:

**Voz B violations:**
- Contiene "puede ser que", "quizás", "tal vez", "a veces puede"
- Usa "sientes", "llevas", "tu" (segunda persona — la experta es descriptiva, no directa)
- No menciona signo o casa para secciones 1-13
- Supera el máximo de palabras del layer

---

Read `references/interpreter-voice.md` for the full INTERPRETER_VOICE_LOCK constant.
Read `references/expert-voice.md` for the full EXPERT_VOICE_LOCK constant with demonstrations.
