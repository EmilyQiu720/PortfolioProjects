import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const __filename = fileURLToPath(import.meta.url);
const projectRoot = path.resolve(path.dirname(__filename), "..");
const modelDir = path.join(projectRoot, "model");
const outputsDir = path.join(projectRoot, "outputs");
const previewDir = path.join(outputsDir, "previews");

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines[0].split(",");
  return lines.slice(1).map((line) => {
    const values = line.split(",");
    const row = {};
    headers.forEach((header, index) => {
      const value = values[index];
      const numeric = Number(value);
      row[header] = value !== "" && !Number.isNaN(numeric) ? numeric : value;
    });
    return row;
  });
}

async function readCsv(relativePath) {
  const text = await fs.readFile(path.join(projectRoot, relativePath), "utf8");
  return parseCsv(text);
}

function colName(indexZeroBased) {
  let n = indexZeroBased + 1;
  let name = "";
  while (n > 0) {
    const remainder = (n - 1) % 26;
    name = String.fromCharCode(65 + remainder) + name;
    n = Math.floor((n - 1) / 26);
  }
  return name;
}

function monthLabels() {
  const labels = [];
  for (let year = 2026; year <= 2027; year += 1) {
    for (let month = 0; month < 12; month += 1) {
      labels.push(new Date(Date.UTC(year, month, 1)));
    }
  }
  return labels;
}

function writeCsvSheet(sheet, rows, title) {
  const headers = Object.keys(rows[0]);
  sheet.getRange("A1").values = [[title]];
  sheet.getRangeByIndexes(2, 0, 1, headers.length).values = [headers];
  sheet.getRangeByIndexes(3, 0, rows.length, headers.length).values = rows.map((row) =>
    headers.map((header) => row[header]),
  );
  sheet.getRangeByIndexes(2, 0, 1, headers.length).format = {
    fill: "#0F766E",
    font: { bold: true, color: "#FFFFFF" },
  };
  sheet.getRange("A1").format = {
    font: { bold: true, color: "#111827", size: 16 },
  };
  sheet.freezePanes.freezeRows(3);
  sheet.showGridLines = false;
  sheet.getUsedRange().format.autofitColumns();
}

function styleTitle(sheet, range, title) {
  const titleRange = sheet.getRange(range);
  titleRange.merge();
  titleRange.values = [[title]];
  titleRange.format = {
    fill: "#111827",
    font: { bold: true, color: "#FFFFFF", size: 16 },
  };
}

function styleSectionHeader(range) {
  range.format = {
    fill: "#E0F2FE",
    font: { bold: true, color: "#0F172A" },
    borders: { preset: "outside", style: "thin", color: "#CBD5E1" },
  };
}

function styleTableHeader(range) {
  range.format = {
    fill: "#0F766E",
    font: { bold: true, color: "#FFFFFF" },
    borders: { preset: "outside", style: "thin", color: "#0F766E" },
  };
}

function applySheetDefaults(sheet) {
  sheet.showGridLines = false;
  sheet.getRange("A:A").format.columnWidth = 24;
  sheet.getRange("B:Y").format.columnWidth = 13;
}

function quoteSheet(name) {
  return `'${name}'`;
}

