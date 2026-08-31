const http = require("http");
const fs = require("fs");
const path = require("path");

const distDir = path.join(__dirname, "dist");
const port = Number(process.env.PORT) || 8080;

const contentTypes = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".ico": "image/x-icon",
  ".webp": "image/webp",
};

const server = http.createServer((req, res) => {
  const requestPath = decodeURIComponent((req.url || "/").split("?")[0]);
  const relativePath =
    requestPath === "/" ? "index.html" : requestPath.replace(/^\/+/, "");

  let filePath = path.join(distDir, relativePath);

  if (!filePath.startsWith(distDir)) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }

  if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    filePath = path.join(distDir, "index.html");
  }

  fs.readFile(filePath, (error, data) => {
    if (error) {
      res.writeHead(500);
      res.end("Internal Server Error");
      return;
    }

    const extension = path.extname(filePath).toLowerCase();

    res.writeHead(200, {
      "Content-Type": contentTypes[extension] || "application/octet-stream",
    });
    res.end(data);
  });
});

server.listen(port, "0.0.0.0", () => {
  console.log(`D.AI.SY frontend listening on port ${port}`);
});