"""Authenticated Windows individual installation; never a public deployment."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import uuid

# -I omits the script directory; add only this trusted bootstrap directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import auth_release as auth
import local_installation as local
from backend_bundle import clean_environment, install_runtime, runtime_fingerprint, verify_runtime


def prepare_runtime(root, version, python_executable):
    directory, _, _, _ = auth.verify_version(root, version)
    fingerprint = runtime_fingerprint(directory)
    with local.writer(root) as base:
        runtimes = local.no_links(base / "runtimes")
        runtimes.mkdir(exist_ok=True)
        target = local.no_links(runtimes / fingerprint)
        if target.exists():
            return verify_runtime(target, fingerprint)
        # Interrupted bootstrap is kept separately and never poisons a final
        # runtime name or the active release. No patient data exists here.
        stage = base / ("runtime-stage-" + uuid.uuid4().hex)
        install_runtime(directory, stage, python_executable)
        os.replace(stage, target)
        return verify_runtime(target, fingerprint)


def _serve(root, expected_version):
    from stable_launcher import make_stable_server
    from backend_runtime import BackendSession
    local.require(sys.stdin.buffer.readline(16) == b"START\n", "Authenticated server requires its supervised parent gate")
    directory, manifest, _, selected = auth.active_signed_snapshot(root)
    local.require(selected["version"] == expected_version, "Active release changed; restart explicitly")
    local.require(os.path.samefile(Path(__file__).parent, directory / "backend/launcher"), "Run the authenticated release bootstrap")
    runtime = Path(root) / "runtimes" / runtime_fingerprint(directory)
    python = verify_runtime(runtime, runtime_fingerprint(directory))
    with make_stable_server(root, verify_release=auth.active_signed_snapshot,
                            backend_factory=lambda d, p, r: BackendSession(d, p, r, python_executable=python)) as server:
        def stop_on_parent_exit():
            while sys.stdin.buffer.read(1):
                pass
            server.shutdown()
        threading.Thread(target=stop_on_parent_exit, daemon=True).start()
        print(json.dumps({"url": f"http://127.0.0.1:{server.server_port}", "version": selected["version"],
                          "source_sha": manifest["source_sha"], "clinical": "CLINICALLY_PENDING", "release": "NO_GO_CLINICAL_RELEASE"}), flush=True)
        server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("publisher-init")
    build = commands.add_parser("build")
    for name in ("dist", "source-root", "wheelhouse", "output", "private-key"):
        build.add_argument("--" + name, required=True)
    build.add_argument("--release-counter", required=True, type=int)
    receive = commands.add_parser("install")
    receive.add_argument("--archive", required=True)
    receive.add_argument("--signature", required=True)
    receive.add_argument("--publisher-file")
    receive.add_argument("--expected-publisher-fingerprint")
    receive.add_argument("--python", default=sys.executable)
    receive.add_argument("--for-rollback", action="store_true")
    prepare = commands.add_parser("prepare-runtime")
    prepare.add_argument("--version", required=True)
    prepare.add_argument("--python", default=sys.executable)
    for name in ("activate", "rollback"):
        commands.add_parser(name).add_argument("--version", required=True)
    commands.add_parser("serve")
    private = commands.add_parser("_serve", help=argparse.SUPPRESS)
    private.add_argument("--expected-version", required=True)
    for name, command in commands.choices.items():
        if name not in {"publisher-init", "build"}:
            command.add_argument("--root", required=True)
    args = parser.parse_args()
    if args.command == "publisher-init":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "Emergency/PublisherSigning/individual-v1"
        result = auth.create_publisher(base)
        result.pop("private_key_path", None)
    elif args.command == "build":
        result = auth.build_signed(args.dist, args.source_root, args.wheelhouse, args.output, args.release_counter, args.private_key)
    elif args.command == "install":
        local.require(bool(args.publisher_file) == bool(args.expected_publisher_fingerprint), "Publisher and independently trusted fingerprint must be provided together")
        result = auth.install_signed(args.archive, args.signature, args.root,
            publisher_file=args.publisher_file, fingerprint=args.expected_publisher_fingerprint, for_rollback=args.for_rollback)
        python = prepare_runtime(args.root, result["version"], args.python)
        result.update(runtime_python=str(python), activated=False)
    elif args.command == "prepare-runtime":
        result = {"python": str(prepare_runtime(args.root, args.version, args.python))}
    elif args.command in {"activate", "rollback"}:
        result = auth.activate_signed(args.root, args.version, rollback=args.command == "rollback")
    elif args.command == "serve":
        directory, _, _, selected = auth.active_signed_snapshot(args.root)
        fingerprint = runtime_fingerprint(directory)
        python = verify_runtime(Path(args.root) / "runtimes" / fingerprint, fingerprint)
        command = [str(python), "-I", "-B", str(directory / "backend/launcher/individual_cli.py"),
                   "_serve", "--root", str(Path(args.root).resolve()), "--expected-version", selected["version"]]
        # No provider credentials or proxy configuration are inherited. The
        # server waits on a private stdio gate until assigned to our kill-on-close
        # job; its own backend child is supervised independently as well.
        from backend_runtime import _WindowsChildJob
        process = subprocess.Popen(command, env=clean_environment(), stdin=subprocess.PIPE,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        job = None
        try:
            job = _WindowsChildJob(process) if os.name == "nt" else None
            process.stdin.write(b"START\n")
            process.stdin.flush()
            return process.wait()
        finally:
            if process.stdin and not process.stdin.closed:
                process.stdin.close()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            if job:
                job.close()
    else:
        _serve(args.root, args.expected_version)
        return 0
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(0)
    except (local.ReleaseError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps({"status": "operation_rejected", "reason_type": type(error).__name__,
                          "clinical": "CLINICALLY_PENDING", "release": "NO_GO_CLINICAL_RELEASE"}), file=sys.stderr)
        raise SystemExit(1)
