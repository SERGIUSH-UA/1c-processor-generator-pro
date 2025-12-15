# Valid StdPicture Names Reference

Complete list of all 129 valid StdPicture names supported by 1C:Enterprise 8.3 platform.

**Generated from:** `constants.VALID_STD_PICTURES`
**Last updated:** 2025-12-05
**Version:** 2.46.0

---

## How to Use

In YAML configuration:
```yaml
commands:
  - name: MyCommand
    title_ru: Моя команда
    picture: StdPicture.Refresh  # ✅ Use names from list below
```

In BSL code (buttons, menus):
```bsl
Кнопка.Картинка = БиблиотекаКартинок.Обновить;  // StdPicture.Refresh
```

**Validation:** The generator automatically validates StdPicture names. If you use an invalid name, you'll get a validation error with suggestions.

---

## Common Pictures (Quick Reference)

### Actions
- `StdPicture.ExecuteTask` - Execute/Run actions
- `StdPicture.Refresh` - Refresh/Reload data
- `StdPicture.Write` - Save/Write actions (✅ use this for "save" buttons)
- `StdPicture.Delete` - Delete actions
- `StdPicture.Close` - Close/Exit actions
- `StdPicture.Stop` - Stop/Cancel operations

### File Operations
- `StdPicture.SaveFile` - Save to file
- `StdPicture.OpenFile` - Open from file
- `StdPicture.LoadReportSettings` - Load settings
- `StdPicture.SaveReportSettings` - Save settings

### UI & Navigation
- `StdPicture.Find` - Search operations
- `StdPicture.CustomizeForm` - Settings/Configuration
- `StdPicture.User` - User-related actions
- `StdPicture.Properties` - Properties/Details
- `StdPicture.Information` - Info messages

### Data Operations
- `StdPicture.MarkToDelete` - Mark for deletion
- `StdPicture.Post` - Post document
- `StdPicture.UndoPosting` - Unpost document
- `StdPicture.InputOnBasis` - Create based on
- `StdPicture.Change` - Edit/Modify

### Lists & Navigation
- `StdPicture.MoveUp` / `StdPicture.MoveDown` - Reorder items
- `StdPicture.MoveLeft` / `StdPicture.MoveRight` - Navigate
- `StdPicture.ExpandAll` / `StdPicture.CollapseAll` - Tree operations
- `StdPicture.ShowInList` - Show in list

### Reports & Documents
- `StdPicture.GenerateReport` - Generate report
- `StdPicture.Print` - Print actions
- `StdPicture.PrintImmediately` - Print without preview
- `StdPicture.ReportSettings` - Report configuration

---

## Full Alphabetical List (All 129 Pictures)

<details>
<summary>Click to expand full list</summary>

### A
- `StdPicture.AccumulationRegister`
- `StdPicture.ActiveUsers`
- `StdPicture.AddToFavorites`
- `StdPicture.AppearanceExclamationMarkIcon`
- `StdPicture.Attach`
- `StdPicture.Attribute`

### B
- `StdPicture.Back`
- `StdPicture.BusinessProcessStart`

### C
- `StdPicture.CancelSearch`
- `StdPicture.Catalog`
- `StdPicture.Change`
- `StdPicture.ChangeListItem`
- `StdPicture.CheckAll`
- `StdPicture.CheckSyntax`
- `StdPicture.ChooseValue`
- `StdPicture.ClearFilter`
- `StdPicture.CloneListItem`
- `StdPicture.CloneObject`
- `StdPicture.Close`
- `StdPicture.CollaborationSystemUser`
- `StdPicture.CollapseAll`
- `StdPicture.CreateFolder`
- `StdPicture.CreateInitialImage`
- `StdPicture.CreateListItem`
- `StdPicture.CustomizeForm`
- `StdPicture.CustomizeList`

