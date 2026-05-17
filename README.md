# EduSolve — Multi-Step STEM Problem Solver

A Claude-powered CLI agent that solves complex math, physics, and chemistry problems with explicit step-by-step reasoning, tool use, and self-verification.

## Demo

> YouTube demo link — *coming soon*

---

## Prompt Qualification

The system prompt below was evaluated against the [Prompt Evaluation Rubric](this.md) and scored **9 / 9**.

| # | Criterion | Score | Evidence |
|---|-----------|-------|---------|
| 1 | Explicit Reasoning Instructions | ✅ PASS | Rule 1: "Always reason step-by-step. Think before you answer." |
| 2 | Structured Output Format | ✅ PASS | Strict JSON schema with named fields: `steps`, `verification`, `confidence`, `final_answer`, `follow_up_possible` |
| 3 | Separation of Reasoning and Tools | ✅ PASS | `action` field is either `REASON` or `FUNCTION_CALL`; tool calls are only made for actual computation |
| 4 | Conversation Loop Support | ✅ PASS | `follow_up_possible` flag + Rule 7 ("update your working context after each tool result") + full message history passed each turn |
| 5 | Instructional Framing | ✅ PASS | Full worked example (car acceleration problem) demonstrates exact format, tags, tool call syntax, and verification |
| 6 | Internal Self-Checks | ✅ PASS | Rule 4: "VERIFY with a sanity check or dimensional analysis"; `verification` is a required output field |
| 7 | Reasoning Type Awareness | ✅ PASS | Rule 2: every step tagged with `[ARITHMETIC \| ALGEBRA \| PHYSICS \| CHEMISTRY \| LOGIC \| LOOKUP]` |
| 8 | Error Handling / Fallbacks | ✅ PASS | Rule 5: confidence threshold < 80% → state confidence + give fallback; `confidence` is a 0-100 field |
| 9 | Overall Clarity and Robustness | ✅ PASS | Numbered rules, machine-parseable schema, closed tag vocabulary, example aligned to schema — minimizes hallucination |

---

## The System Prompt

```
You are EduSolve, a rigorous multi-step STEM problem solver.

RULES:
1. Always reason step-by-step. Think before you answer.
2. Tag each reasoning step with its type: [ARITHMETIC] [ALGEBRA] [PHYSICS] [CHEMISTRY] [LOGIC] [LOOKUP]
3. Use the `calculate` or `convert_units` tools whenever you need to compute or convert — never compute in your head.
4. After every tool result, VERIFY it with a sanity check or dimensional analysis before using it in the next step.
5. If your confidence in the final answer is below 80%, explicitly state your confidence level and provide a fallback approach or alternative method.
6. Output all reasoning as numbered steps before the final answer.
7. After each tool result is returned, update your working context and continue reasoning from the updated values.

OUTPUT FORMAT — respond only with valid JSON matching this schema:
{
  "steps": [
    {
      "step": <integer>,
      "type": "<ARITHMETIC | ALGEBRA | PHYSICS | CHEMISTRY | LOGIC | LOOKUP>",
      "reasoning": "<what you are doing and why>",
      "action": "<REASON | FUNCTION_CALL>",
      "expression": "<math expression — only when action is FUNCTION_CALL, else null>"
    }
  ],
  "verification": "<sanity check confirming the answer is plausible>",
  "confidence": <integer 0-100>,
  "final_answer": "<complete answer in plain English with units>",
  "follow_up_possible": <true | false>
}
```

---

## Installation

```bash
git clone <this-repo>
cd EAGV3
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
python main.py
```

## Usage

```
Problem: A ball is thrown upward at 20 m/s. How high does it go and how long until it lands?

  → Calling calculate({"expression": "20**2 / (2 * 9.8)"})
  ← {"result": 20.408163, "expression": "20**2 / (2 * 9.8)"}
  → Calling calculate({"expression": "2 * 20 / 9.8"})
  ← {"result": 4.081633, "expression": "2 * 20 / 9.8"}

╭─ Final Answer ──────────────────────────────────────────────╮
│ The ball reaches a maximum height of ≈ 20.41 m and lands    │
│ after ≈ 4.08 seconds.                                       │
│                                                             │
│ Verification: Using energy: KE = PE → ½mv² = mgh ✓         │
│ Confidence: 97%                                             │
╰─────────────────────────────────────────────────────────────╯
```

## Commands

| Input | Effect |
|-------|--------|
| Any STEM problem | Solves with step-by-step reasoning + tool calls |
| A follow-up question | Continues from prior context |
| `clear` | Resets conversation history |
| `exit` / `quit` | Exits the program |

## Project Structure

```
EAGV3/
├── main.py          # CLI entry point + multi-turn conversation loop
├── prompt.py        # System prompt (9/9 rubric score)
├── tools.py         # calculator + unit_converter tool definitions
├── requirements.txt # anthropic, rich, simpleeval
└── README.md        # This file
```

## Tools Available to the Agent

| Tool | Description |
|------|-------------|
| `calculate(expression)` | Evaluates math expressions: `+`, `-`, `*`, `/`, `**`, `%`, `sqrt`, `sin`, `cos`, `log`, `exp`, `pi`, `e`, etc. |
| `convert_units(value, from_unit, to_unit)` | Converts between mph/m/s, °C/°F/K, kg/lbs, m/ft, km/miles, J/cal, Pa/atm, s/min/h |
