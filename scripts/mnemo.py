"""Mnemosyne: bootstrap, continuity and staging CLI for the DE workspace.

The CLI intentionally uses only the Python standard library so it can run before
uv creates the project environment.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import platform
import re
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
import textwrap
import tomllib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

APP = "mnemo"
CONFIG_NAME = "mnemosyne.toml"
DEVICE_FILE = Path(".mnemosyne/device")


class MnemoError(RuntimeError):
    """Expected operational failure with a user-readable message."""


@dataclass
class Result:
    args: list[str]
    returncode: int
    stdout: str = ""
    stderr: str = ""


def info(message: str) -> None:
    print(f"[INFO] {message}")


def ok(message: str) -> None:
    print(f"[ OK ] {message}")


def warn(message: str) -> None:
    print(f"[WARN] {message}", file=sys.stderr)


def command_text(args: Sequence[str]) -> str:
    return shlex.join(str(item) for item in args)


def run(
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    check: bool = False,
    capture: bool = False,
    env: dict[str, str] | None = None,
    announce: bool = True,
) -> Result:
    command = [str(item) for item in args]
    if announce:
        print(f"$ {command_text(command)}")
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        check=False,
    )
    result = Result(
        command,
        completed.returncode,
        completed.stdout or "",
        completed.stderr or "",
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "sin detalle"
        raise MnemoError(f"falló `{command_text(command)}`: {detail}")
    return result


def git(root: Path, args: Sequence[str], **kwargs: Any) -> Result:
    return run(["git", *args], cwd=root, **kwargs)


def load_config(root: Path) -> dict[str, Any]:
    path = root / CONFIG_NAME
    if not path.exists():
        raise MnemoError(f"falta {CONFIG_NAME} en {root}")
    try:
        with path.open("rb") as stream:
            return tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise MnemoError(f"no se pudo leer {path}: {exc}") from exc


def resolve_repo(raw: str | None, *, required: bool = True) -> Path | None:
    start = Path(raw).expanduser().resolve() if raw else Path.cwd().resolve()
    result = run(
        ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
        capture=True,
        announce=False,
    )
    if result.returncode == 0:
        return Path(result.stdout.strip()).resolve()
    if (start / CONFIG_NAME).exists():
        return start
    if required:
        raise MnemoError("ejecuta el comando dentro de andry-de-zoomcamp o usa --repo")
    return None


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def os_release() -> dict[str, str]:
    data: dict[str, str] = {}
    path = Path("/etc/os-release")
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" not in line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        data[key] = value.strip().strip('"')
    return data


def confirm(prompt: str, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        raise MnemoError("la operación requiere confirmación; repite con --yes")
    answer = input(f"{prompt} [y/N]: ").strip().lower()
    return answer in {"y", "yes", "s", "si", "sí"}


def first_line(result: Result) -> str:
    text = (result.stdout or result.stderr).strip()
    return text.splitlines()[0] if text else "sin salida"


def probe(label: str, command: Sequence[str]) -> dict[str, Any]:
    executable = shutil.which(command[0])
    if executable is None:
        return {"name": label, "ok": False, "detail": "no instalado"}
    result = run(command, capture=True, announce=False)
    return {
        "name": label,
        "ok": result.returncode == 0,
        "detail": first_line(result),
    }


def compose_probe() -> dict[str, Any]:
    if shutil.which("docker") is None:
        return {"name": "Docker Compose", "ok": False, "detail": "docker no instalado"}
    result = run(["docker", "compose", "version"], capture=True, announce=False)
    return {
        "name": "Docker Compose",
        "ok": result.returncode == 0,
        "detail": first_line(result),
    }


def detect_device(root: Path, config: dict[str, Any]) -> tuple[str, str]:
    local_file = root / DEVICE_FILE
    selected = local_file.read_text(encoding="utf-8").strip() if local_file.exists() else ""
    devices = config.get("devices", {})
    if selected and selected in devices:
        return selected, str(devices[selected].get("role", "unknown"))

    hostname = socket.gethostname().lower()
    for name, details in devices.items():
        candidates = [str(item).lower() for item in details.get("hostnames", [])]
        if hostname in candidates:
            return str(name), str(details.get("role", "unknown"))
    return socket.gethostname(), "unregistered"


def cmd_device(args: argparse.Namespace) -> int:
    root = resolve_repo(args.repo)
    assert root is not None
    config = load_config(root)
    devices = config.get("devices", {})
    if args.action == "show":
        name, role = detect_device(root, config)
        print(f"Nodo: {name}\nRol: {role}\nHostname: {socket.gethostname()}")
        return 0

    if args.name not in devices:
        choices = ", ".join(devices) or "ninguno configurado"
        raise MnemoError(f"nodo desconocido `{args.name}`; opciones: {choices}")
    path = root / DEVICE_FILE
    atomic_write(path, f"{args.name}\n")
    ok(f"nodo local registrado como {args.name}")
    return 0


def git_status(root: Path) -> str:
    result = git(root, ["status", "--short", "--branch"], capture=True, announce=False)
    if result.returncode != 0:
        raise MnemoError(result.stderr.strip() or "no se pudo leer git status")
    return result.stdout.rstrip()


def git_dirty(root: Path) -> bool:
    result = git(root, ["status", "--porcelain"], capture=True, announce=False)
    return bool(result.stdout.strip())


def repository_in_progress(root: Path) -> list[str]:
    markers = {
        "merge": "MERGE_HEAD",
        "rebase": "rebase-merge",
        "rebase aplicado": "rebase-apply",
        "cherry-pick": "CHERRY_PICK_HEAD",
        "revert": "REVERT_HEAD",
    }
    active: list[str] = []
    for label, marker in markers.items():
        result = git(
            root,
            ["rev-parse", "--git-path", marker],
            capture=True,
            announce=False,
        )
        if result.returncode == 0:
            path = Path(result.stdout.strip())
            if not path.is_absolute():
                path = root / path
            if path.exists():
                active.append(label)
    return active


def upstream(root: Path) -> str | None:
    result = git(
        root,
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
        capture=True,
        announce=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def ahead_behind(root: Path) -> tuple[int, int]:
    result = git(
        root,
        ["rev-list", "--left-right", "--count", "HEAD...@{upstream}"],
        capture=True,
        announce=False,
        check=True,
    )
    fields = result.stdout.split()
    if len(fields) != 2:
        raise MnemoError("Git devolvió un conteo ahead/behind inesperado")
    return int(fields[0]), int(fields[1])


def sync_repository(root: Path, *, strict_online: bool = False) -> bool:
    if upstream(root) is None:
        warn("la rama actual no posee upstream; configura origin antes de sincronizar")
        return False

    fetched = git(root, ["fetch", "--prune"], check=False)
    if fetched.returncode != 0:
        message = "no se pudo contactar el remoto; el trabajo local permanece disponible"
        if strict_online:
            raise MnemoError(message)
        warn(message)
        return False

    ahead, behind = ahead_behind(root)
    if ahead and behind:
        raise MnemoError(
            f"la rama divergió ({ahead} commits locales, {behind} remotos); "
            "crea una rama de rescate y revisa el conflicto"
        )
    if behind:
        git(root, ["pull", "--ff-only"], check=True)
    if ahead:
        pushed = git(root, ["push"], check=False)
        if pushed.returncode != 0:
            if strict_online:
                raise MnemoError("el push falló; el commit continúa guardado localmente")
            warn("el push falló; el commit continúa guardado localmente")
            return False
    ok("repositorio sincronizado")
    return True


def cmd_doctor(args: argparse.Namespace) -> int:
    root = resolve_repo(args.repo, required=False)
    release = os_release()
    checks = [
        probe("Git", ["git", "--version"]),
        probe("SSH", ["ssh", "-V"]),
        probe("Docker", ["docker", "--version"]),
        compose_probe(),
        probe("uv", ["uv", "--version"]),
        probe("Terraform", ["terraform", "version"]),
        probe("Neovim", ["nvim", "--version"]),
        probe("tmux", ["tmux", "-V"]),
        probe("jq", ["jq", "--version"]),
        probe("ripgrep", ["rg", "--version"]),
    ]

    report: dict[str, Any] = {
        "hostname": socket.gethostname(),
        "os": release.get("PRETTY_NAME", platform.system()),
        "architecture": platform.machine(),
        "python": platform.python_version(),
        "checks": checks,
    }
    if root is not None:
        try:
            config = load_config(root)
            name, role = detect_device(root, config)
            report["repository"] = str(root)
            report["device"] = name
            report["role"] = role
            report["git_status"] = git_status(root)
            report["current_exists"] = (root / config["project"]["current_file"]).exists()
            report["operation_in_progress"] = repository_in_progress(root)
        except MnemoError as exc:
            report["repository_error"] = str(exc)

    if shutil.which("docker"):
        docker_info = run(
            ["docker", "info", "--format", "{{.ServerVersion}}"],
            capture=True,
            announce=False,
        )
        report["docker_engine_access"] = docker_info.returncode == 0
        if docker_info.returncode != 0:
            report["docker_engine_detail"] = first_line(docker_info)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Nodo: {report['hostname']}")
        print(f"Sistema: {report['os']}")
        print(f"Arquitectura: {report['architecture']}")
        print(f"Python de arranque: {report['python']}")
        if "device" in report:
            print(f"Identidad Mnemosyne: {report['device']} ({report['role']})")
        print()
        for check in checks:
            marker = "OK" if check["ok"] else "FALTA"
            print(f"{marker:5} {check['name']}: {check['detail']}")
        if "git_status" in report:
            print("\nGit:")
            print(report["git_status"] or "árbol limpio")
        if report.get("operation_in_progress"):
            warn("operación Git inconclusa: " + ", ".join(report["operation_in_progress"]))

    missing = [check["name"] for check in checks if not check["ok"]]
    if missing and not args.soft:
        return 1
    return 0


def bootstrap_plan(profile: str) -> tuple[str, list[list[str]], list[str]]:
    release = os_release()
    identifiers = {
        release.get("ID", "").lower(),
        *release.get("ID_LIKE", "").lower().split(),
    }
    notes: list[str] = []
    commands: list[list[str]] = []

    if {"arch", "manjaro", "cachyos"} & identifiers:
        packages = [
            "base-devel",
            "git",
            "openssh",
            "docker",
            "docker-compose",
            "uv",
            "terraform",
            "neovim",
            "tmux",
            "jq",
            "ripgrep",
            "make",
            "python",
        ]
        commands.append(["sudo", "pacman", "-Syu", "--needed", *packages])
        notes.append("pacman -Syu puede actualizar el sistema completo para evitar una actualización parcial")
        return "arch", commands, notes

    if {"ubuntu", "debian"} & identifiers:
        packages = [
            "git",
            "openssh-client",
            "tmux",
            "jq",
            "ripgrep",
            "make",
            "neovim",
            "python3",
            "python3-venv",
            "pipx",
        ]
        commands.extend(
            [
                ["sudo", "apt-get", "update"],
                ["sudo", "apt-get", "install", "-y", *packages],
            ]
        )
        if profile == "uranus":
            notes.append("no se reinstalará Docker; Uranus ya lo posee")
        else:
            notes.append(
                "Docker no se instala automáticamente en Debian/Ubuntu; "
                "usa su repositorio oficial si este nodo lo necesita"
            )
        notes.append("si uv falta después de APT, se instalará de forma aislada con pipx")
        if profile == "workstation":
            notes.append("Terraform en Ubuntu requiere el repositorio oficial de HashiCorp y queda fuera de este cambio automático")
        return "debian", commands, notes

    raise MnemoError(
        f"distribución no automatizada: {release.get('PRETTY_NAME', 'desconocida')}; "
        "usa la documentación oficial y actualiza el plan"
    )


def cmd_bootstrap(args: argparse.Namespace) -> int:
    family, commands, notes = bootstrap_plan(args.profile)
    print(f"Perfil: {args.profile}\nFamilia detectada: {family}")
    print("\nPlan:")
    for command in commands:
        print(f"  $ {command_text(command)}")
    for note in notes:
        print(f"  - {note}")
    if args.enable_docker:
        print("  $ sudo systemctl enable --now docker")

    if not args.apply:
        print("\nVista previa. Repite con --apply para instalar.")
        return 0
    if not confirm("¿Aplicar este plan de paquetes?", args.yes):
        info("instalación cancelada")
        return 0

    for command in commands:
        run(command, check=True)

    if family == "debian" and shutil.which("uv") is None:
        run(["pipx", "install", "uv"], check=True)
        run(["pipx", "ensurepath"], check=False)

    uv_path = shutil.which("uv")
    if uv_path is None:
        candidate = Path.home() / ".local" / "bin" / "uv"
        uv_path = str(candidate) if candidate.exists() else None
    if uv_path:
        run([uv_path, "python", "install", "3.12"], check=False)
    else:
        warn("uv todavía no aparece en PATH; abre una terminal nueva y ejecuta `uv python install 3.12`")

    if args.enable_docker:
        run(["sudo", "systemctl", "enable", "--now", "docker"], check=True)
        warn("no se modificó el grupo docker; revisa la política y permisos del nodo")

    ok("bootstrap finalizado; ejecuta `./mnemo doctor`")
    return 0


def cmd_onboard(args: argparse.Namespace) -> int:
    if not args.apply:
        preview = argparse.Namespace(
            profile=args.profile,
            apply=False,
            yes=args.yes,
            enable_docker=args.enable_docker,
        )
        cmd_bootstrap(preview)
        print(
            "\nOrden completa para este nodo:\n"
            f"  ./mnemo onboard {args.name} --profile {args.profile} --apply"
        )
        return 0

    bootstrap_args = argparse.Namespace(
        profile=args.profile,
        apply=True,
        yes=args.yes,
        enable_docker=args.enable_docker,
    )
    cmd_bootstrap(bootstrap_args)
    cmd_device(argparse.Namespace(repo=args.repo, action="set", name=args.name))
    return cmd_start(
        argparse.Namespace(
            repo=args.repo,
            offline=args.offline,
            strict_online=False,
            no_deps=False,
        )
    )


def current_path(root: Path, config: dict[str, Any]) -> Path:
    return root / str(config["project"].get("current_file", "CURRENT.md"))


def show_current(root: Path, config: dict[str, Any]) -> None:
    path = current_path(root, config)
    if not path.exists():
        warn(f"falta {path.name}")
        return
    print(f"\n--- {path.name} ---")
    print(path.read_text(encoding="utf-8").rstrip())
    print(f"--- fin de {path.name} ---")


def cmd_current(args: argparse.Namespace) -> int:
    root = resolve_repo(args.repo)
    assert root is not None
    show_current(root, load_config(root))
    return 0


def sync_dependencies(root: Path) -> None:
    if shutil.which("uv") is None:
        warn("uv no está disponible; ejecuta el bootstrap antes de reconstruir dependencias")
        return
    if (root / "uv.lock").exists():
        run(["uv", "sync", "--locked"], cwd=root, check=True)
    elif (root / "pyproject.toml").exists():
        warn("no existe uv.lock; `uv sync` creará el primer lockfile")
        run(["uv", "sync"], cwd=root, check=True)


def cmd_start(args: argparse.Namespace) -> int:
    root = resolve_repo(args.repo)
    assert root is not None
    config = load_config(root)
    active = repository_in_progress(root)
    if active:
        raise MnemoError("termina primero la operación Git: " + ", ".join(active))

    name, role = detect_device(root, config)
    info(f"iniciando en {name} ({role})")
    dirty = git_dirty(root)
    if dirty:
        warn("hay cambios locales; no se ejecutará pull ni push automático")
        print(git_status(root))
    elif not args.offline:
        sync_repository(root, strict_online=args.strict_online)
    else:
        info("modo offline: se omite el remoto")

    if not args.no_deps:
        sync_dependencies(root)
    show_current(root, config)
    print("\nSiguiente regla: completa un resultado pequeño y verificable antes de abrir otro tema.")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    root = resolve_repo(args.repo)
    assert root is not None
    if repository_in_progress(root):
        raise MnemoError("hay una operación Git inconclusa")
    if git_dirty(root):
        raise MnemoError("el árbol tiene cambios; usa `./mnemo end` o revísalos antes de sincronizar")
    synchronized = sync_repository(root, strict_online=args.strict_online)
    return 0 if synchronized or not args.strict_online else 1


def next_session_id(path: Path) -> str:
    if not path.exists():
        return "S001"
    matches = re.findall(r"\bS(\d{3,})\b", path.read_text(encoding="utf-8"))
    number = max((int(item) for item in matches), default=0) + 1
    return f"S{number:03d}"


def require_field(value: str | None, prompt: str) -> str:
    if value and value.strip():
        return value.strip()
    if not sys.stdin.isatty():
        raise MnemoError(f"falta --{prompt.lower().replace(' ', '-')} en modo no interactivo")
    answer = input(f"{prompt}: ").strip()
    if not answer:
        raise MnemoError(f"{prompt} no puede quedar vacío")
    return answer


def render_current(
    *,
    session: str,
    device: str,
    role: str,
    done: str,
    next_goal: str,
    command: str,
    expected: str,
    notes: str,
    sync_state: str,
) -> str:
    date = dt.datetime.now().astimezone().isoformat(timespec="minutes")
    notes = notes.strip() or "Ninguno registrado."
    return textwrap.dedent(
        f"""\
        # Punto de continuación

        - **Sesión:** {session}
        - **Fecha:** {date}
        - **Nodo:** {device}
        - **Rol:** {role}
        - **Estado de sincronización:** {sync_state}

        ## Último resultado comprobado

        {done}

        ## Próximo objetivo

        {next_goal}

        ## Próximo comando exacto

        ```bash
        {command}
        ```

        ## Resultado esperado

        {expected}

        ## Bloqueos y notas

        {notes}
        """
    )


def changed_paths(root: Path) -> list[str]:
    commands = [
        ["diff", "--name-only", "-z"],
        ["diff", "--cached", "--name-only", "-z"],
        ["ls-files", "--others", "--exclude-standard", "-z"],
    ]
    paths: set[str] = set()
    for command in commands:
        result = git(root, command, capture=True, announce=False, check=True)
        paths.update(item for item in result.stdout.split("\0") if item)
    return sorted(paths)


def forbidden_path(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    parts = [part for part in normalized.split("/") if part]
    name = parts[-1] if parts else normalized
    if any(part in {".venv", "data", "volumes", ".terraform"} for part in parts):
        return True
    if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
        return True
    if name.endswith((".pem", ".key", ".db", ".sqlite", ".sqlite3")):
        return True
    if name.startswith("terraform.tfstate"):
        return True
    if name.endswith(".tfvars") and not name.endswith(".tfvars.example"):
        return True
    return name.endswith(".json") and ("credential" in name or "service-account" in name)


SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(
        r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token)\b\s*[:=]\s*[\"'][^\"'${<]{8,}[\"']"
    ),
]


def scan_changed_files(root: Path, paths: Iterable[str]) -> list[str]:
    findings: list[str] = []
    for raw in paths:
        if forbidden_path(raw):
            findings.append(f"ruta bloqueada: {raw}")
            continue
        path = root / raw
        if not path.exists() or not path.is_file() or path.stat().st_size > 1_000_000:
            continue
        if path.name.endswith(".example"):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(content):
                findings.append(f"posible secreto en {raw}: patrón {pattern.pattern[:35]}…")
                break
    return findings


def run_checks(root: Path, config: dict[str, Any]) -> None:
    commands = config.get("session", {}).get("check_commands", [])
    if not commands:
        warn("no hay comprobaciones configuradas")
        return
    for raw in commands:
        command = shlex.split(str(raw))
        if not command:
            continue
        if shutil.which(command[0]) is None:
            raise MnemoError(f"no se puede ejecutar la comprobación: falta {command[0]}")
        run(command, cwd=root, check=True)


def stage_paths(root: Path, paths: list[str]) -> None:
    if not paths:
        return
    git(root, ["add", "-A", "--", *paths], check=True)


def cmd_end(args: argparse.Namespace) -> int:
    root = resolve_repo(args.repo)
    assert root is not None
    config = load_config(root)
    active = repository_in_progress(root)
    if active:
        raise MnemoError("termina primero la operación Git: " + ", ".join(active))

    device, role = detect_device(root, config)
    path = current_path(root, config)
    session = args.session or next_session_id(path)
    done = require_field(args.done, "done")
    next_goal = require_field(args.next_goal, "next")
    command = require_field(args.command, "command")
    expected = require_field(args.expected, "expected")
    notes = args.notes or ""
    state = "consultar `git status --short --branch`; Git es la autoridad"
    atomic_write(
        path,
        render_current(
            session=session,
            device=device,
            role=role,
            done=done,
            next_goal=next_goal,
            command=command,
            expected=expected,
            notes=notes,
            sync_state=state,
        ),
    )
    ok(f"{path.name} actualizado para {session}")

    if not args.skip_checks:
        run_checks(root, config)

    paths = changed_paths(root)
    findings = scan_changed_files(root, paths)
    if findings:
        for finding in findings:
            warn(finding)
        raise MnemoError("checkpoint cancelado para evitar versionar datos sensibles")

    print("\nArchivos del checkpoint:")
    for item in paths:
        print(f"  {item}")
    if args.no_commit:
        info("cierre documental completado sin commit por --no-commit")
        return 0
    if not confirm("¿Crear el checkpoint y sincronizar cuando sea posible?", args.yes):
        info("CURRENT.md quedó actualizado; no se creó commit")
        return 0

    stage_paths(root, paths)
    staged = git(root, ["diff", "--cached", "--quiet"], announce=False)
    if staged.returncode == 0:
        info("no hay cambios que confirmar")
    else:
        message = args.message or f"study({session}): checkpoint from {device}"
        git(root, ["commit", "-m", message], check=True)

    if args.offline:
        warn("modo offline: el commit queda local; ejecuta `./mnemo sync` cuando haya red")
    else:
        sync_repository(root, strict_online=False)

    print("\nEstado final:")
    print(git_status(root))
    print(f"\nPróximo comando: {command}")
    return 0


def nvim_config_destination() -> Path:
    base = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return base / "mnemosyne-nvim" / "init.lua"


def install_nvim_config(root: Path, *, force: bool = False) -> Path:
    source = root / "tools" / "nvim" / "init.lua"
    if not source.exists():
        raise MnemoError(f"falta la plantilla {source}")
    destination = nvim_config_destination()
    if destination.exists() and destination.read_bytes() == source.read_bytes():
        return destination
    if destination.exists() and not force:
        raise MnemoError(
            f"ya existe {destination}; revísalo o usa `./mnemo edit --force-config` para respaldarlo"
        )
    if destination.exists():
        stamp = dt.datetime.now(dt.UTC).strftime("%Y%m%d-%H%M%S")
        backup = destination.with_name(f"init.lua.backup-{stamp}")
        shutil.copy2(destination, backup)
        warn(f"configuración anterior respaldada en {backup}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    ok(f"configuración aislada instalada en {destination}")
    return destination


def cmd_edit(args: argparse.Namespace) -> int:
    root = resolve_repo(args.repo)
    assert root is not None
    if shutil.which("nvim") is None:
        raise MnemoError("Neovim no está instalado; ejecuta el bootstrap")
    install_nvim_config(root, force=args.force_config)
    env = os.environ.copy()
    env["NVIM_APPNAME"] = "mnemosyne-nvim"
    if args.print_command:
        print(f"NVIM_APPNAME=mnemosyne-nvim nvim {shlex.quote(str(root))}")
        return 0
    os.execvpe("nvim", ["nvim", str(root)], env)
    return 0


def remote_settings(config: dict[str, Any]) -> dict[str, Any]:
    settings = config.get("remote", {})
    required = {"host", "root", "compose_file", "project_name"}
    missing = required - settings.keys()
    if missing:
        raise MnemoError("faltan opciones remotas: " + ", ".join(sorted(missing)))
    root = str(settings["root"])
    if not re.fullmatch(r"~/[A-Za-z0-9_.\-/]+", root):
        raise MnemoError("remote.root debe ser una ruta segura que empiece por ~/")
    return settings


def remote_cd(root: str) -> str:
    suffix = root[2:]
    return f'cd "$HOME/{suffix}"'


def ssh_run(host: str, remote_command: str, *, check: bool = False) -> Result:
    return run(["ssh", host, remote_command], check=check)


def compose_remote_command(settings: dict[str, Any], tail: str) -> str:
    compose = shlex.quote(str(settings["compose_file"]))
    project = shlex.quote(str(settings["project_name"]))
    return (
        f"{remote_cd(str(settings['root']))} && "
        f"docker compose -p {project} -f {compose} --profile datalake {tail}"
    )


def cmd_remote(args: argparse.Namespace) -> int:
    root = resolve_repo(args.repo)
    assert root is not None
    settings = remote_settings(load_config(root))
    host = str(settings["host"])

    if args.action == "tunnel":
        if args.service == "postgres":
            local = int(settings.get("postgres_local_port", 15432))
            remote = int(settings.get("postgres_remote_port", 5432))
            forwards = [f"{local}:127.0.0.1:{remote}"]
        elif args.service == "datalake":
            port = int(settings.get("object_remote_port", 9100))
            console = int(settings.get("object_console_remote_port", 9101))
            forwards = [f"{port}:127.0.0.1:{port}", f"{console}:127.0.0.1:{console}"]
        else:
            raise MnemoError("tunnel requiere `postgres` o `datalake`")
        command = ["ssh", "-N"]
        for forward in forwards:
            command.extend(["-L", forward])
        command.append(host)
        info("abre el túnel; termina con Ctrl-C")
        return run(command).returncode

    if args.action == "status" and args.service == "postgres":
        return ssh_run(host, "ss -lnt", check=False).returncode

    if args.service not in {None, "datalake"}:
        raise MnemoError("solo `datalake` pertenece al Compose de Mnemosyne")

    if args.action == "status":
        tail = "ps"
    elif args.action == "up":
        tail = "up -d objectstore"
    elif args.action == "stop":
        tail = "stop objectstore"
    elif args.action == "logs":
        tail = "logs --tail=100 objectstore"
    else:
        raise MnemoError(f"acción remota desconocida: {args.action}")

    prefix = ""
    if args.action == "up":
        prefix = f"{remote_cd(str(settings['root']))} && git pull --ff-only && "
        command = compose_remote_command(settings, tail)
        command = prefix + command.split(" && ", 1)[1]
    else:
        command = compose_remote_command(settings, tail)
    return ssh_run(host, command, check=args.action in {"up", "stop"}).returncode


def maybe_launch_tui(argv: list[str]) -> int | None:
    """Decide whether to launch the dark TUI.

    Returns int to exit (0 or 1) if TUI handled the invocation,
    or None to continue with normal CLI parsing.
    Guarded so CLI works without textual installed.
    """
    if "--no-tui" in argv:
        return None
    # Wrapper `mnemo` always injects --repo <path>; ignore it for TUI decision
    filtered: list[str] = []
    skip_next = False
    for arg in argv:
        if skip_next:
            skip_next = False
            continue
        if arg == "--repo":
            skip_next = True
            continue
        if arg.startswith("--repo="):
            continue
        filtered.append(arg)
    if filtered:
        return None
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return None
    if importlib.util.find_spec("textual") is None:
        print("TUI not installed — run `uv sync` to enable")
        return 0
    try:
        from mnemo_tui.app import run_tui  # type: ignore[import-not-found]

        return int(run_tui())
    except Exception as exc:  # noqa: BLE001  # pragma: no cover - startup failure path
        print(f"TUI failed to start: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=APP,
        description="Continuidad local-first para andry-de-zoomcamp.",
    )
    parser.add_argument("--repo", help="Ruta del repositorio; por defecto se detecta")
    parser.add_argument("--no-tui", action="store_true", help="Disable TUI and force CLI")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    doctor = subparsers.add_parser("doctor", help="Diagnóstico de solo lectura")
    doctor.add_argument("--json", action="store_true")
    doctor.add_argument("--soft", action="store_true", help="No fallar por herramientas ausentes")
    doctor.set_defaults(handler=cmd_doctor)

    bootstrap = subparsers.add_parser("bootstrap", help="Preparar herramientas del sistema")
    bootstrap.add_argument("--profile", choices=["workstation", "uranus"], default="workstation")
    bootstrap.add_argument("--apply", action="store_true")
    bootstrap.add_argument("--yes", action="store_true")
    bootstrap.add_argument("--enable-docker", action="store_true")
    bootstrap.set_defaults(handler=cmd_bootstrap)

    onboard = subparsers.add_parser("onboard", help="Preparar por completo un nodo nuevo")
    onboard.add_argument("name", choices=["PCrda", "laptop", "tecnologia04", "Uranus"])
    onboard.add_argument("--profile", choices=["workstation", "uranus"], default="workstation")
    onboard.add_argument("--apply", action="store_true")
    onboard.add_argument("--yes", action="store_true")
    onboard.add_argument("--enable-docker", action="store_true")
    onboard.add_argument("--offline", action="store_true")
    onboard.set_defaults(handler=cmd_onboard)

    start = subparsers.add_parser("start", help="Comenzar o reanudar una sesión")
    start.add_argument("--offline", action="store_true")
    start.add_argument("--strict-online", action="store_true")
    start.add_argument("--no-deps", action="store_true")
    start.set_defaults(handler=cmd_start)

    current = subparsers.add_parser("current", help="Mostrar el punto de continuación")
    current.set_defaults(handler=cmd_current)

    sync = subparsers.add_parser("sync", help="Sincronizar un árbol limpio")
    sync.add_argument("--strict-online", action="store_true")
    sync.set_defaults(handler=cmd_sync)

    end = subparsers.add_parser("end", help="Cerrar sesión y crear un checkpoint")
    end.add_argument("--session")
    end.add_argument("--done")
    end.add_argument("--next", dest="next_goal")
    end.add_argument("--command")
    end.add_argument("--expected")
    end.add_argument("--notes")
    end.add_argument("--message")
    end.add_argument("--skip-checks", action="store_true")
    end.add_argument("--no-commit", action="store_true")
    end.add_argument("--offline", action="store_true")
    end.add_argument("--yes", action="store_true")
    end.set_defaults(handler=cmd_end)

    device = subparsers.add_parser("device", help="Registrar o mostrar el nodo")
    device.add_argument("action", choices=["show", "set"])
    device.add_argument("name", nargs="?")
    device.set_defaults(handler=cmd_device)

    edit = subparsers.add_parser("edit", help="Abrir Neovim con configuración aislada")
    edit.add_argument("--force-config", action="store_true")
    edit.add_argument("--print-command", action="store_true")
    edit.set_defaults(handler=cmd_edit)

    remote = subparsers.add_parser("remote", help="Operar solo el staging Mnemosyne en Uranus")
    remote.add_argument("action", choices=["status", "up", "stop", "logs", "tunnel"])
    remote.add_argument("service", nargs="?", choices=["datalake", "postgres"])
    remote.set_defaults(handler=cmd_remote)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    raw = list(argv) if argv is not None else list(sys.argv[1:])
    tui_result = maybe_launch_tui(raw)
    if tui_result is not None:
        return tui_result
    # filter --no-tui before argparse (already handled by guard)
    filtered = [a for a in raw if a != "--no-tui"]
    parser = build_parser()
    args = parser.parse_args(filtered)
    if args.subcommand == "device" and args.action == "set" and not args.name:
        parser.error("device set requiere el nombre del nodo")
    try:
        return int(args.handler(args))
    except MnemoError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\nOperación interrumpida; no se forzó ningún paso pendiente.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