### D
- `StdPicture.DataCompositionConditionalAppearance`
- `StdPicture.DataCompositionDataParameters`
- `StdPicture.DataCompositionFilter`
- `StdPicture.DataCompositionGroupFields`
- `StdPicture.DataCompositionNewChart`
- `StdPicture.DataCompositionNewGroup`
- `StdPicture.DataCompositionNewNestedScheme`
- `StdPicture.DataCompositionNewTable`
- `StdPicture.DataCompositionOrder`
- `StdPicture.DataCompositionOutputParameters`
- `StdPicture.DataCompositionSelection`
- `StdPicture.DataCompositionSettingsWizard`
- `StdPicture.DataCompositionStandardSettings`
- `StdPicture.DataCompositionUserFields`
- `StdPicture.DataHistory`
- `StdPicture.DebitCredit`
- `StdPicture.Delete`
- `StdPicture.DeleteDirectly`
- `StdPicture.Document`
- `StdPicture.DocumentJournal`

### E
- `StdPicture.EndEdit`
- `StdPicture.EventLog`
- `StdPicture.EventLogByUser`
- `StdPicture.ExchangePlan`
- `StdPicture.ExecuteTask`
- `StdPicture.ExpandAll`
- `StdPicture.ExternalDataSourceTable`

### F
- `StdPicture.FilterByCurrentValue`
- `StdPicture.FilterCriterion`
- `StdPicture.Find`
- `StdPicture.FindInList`
- `StdPicture.FindNext`
- `StdPicture.FindPrevious`
- `StdPicture.Form`
- `StdPicture.FormHelp`
- `StdPicture.Forward`

### G
- `StdPicture.GenerateReport`
- `StdPicture.GetURL`
- `StdPicture.GoBack`
- `StdPicture.GroupConversation`

### I
- `StdPicture.Information`
- `StdPicture.InformationRegister`
- `StdPicture.InputFieldCalculator`
- `StdPicture.InputFieldCalendar`
- `StdPicture.InputFieldChooseType`
- `StdPicture.InputFieldClear`
- `StdPicture.InputFieldOpen`
- `StdPicture.InputFieldSelect`
- `StdPicture.InputOnBasis`

### L
- `StdPicture.ListSettings`
- `StdPicture.ListViewMode`
- `StdPicture.ListViewModeHierarchicalList`
- `StdPicture.ListViewModeList`
- `StdPicture.ListViewModeTree`
- `StdPicture.LoadReportSettings`

### M
- `StdPicture.MarkToDelete`
- `StdPicture.MoveDown`
- `StdPicture.MoveItem`
- `StdPicture.MoveLeft`
- `StdPicture.MoveRight`
- `StdPicture.MoveUp`

### N
- `StdPicture.Notifications`

### O
- `StdPicture.OpenFile`

### P
- `StdPicture.Picture`
- `StdPicture.Post`
- `StdPicture.Print`
- `StdPicture.PrintImmediately`
- `StdPicture.Properties`

### Q
- `StdPicture.QueryWizard`
- `StdPicture.QueryWizardCreateTempTableDropQuery`

### R
- `StdPicture.ReadChanges`
- `StdPicture.Refresh`
- `StdPicture.Replace`
- `StdPicture.Report`
- `StdPicture.ReportSettings`
- `StdPicture.Reread`
- `StdPicture.RestoreValues`

### S
- `StdPicture.SaveFile`
- `StdPicture.SaveReportSettings`
- `StdPicture.SaveValues`
- `StdPicture.ScheduledJob`
- `StdPicture.ScheduledJobs`
- `StdPicture.SelectAll`
- `StdPicture.SetDateInterval`
- `StdPicture.SetListItemDeletionMark`
- `StdPicture.SetTime`
- `StdPicture.SettingsStorage`
- `StdPicture.ShowData`
- `StdPicture.ShowInList`
- `StdPicture.SortListAsc`
- `StdPicture.SortListDesc`
- `StdPicture.SpreadsheetReadOnly`
- `StdPicture.Stop`
- `StdPicture.SyncContents`

### U
- `StdPicture.UncheckAll`
- `StdPicture.UndoPosting`
- `StdPicture.UnselectAll`
- `StdPicture.User`
- `StdPicture.UserWithAuthentication`
- `StdPicture.UserWithoutNecessaryProperties`

