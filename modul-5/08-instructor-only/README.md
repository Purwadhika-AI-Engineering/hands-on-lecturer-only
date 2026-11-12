# AcmeBot: AI Security & Guardrails lab

Module 05 · Session 08 · Job Connector AI Engineering

AcmeBot is a customer-support agent for a fictional Indonesian online shop. It has a RAG knowledge base and three tools
(Text-to-SQL, e-mail, file reader). It works, and it is **vulnerable by design**.
In this lab you attack it, defend it layer by layer, then prove the defenses work with an automated attack suite.

> **Rules of engagement.** All data here is synthetic. Attack **only your own AcmeBot container**.
> Never use these techniques on systems you do not own or have written permission to test.

## 1. Setup (5 minutes, do this before class)

You need Docker Desktop and an OpenAI API key from **your own project with a spend limit** (your instructor will tell you how).

```bash
cp .env.example .env          # then put your key in .env
docker compose up -d --build  # first build takes a few minutes
open http://localhost:8000    # or just visit it in a browser
```

Check it works: ask "What is your refund policy?" in the chat page. Then run `make test` (or the raw command in the Makefile): 7 tests should pass.

No key or no internet? Add `LLM_MODE=fake` to `.env`. That swaps in a scripted stand-in model so you can still do the whole lab against your guards.
It is a plumbing check, not a real LLM: the real attack suite should always be run with the real model.

Handy: the page has **Show outbox** (emails the bot "sent") and **Reset lab** (restores the database, outbox and uploads). Reset between experiments.

## 2. How a request flows

```
user message
   │
   ▼  Layer 5  runtime_guard.check_request      rate limit, size, budget
   ▼  Layer 1  input_guard.check                injection / jailbreak / harmful input
   ▼  retrieval ── Layer 2  data_guard.filter_chunks + format_context     who may see which documents, how they are shown
   ▼  agent (OpenAI model + 3 tools)
         └─ every tool call ── Layer 3  tool_guard.authorize + sql_policy + file_policy
   ▼  Layer 4  output_guard.filter              PII, secrets, unsafe links
answer  (+ tool_calls and guard_events so you can see what happened)
```

Uploads go through `data_guard.screen_document` before they are indexed. Risky tool calls can wait in a human approval queue (`GET /approvals`).

## 3. The lab (65 minutes)

### Step 1 · ATTACK (15 min): play the red team
Open `FINDINGS.md`. Probe AcmeBot through the chat page and find **3 or more vulnerabilities**. For each one record what you did, the impact, and the OWASP ID.
Try the sample files in `samples/` (upload them with the page's upload button). Think like an attacker: what can a customer, a document, or a supplier make the bot do?

When you have your own findings, get the full picture and a baseline:

```bash
make attack NAME=before
```

(No `make`? `NAME=before docker compose --profile tools run --rm promptfoo`. On PowerShell: `$env:NAME="before"; docker compose --profile tools run --rm promptfoo`.)

### Step 2 · DEFEND (30 min): play the blue team
Edit the five files in `app/guards/`. Each one is a layer; each is a pass-through stub with hints in its docstring. The app reloads when you save.

| Layer | File | Protects against |
|---|---|---|
| 1 Input | `input_guard.py` | prompt injection, jailbreaks |
| 2 Data / RAG | `data_guard.py` | poisoned documents, access control, untrusted context |
| 3 Tool | `tool_guard.py` | excessive agency: SQL, files, e-mail |
| 4 Output | `output_guard.py` | PII and secret leaks, unsafe links |
| 5 Runtime | `runtime_guard.py` | unbounded consumption |

Also fix `app/prompts.py` (one finding there is not solved by a filter).
Fast feedback loop, free and offline: `make test-defenses`. Each failing test names the attack still working. These use a scripted gullible model, so passing means "my guards work even when the model is fooled".

Hardening the container (non-root, read-only filesystem, dropped capabilities) is a stretch goal. Try it before looking at the instructor material.

### Step 3 · VERIFY (20 min): prove it
```bash
make attack NAME=after     # the real model, the full suite, 18 tests
make compare               # pass-rate per OWASP category: before vs after
```
Open `promptfoo/results/after.json` or read the printed table. Inspect `guard_events` for a blocked attack in the chat page to see *which layer* caught it.
Then fill in `REPORT_TEMPLATE.md`. **Be honest about what still gets through.**

## 4. What to hand in
1. Your repo (the hardened app, runnable with `docker compose up`)
2. `FINDINGS.md`: at least 3 vulnerabilities with impact and OWASP ID
3. `REPORT_TEMPLATE.md` filled in: pass-rate before vs after, defenses per layer, residual risks
4. The two result files in `promptfoo/results/` (`before.json`, `after.json`)

A strong submission shows: attacks blocked across **at least two layers**, normal use still working, and a clear-eyed list of what a determined attacker could still do.

## 5. Stretch goals
- Add the OpenAI Moderation API to your input guard (`ENABLE_MODERATION=1`). Does it stop *any* of the injections? Why not?
- Try [openai-guardrails-python](https://github.com/openai/openai-guardrails-python) or [Presidio](https://microsoft.github.io/presidio/) in place of your regexes.
- Add an LLM-based injection classifier. Measure its cost and its false positives on the normal-use tests.
- Harden the container and prove the app still runs.
- Write one new attack that beats your own defenses, add it to `promptfoo/promptfooconfig.yaml`, then fix it.

## 6. Troubleshooting
| Symptom | Fix |
|---|---|
| `Could not build the knowledge base` at startup | `OPENAI_API_KEY` missing or wrong in `.env` (or set `LLM_MODE=fake`) |
| Port 8000 in use | change the left side of `"8000:8000"` in `docker-compose.yml` |
| Guard edits do nothing | check `docker compose logs app` for a Python error; a guard that crashes **blocks** the request (fail closed) |
| Empty answers after you set a token cap | the gpt-5 family spends output tokens on reasoning; raise `max_output_tokens` |
| Want to swap models | set `OPENAI_MODEL` in `.env` |

## 7. Repo map
```
app/            the application (guards/ is where you work)
data/           synthetic documents, public files, fake credentials
samples/        two sample invoices, one carries a hidden injection
promptfoo/      attack suite: promptfooconfig.yaml, checks.js, provider.js
tests/          offline tests: test_plumbing.py (always green), test_defenses.py (your goal)
scripts/        compare.py
instructor/     answer key and demo script (not part of the student handout)
```