async function main() {
  await fs.mkdir(modelDir, { recursive: true });
  await fs.mkdir(previewDir, { recursive: true });

  const assumptions = await readCsv("data/assumptions.csv");
  const actuals = await readCsv("data/historical_actuals.csv");
  const hiring = await readCsv("data/hiring_plan.csv");
  const months = monthLabels();

  const workbook = Workbook.create();
  const sheets = {};
  [
    "README",
    "Assumptions",
    "Historical Actuals",
    "Hiring Plan",
    "Scenario Controls",
    "Revenue Forecast",
    "Expense Forecast",
    "Cash Flow",
    "Sensitivity Analysis",
    "Dashboard",
    "Validation Checks",
  ].forEach((name) => {
    sheets[name] = workbook.worksheets.add(name);
    applySheetDefaults(sheets[name]);
  });

  buildReadme(sheets.README);
  writeCsvSheet(sheets.Assumptions, assumptions, "Scenario Assumptions");
  writeCsvSheet(sheets["Historical Actuals"], actuals, "Historical Actuals");
  writeCsvSheet(sheets["Hiring Plan"], hiring, "Hiring Plan");
  buildScenarioControls(sheets["Scenario Controls"]);
  buildRevenueForecast(sheets["Revenue Forecast"], months);
  buildExpenseForecast(sheets["Expense Forecast"], months);
  buildCashFlow(sheets["Cash Flow"], months);
  buildSensitivity(sheets["Sensitivity Analysis"]);
  buildDashboard(sheets.Dashboard, months);
  buildChecks(sheets["Validation Checks"]);

  formatModelSheets(sheets);
  await createCharts(sheets);

  const errors = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 300 },
    summary: "final formula error scan",
  });
  console.log(errors.ndjson);

  const dashboardCheck = await workbook.inspect({
    kind: "table",
    sheetId: "Dashboard",
    range: "A1:H18",
    include: "values,formulas",
    tableMaxRows: 18,
    tableMaxCols: 8,
    maxChars: 4000,
  });
  console.log(dashboardCheck.ndjson);

  for (const sheetName of Object.keys(sheets)) {
    const preview = await workbook.render({
      sheetName,
      autoCrop: "all",
      scale: 1,
      format: "png",
    });
    const previewBytes = new Uint8Array(await preview.arrayBuffer());
    await fs.writeFile(path.join(previewDir, `${sheetName.replace(/[^A-Za-z0-9]+/g, "_")}.png`), previewBytes);
    if (sheetName === "Dashboard") {
      await fs.writeFile(path.join(outputsDir, "dashboard_preview.png"), previewBytes);
    }
  }

  const workbookOutput = await SpreadsheetFile.exportXlsx(workbook);
  await workbookOutput.save(path.join(modelDir, "fpa_scenario_planning_model.xlsx"));
  await workbookOutput.save(path.join(outputsDir, "fpa_scenario_planning_model.xlsx"));

  console.log("Workbook generated successfully.");
}

function buildReadme(sheet) {
  styleTitle(sheet, "A1:H1", "FP&A Scenario Planning Model");
  sheet.getRange("A3:B12").values = [
    ["Purpose", "Forecast SaaS growth, expenses, cash, burn, runway, and sensitivity under multiple scenarios."],
    ["Audience", "Executive team, finance, strategy, and operating leaders."],
    ["Model Horizon", "24 monthly forecast periods from Jan 2026 through Dec 2027."],
    ["Scenario Logic", "Change selected scenario on Scenario Controls to switch all forecast assumptions."],
    ["Input Tabs", "Assumptions, Historical Actuals, Hiring Plan."],
    ["Calculation Tabs", "Revenue Forecast, Expense Forecast, Cash Flow, Sensitivity Analysis."],
    ["Output Tabs", "Dashboard and Validation Checks."],
    ["Color Convention", "Teal headers = source/input tables; blue headers = calculations; dark header = presentation output."],
    ["Refresh", "Update source CSVs and rerun scripts/build_workbook.mjs."],
    ["Owner", "Emily Qiu"],
  ];
  sheet.getRange("A3:A12").format = { font: { bold: true }, fill: "#F1F5F9" };
  sheet.getRange("B3:B12").format.wrapText = true;
  sheet.getRange("A:B").format.autofitColumns();
  sheet.getRange("B:B").format.columnWidth = 92;
}

function buildScenarioControls(sheet) {
  styleTitle(sheet, "A1:D1", "Scenario Controls");
  sheet.getRange("A3:B3").values = [["Selected Scenario", "Base"]];
  sheet.getRange("B3").dataValidation = {
    rule: { type: "list", formula1: "Assumptions!$A$4:$A$6" },
  };
  sheet.getRange("A5:B16").values = [
    ["Starting Cash", null],
    ["Starting Customers", null],
    ["Starting ARPA", null],
    ["Monthly New Customers", null],
    ["Monthly Churn", null],
    ["Monthly Expansion", null],
    ["ARPA Growth", null],
    ["Gross Margin", null],
    ["CAC Per Customer", null],
    ["Base Payroll Per FTE", null],
    ["NonPayroll Opex", null],
    ["Sales & Marketing Budget", null],
  ];
  for (let row = 5; row <= 16; row += 1) {
    const sourceCol = colName(row - 4);
    sheet.getRange(`B${row}`).formulas = [[`=INDEX('Assumptions'!$${sourceCol}$4:$${sourceCol}$6,MATCH($B$3,'Assumptions'!$A$4:$A$6,0))`]];
  }
  sheet.getRange("A3:B3").format = { fill: "#FEF3C7", font: { bold: true } };
  styleTableHeader(sheet.getRange("A5:B5"));
  sheet.getRange("A6:A16").format = { fill: "#F8FAFC" };
  sheet.getRange("B5:B16").format = { fill: "#EFF6FF", font: { bold: true } };
}

