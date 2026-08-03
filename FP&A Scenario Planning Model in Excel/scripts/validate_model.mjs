import path from "node:path";
import { fileURLToPath } from "node:url";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const __filename = fileURLToPath(import.meta.url);
const projectRoot = path.resolve(path.dirname(__filename), "..");
const workbookPath = path.join(projectRoot, "model", "fpa_scenario_planning_model.xlsx");

const input = await FileBlob.load(workbookPath);
const workbook = await SpreadsheetFile.importXlsx(input);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "formula error scan",
});

const validation = await workbook.inspect({
  kind: "table",
  sheetId: "Validation Checks",
  range: "A3:E10",
  include: "values,formulas",
  tableMaxRows: 8,
  tableMaxCols: 5,
  maxChars: 3000,
});

console.log(errors.ndjson);
console.log(validation.ndjson);
