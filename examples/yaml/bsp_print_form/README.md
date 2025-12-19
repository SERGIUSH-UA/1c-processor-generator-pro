# BSP Print Form Example

This example demonstrates how to generate BSP-compatible external print forms.

## Features

- **СведенияОВнешнейОбработке()** - Auto-generated BSP registration function
- **Печать()** - Print procedure with УправлениеПечатью integration
- **Multi-command support** - Multiple print forms in one processor
- **MXL and Word** - Both spreadsheet and Office document templates

## Usage

```bash
# Generate XML structure
python -m 1c_processor_generator yaml \
  --config examples/yaml/bsp_print_form/config.yaml \
  --output output

# Generate EPF (requires PRO license)
python -m 1c_processor_generator yaml \
  --config examples/yaml/bsp_print_form/config.yaml \
  --output output \
  --output-format epf
```

## Generated ObjectModule.bsl

The generator produces:

```bsl
#Если Сервер Или ТолстыйКлиентОбычноеПриложение Или ВнешнееСоединение Тогда

#Область ПрограммныйИнтерфейс

Функция СведенияОВнешнейОбработке() Экспорт
    ПараметрыРегистрации = Новый Структура;
    ПараметрыРегистрации.Вставить("Вид", "ПечатнаяФорма");
    ПараметрыРегистрации.Вставить("Версия", "1.0");
    // ... команды та призначення
    Возврат ПараметрыРегистрации;
КонецФункции

Процедура Печать(МассивОбъектов, КоллекцияПечатныхФорм, ОбъектыПечати, ПараметрыВывода) Экспорт
    // Auto-generated handlers for each command
КонецПроцедуры

#КонецОбласти

#КонецЕсли
```

## Requirements

- PRO License for BSP integration feature
- 1C:Enterprise 8.3 with БСП (Standard Subsystems Library)

## BSP Types Supported

| YAML Type | BSP Kind |
|-----------|----------|
| `print_form` | ПечатнаяФорма |
| `object_filling` | ЗаполнениеОбъекта |
| `creation_of_related` | СозданиеСвязанныхОбъектов |
| `report` | Отчет |
| `additional_processor` | ДополнительнаяОбработка |

## Command Usage Types

| YAML Usage | BSP Usage |
|------------|-----------|
| `server_method` | ВызовСерверногоМетода |
| `client_method` | ВызовКлиентскогоМетода |
| `open_form` | ОткрытиеФормы |
