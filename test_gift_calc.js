// Unit tests for gift_calc.js (run with: node test_gift_calc.js)
const gc = require("./gift_calc.js");
// gift_calc.js uses global functions, not module.exports. Load via eval in global context.
const fs = require("fs");
const code = fs.readFileSync("./gift_calc.js", "utf8");
eval(code);

let passed = 0, failed = 0;
function assert(cond, msg) { if (!cond) { console.error("FAIL:", msg); failed++; } else { passed++; } }
function throws(fn, msg) { try { fn(); console.error("FAIL (no throw):", msg); failed++; } catch(e) { passed++; } }

// official example
const inputs = [
  { unique_id:"g1", base_gift_id:1, craft_chance_permille:100, attributes:[{type:"backdrop",id:"green"}] },
  { unique_id:"g2", base_gift_id:1, craft_chance_permille:100, attributes:[{type:"backdrop",id:"green"}] },
  { unique_id:"g3", base_gift_id:1, craft_chance_permille:100, attributes:[{type:"backdrop",id:"black"}] }
];
const cfg = [[100],[100,200],[60,180,450],[100,200,300,400]];
const probs = computeAttributePersistence(inputs, cfg);
assert(probs.backdrop.green === 0.18, "green 18%");
assert(probs.backdrop.black === 0.06, "black 6%");

// craft success
const r = computeCraftSuccess([{unique_id:"g1",base_gift_id:1,craft_chance_permille:300,attributes:[]},{unique_id:"g2",base_gift_id:1,craft_chance_permille:400,attributes:[]}]);
assert(r.totalPermille === 700, "total 700");
assert(r.successProb === 0.7, "prob 0.7");
assert(r.uiPct === 70, "ui 70");

// validation
throws(() => computeCraftSuccess([]), "empty inputs");
throws(() => computeCraftSuccess([{unique_id:"g1",base_gift_id:1,craft_chance_permille:100,attributes:[]},{unique_id:"g2",base_gift_id:2,craft_chance_permille:100,attributes:[]}]), "different base");
throws(() => computeCraftSuccess([{unique_id:"g1",base_gift_id:1,craft_chance_permille:-1,attributes:[]}]), "negative permille");
throws(() => computeCraftSuccess([{unique_id:"g1",base_gift_id:1,craft_chance_permille:1001,attributes:[]}]), "permille >1000");

// fee impact
const fee = computeFeeImpact(100, 120, 5, 5, 1);
assert(fee.profitable === true, "fee profitable");
const fee2 = computeFeeImpact(100, 105, 10, 10, 2);
assert(fee2.profitable === false, "fee loss");

// market stats
const ms = marketStats([10,20,30,40]);
assert(ms.median === 25, "median 25");
assert(ms.mean === 25, "mean 25");
throws(() => marketStats([]), "empty prices");

console.log(`\nJS tests: ${passed} passed, ${failed} failed`);
if (failed > 0) process.exit(1);