# EduSolve — Multi-Step STEM Problem Solver

A Claude-powered CLI agent that solves complex math, physics, and chemistry problems with explicit step-by-step reasoning, tool use, and self-verification.

## Demo

> YouTube demo link — *coming soon*

---

## Prompt Qualification

The system prompt was evaluated against the [Prompt Evaluation Rubric](https://github.com/sidharth80/EduSolve/blob/main/README.md) using a judge LLM and scored **9 / 9**.

### Evaluator Test Output

The prompt was passed to a judge model running the rubric criteria. This is the raw evaluator output:

```json
{
  "explicit_reasoning": {
    "score": "PASS",
    "reason": "Rule 1 explicitly states 'Always reason step-by-step. Think before you answer.' — both required phrases are present."
  },
  "structured_output": {
    "score": "PASS",
    "reason": "A strict JSON schema with named fields (steps, verification, confidence, final_answer, follow_up_possible) is fully specified and labeled 'strict JSON'."
  },
  "tool_separation": {
    "score": "PASS",
    "reason": "Rule 3 reserves FUNCTION_CALL for computation/conversion while numbered reasoning steps handle inference; the example shows this split clearly across Step 1 (FUNCTION_CALL) vs Steps 2-4 (REASON/LOGIC)."
  },
  "conversation_loop": {
    "score": "PASS",
    "reason": "Rule 7 ('Update your working context after each tool result') and the 'follow_up_possible' flag in the schema explicitly support multi-turn continuation."
  },
  "instructional_framing": {
    "score": "PASS",
    "reason": "A concrete worked example (car acceleration problem) demonstrates the exact step format, tag usage, FUNCTION_CALL syntax, and verification style expected."
  },
  "internal_self_checks": {
    "score": "PASS",
    "reason": "Rule 4 mandates a post-computation sanity check or dimensional analysis, and 'verification' is a required top-level field in the output schema."
  },
  "reasoning_type_awareness": {
    "score": "PASS",
    "reason": "Rule 2 requires tagging every step with an explicit type from a defined vocabulary ([ARITHMETIC], [ALGEBRA], [PHYSICS], [LOGIC], [LOOKUP]), captured in the step schema's 'type' field."
  },
  "fallbacks": {
    "score": "PASS",
    "reason": "Rule 5 specifies a concrete confidence threshold (< 80%) and requires the model to state confidence and provide a fallback approach when uncertain; the 'confidence' field (0-100) reinforces this."
  },
  "overall_clarity": {
    "score": "PASS",
    "reason": "Rules are numbered and unambiguous, the output schema is machine-parseable, the example is well-aligned with the schema, and the tag vocabulary is closed — collectively minimizing hallucination and drift risk."
  },
  "total_score": "9/9",
  "verdict": "The EduSolve prompt is exceptionally well-constructed. It earns a clean 9/9 by covering every rubric criterion: explicit chain-of-thought instructions, a strict parseable JSON schema, clear tool-vs-reasoning separation, multi-turn support hooks, a worked example, mandatory self-verification, typed reasoning tags, a quantified confidence-based fallback policy, and clear unambiguous language throughout."
}
```

### Human-readable Scorecard

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
