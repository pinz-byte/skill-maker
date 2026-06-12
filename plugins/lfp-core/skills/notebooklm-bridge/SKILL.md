---
name: notebooklm-bridge
description: >
  Two-way bridge between Google NotebookLM and Cowork. Queries any NotebookLM notebook
  from inside a Cowork session using Chrome browser automation -- types the question,
  submits it, waits for the sourced response, and returns the full answer. Enables
  iterative Q&A: ask once, get more if needed, chain queries. Use whenever the user
  says "ask the notebook", "query notebooklm", "get from the notebook", "what does the
  notebook say about", "pull from notebooklm", "notebook bridge", "ask notebooklm",
  "check the notebook", or provides a notebooklm.google.com URL alongside a question.
  Also trigger when the user wants to retrieve research from NotebookLM to act on in
  Cowork (summarize, draft, reformat, share). Default notebook: Claude AIOS Blueprint.
---

# NotebookLM Bridge

Query any NotebookLM notebook from Cowork. Uses Chrome MCP to interact with the
NotebookLM web UI -- no API needed. Supports iterative Q&A: one query or many in
sequence, each building on the last.

## Default Notebook

Unless the user specifies a URL, use this notebook:
```
https://notebooklm.google.com/notebook/e71f60e0-8b9e-4f76-b606-ede027c89abc
```
Title: "The Blueprint for Building a Claude 4.8 AI Operating System"

If the user provides a different NotebookLM URL, use that instead.

## Step-by-Step Protocol

### 1. Get Chrome tab context

```
mcp__Claude_in_Chrome__tabs_context_mcp (createIfEmpty: true)
```

Check if the target notebook is already open in a tab. If yes, use that tab ID.
If no, navigate to the notebook URL:

```
mcp__Claude_in_Chrome__navigate(url: <notebook_url>)
```

Wait 3 seconds for the page to load.

### 2. Find the chat input

```
mcp__Claude_in_Chrome__find(
  query: "Ask a question text input chat box",
  tabId: <tab_id>
)
```

The input has placeholder text "Ask a question or create something".
Use the ref from the result in the next step.

### 3. Type the query

```
mcp__Claude_in_Chrome__form_input(
  ref: <input_ref>,
  tabId: <tab_id>,
  value: "<the user's question>"
)
```

### 4. Submit

Do NOT use Return/Enter -- it does not submit in NotebookLM.
Find and click the blue send button:

```
mcp__Claude_in_Chrome__find(
  query: "send submit button chat",
  tabId: <tab_id>
)
```

Then click it. Alternatively, click at the position of the arrow button visible
to the right of the input field.

### 5. Wait for response

NotebookLM typically takes 8-15 seconds to generate a response.
Wait 10 seconds, then take a screenshot to check if "Responding..." is gone.
If still responding, wait another 5 seconds.

```
mcp__Claude_in_Chrome__computer(action: "wait", duration: 10, tabId: <tab_id>)
mcp__Claude_in_Chrome__computer(action: "screenshot", tabId: <tab_id>)
```

### 6. Extract the response

Use JavaScript to pull the latest response text:

```javascript
mcp__Claude_in_Chrome__javascript_tool(
  action: "javascript_exec",
  tabId: <tab_id>,
  text: `
    const chatPanel = document.querySelector('[class*="chat"]') || document.querySelector('main');
    chatPanel ? chatPanel.innerText.slice(-4000) : 'extraction failed';
  `
)
```

The result includes the full recent chat history. The last Q&A exchange is at the
bottom -- identify it by the user's query text appearing before the response.

### 7. Return to Cowork

Present the extracted response to the user with:
- The question asked
- The NotebookLM answer (cleaned of citation numbers like [1], [2])
- A note on which sources were cited (e.g., "2 sources")
- Offer to ask a follow-up or do something with the content

## Iterative Q&A Pattern

After returning the first response, always offer:
- "Want me to ask a follow-up question?"
- "Should I pull more detail on any specific part?"
- "Ready to use this content -- want a summary doc, Notion page, or Slack message?"

The Chrome tab stays open between queries, so follow-up questions are instant
(no re-navigation needed, just steps 2-7 again).

## Multiple Notebooks

If the user has multiple notebooks, ask for the URL or offer to list known ones.
Store frequently used notebooks as data capsules for fast retrieval.

Known notebooks (LFP ecosystem):
| Notebook | URL |
|---|---|
| Claude AIOS Blueprint | https://notebooklm.google.com/notebook/e71f60e0-8b9e-4f76-b606-ede027c89abc |

## What NotebookLM Does That Claude Cannot

NotebookLM queries are SOURCE-GROUNDED -- every claim is cited back to the original
YouTube transcript or document. Use this bridge when you need:
- Precise quotes or timestamps from video content
- Cross-source synthesis (multiple videos/docs at once)
- Facts you want attributed to a specific source, not generated

## Error Handling

| Symptom | Fix |
|---|---|
| Page shows login screen | User needs to be logged into Google in Chrome |
| "Responding..." never clears | Wait longer; try screenshot after 20s total |
| Input ref not found | Page may not be fully loaded; wait 3s and retry find |
| Extracted text is empty | Try get_page_text as fallback; or read_page accessibility tree |
| Wrong notebook content | Verify URL matches the intended notebook |