### W
- `StdPicture.Write`
- `StdPicture.WriteAndClose`
- `StdPicture.WriteChanges`

</details>

---

## Pictures That DO NOT Exist (Common Mistakes)

These are **NOT** valid StdPicture names, despite seeming logical:

❌ `StdPicture.CheckMark` - Does not exist
- ✅ Use instead: `StdPicture.Write` (has checkmark icon)

❌ `StdPicture.Save` - Does not exist
- ✅ Use instead: `StdPicture.Write` or `StdPicture.SaveFile`

❌ `StdPicture.Load` - Does not exist
- ✅ Use instead: `StdPicture.OpenFile`

❌ `StdPicture.Export` - Does not exist
- ✅ Use instead: `StdPicture.SaveFile`

❌ `StdPicture.Import` - Does not exist
- ✅ Use instead: `StdPicture.OpenFile`

❌ `StdPicture.Settings` - Does not exist
- ✅ Use instead: `StdPicture.CustomizeForm`

❌ `StdPicture.Edit` - Does not exist
- ✅ Use instead: `StdPicture.Change`

❌ `StdPicture.Clear` - Does not exist
- ✅ Use instead: `StdPicture.InputFieldClear`

---

## How Pictures Are Validated

The generator validates StdPicture names in `validators.py`:

```python
from constants import VALID_STD_PICTURES

def validate_picture(picture: str):
    if picture.startswith("StdPicture."):
        if picture in VALID_STD_PICTURES:
            return True  # Valid
        else:
            return False  # Invalid - will show error
```

**Validation happens BEFORE generation**, so you'll get clear error messages:

```bash
❌ Команда 'СохранитьВыбранный': Невідома стандартна картинка: StdPicture.CheckMark
   Використовуйте одну з доступних StdPicture (наприклад: StdPicture.ExecuteTask,
   StdPicture.Refresh, StdPicture.Print)
```

---

## Tips for Choosing Pictures

### For Save/Write Actions
✅ `StdPicture.Write` - Most common (has checkmark)
✅ `StdPicture.SaveFile` - For file operations
✅ `StdPicture.WriteAndClose` - Save and close

### For Delete/Remove Actions
✅ `StdPicture.Delete` - Standard delete
✅ `StdPicture.MarkToDelete` - Mark for deletion
✅ `StdPicture.DeleteDirectly` - Delete without confirmation

### For Execute/Run Actions
✅ `StdPicture.ExecuteTask` - Standard execute icon
✅ `StdPicture.GenerateReport` - For reports
✅ `StdPicture.Post` - For posting documents

### For Find/Search Actions
✅ `StdPicture.Find` - Standard search
✅ `StdPicture.FindInList` - Search in list
✅ `StdPicture.FilterByCurrentValue` - Filter operations

### For UI/Settings
✅ `StdPicture.CustomizeForm` - Form settings
✅ `StdPicture.Properties` - Properties dialog
✅ `StdPicture.ListSettings` - List settings

---

## CommonPicture Support

The generator also supports `CommonPicture.*` for configuration-specific pictures:

```yaml
commands:
  - name: MyCommand
    picture: CommonPicture.MyCustomIcon  # ✅ OK (not validated)
```

**Note:** CommonPicture names are **NOT validated** because they're configuration-specific. Make sure the picture exists in your 1C configuration.

---

## Version History

### v2.6.0 (2025-10-13)
- ✨ Created VALID_PICTURES.md with full list
- 📚 Added common mistakes section
- 📚 Added tips for choosing pictures

### v2.2.0 (2025-10-10)
- ✨ Added StdPicture validation with 130+ known pictures
- 🐛 Fixed CheckMark example in documentation

---

## See Also

- **YAML_GUIDE.md** - Complete YAML API documentation
- **LLM_PROMPT.md** - LLM guide with examples
- **constants.py** - Source of VALID_STD_PICTURES list
- **validators.py** - Validation logic

---

**Reference:** This list is extracted from `1c_processor_generator/constants.py:VALID_STD_PICTURES`
