#!/usr/bin/env python3
"""
scan_project.py — Scans a project root and emits structured JSON
for CLAUDE.md generation.

Usage:
    python3 scan_project.py [project_root]

Defaults to current working directory.
"""

import json
import os
import re
import sys
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else os.getcwd()).resolve()
MAX_FILE_BYTES = 32_000   # max bytes to read from any single file
MAX_LINES_PER_FILE = 300  # cap for deep-read files (README, etc.)

# ── Helpers ───────────────────────────────────────────────────────────────────
def read_text(path: Path, max_bytes=MAX_FILE_BYTES) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:max_bytes]
    except Exception:
        return ""

def read_json_safe(path: Path) -> dict:
    try:
        return json.loads(read_text(path))
    except Exception:
        return {}

def file_exists(*parts) -> bool:
    return (ROOT / Path(*parts)).exists()

def find_files(pattern: str, max_depth: int = 4) -> list[Path]:
    results = []
    for p in ROOT.rglob(pattern):
        depth = len(p.relative_to(ROOT).parts)
        if depth <= max_depth:
            results.append(p)
    return results

def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


# ── Detectors ─────────────────────────────────────────────────────────────────

def detect_package_manager() -> dict:
    """Detect JS/TS package manager and extract scripts + deps."""
    pkg = read_json_safe(ROOT / "package.json")
    if not pkg:
        return {}

    pm = "npm"
    if (ROOT / "yarn.lock").exists():
        pm = "yarn"
    elif (ROOT / "pnpm-lock.yaml").exists():
        pm = "pnpm"
    elif (ROOT / "bun.lockb").exists():
        pm = "bun"

    scripts = pkg.get("scripts", {})
    deps = list(pkg.get("dependencies", {}).keys())
    dev_deps = list(pkg.get("devDependencies", {}).keys())

    # Classify key scripts
    key_scripts = {}
    for name, cmd in scripts.items():
        if name in ("dev", "start", "build", "test", "lint", "preview",
                    "deploy", "format", "typecheck", "clean", "serve"):
            key_scripts[name] = f"{pm} run {name}"
        elif any(kw in name for kw in ("test", "lint", "build", "deploy", "check")):
            key_scripts[name] = f"{pm} run {name}"

    return {
        "package_manager": pm,
        "scripts": key_scripts,
        "all_scripts": scripts,
        "dependencies": deps,
        "dev_dependencies": dev_deps,
        "name": pkg.get("name", ""),
        "version": pkg.get("version", ""),
        "description": pkg.get("description", ""),
        "main": pkg.get("main") or pkg.get("module", ""),
        "engines": pkg.get("engines", {}),
    }


def detect_python() -> dict:
    """Detect Python project type and commands."""
    result = {}

    if (ROOT / "pyproject.toml").exists():
        content = read_text(ROOT / "pyproject.toml")
        result["config"] = "pyproject.toml"
        result["has_poetry"] = "[tool.poetry]" in content
        result["has_hatch"] = "[tool.hatch" in content
        result["has_ruff"] = "[tool.ruff]" in content
        result["has_black"] = "[tool.black]" in content
        result["has_pytest"] = "[tool.pytest" in content

        # Extract name
        m = re.search(r'name\s*=\s*"([^"]+)"', content)
        if m:
            result["name"] = m.group(1)

    if (ROOT / "requirements.txt").exists():
        reqs = read_text(ROOT / "requirements.txt")
        result["requirements"] = [
            r.strip().split("==")[0].split(">=")[0]
            for r in reqs.splitlines()
            if r.strip() and not r.startswith("#")
        ]

    if (ROOT / "setup.py").exists() or (ROOT / "setup.cfg").exists():
        result["setup"] = True

    if (ROOT / "Makefile").exists():
        makefile = read_text(ROOT / "Makefile")
        targets = re.findall(r"^(\w[\w\-]+)\s*:", makefile, re.MULTILINE)
        result["make_targets"] = targets[:20]

    if result:
        # Infer runner
        if result.get("has_poetry"):
            result["runner"] = "poetry run"
            result["commands"] = {
                "install": "poetry install",
                "test": "poetry run pytest",
                "lint": "poetry run ruff check .",
                "format": "poetry run black .",
            }
        else:
            result["runner"] = "python3"
            result["commands"] = {
                "install": "pip install -r requirements.txt",
                "test": "pytest",
                "lint": "ruff check . || flake8 .",
            }

    return result


