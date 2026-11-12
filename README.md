# Serin AI agent plugins

This repo holds the plugins that connect AI agents (Claude Code, Codex / ChatGPT,
OpenCode, Cursor and others) to the **Serin MCP server**, Serin's recruiting
tools for jobs, applicants, interview evaluations and candidate outreach.

The server itself lives in [`serin_mcp`](https://github.com/Blink-Analytics/serin_mcp)
and runs at `https://mcp.serin-ai.com/mcp`. This repo contains no server code.
It holds only the packaging each agent needs:

- **MCP connection config**: the server URL. Authentication is OAuth: the first
  connection opens a browser to sign in to Serin, and recruiters pick the
  organization the connection acts on.
- **Skills**: `skills/*/SKILL.md` teach the agent how to use the tools safely,
  for example how to preview an email before sending it. Start with
  `skills/using-serin-mcp`.

A Serin recruiter account is required.

## Install

### Claude Code

```text
/plugin marketplace add Blink-Analytics/serin-ai
/plugin install serin-mcp@serin-labs
```

Then run `/mcp`, select **serin** and choose **Authenticate**.

### Codex / ChatGPT (OpenAI)

**Codex CLI**

1. Add the server and sign in:

   ```bash
   codex mcp add serin --url https://mcp.serin-ai.com/mcp
   codex mcp login serin
   ```

2. Install the skills:

   ```bash
   npx skills add Blink-Analytics/serin-ai
   ```

**ChatGPT**

Add Serin as a custom MCP connector (in **Plugins → Add → Add custom MCP server**). Use
`https://mcp.serin-ai.com/mcp` as the server URL and choose OAuth when
asked how to authenticate. Sign in with your Serin recruiter account when
prompted.

### OpenCode

1. Add the server to `~/.config/opencode/opencode.json` (global) or to
   `opencode.json` in your project. Copy it from
   [`opencode/opencode.json`](opencode/opencode.json):

   ```json
   {
     "$schema": "https://opencode.ai/config.json",
     "mcp": {
       "serin": { "type": "remote", "url": "https://mcp.serin-ai.com/mcp", "enabled": true }
     }
   }
   ```

2. Install the skills:

   ```bash
   npx skills add Blink-Analytics/serin-ai
   ```

   Or copy the folders under `skills/` into `~/.config/opencode/skills/`.

3. Authenticate: `opencode mcp auth serin`

### Other MCP clients (Cursor, Gemini CLI, VS Code, etc.)

Add a remote MCP server using streamable HTTP with this URL:

```text
https://mcp.serin-ai.com/mcp
```

The client must support OAuth for MCP. The server advertises discovery and
dynamic client registration. To give the agent the skills, run
`npx skills add Blink-Analytics/serin-ai`, or copy `skills/` into the folder
your client reads skills from.

## Repo layout

| Path | Used by |
|---|---|
| `skills/` | Every agent. **The single source of truth for skills** |
| `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`, `.mcp.json` | Claude Code |
| `openai/plugin.json`, `openai/mcp.json` | Codex / ChatGPT, packed by `scripts/build_openai_zip.py` |
| `opencode/opencode.json` | OpenCode config snippet |
| `assets/icon.png` | Plugin icon (Claude listing + OpenAI package) |

## Maintaining

- Edit skills only in `skills/`. Every agent package reads from that folder.
- When you release, bump `version` in **both** `.claude-plugin/plugin.json` and
  `openai/plugin.json`, then rebuild the OpenAI zip. Claude Code users only get
  updates after the version changes.
- Check the Claude plugin with `claude plugin validate .`.