function writeMonthHeader(sheet, rowNumber, months) {
  sheet.getRangeByIndexes(rowNumber - 1, 1, 1, months.length).values = [months];
  sheet.getRangeByIndexes(rowNumber - 1, 1, 1, months.length).format.numberFormat = "mmm yyyy";
}

function buildRevenueForecast(sheet, months) {
  styleTitle(sheet, "A1:Y1", "Revenue Forecast");
  writeMonthHeader(sheet, 3, months);
  sheet.getRange("A3:A12").values = [
    ["Month"],
    ["Beginning Customers"],
    ["New Customers"],
    ["Churned Customers"],
    ["Ending Customers"],
    ["ARPA"],
    ["MRR"],
    ["ARR"],
    ["NRR"],
    ["CAC Spend"],
  ];
  for (let index = 0; index < 24; index += 1) {
    const col = colName(index + 1);
    const prevCol = colName(index);
    const formulas = [
      null,
      index === 0 ? "='Scenario Controls'!$B$6" : `='Revenue Forecast'!${prevCol}7`,
      "='Scenario Controls'!$B$8",
      `=${col}4*'Scenario Controls'!$B$9`,
      `=${col}4+${col}5-${col}6`,
      index === 0 ? "='Scenario Controls'!$B$7*(1+'Scenario Controls'!$B$11)" : `=${prevCol}8*(1+'Scenario Controls'!$B$11)`,
      `=${col}7*${col}8`,
      `=${col}9*12`,
      "=1-'Scenario Controls'!$B$9+'Scenario Controls'!$B$10",
      `=${col}5*'Scenario Controls'!$B$13`,
    ];
    for (let row = 4; row <= 12; row += 1) {
      sheet.getRange(`${col}${row}`).formulas = [[formulas[row - 3]]];
    }
  }
}

function buildExpenseForecast(sheet, months) {
  styleTitle(sheet, "A1:Y1", "Expense Forecast");
  writeMonthHeader(sheet, 3, months);
  sheet.getRange("A3:A13").values = [
    ["Month"],
    ["Engineering FTE"],
    ["Sales FTE"],
    ["Customer Success FTE"],
    ["G&A FTE"],
    ["Total Headcount"],
    ["Payroll"],
    ["NonPayroll Opex"],
    ["Sales & Marketing"],
    ["Total Opex"],
    ["Opex per Customer"],
  ];
  for (let index = 0; index < 24; index += 1) {
    const col = colName(index + 1);
    const hiringRow = index + 4;
    sheet.getRange(`${col}4`).formulas = [[`='Hiring Plan'!B${hiringRow}`]];
    sheet.getRange(`${col}5`).formulas = [[`='Hiring Plan'!C${hiringRow}`]];
    sheet.getRange(`${col}6`).formulas = [[`='Hiring Plan'!D${hiringRow}`]];
    sheet.getRange(`${col}7`).formulas = [[`='Hiring Plan'!E${hiringRow}`]];
    sheet.getRange(`${col}8`).formulas = [[`=SUM(${col}4:${col}7)`]];
    sheet.getRange(`${col}9`).formulas = [[`=${col}8*'Scenario Controls'!$B$14`]];
    sheet.getRange(`${col}10`).formulas = [["='Scenario Controls'!$B$15"]];
    sheet.getRange(`${col}11`).formulas = [[`='Scenario Controls'!$B$16+'Revenue Forecast'!${col}12`]];
    sheet.getRange(`${col}12`).formulas = [[`=SUM(${col}9:${col}11)`]];
    sheet.getRange(`${col}13`).formulas = [[`=IFERROR(${col}12/'Revenue Forecast'!${col}7,0)`]];
  }
}

