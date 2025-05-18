const path = require("path");
const fs = require("fs");
const XLSX = require("xlsx");
const classifyPOIs = require("../utils/classifyPOIs"); // Adjust path if needed

async function generatePoiScenarioExcel() {
  try {
    const poisPath = path.join(__dirname, "..","data", "POIs", "POI_4815075.geojson");
    if (!fs.existsSync(poisPath)) throw new Error("POI file not found");
    const poiData = JSON.parse(fs.readFileSync(poisPath, "utf8"));

    const streetsNamePath = path.join(__dirname,"..", "data", "STREETS_NAMING_ADDRESSING", "SREETS_NAMING_ADDRESSING_4815075.geojson");
    if (!fs.existsSync(streetsNamePath)) throw new Error("Streets Naming file not found");
    const streetsNameData = JSON.parse(fs.readFileSync(streetsNamePath, "utf8"));

    poiData.features = classifyPOIs(poiData.features, streetsNameData.features);

    const grouped = {};
    for (const poi of poiData.features) {
      const scenario = poi.properties._scenario || 1;
      if (!grouped[scenario]) grouped[scenario] = [];
      grouped[scenario].push(poi.properties);
    }

    const wb = XLSX.utils.book_new();
    for (const [scenario, data] of Object.entries(grouped)) {
      const ws = XLSX.utils.json_to_sheet(data);
      XLSX.utils.book_append_sheet(wb, ws, `Scenario_${scenario}`);
    }

    const excelFilePath = path.join(__dirname,"..","data", "POI_Scenarios.xlsx");
    XLSX.writeFile(wb, excelFilePath);
    console.log(`Successfully created ${excelFilePath}`);

  } catch (error) {
    console.error("Error during processing:", error.message);
  }
}

generatePoiScenarioExcel();