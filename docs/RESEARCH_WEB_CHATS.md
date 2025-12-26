# Research: Web Chat Platforms for 1C Processor Generator

> **Date:** December 2025
> **Status:** Complete
> **Purpose:** Analysis of web chat platforms (Claude.ai, ChatGPT, Gemini) for LLM-assisted 1C processor generation

---

## Executive Summary

This document analyzes three major web chat platforms for their suitability in generating 1C:Enterprise processors using our YAML+BSL generator. The key finding is that **context window limitations** vary dramatically between platforms and pricing tiers, requiring platform-specific documentation strategies.

**Key Numbers:**
| Platform | Free Tier | Paid Tier |
|----------|-----------|-----------|
| ChatGPT | **8K tokens** | 128K tokens (GPT-4o) |
| Gemini | **32K tokens** | 1M tokens (Advanced) |
| Claude.ai | **100K tokens** | 200K tokens (Pro) |

**Critical Insight:** Our current `LLM_CORE.md` (~20K tokens) doesn't fit in ChatGPT Free tier at all.

---

## 1. Platform Analysis

### 1.1 Claude.ai Web

**Context Windows:**
| Tier | Context | Messages/Day | Price |
|------|---------|--------------|-------|
| Free | 100K tokens | ~40 short | $0 |
| Pro | 200K tokens | 5x free | $20/mo |
| Enterprise | 500K tokens | Higher | Custom |
| Extended | 1M tokens | Premium rates | - |

**Key Features:**
- **GitHub Integration** - Connect repositories directly for codebase context
- **CLAUDE.md** - Automatically pulled into context (perfect for our use case)
- **"Configure files"** - Strategic file selection within token limits
- **Projects** - Organize conversations with shared context
- **Memory** - Can reference past conversations

**Best Practice for Our Generator:**
1. User connects GitHub repo with `1c-processor-generator`
2. CLAUDE.md automatically provides core instructions
3. User uploads specific examples or references `docs/LLM_CORE.md`
4. Claude generates YAML+BSL