function buildCashFlow(sheet, months) {
  styleTitle(sheet, "A1:Y1", "Cash Flow");
  writeMonthHeader(sheet, 3, months);
  sheet.getRange("A3:A12").values = [
    ["Month"],
    ["MRR"],
    ["Gross Profit"],
    ["Total Opex"],
    ["Net Burn"],
    ["Ending Cash"],
    ["Runway (Months)"],
    ["Gross Margin"],
    ["Headcount"],
    ["CAC Payback (Months)"],
  ];
  for (let index = 0; index < 24; index += 1) {
    const col = colName(index + 1);
    const prevCol = colName(index);
    sheet.getRange(`${col}4`).formulas = [[`='Revenue Forecast'!${col}9`]];
    sheet.getRange(`${col}5`).formulas = [[`=${col}4*'Scenario Controls'!$B$12`]];
    sheet.getRange(`${col}6`).formulas = [[`='Expense Forecast'!${col}12`]];
    sheet.getRange(`${col}7`).formulas = [[`=${col}6-${col}5`]];
    sheet.getRange(`${col}8`).formulas = [[index === 0 ? `='Scenario Controls'!$B$5-${col}7` : `=${prevCol}8-${col}7`]];
    sheet.getRange(`${col}9`).formulas = [[`=IF(${col}7>0,${col}8/${col}7,"Cash-flow positive")`]];
    sheet.getRange(`${col}10`).formulas = [["='Scenario Controls'!$B$12"]];
    sheet.getRange(`${col}11`).formulas = [[`='Expense Forecast'!${col}8`]];
    sheet.getRange(`${col}12`).formulas = [[`=IFERROR('Scenario Controls'!$B$13/('Revenue Forecast'!${col}8*'Scenario Controls'!$B$12),0)`]];
  }
}

function buildSensitivity(sheet) {
  styleTitle(sheet, "A1:H1", "Runway Sensitivity");
  sheet.getRange("A3").values = [["Rows flex monthly new customers; columns flex monthly churn. Output is approximate ending runway in months."]];
  sheet.getRange("A5:F5").values = [["Growth / Churn", "-20% churn", "-10% churn", "Base churn", "+10% churn", "+20% churn"]];
  sheet.getRange("A6:A10").values = [["-20% growth"], ["-10% growth"], ["Base growth"], ["+10% growth"], ["+20% growth"]];
  const growthFactors = [0.8, 0.9, 1.0, 1.1, 1.2];
  const churnFactors = [0.8, 0.9, 1.0, 1.1, 1.2];
  for (let row = 0; row < growthFactors.length; row += 1) {
    for (let col = 0; col < churnFactors.length; col += 1) {
      const cell = `${colName(col + 1)}${row + 6}`;
      const growthFactor = growthFactors[row];
      const churnFactor = churnFactors[col];
      sheet.getRange(cell).formulas = [[
        `=MAX(0,('Scenario Controls'!$B$5-24*(('Scenario Controls'!$B$14*AVERAGE('Expense Forecast'!$B$8:$Y$8)+'Scenario Controls'!$B$15+'Scenario Controls'!$B$16)-(('Scenario Controls'!$B$6+24*'Scenario Controls'!$B$8*${growthFactor}-12*'Scenario Controls'!$B$6*'Scenario Controls'!$B$9*${churnFactor})*'Scenario Controls'!$B$7*'Scenario Controls'!$B$12)))/MAX(1,(('Scenario Controls'!$B$14*AVERAGE('Expense Forecast'!$B$8:$Y$8)+'Scenario Controls'!$B$15+'Scenario Controls'!$B$16)-(('Scenario Controls'!$B$6+24*'Scenario Controls'!$B$8*${growthFactor}-12*'Scenario Controls'!$B$6*'Scenario Controls'!$B$9*${churnFactor})*'Scenario Controls'!$B$7*'Scenario Controls'!$B$12))))`,
      ]];
    }
  }
  styleTableHeader(sheet.getRange("A5:F5"));
  sheet.getRange("A6:A10").format = { fill: "#F8FAFC", font: { bold: true } };
}

