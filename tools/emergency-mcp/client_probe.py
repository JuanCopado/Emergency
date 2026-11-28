"""Trusted-operator MCP stdio probe; no configuration edits or secret echo."""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import time
from mcp import Client, StdioServerParameters

async def probe(spec):
    started = time.monotonic()
    parameters = StdioServerParameters(command=spec["command"], args=spec.get("args", []),
                                       env=spec.get("env"), cwd=spec.get("cwd"))
    async with Client(parameters, read_timeout_seconds=45) as client:
        listed = await client.list_tools()
        rows = [{"name": tool.name, "annotations": tool.annotations.model_dump() if tool.annotations else None,
                 "input_schema_sha256": hashlib.sha256(json.dumps(tool.input_schema, sort_keys=True).encode()).hexdigest()}
                for tool in listed.tools]
        calls = []
        for call in spec.get("calls", []):
            result = await client.call_tool(call["name"], call.get("arguments", {}))
            raw = result.model_dump(mode="json")
            encoded = json.dumps(raw, sort_keys=True).encode()
            row = {"tool": call["name"], "is_error": result.is_error,
                   "response_bytes": len(encoded), "response_sha256": hashlib.sha256(encoded).hexdigest()}
            if spec.get("include_responses") is True:
                row["response"] = raw
            calls.append(row)
        info = client.server_info.model_dump(mode="json") if client.server_info else None
        return {"initialize": "PASS", "server_info": info, "tools": rows, "calls": calls,
                "elapsed_ms": round((time.monotonic()-started)*1000, 3),
                "credentials_or_environment_echoed": False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8-sig"))
    result = asyncio.run(probe(spec))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf8")
    print(json.dumps({"initialize": result["initialize"], "tools": len(result["tools"]),
                      "calls": [{"tool": row["tool"], "is_error": row["is_error"]} for row in result["calls"]]}))

if __name__ == "__main__":
    main()
