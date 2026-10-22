"""Local Gift Crafting Optimizer web app (no external deps)."""
import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gift_calc

INDEX = os.path.join(HERE, "index.html")


def parse_scenario(s):
    # s: dict with keys base_gift_id, inputs: list of {permille, patterns:[], backdrops:[]}, config: list[list[int]]
    base = int(s["base_gift_id"])
    inputs = []
    for inp in s["inputs"]:
        attrs = []
        for pid in inp.get("patterns", []):
            attrs.append({"type": "pattern", "id": pid})
        for bid in inp.get("backdrops", []):
            attrs.append({"type": "backdrop", "id": bid})
        inputs.append(gift_calc.CraftInputGift(
            unique_id=inp.get("id", "g"),
            base_gift_id=base,
            craft_chance_permille=int(inp["permille"]),
            attributes=attrs,
        ))
    config = s["config"]
    # validate config shape
    if not (isinstance(config, list) and len(config) >= len(inputs)):
        raise ValueError("config must have at least %d rows" % len(inputs))
    for i in range(len(inputs)):
        row = config[i]
        if not (isinstance(row, list) and len(row) == i + 1):
            raise ValueError("config row %d must have %d entries" % (i, i + 1))
    success = gift_calc.compute_craft_success(inputs)
    attr_probs = gift_calc.compute_attribute_persistence(inputs, config)
    dist = gift_calc.expected_craft_outcome_distribution(inputs, config)
    return {
        "inputs_count": len(inputs),
        "total_permille": success.total_permille,
        "success_probability": success.success_probability,
        "ui_percentage": success.ui_percentage,
        "attribute_persistence": {k: {str(kk): vv for kk, vv in v.items()} for k, v in attr_probs.items()},
        "attribute_groups": {k: {str(kk): vv for kk, vv in v.items()} for k, v in success.attribute_groups.items()},
        "limitations": dist["limitations"],
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self.serve_file(INDEX, "text/html; charset=utf-8")
            return
        if path.startswith("/static/"):
            fpath = os.path.join(HERE, path.lstrip("/"))
            if os.path.isfile(fpath):
                ctype = "text/css" if fpath.endswith(".css") else "application/javascript"
                self.serve_file(fpath, ctype + "; charset=utf-8")
                return
        self.send_error(404)

    def serve_file(self, path, ctype):
        with open(path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if urlparse(self.path).path != "/api/calc":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw.decode("utf-8"))
            scenarios = body.get("scenarios", [])
            if not isinstance(scenarios, list) or not scenarios:
                raise ValueError("scenarios must be a non-empty list")
            results = []
            for sc in scenarios:
                results.append(parse_scenario(sc))
            out = {"ok": True, "results": results}
        except Exception as e:
            out = {"ok": False, "error": str(e)}
        data = json.dumps(out).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = 8765
    httpd = HTTPServer(("127.0.0.1", port), Handler)
    print("Gift Crafting Optimizer running at http://127.0.0.1:%d" % port)
    httpd.serve_forever()