function buildDashboard(sheet, months) {
  styleTitle(sheet, "A1:H1", "Executive Dashboard");
  sheet.getRange("A3:H3").values = [["Selected Scenario", "MRR", "ARR", "Ending Cash", "Runway", "Burn", "CAC Payback", "Headcount"]];
  sheet.getRange("A4:H4").formulas = [[
    "='Scenario Controls'!$B$3",
    "='Cash Flow'!Y4",
    "='Revenue Forecast'!Y10",
    "='Cash Flow'!Y8",
    "='Cash Flow'!Y9",
    "='Cash Flow'!Y7",
    "='Cash Flow'!Y12",
    "='Cash Flow'!Y11",
  ]];
  sheet.getRange("A7:D31").values = [["Month", "MRR", "Ending Cash", "Net Burn"], ...months.map(() => [null, null, null, null])];
  for (let index = 0; index < 24; index += 1) {
    const sourceCol = colName(index + 1);
    const row = index + 8;
    sheet.getRange(`A${row}`).formulas = [[`=TEXT('Cash Flow'!${sourceCol}3,"mmm yyyy")`]];
    sheet.getRange(`B${row}`).formulas = [[`='Cash Flow'!${sourceCol}4`]];
    sheet.getRange(`C${row}`).formulas = [[`='Cash Flow'!${sourceCol}8`]];
    sheet.getRange(`D${row}`).formulas = [[`='Cash Flow'!${sourceCol}7`]];
  }
  sheet.getRange("F7:H31").values = [["Month", "Headcount", "ARR"], ...months.map(() => [null, null, null])];
  for (let index = 0; index < 24; index += 1) {
    const sourceCol = colName(index + 1);
    const row = index + 8;
    sheet.getRange(`F${row}`).formulas = [[`=TEXT('Cash Flow'!${sourceCol}3,"mmm yyyy")`]];
    sheet.getRange(`G${row}`).formulas = [[`='Cash Flow'!${sourceCol}11`]];
    sheet.getRange(`H${row}`).formulas = [[`='Revenue Forecast'!${sourceCol}10`]];
  }
}

function buildChecks(sheet) {
  styleTitle(sheet, "A1:E1", "Validation Checks");
  sheet.getRange("A3:B3").values = [["MODEL STATUS", null]];
  sheet.getRange("B3").formulas = [["=IF(COUNTIF(B6:B10,\"FAIL\")=0,\"PASS\",\"FAIL\")"]];
  sheet.getRange("A5:E5").values = [["Check", "Status", "Delta", "Where to fix", "Notes"]];
  sheet.getRange("A6:E10").values = [
    ["Scenario is valid", null, null, "Scenario Controls!B3", "Selected scenario must exist in Assumptions."],
    ["Assumptions are populated", null, null, "Assumptions", "Required scenario input cells cannot be blank."],
    ["Customer roll-forward ties", null, null, "Revenue Forecast", "Ending customers must equal beginning + new - churned."],
    ["Cash roll-forward ties", null, null, "Cash Flow", "Ending cash must reconcile from starting cash and monthly burn."],
    ["Ending cash remains positive", null, null, "Cash Flow", "Flag if forecast cash goes below zero."],
  ];
  sheet.getRange("B6").formulas = [["=IF(COUNTIF('Assumptions'!$A$4:$A$6,'Scenario Controls'!$B$3)=1,\"PASS\",\"FAIL\")"]];
  sheet.getRange("C6").formulas = [["=COUNTIF('Assumptions'!$A$4:$A$6,'Scenario Controls'!$B$3)-1"]];
  sheet.getRange("B7").formulas = [["=IF(COUNTBLANK('Scenario Controls'!$B$5:$B$16)=0,\"PASS\",\"FAIL\")"]];
  sheet.getRange("C7").formulas = [["=COUNTBLANK('Scenario Controls'!$B$5:$B$16)"]];
  sheet.getRange("B8").formulas = [["=IF(ABS(C8)<1,\"PASS\",\"FAIL\")"]];
  sheet.getRange("C8").formulas = [["=SUM('Revenue Forecast'!B7:Y7-('Revenue Forecast'!B4:Y4+'Revenue Forecast'!B5:Y5-'Revenue Forecast'!B6:Y6))"]];
  sheet.getRange("B9").formulas = [["=IF(ABS(C9)<1,\"PASS\",\"FAIL\")"]];
  sheet.getRange("C9").formulas = [["='Cash Flow'!B8-('Scenario Controls'!$B$5-'Cash Flow'!B7)+SUM('Cash Flow'!C8:Y8-('Cash Flow'!B8:X8-'Cash Flow'!C7:Y7))"]];
  sheet.getRange("B10").formulas = [["=IF(C10>=0,\"PASS\",\"FAIL\")"]];
  sheet.getRange("C10").formulas = [["=MIN('Cash Flow'!B8:Y8)"]];
  styleTableHeader(sheet.getRange("A5:E5"));
}

