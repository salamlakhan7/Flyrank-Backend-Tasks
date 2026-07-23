# AI-FL-03 — The Prompt Ladder

A weak baseline prompt improved across five versions, each adding
exactly one named layer, with real output comparisons and four honest
notes per version.

## The baseline

"Write backend code" — genuinely weak, the kind of prompt that gets
typed when in a hurry, with no audience, no context, and no
constraints attached.

## The five layers, in order

1. **A defined audience + a clearer goal** — named who the code is for
   and what specific action it should perform.
2. **Real context** — gave the model the actual existing schema
   instead of letting it invent one.
3. **Specified output format + constraints** — required Pydantic,
   a line limit, and the correct REST status code.
4. **An example of what good looks like** — one real snippet showing
   an existing style pattern (`HTTPException` usage) for the model
   to match.
5. **Quality criteria + verification requirements** — asked for the
   exact test command and one named edge case.

## What actually happened

Six real runs total (baseline + 5 versions), each output genuinely
different from the last, not five versions of the same answer restated.
The full comparison, with output excerpts and notes per version, is in
`The_Prompt_Ladder.pdf`.

## The one honest note

Version 1 to Version 2 (adding real context) was the biggest jump.
Skipping that step would have let every later version keep building on
an invented schema instead of the real one — the kind of "this made it
worse if skipped" moment the assignment specifically asks to name.

## Final reusable prompt

> Write backend code for [specific endpoint/action], for [audience].
> Context: [real existing schema/stack]. Return only [format], under
> [X] lines, matching [convention]. Match this style: [real snippet
> from my codebase]. Include the exact test command and name one edge
> case it should reject.