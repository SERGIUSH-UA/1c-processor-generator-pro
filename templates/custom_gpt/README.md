# Custom GPT Template: 1C Processor Generator

## How to Create the Custom GPT

### Step 1: Go to GPT Builder

1. Visit [chat.openai.com](https://chat.openai.com)
2. Click **"Explore GPTs"** → **"Create"**
3. Or go directly to [https://chatgpt.com/gpts/editor](https://chatgpt.com/gpts/editor)

### Step 2: Configure Basic Info

**Name:** 1C Processor Generator

**Description:**
```
Generate 1C:Enterprise external processors (.epf) from natural language descriptions.
Creates YAML configs and BSL handlers for the 1c-processor-generator tool.
Supports Russian and Ukrainian languages.
```

**Profile Picture:** Use a 1C-related icon or generate one

### Step 3: Set Instructions

Copy the content from `instructions.md` into the **Instructions** field.

### Step 4: Upload Knowledge Files

Upload these files to **Knowledge**:
1. `knowledge_base.md` (this folder) - YAML/BSL reference
2. `styling_guide.md` (this folder) - Colors, fonts, ConditionalAppearance
3. `../../docs/LLM_WEB_LITE.md` - Core documentation
4. `../../docs/VALID_PICTURES.md` (optional - for StdPicture reference)

### Step 5: Configure Capabilities

Enable:
- [x] Web Browsing (for documentation lookup)
- [ ] DALL-E Image Generation (not needed)
- [ ] Code Interpreter (not needed)

### Step 6: Conversation Starters

Add these:
1. "Створи просту обробку для введення даних клієнта"
2. "Потрібен звіт по продажах з фільтрами та таблицею"
3. "Зроби майстер-деталь форму: категорії → товари"
4. "Допоможи імпортувати дані з Excel в 1С"

### Step 7: Save & Test

1. Click **Save** → **Only me** (for testing)
2. Test with the conversation starters
3. Verify output format (config.yaml + handlers.bsl)
4. When ready, change to **Anyone with a link** or **Public**

---

## Files in this Directory

| File | Purpose |
|------|---------|
| `instructions.md` | System instructions for GPT |
| `knowledge_base.md` | YAML/BSL reference for knowledge upload |
| `styling_guide.md` | UI styling: colors, fonts, ConditionalAppearance |
| `README.md` | This setup guide |

---

## Testing Checklist

After creating the GPT, test these scenarios:

- [ ] Simple form with 2-3 fields
- [ ] Form with table (ValueTable)
- [ ] Master-detail relationship
- [ ] Form with server-side data loading
- [ ] Command with picture and shortcut
- [ ] Validation in handler

---

## Maintenance

When updating the generator:
1. Update `knowledge_base.md` with new features
2. Update `instructions.md` if rules change
3. Re-upload files to the GPT

---

## GPT Store Submission

For public listing:
1. Ensure description mentions "1C:Enterprise"
2. Add category: "Programming"
3. Test thoroughly with different prompts
4. Consider adding example outputs in description