function formatModelSheets(sheets) {
  for (const sheet of Object.values(sheets)) {
    const used = sheet.getUsedRange();
    if (used) {
      used.format.font = { name: "Aptos", size: 10 };
      used.format.autofitRows();
    }
  }

  const assumptions = sheets.Assumptions;
  assumptions.getRange("B4:B6").format.numberFormat = "$#,##0";
  assumptions.getRange("C4:D6").format.numberFormat = "#,##0";
  assumptions.getRange("E4:E6").format.numberFormat = "#,##0";
  assumptions.getRange("F4:H6").format.numberFormat = "0.0%";
  assumptions.getRange("I4:I6").format.numberFormat = "0.0%";
  assumptions.getRange("J4:M6").format.numberFormat = "$#,##0";

  const actuals = sheets["Historical Actuals"];
  actuals.getRange("A4:A9").format.numberFormat = "yyyy-mm-dd";
  actuals.getRange("B4:B9").format.numberFormat = "#,##0";
  actuals.getRange("C4:D9").format.numberFormat = "$#,##0";
  actuals.getRange("E4:E9").format.numberFormat = "0.0%";
  actuals.getRange("F4:I9").format.numberFormat = "$#,##0";

  const hiring = sheets["Hiring Plan"];
  hiring.getRange("A4:A27").format.numberFormat = "yyyy-mm-dd";
  hiring.getRange("B4:E27").format.numberFormat = "#,##0";

  const controls = sheets["Scenario Controls"];
  controls.getRange("B5:B7").format.numberFormat = "$#,##0";
  controls.getRange("B8:B8").format.numberFormat = "#,##0";
  controls.getRange("B9:B12").format.numberFormat = "0.0%";
  controls.getRange("B13:B16").format.numberFormat = "$#,##0";

  const revenue = sheets["Revenue Forecast"];
  styleTableHeader(revenue.getRange("A3:Y3"));
  revenue.getRange("A4:A12").format = { fill: "#F8FAFC", font: { bold: true } };
  revenue.getRange("B4:Y7").format.numberFormat = "#,##0";
  revenue.getRange("B8:Y10").format.numberFormat = "$#,##0";
  revenue.getRange("B11:Y11").format.numberFormat = "0.0%";
  revenue.getRange("B12:Y12").format.numberFormat = "$#,##0";
  revenue.freezePanes.freezeRows(3);
  revenue.freezePanes.freezeColumns(1);

  const expense = sheets["Expense Forecast"];
  styleTableHeader(expense.getRange("A3:Y3"));
  expense.getRange("A4:A13").format = { fill: "#F8FAFC", font: { bold: true } };
  expense.getRange("B4:Y8").format.numberFormat = "#,##0";
  expense.getRange("B9:Y13").format.numberFormat = "$#,##0";
  expense.freezePanes.freezeRows(3);
  expense.freezePanes.freezeColumns(1);

  const cash = sheets["Cash Flow"];
  styleTableHeader(cash.getRange("A3:Y3"));
  cash.getRange("A4:A12").format = { fill: "#F8FAFC", font: { bold: true } };
  cash.getRange("B4:Y8").format.numberFormat = "$#,##0";
  cash.getRange("B9:Y9").format.numberFormat = "0.0";
  cash.getRange("B10:Y10").format.numberFormat = "0.0%";
  cash.getRange("B11:Y11").format.numberFormat = "#,##0";
  cash.getRange("B12:Y12").format.numberFormat = "0.0";
  cash.freezePanes.freezeRows(3);
  cash.freezePanes.freezeColumns(1);

  const sensitivity = sheets["Sensitivity Analysis"];
  sensitivity.getRange("B6:F10").format.numberFormat = "0.0";
  sensitivity.getRange("A3:F3").format.wrapText = true;

  const dashboard = sheets.Dashboard;
  dashboard.getRange("A3:H3").format = { fill: "#111827", font: { bold: true, color: "#FFFFFF" } };
  dashboard.getRange("A4:H4").format = { fill: "#ECFEFF", font: { bold: true, size: 13 } };
  dashboard.getRange("B4:D4").format.numberFormat = "$#,##0";
  dashboard.getRange("E4:E4").format.numberFormat = "0.0";
  dashboard.getRange("F4:F4").format.numberFormat = "$#,##0";
  dashboard.getRange("G4:G4").format.numberFormat = "0.0";
  dashboard.getRange("H4:H4").format.numberFormat = "#,##0";
  dashboard.getRange("A7:D31").format.numberFormat = "$#,##0";
  dashboard.getRange("A8:A31").format.numberFormat = "mmm yyyy";
  dashboard.getRange("F8:F31").format.numberFormat = "mmm yyyy";
  dashboard.getRange("G8:G31").format.numberFormat = "#,##0";
  dashboard.getRange("H8:H31").format.numberFormat = "$#,##0";
  styleTableHeader(dashboard.getRange("A7:D7"));
  styleTableHeader(dashboard.getRange("F7:H7"));

  const checks = sheets["Validation Checks"];
  checks.getRange("A3:B3").format = { fill: "#FEF3C7", font: { bold: true, size: 13 } };
  checks.getRange("C6:C10").format.numberFormat = "#,##0.0";
  checks.getRange("E6:E10").format.wrapText = true;
  checks.getRange("A:E").format.autofitColumns();
  checks.getRange("E:E").format.columnWidth = 52;
}

