const fs = require("fs");
const path = require("path");

const buildPath = path.join(__dirname, "build/static/js");
const outputPath = path.join(__dirname, "build/widget.js");

const files = fs.readdirSync(buildPath);
const jsFile = files.find(
  (file) => file.endsWith(".js") && file.startsWith("main.")
);

if (jsFile) {
  fs.copyFileSync(path.join(buildPath, jsFile), outputPath);
  console.log("✅ Skopiowano:", jsFile, "-> widget.js");
} else {
  console.error("❌ Nie znaleziono pliku JavaScript w build/static/js/");
}