def detect_stack() -> dict:
    """Infer frontend/backend framework from deps and config files."""
    stack = {"frameworks": [], "bundler": None, "css": None,
             "testing": [], "orm": None, "database": None,
             "state_management": None, "language": None}

    # JS/TS framework detection
    js = detect_package_manager()
    all_deps = set(js.get("dependencies", []) + js.get("dev_dependencies", []))

    # Language
    if (ROOT / "tsconfig.json").exists() or any(p.suffix == ".ts" for p in ROOT.glob("src/**/*.ts")):
        stack["language"] = "TypeScript"
    elif all_deps:
        stack["language"] = "JavaScript"

    # Frameworks
    fw_map = {
        "react": "React", "next": "Next.js", "vue": "Vue",
        "nuxt": "Nuxt", "svelte": "Svelte", "sveltekit": "SvelteKit",
        "solid-js": "Solid", "astro": "Astro", "remix": "Remix",
        "express": "Express", "fastify": "Fastify", "nestjs": "NestJS",
        "@nestjs/core": "NestJS", "hono": "Hono", "koa": "Koa",
        "electron": "Electron", "expo": "Expo", "react-native": "React Native",
    }
    for pkg_name, label in fw_map.items():
        if pkg_name in all_deps:
            stack["frameworks"].append(label)

    # Bundler
    for b in ("vite", "webpack", "esbuild", "rollup", "parcel", "turbopack"):
        if b in all_deps or file_exists(f"{b}.config.ts") or file_exists(f"{b}.config.js"):
            stack["bundler"] = b
            break

    # CSS
    for css in ("tailwindcss", "sass", "styled-components", "@emotion/react",
                "unocss", "stitches", "chakra-ui", "@mui/material"):
        if css in all_deps:
            stack["css"] = css
            break

    # Testing
    for t in ("jest", "vitest", "mocha", "cypress", "playwright", "@testing-library/react",
              "pytest", "unittest"):
        if t in all_deps:
            stack["testing"].append(t)

    # ORM / DB
    db_map = {
        "prisma": "Prisma", "@prisma/client": "Prisma",
        "drizzle-orm": "Drizzle", "typeorm": "TypeORM",
        "sequelize": "Sequelize", "mongoose": "Mongoose",
        "firebase": "Firebase", "firebase-admin": "Firebase Admin",
        "@supabase/supabase-js": "Supabase",
        "pg": "PostgreSQL (pg)", "mysql2": "MySQL", "better-sqlite3": "SQLite",
        "redis": "Redis", "ioredis": "Redis (ioredis)",
    }
    for pkg_name, label in db_map.items():
        if pkg_name in all_deps:
            stack["orm"] = stack["orm"] or label
            stack["database"] = stack["database"] or label

    # State
    for s in ("redux", "@reduxjs/toolkit", "zustand", "jotai", "recoil", "mobx", "valtio"):
        if s in all_deps:
            stack["state_management"] = s
            break

    # Python stack
    py = detect_python()
    if py:
        stack["language"] = stack["language"] or "Python"
        for fw in ("fastapi", "django", "flask", "starlette", "tornado", "aiohttp"):
            if fw in py.get("requirements", []):
                stack["frameworks"].append(fw.capitalize())

    # Other languages
    if file_exists("Cargo.toml"):
        stack["language"] = stack["language"] or "Rust"
        stack["frameworks"].append("Rust/Cargo")
    if file_exists("go.mod"):
        stack["language"] = stack["language"] or "Go"
        stack["frameworks"].append("Go Modules")
    if file_exists("pom.xml"):
        stack["language"] = stack["language"] or "Java"
        stack["frameworks"].append("Maven")
    if file_exists("build.gradle") or file_exists("build.gradle.kts"):
        stack["language"] = stack["language"] or "Kotlin/Java"
        stack["frameworks"].append("Gradle")

    return stack