**Sources:**
- [Using the GitHub Integration](https://support.claude.com/en/articles/10167454-using-the-github-integration)
- [Claude Context Window Limits 2025](https://www.datastudios.org/post/claude-context-window-token-limits-memory-policy-and-2025-rules)

---

### 1.2 ChatGPT

**Context Windows:**
| Tier | Model | Context | Messages | Price |
|------|-------|---------|----------|-------|
| Free | GPT-3.5 | **8K tokens** | 10/5hr | $0 |
| Plus | GPT-4o | 128K tokens | 80/3hr | $20/mo |
| Plus | GPT-4 | 32K tokens | 40/3hr | $20/mo |
| Plus | o1-preview | 128K tokens | 30/week | $20/mo |
| Team | GPT-4o | 128K tokens | 160/3hr | $30/user/mo |

**Key Features:**
- **Projects** - Workspaces with custom instructions and files
- **Custom Instructions** - Persist across conversations
- **File Uploads** - PDF, DOCX, XLSX, TXT, ZIP, images (up to 500MB)
- **Memory** - Remembers past chats within project
- **Sharing** - Share projects with team members
- **Custom GPTs** - Create specialized assistants (GPT Store)

**Projects Feature (2025 Updates):**
- Deep research support
- Voice mode support
- Mobile file upload
- Project sharing for all users (Oct 2025)

**Critical Limitation:**
> Free tier has only **8K tokens** - our `LLM_CORE.md` (20K tokens) won't fit!

**Recommended Approach:**
1. Create "1C Processor Generator" Custom GPT
2. Embed lite documentation in system instructions
3. Upload knowledge base files
4. Users interact with pre-configured assistant

**Sources:**
- [Projects in ChatGPT](https://help.openai.com/en/articles/10169521-using-projects-in-chatgpt)
- [ChatGPT Custom Instructions](https://help.openai.com/en/articles/8096356-chatgpt-custom-instructions)
- [ChatGPT Token Limits 2025](https://www.datastudios.org/post/chatgpt-token-limits-and-context-windows-updated-for-all-models-in-2025)

---

### 1.3 Google Gemini

**Context Windows:**
| Tier | Context | Files | Price |
|------|---------|-------|-------|
| Free | 32K tokens | 10/prompt, 100MB each | $0 |
| Advanced | 1M tokens | Higher limits | $20/mo |
| Deep Think | 192K tokens | - | - |

**File Limits:**
- Up to 10 files per prompt
- Each file up to 100MB (except video: 2GB)
- Video: 5 min (free) / 1 hour (paid)
- Audio: 10 min (free) / 3 hours (paid)
- Supported: PDF, DOCX, XLSX, TXT, images, audio, video

**Key Features:**
- **Projects** (Late 2025) - Persistent workspaces like ChatGPT
- **Temporary Chat** - Privacy mode (not saved, not used for training)
- **Connected Apps** - Google Drive, Workspace integration
- **Deep Research** - Extended context for complex analysis
- **Mixed Media** - Upload multiple file types in one prompt

**Context Management:**
> "The system treats all attachments as shared context within the same conversation, meaning you can ask several follow-ups without re-uploading the files."

**Recommended Approach:**
1. User uploads `LLM_WEB_LITE.md` (our compressed doc)
2. Optionally uploads examples from `examples/yaml/`
3. Gemini generates YAML+BSL
4. Files remain accessible throughout conversation

**Sources:**
- [Gemini File Upload Guide](https://support.google.com/gemini/answer/14903178)
- [Gemini Apps Privacy Controls](https://blog.google/products/gemini/temporary-chats-privacy-controls/)
- [Gemini Projects Update](https://www.gemini.org.in/gemini/2025/12/google-gemini-projects-update)

---

## 2. Platform Comparison Matrix

### 2.1 Context & Files

| Feature | Claude.ai | ChatGPT | Gemini |
|---------|-----------|---------|--------|
| **Free Context** | 100K | 8K | 32K |
| **Paid Context** | 200K-1M | 128K | 1M |
| **File Upload** | Via GitHub/Projects | 500MB | 100MB |
| **File Types** | Code, docs | PDF, DOCX, images | All media |
| **GitHub Integration** | Native | Via paste | Manual |

### 2.2 Features for Development

| Feature | Claude.ai | ChatGPT | Gemini |
|---------|-----------|---------|--------|
| **Custom Instructions** | CLAUDE.md | Projects | Coming |
| **Custom Assistants** | Projects | Custom GPTs | - |
| **Code Generation** | Excellent | Good | Good |
| **1C/BSL Knowledge** | Best | Moderate | Limited |
| **Cyrillic Support** | Excellent | Good | Good |

### 2.3 Best Use Cases

| Platform | Best For |
|----------|----------|
| **Claude.ai** | Full workflow with GitHub repo access |
| **ChatGPT** | Custom GPT for standardized generation |
| **Gemini** | Quick one-off generations with file upload |

---

## 3. Documentation Strategy

### 3.1 Current Documentation Problem

Our existing LLM documentation is optimized for CLI agents (Claude Code, Codex) that have:
- Automatic file access
- Large context windows
- Multi-file navigation

**Current Sizes:**
| Document | Lines | ~Tokens |
|----------|-------|---------|
| LLM_CORE.md | 1,742 | 20K |
| LLM_PATTERNS_ESSENTIAL.md | 1,273 | 14.5K |
| LLM_DATA_GUIDE.md | 680 | 7.5K |
| LLM_PRACTICES.md | 587 | 6.5K |
| QUICK_REFERENCE.md | 710 | 8K |
| **Total Essential** | ~5,000 | ~56K |

**Problem:** ChatGPT Free (8K) can't even load our core document!

### 3.2 Solution: Tiered Documentation

**Tier 1: Ultra-Lite (~3K tokens)**
- For ChatGPT Free
- Covers bare minimum: YAML structure, 1 pattern, command
- File: `WEB_QUICK_START.md`

**Tier 2: Lite (~5K tokens)**
- For Gemini Free (32K context with room for conversation)
- Covers 80% use cases: 3 patterns, BSL rules, common errors
- File: `LLM_WEB_LITE.md`

**Tier 3: Full (~20K tokens)**
- For Claude.ai, ChatGPT Plus, Gemini Advanced
- Current `LLM_CORE.md` with just-in-time retrieval
- Files: Existing documentation

### 3.3 Platform-Specific Recommendations

**For Claude.ai Users:**
1. Connect GitHub repo
2. CLAUDE.md handles basics
3. Reference `docs/LLM_CORE.md` for details
4. Use "Configure files" for examples

**For ChatGPT Free Users:**
1. Copy `WEB_QUICK_START.md` into chat
2. Ask for simple form first
3. Iterate with follow-up questions
4. Or use Custom GPT (recommended)

**For ChatGPT Plus Users:**
1. Create Project "1C Generator"
2. Upload `LLM_WEB_LITE.md` as file
3. Set custom instructions from template
4. Or use Custom GPT

**For Gemini Users:**
1. Upload `LLM_WEB_LITE.md`
2. Optionally upload example YAML
3. Generate in conversation
4. Files persist throughout chat

---

## 4. Best Practices for Limited Context

### 4.1 Token Budgeting

Allocate tokens strategically:
```
Total Budget: 8K (ChatGPT Free)
- System overhead: ~1K
- Documentation: ~3K
- User prompt: ~1K
- Response: ~3K
```

### 4.2 Compression Techniques

1. **Remove redundancy** - Don't repeat concepts
2. **Use tables** - More info per token than prose
3. **Code examples > text** - Show, don't tell
4. **Reference, don't embed** - "See Pattern 1" vs full pattern

### 4.3 Structured Formats

Use markdown structure for better parsing:
```markdown
## Pattern: Simple Form
**Use when:** Single form with input fields
**YAML:**
```yaml
# minimal example
```
**BSL:** (body only)
```

### 4.4 Warning: Over-Specification Hurts

Research shows:
> "LLMs' performance can drop by **19%** as we specify more requirements."
> "Requirement-aware optimizers can produce shorter prompts (**-43% tokens**) that are easier to follow."

**Implication:** Our lite docs should focus on **essential rules only**, not comprehensive coverage.

---

## 5. Custom GPT / Claude Project Strategy

### 5.1 Custom GPT "1C Processor Generator"

**Advantages:**
- Pre-configured system instructions
- Knowledge base uploaded once
- Users get consistent experience
- Publishable to GPT Store

**System Instructions Structure:**
```
1. Role definition (50 tokens)
2. YAML rules (200 tokens)
3. BSL rules (200 tokens)
4. Critical errors (100 tokens)
5. Output format (50 tokens)
Total: ~600 tokens system
```

**Knowledge Base Files:**
- `knowledge_base.md` - Full documentation
- `examples/*.yaml` - Example configs
- `VALID_PICTURES.md` - StdPicture reference

### 5.2 Claude Project

**Setup:**
1. Create project "1C Processor Generator"
2. Add `CLAUDE.md` as custom instructions
3. Connect GitHub repo (optional)
4. Add example files

**Advantages over chat:**
- Persistent instructions
- Shared context
- Reusable across conversations

---

## 6. Recommendations

### 6.1 Immediate Actions

1. **Create `LLM_WEB_LITE.md`** - Compressed documentation (<8K tokens)
2. **Create `WEB_QUICK_START.md`** - Ultra-minimal guide (<3K tokens)
3. **Create Custom GPT template** - Ready for GPT Store
4. **Create Claude Project template** - Ready to share

### 6.2 Documentation Updates

1. **Add platform-specific guides** - `WEB_CHAT_GUIDE.md`
2. **Update CLAUDE.md** - Reference new docs
3. **Create template zips** - One-click setup

### 6.3 Long-term Considerations

1. **Monitor platform updates** - Gemini Projects, ChatGPT improvements
2. **Gather user feedback** - Which platform works best?
3. **Consider API integrations** - For advanced users

---

## 7. Appendix: Sources

### Official Documentation
- [Claude GitHub Integration](https://support.claude.com/en/articles/10167454-using-the-github-integration)
- [ChatGPT Projects](https://help.openai.com/en/articles/10169521-using-projects-in-chatgpt)
- [Gemini File Upload](https://support.google.com/gemini/answer/14903178)

### Context & Limits
- [Claude Context Window 2025](https://www.datastudios.org/post/claude-context-window-token-limits-memory-policy-and-2025-rules)
- [ChatGPT Token Limits 2025](https://www.datastudios.org/post/chatgpt-token-limits-and-context-windows-updated-for-all-models-in-2025)
- [Gemini Context & Limits](https://9to5google.com/2025/02/25/free-gemini-document-upload/)

### Best Practices
- [Context Engineering Best Practices 2025](https://www.kubiya.ai/blog/context-engineering-best-practices)
- [LLM Context Engineering Guide](https://medium.com/the-low-end-disruptor/llm-context-engineering-a-practical-guide-248095d4bf71)
- [Optimizing LLM Accuracy](https://platform.openai.com/docs/guides/optimizing-llm-accuracy)

### ChatGPT Specific
- [ChatGPT Projects Guide](https://www.datacamp.com/blog/chatgpt-projects)
- [Custom GPTs vs Projects](https://www.adventuresincre.com/chatgpt-projects-vs-custom-gpts/)

### Gemini Specific
- [Gemini Projects Update](https://www.gemini.org.in/gemini/2025/12/google-gemini-projects-update)
- [Gemini Privacy Controls](https://blog.google/products/gemini/temporary-chats-privacy-controls/)

---

*Last updated: December 2025*