async function createCharts(sheets) {
  const dashboard = sheets.Dashboard;
  dashboard.deleteAllDrawings();

  const mrrChart = dashboard.charts.add("line", { chartType: "line", title: "MRR Trend ($)", hasLegend: false });
  const mrrSeries = mrrChart.series.add("MRR");
  mrrSeries.categoryFormula = "'Dashboard'!$A$8:$A$31";
  mrrSeries.formula = "'Dashboard'!$B$8:$B$31";
  mrrChart.title = "MRR Trend ($)";
  mrrChart.hasLegend = false;
  mrrChart.xAxis = { axisType: "textAxis", tickLabelInterval: 3, textStyle: { fontSize: 8 } };
  mrrChart.yAxis = { numberFormatCode: "$#,##0" };
  mrrChart.setPosition("J3", "Q17");

  const cashChart = dashboard.charts.add("line", { chartType: "line", title: "Ending Cash Trend ($)", hasLegend: false });
  const cashSeries = cashChart.series.add("Ending Cash");
  cashSeries.categoryFormula = "'Dashboard'!$A$8:$A$31";
  cashSeries.formula = "'Dashboard'!$C$8:$C$31";
  cashChart.title = "Ending Cash Trend ($)";
  cashChart.hasLegend = false;
  cashChart.xAxis = { axisType: "textAxis", tickLabelInterval: 3, textStyle: { fontSize: 8 } };
  cashChart.yAxis = { numberFormatCode: "$#,##0" };
  cashChart.setPosition("J19", "Q33");

  const burnChart = dashboard.charts.add("bar", { chartType: "bar", title: "Monthly Net Burn ($)", hasLegend: false });
  const burnSeries = burnChart.series.add("Net Burn");
  burnSeries.categoryFormula = "'Dashboard'!$A$8:$A$31";
  burnSeries.formula = "'Dashboard'!$D$8:$D$31";
  burnChart.title = "Monthly Net Burn ($)";
  burnChart.hasLegend = false;
  burnChart.xAxis = { axisType: "textAxis", tickLabelInterval: 3, textStyle: { fontSize: 8 } };
  burnChart.yAxis = { numberFormatCode: "$#,##0" };
  burnChart.setPosition("R3", "Y17");

  const headcountChart = dashboard.charts.add("line", { chartType: "line", title: "Headcount Plan (FTE)", hasLegend: false });
  const headcountSeries = headcountChart.series.add("Headcount");
  headcountSeries.categoryFormula = "'Dashboard'!$F$8:$F$31";
  headcountSeries.formula = "'Dashboard'!$G$8:$G$31";
  headcountChart.title = "Headcount Plan (FTE)";
  headcountChart.hasLegend = false;
  headcountChart.xAxis = { axisType: "textAxis", tickLabelInterval: 3, textStyle: { fontSize: 8 } };
  headcountChart.yAxis = { numberFormatCode: "#,##0" };
  headcountChart.setPosition("R19", "Y33");
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