def detect_architecture() -> dict:
    """Infer directory architecture patterns."""
    arch = {
        "src_structure": [],
        "notable_dirs": [],
        "config_files": [],
        "monorepo": False,
        "docker": False,
        "ci": [],
    }

    # Src structure (top-level dirs inside src/ or root)
    src = ROOT / "src"
    scan_root = src if src.exists() else ROOT
    try:
        for item in sorted(scan_root.iterdir()):
            if item.is_dir() and not item.name.startswith(".") and item.name not in (
                "node_modules", "__pycache__", ".git", "dist", "build", ".next", "coverage"
            ):
                arch["src_structure"].append(item.name)
    except Exception:
        pass

    # Notable dirs
    notable = [
        "api", "components", "pages", "app", "lib", "utils", "hooks",
        "services", "models", "controllers", "routes", "middleware",
        "store", "context", "types", "styles", "assets", "public",
        "tests", "test", "__tests__", "spec", "scripts", "migrations",
        "prisma", "drizzle", "infra", "k8s", "terraform",
    ]
    for d in notable:
        if (ROOT / d).exists() or (ROOT / "src" / d).exists():
            arch["notable_dirs"].append(d)

    # Config files
    config_markers = [
        ".env.example", ".env.local.example", "docker-compose.yml",
        "docker-compose.yaml", "Dockerfile", ".dockerignore",
        "nginx.conf", "vercel.json", "netlify.toml", "fly.toml",
        "render.yaml", "railway.json", ".firebaserc", "firebase.json",
        "turbo.json", "nx.json", "lerna.json", "rush.json",
        "jest.config.ts", "jest.config.js", "vitest.config.ts",
        "playwright.config.ts", "cypress.config.ts",
        "eslint.config.js", ".eslintrc.js", ".eslintrc.json",
        ".prettierrc", "prettier.config.js",
        "tailwind.config.ts", "tailwind.config.js",
        "tsconfig.json", "tsconfig.*.json",
        ".nvmrc", ".node-version",
        "wrangler.toml", "supabase/config.toml",
    ]
    for marker in config_markers:
        if "*" in marker:
            if list(ROOT.glob(marker)):
                arch["config_files"].append(marker)
        elif (ROOT / marker).exists():
            arch["config_files"].append(marker)

    # Monorepo
    if (ROOT / "packages").exists() or (ROOT / "apps").exists():
        if any(f.exists() for f in [ROOT / "turbo.json", ROOT / "nx.json",
                                     ROOT / "lerna.json", ROOT / "pnpm-workspace.yaml"]):
            arch["monorepo"] = True
            # List workspaces
            for sub in (ROOT / "packages", ROOT / "apps"):
                if sub.exists():
                    arch["workspaces"] = arch.get("workspaces", []) + [
                        d.name for d in sub.iterdir() if d.is_dir()
                    ]

    # Docker
    if file_exists("Dockerfile") or file_exists("docker-compose.yml"):
        arch["docker"] = True

    # CI/CD
    if (ROOT / ".github" / "workflows").exists():
        workflows = list((ROOT / ".github" / "workflows").glob("*.yml"))
        arch["ci"].append(f"GitHub Actions ({len(workflows)} workflows)")
    if (ROOT / ".gitlab-ci.yml").exists():
        arch["ci"].append("GitLab CI")
    if (ROOT / "Jenkinsfile").exists():
        arch["ci"].append("Jenkins")
    if (ROOT / ".circleci").exists():
        arch["ci"].append("CircleCI")

    return arch


def detect_env_vars() -> list[str]:
    """Extract env var names from .env.example or similar."""
    for candidate in [".env.example", ".env.local.example", ".env.sample", ".env"]:
        path = ROOT / candidate
        if path.exists() and candidate != ".env":  # skip actual .env
            content = read_text(path)
            vars_ = re.findall(r"^([A-Z_][A-Z0-9_]+)\s*=", content, re.MULTILINE)
            if vars_:
                return list(dict.fromkeys(vars_))  # dedupe, preserve order
    return []


