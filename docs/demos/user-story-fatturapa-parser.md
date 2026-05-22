# User Story: Parser FatturaPA Automatico

## Storia

**Come** sviluppatore di un'azienda che riceve fatture da fornitori italiani,
**voglio** estrarre automaticamente i dati chiave da file XML FatturaPA
**in modo da** non dover aprire manualmente ogni fattura per trovare importi, date e partite IVA.

## Contesto

FatturaPA è il formato XML obbligatorio per la fatturazione elettronica B2B/B2G in Italia dal 2019.
Ogni fattura è un file XML di 100-300 righe. Un'azienda media ne riceve 50-200 al mese.
Aprirle manualmente per riconciliare con il gestionale è lavoro che può essere eliminato.

## Criterio di accettazione

Data una fattura XML valida FatturaPA v1.2, la funzione:

```python
parse_fattura(xml_path: str) -> dict
```

restituisce un dizionario con questi campi obbligatori:

| Campo | Tipo | Esempio | Fonte XPath |
|-------|------|---------|-------------|
| `numero` | str | `"2026/001"` | `//DatiGeneraliDocumento/Numero` |
| `data` | str | `"2026-05-22"` | `//DatiGeneraliDocumento/Data` |
| `piva_cedente` | str | `"01234567890"` | `//CedentePrestatore/.../IdCodice` |
| `imponibile` | float | `1000.0` | `//DatiRiepilogo/ImponibileImporto` |
| `iva` | float | `220.0` | `//DatiRiepilogo/Imposta` |
| `totale` | float | `1220.0` | `//ImportoTotaleDocumento` |

## Cosa NON rientra nello scope

- Validazione XSD della fattura (non è un validatore)
- Gestione di fatture multi-body (più `FatturaElettronicaBody` per file)
- Parsing di allegati PDF embedded
- Connessione a SDI o servizi Agenzia Entrate

## File di test

La fattura di esempio per la demo è: [`fattura_esempio.xml`](fattura_esempio.xml)

Cedente: Acme Srl (P.IVA 01234567890)
Cessionario: Cliente SpA (P.IVA 09876543210)
Imponibile: €1.000,00 · IVA 22%: €220,00 · Totale: €1.220,00

## Come viene usata in questa demo

La pipeline a 3 agenti riceve questa user story come input.
Lo **Spec Agent** (Haiku) la trasforma in una spec tecnica (`SPEC.md`).
Il **Build Agent** (Sonnet) implementa `parser.py` leggendo la spec.
Il **Quality Agent** (Opus) valuta se l'implementazione soddisfa i criteri di accettazione.

Il file XML non entra mai nel contesto degli agenti: lavorano solo sulla spec.
Solo il Quality Agent esegue `parser.py` sulla fattura reale per la verifica finale.
