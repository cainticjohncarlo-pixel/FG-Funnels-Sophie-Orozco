---
name: env-windows-bash-heredoc-limit
description: "On this Windows machine, Bash tool heredocs above roughly 30KB fail with ENAMETOOLONG, and double backslashes inside heredocs collapse to single; use the Write tool for large files or anything with backslashes"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7b44ccac-ac58-4ddb-bda5-6c750ddd51da
  modified: 2026-09-12T02:45:31.912Z
---

The Bash tool on this machine (Git Bash on Windows 10) spawns the command through a length-limited path. A `cat > file <<'EOF'` heredoc carrying a ~48KB HTML file failed with `ENAMETOOLONG: name too long, uv_spawn`. Small heredocs (a few KB) work fine.

**Second gotcha (confirmed 12 Sep 2026):** even in a quoted `<<'EOF'` heredoc, every double backslash arrives as a single backslash. A Python literal written as a-backslash-backslash-b came through as a-backslash-b (which Python then read as a backspace), and regex patterns with escaped brackets broke with "unterminated character set". Single backslashes are also unreliable.

**Why:** Auto mode prefers Bash for file writes, but the spawn limit makes large heredocs impossible, not just slow. The backslash collapse silently corrupts any inline script that needs literal backslashes (regex, Windows paths, escape sequences).
**How to apply:** For any file over roughly 20-30KB (full HTML pages, big JSON), use the Write tool directly instead of a heredoc. For inline Python that needs a backslash, build it with `chr(92)` or avoid regex in favour of `str.find`/`split`, or write the script to a file with the Write tool and run it. Keep Bash heredocs for short, backslash-free scripts and config files. Related: [[reference-skills-sh-cli]] notes other Windows path-length gotchas.