def detect_conventions() -> dict:
    """Infer coding conventions from config files and existing code."""
    conv = {"style": [], "commit": None, "branch": None, "notes": []}

    # Prettier
    if any((ROOT / f).exists() for f in [".prettierrc", ".prettierrc.json",
                                          ".prettierrc.js", "prettier.config.js"]):
        conv["style"].append("Prettier (auto-format on save)")

    # ESLint
    if any((ROOT / f).exists() for f in [".eslintrc", ".eslintrc.js", ".eslintrc.json",
                                          "eslint.config.js", ".eslintrc.cjs"]):
        conv["style"].append("ESLint")

    # TypeScript strict
    ts = read_json_safe(ROOT / "tsconfig.json")
    if ts.get("compilerOptions", {}).get("strict"):
        conv["style"].append("TypeScript strict mode")
    if ts.get("compilerOptions", {}).get("noImplicitAny"):
        conv["style"].append("TypeScript noImplicitAny")

    # Husky / lint-staged
    pkg = read_json_safe(ROOT / "package.json")
    all_deps = set(list(pkg.get("dependencies", {}).keys()) +
                   list(pkg.get("devDependencies", {}).keys()))
    if "husky" in all_deps:
        conv["style"].append("Husky pre-commit hooks")
    if "lint-staged" in all_deps:
        conv["style"].append("lint-staged")

    # Commitlint / conventional commits
    if (ROOT / ".commitlintrc.json").exists() or "commitlint" in all_deps:
        conv["commit"] = "Conventional Commits (enforced)"
    elif (ROOT / ".gitmessage").exists():
        conv["commit"] = "Custom commit template (.gitmessage)"

    # Path aliases
    ts_paths = ts.get("compilerOptions", {}).get("paths", {})
    if ts_paths:
        aliases = list(ts_paths.keys())[:5]
        conv["notes"].append(f"Path aliases: {', '.join(aliases)}")

    # Import style inference (check a few source files)
    sample_files = list((ROOT / "src").glob("**/*.ts"))[:5] if (ROOT / "src").exists() else []
    has_named = any(
        "export {" in read_text(f)[:2000] or "export const" in read_text(f)[:2000]
        for f in sample_files
    )
    has_default = any(
        "export default" in read_text(f)[:2000]
        for f in sample_files
    )
    if has_named and not has_default:
        conv["notes"].append("Prefers named exports over default exports")

    return conv


def extract_readme_summary() -> str:
    """Pull first meaningful paragraph from README."""
    for candidate in ["README.md", "readme.md", "README.rst", "README.txt"]:
        path = ROOT / candidate
        if path.exists():
            content = read_text(path, max_bytes=3000)
            lines = content.splitlines()
            # Skip title line and blanks, grab first paragraph
            para = []
            in_para = False
            for line in lines:
                if line.startswith("#") and not para:
                    continue
                if line.strip():
                    in_para = True
                    para.append(line.strip())
                elif in_para:
                    break
            return " ".join(para)[:500]
    return ""


def detect_deployment_targets() -> list[str]:
    """Infer where this project deploys."""
    targets = []
    if file_exists("vercel.json") or file_exists(".vercelignore"):
        targets.append("Vercel")
    if file_exists("netlify.toml"):
        targets.append("Netlify")
    if file_exists("fly.toml"):
        targets.append("Fly.io")
    if file_exists("render.yaml"):
        targets.append("Render")
    if file_exists("railway.json") or file_exists("railway.toml"):
        targets.append("Railway")
    if file_exists(".firebaserc") or file_exists("firebase.json"):
        targets.append("Firebase")
    if file_exists("wrangler.toml"):
        targets.append("Cloudflare Workers")
    if file_exists("Dockerfile"):
        targets.append("Docker container")
    if (ROOT / ".github" / "workflows").exists():
        wf_text = " ".join(
            read_text(p) for p in (ROOT / ".github" / "workflows").glob("*.yml")
        )
        if "aws" in wf_text.lower():
            targets.append("AWS")
        if "gcloud" in wf_text.lower() or "gcp" in wf_text.lower():
            targets.append("Google Cloud")
    return targets


# ── Assemble output ────────────────────────────────────────────────────────────
def main():
    js_info = detect_package_manager()
    py_info = detect_python()
    stack = detect_stack()
    arch = detect_architecture()
    env_vars = detect_env_vars()
    conventions = detect_conventions()
    readme_summary = extract_readme_summary()
    deploy_targets = detect_deployment_targets()

    # Build unified commands dict
    commands = {}
    if js_info:
        commands.update(js_info.get("scripts", {}))
    if py_info:
        commands.update(py_info.get("commands", {}))
    if py_info.get("make_targets"):
        for t in py_info["make_targets"][:8]:
            commands[f"make {t}"] = f"make {t}"

    output = {
        "project_root": str(ROOT),
        "project_name": (
            js_info.get("name")
            or py_info.get("name")
            or ROOT.name
        ),
        "description": js_info.get("description") or readme_summary[:200],
        "readme_summary": readme_summary,
        "stack": stack,
        "commands": commands,
        "architecture": arch,
        "env_vars": env_vars,
        "conventions": conventions,
        "deploy_targets": deploy_targets,
        "has_js": bool(js_info),
        "has_python": bool(py_info),
        "package_manager": js_info.get("package_manager"),
        "engines": js_info.get("engines", {}),
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
