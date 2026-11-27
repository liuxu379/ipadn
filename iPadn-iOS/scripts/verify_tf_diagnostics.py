#!/usr/bin/env python3
"""Compile and test the actual Foundation-only diagnostic formatter without iOS SDK."""
from pathlib import Path
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / "TestFlightKit/TFLogin.swift").read_text()
match = re.search(r"^    static func safeAuthResponseSummary\(_ data: Data\) -> String \{\n.*?^    \}", source, re.M | re.S)
if not match:
    raise SystemExit("Cannot locate diagnostic formatter")
tests = r'''
func check(_ condition: @autoclosure () -> Bool, _ message: String) {
    guard condition() else { fatalError(message) }
}
check(Probe.safeAuthResponseSummary(Data()) == "format=empty", "empty")
check(Probe.safeAuthResponseSummary(Data("{}\n".utf8)).contains("shape=dict"), "empty dict")
let fixture: [String: Any] = ["Response": ["Status": ["ec": 0, "au": "hsa2"], "token": "SECRET_FIXTURE"]]
let plist = try PropertyListSerialization.data(fromPropertyList: fixture, format: .xml, options: 0)
let summary = Probe.safeAuthResponseSummary(plist)
check(summary.contains("businessStatus=zero") && summary.contains("challenge=hsa2"), "plist")
check(!summary.contains("SECRET_FIXTURE"), "redaction")
let unknown = Probe.safeAuthResponseSummary(Data(#"{"Response":{"Status":{"ec":"SECRET_CODE","au":"SECRET_CHALLENGE"},"serviceErrors":[{"message":"SECRET_MSG"}]}}"#.utf8))
check(unknown.contains("businessStatus=present") && unknown.contains("challenge=other") && unknown.contains("serviceErrors=1"), "unknown")
check(!unknown.contains("SECRET_"), "unknown redaction")
check(Probe.safeAuthResponseSummary(Data(repeating: 0, count: 262145)) == "format=oversize", "limit")
check(Probe.safeAuthResponseSummary(Data([0xff, 0, 1])) == "format=unparsed", "invalid")
let negative = Probe.safeAuthResponseSummary(Data(#"{"ec":-1234}"#.utf8))
check(negative.contains("businessStatus=nonzero") && !negative.contains("1234"), "negative")
print("Diagnostic formatter fixtures passed")
'''
with tempfile.TemporaryDirectory(prefix="tf-diagnostics-") as temp:
    folder = Path(temp)
    swift = folder / "main.swift"
    swift.write_text("import Foundation\nenum Probe {\n" + match.group(0) + "\n}\n" + tests)
    exe = folder / "probe"
    subprocess.run(["swiftc", str(swift), "-o", str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
