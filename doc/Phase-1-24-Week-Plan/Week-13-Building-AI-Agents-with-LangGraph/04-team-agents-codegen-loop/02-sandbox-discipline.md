# Sandbox Discipline — Subprocess and Container Hardening

**What you'll learn:** generated code runs in a sandbox — always. The
subprocess pattern with hard limits, the container upgrade, and the
escape-drill that proves the walls.

## 1. The subprocess pattern (minimum viable)

```python
import subprocess

def run_in_sandbox(code: str, test_code: str, timeout_s: int = 30) -> "Result":
    payload = code + "\n\n" + test_code
    proc = subprocess.run(
        ["python", "-c", payload],
        capture_output=True, text=True,
        timeout=timeout_s,
        cwd="data/sandbox",                  # disposable cwd
        env={"PATH": "/usr/bin:/bin"},       # minimal env: no secrets
    )
    return Result(returncode=proc.returncode,
                  stdout=proc.stdout[-2000:], stderr=proc.stderr[-1000:])
```

| Limit | Why |
|---|---|
| `timeout` | runaway loops die |
| disposable `cwd` | generated code writes junk somewhere safe |
| minimal `env` | no API keys, no tokens in the child |
| output caps | a 2 GB stdout cannot OOM your host |

The subprocess is the *minimum*: it isolates the filesystem view and the
environment, but not the network or the kernel. Good enough for
plan/write/test on trusted-adjacent corpora; not good enough for
user-submitted code.

## 2. The container upgrade (when the code is truly untrusted)

```python
DOCKER_RUN = [
    "docker", "run", "--rm",
    "--network", "none",             # no egress
    "--memory", "512m",
    "--cpus", "1",
    "--read-only",
    "--cap-drop", "ALL",
    "-v", f"{sandbox_dir}:/sandbox:ro",
    "-w", "/sandbox",
    "python:3.12-slim",
    "python", "-c", payload,
]
```

| Flag | Closes |
|---|---|
| `--network none` | exfiltration, C2 |
| `--memory/--cpus` | resource bombs |
| `--read-only` + ro mount | host writes |
| `--cap-drop ALL` | privilege games |

The container is the W10 read-only-first posture, kernel-enforced. The
cost is ~1–3 s per run — acceptable inside a repair loop bounded at 4
attempts.

## 3. The escape drill (proving the walls)

```python
ESCAPE_PROBES = [
    "import os; os.system('curl https://evil.example')",   # network
    "open('/etc/passwd').read()",                           # host read
    "while True: pass",                                     # cpu bomb
    "open('/sandbox/../escape.txt','w')",                   # path escape
]

@pytest.mark.parametrize("probe", ESCAPE_PROBES)
def test_sandbox_contains(probe):
    result = run_in_sandbox(probe, "assert True")
    assert result.contained        # no egress, no host read, killed, or jailed
```

The drill runs *deliberately malicious* generated code through your
sandbox and asserts containment. It runs in CI like any other test —
the walls are only walls if they are tested.

## 4. The discipline rules

```text
[ ] generated code never runs in the host interpreter
[ ] every sandbox run has a timeout and output caps
[ ] env is minimal; secrets never cross the boundary
[ ] the escape drill is in CI
[ ] sandbox artifacts (stdout/files) are quarantined, not trusted
```

## Exercises

1. Build the subprocess sandbox; run the four escape probes; document
   which walls hold and which need the container.
2. Container drill: upgrade to Docker; rerun the probes; measure the
   per-run overhead vs the subprocess sandbox.
3. Integration drill: wire the sandbox into the repair graph's test
   node; verify the loop handles a code-bomb probe as "test failed" and
   repairs or exits.