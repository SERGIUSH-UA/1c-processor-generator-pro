# Troubleshooting Guide

## Common Issues

### YAML Validation Errors

**Issue:** Invalid YAML structure
```
Error: YAML parsing failed
```
**Solution:** Check YAML syntax, indentation must be 2 spaces.

### BSL Handler Not Found

**Issue:** Handler file not found
```
Error: Handler not found: ОбработатьДанные
```
**Solution:** Ensure handler name in YAML matches procedure name in handlers.bsl

### EPF Compilation Failed

**Issue:** EPF generation failed
```
Error: EPF compilation failed
```
**Solutions:**
1. Check 1C platform is installed
2. Verify XML structure is valid
3. Check BSL syntax errors in handlers

### Encoding Issues

**Issue:** Cyrillic characters display incorrectly
**Solution:** Ensure files are saved as UTF-8 with BOM

## BSL Syntax Errors

### Mixed Language Keywords

**Issue:** Keywords in wrong language
```
Error: Expected 'КонецПроцедуры', found 'EndProcedure'
```
**Solution:** Use consistent language (Russian or English) within each procedure.

### Missing Directives

**Issue:** Missing &НаКлиенте or &НаСервере
**Solution:** Add appropriate directive before each procedure.

## Form Element Issues

### Table Not Displaying Data

**Issue:** Table shows no data
**Solutions:**
1. Check data path matches attribute name
2. Verify columns are properly defined
3. Check OnCreateAtServer initializes data

### Button Not Working

**Issue:** Button click does nothing
**Solutions:**
1. Check command name matches handler name
2. Verify handler has correct parameters
3. Check &НаКлиенте directive is present

## Getting Help

- Documentation: `docs/LLM_CORE.md`
- Examples: `examples/yaml/`
- Support: https://itdeo.tech/account
