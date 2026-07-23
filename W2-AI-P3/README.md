# FL-02 — Prompting Fundamentals on Real Tasks v2

A naive prompt improved across five versions, each tied to one named
technique (role assignment, context and motivation, few-shot examples,
output structure, step decomposition), run on a real FL-01 target task,
with a genuine cross-model comparison against ChatGPT.

## The real task

Target task from the FL-01 workflow audit: **coding assignment
implementation**. Deliberately kept distinct from the separate Prompt
Ladder exercise, which used general-purpose layers rather than these
five specifically named techniques.

## The five named techniques, in order

1. **Role assignment** — "You are a senior FastAPI engineer mentoring
   a junior developer."
2. **Context and motivation** — the real schema, and who actually
   reviews this code and why.
3. **Few-shot example** — one exact input/output pair the response
   had to match precisely.
4. **Output structure** — three labeled sections: CODE, TEST, EDGE CASE.
5. **Step decomposition** — forced separate reasoning steps before
   combining into a final answer.

## The real catch

Step decomposition (Version 5) surfaced a genuine bug four prior
"correct-looking" versions had silently carried: `len(tasks) + 1` as
an id strategy breaks once deletes are introduced. That's the one
concrete "this made it worse if skipped" moment in the whole ladder.

## Cross-model comparison — Claude vs. ChatGPT

Both models were given the exact same final prompt.

- **Role-assignment stage:** ChatGPT added a full SQLAlchemy model,
  session dependency, and a suggested folder structure, none of which
  was asked for. Claude stayed scoped to the stated in-memory context.
  Honest read: ChatGPT's answer looks more impressive but arguably
  follows the prompt worse.
- **Final combined code:** both converged on nearly identical output.
  One real difference: ChatGPT explicitly separated the request schema
  from the response schema; Claude didn't make that split as explicit.
- **Neither model** reproduced the id-collision catch from Claude's
  earlier step-decomposition run in this same exercise.

Full outputs and reasoning for every version are in
`Prompting_Fundamentals_v2.pdf`.

## Final reusable template

See the PDF for the full template — it folds in one lesson directly
from the cross-model run: explicitly stating "do not over-engineer
beyond the stated requirements," since that's exactly what would have
kept ChatGPT's role-assignment response properly scoped.