"""以唯讀方式檢查 repo 的共用規則、登記資料與提交紀錄。"""

import argparse
import configparser
import datetime
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from functools import cached_property

try:
    import yaml
except ImportError:
    print("請先安裝 PyYAML：pip install pyyaml")
    raise SystemExit(2)


BEGIN = re.compile(
    r"<!-- BEGIN SHARED RULES profile=(?P<profile>\S+) source_commit=(?P<commit>\S+) "
    r"sha256=(?P<sha>[0-9a-f]{64}) tool_sha256=(?P<tool>[0-9a-f]{64}) -->"
)
END = "<!-- END SHARED RULES -->"
HOME_PATH = re.compile(r"[A-Za-z]:[\\/](?:Users|Documents and Settings)[\\/]|(?<![\w.])/(?:Users|home)/[A-Za-z0-9._-]+/")
SECRET = re.compile(
    r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----|"
    r"https?://(?:(?:canary|ptb)\.)?discord(?:app)?\.com/api/(?:v\d+/)?webhooks/\d+/[A-Za-z0-9_-]{20,}|"
    r"xox[abprs]-[A-Za-z0-9-]{10,}|ghp_[a-zA-Z0-9]{36}|sk_live_[A-Za-z0-9]{10,}"
)


class InputError(ValueError):
    """已轉換成中文且可直接顯示的輸入錯誤。"""


def relative_label(root, path):
    """跨磁碟路徑無相對表示法，僅顯示檔名。"""
    try:
        return Path(os.path.relpath(root / path, root)).as_posix()
    except ValueError:
        return Path(path).name


def block_parts(text):
    """依整行辨識標記，保留原有區塊前後的換行。"""
    markers = list(re.finditer(r"^<!-- (?:BEGIN|END) SHARED RULES[^\n]*$", text, re.M))
    if not markers:
        return None
    if len(markers) == 2:
        first, last = markers
        fields = BEGIN.fullmatch(first.group())
        if fields and last.group() == END:
            return (text[:first.start()], fields, text[first.end()+1:last.start()], text[last.end():])
    raise InputError("AGENTS.md 的共用規則標記格式或順序錯誤")


def digest(data):
    return hashlib.sha256(data).hexdigest()


class Skip(Exception):
    """此項沒有設定或缺少適用的比較基準。"""


class Checks:
    def __init__(self, root, config, base):
        self.root = root
        self.config = config
        self.base_ref = base
        self.limits = {"agents_head": 60, "agents_shared": 90, "active_context": 80,
                       "progress": 150, **config.get("limits", {})}

    def git(self, *args, check=True):
        return subprocess.run(["git", "--no-optional-locks", *args], cwd=self.root,
                              capture_output=True, check=check)

    @cached_property
    def base(self):
        if self.base_ref:
            result = self.git("rev-parse", "--verify", "--end-of-options",
                              self.base_ref + "^{commit}", check=False)
            if result.returncode == 0:
                return result.stdout.decode().strip()
        return None

    def setting(self, key, default=None):
        value = self.config.get(key, default)
        if not value:
            raise Skip("未設定")
        return value

    def read_text(self, path):
        try:
            return (self.root / path).read_text(encoding="utf-8")
        except UnicodeError:
            raise InputError(f"{relative_label(self.root, path)} 無法以 UTF-8 解碼") from None

    @cached_property
    def block(self):
        parts = block_parts(self.read_text("AGENTS.md"))
        if parts is None:
            raise InputError("AGENTS.md 缺少共用規則區塊")
        return parts

    def integrity(self):
        _, fields, content, _ = self.block
        issues = []
        if digest(content.encode()) != fields["sha"]:
            issues.append("共用規則內容的 SHA-256 不符")
        if digest((self.root / "tools/repo_check.py").read_bytes()) != fields["tool"]:
            issues.append("tools/repo_check.py 的 SHA-256 不符")
        return issues

    def agents_size(self):
        head, _, content, tail = self.block
        issues = []
        for key, part in [("agents_head", head), ("agents_shared", content)]:
            count = len(part.splitlines())
            if count > self.limits[key]:
                issues.append(f"AGENTS.md 的 {key} 有 {count} 行，上限 {self.limits[key]} 行")
        if tail.strip():
            issues.append("共用區塊後面有非空白文字")
        return issues

    def memory_size(self):
        folder = self.setting("memory_bank", "memory-bank")
        issues = []
        for filename, key in [("activeContext.md", "active_context"), ("progress.md", "progress")]:
            path = self.root / folder / filename
            if not path.is_file():
                issues.append(f"缺少 {filename}")
                continue
            count = len(path.read_text(encoding="utf-8").splitlines())
            if count > self.limits[key]:
                issues.append(f"{filename} 有 {count} 行，上限 {self.limits[key]} 行")
        return issues

    def paths(self, *args):
        return [os.fsdecode(p) for p in self.git(*args).stdout.split(b"\0") if p]

    @cached_property
    def tracked(self):
        return self.paths("ls-files", "-z")

    def texts(self):
        excluded = ["tools/repo_check.py", ".codebase-memory/*", *self.config.get("scan_exclude", [])]
        for name in self.tracked:
            path = self.root / name
            if any(fnmatch.fnmatchcase(name, pattern) for pattern in excluded):
                continue
            if path.is_symlink() or not path.is_file() or path.stat().st_size > 5 * 1024**2:
                continue
            with path.open("rb") as f:
                prefix = f.read(8192)
                if b"\0" not in prefix:
                    yield name, (prefix + f.read()).decode("utf-8", "replace")

    def home_paths(self):
        issues = []
        for name, text in self.texts():
            for line, value in enumerate(text.splitlines(), 1):
                if HOME_PATH.search(value):
                    issues.append(f"{name}:{line} 含有本機絕對路徑")
                    if len(issues) == 20:
                        return issues
        return issues

    def secrets(self):
        issues = set()
        for name in self.tracked:
            path = Path(name)
            if ((path.name == ".env" or path.name.startswith(".env.")) and path.name != ".env.example"
                    or path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}):
                issues.add(f"{name} 不得追蹤")
        issues.update(f"{name} 含有疑似 secret" for name, text in self.texts() if SECRET.search(text))
        return sorted(issues)

    def claude(self):
        lines = self.read_text("CLAUDE.md").splitlines()
        return [] if any(line.strip() == "@AGENTS.md" for line in lines) else ["CLAUDE.md 缺少 @AGENTS.md 行"]

    def commits(self):
        if not self.base:
            raise Skip("無法解析 base")
        issues = []
        for sha in self.git("rev-list", "--no-merges", self.base + "..HEAD").stdout.decode().splitlines():
            msg = self.git("show", "-s", "--format=%B", sha).stdout.decode("utf-8", "replace")
            agent = re.search(r"^Agent: (Claude|GPT|使用者)\s*$", msg, re.M)
            if not agent:
                issues.append(f"{sha[:12]} 缺少有效的 Agent 行")
            elif agent[1] != "使用者":
                if not re.search("[一-鿿]", msg.partition("\n")[0]):
                    issues.append(f"{sha[:12]} 標題缺少中文")
                if not re.search(r"^\s*(?:-\s*)?驗證[:：]", msg, re.M):
                    issues.append(f"{sha[:12]} 缺少驗證行")
        return issues

    def protected(self):
        patterns = self.setting("protected_paths")
        if not self.base:
            return ["無法解析 base"]
        names = self.paths("diff", "--no-renames", "--name-only", "-z", self.base, "--")
        names += self.paths("ls-files", "--others", "--exclude-standard", "-z")
        return sorted({f"{p} 是受保護路徑且有異動" for p in names
                       if any(fnmatch.fnmatchcase(p, pat) for pat in patterns)})

    def registry(self, path, key, text=None):
        if text is None:
            text = (self.root / path).read_bytes()
        label = relative_label(self.root, path)
        try:
            document = yaml.safe_load(text)
        except (ValueError, yaml.YAMLError):
            raise InputError(f"{label} 無法解析為 YAML") from None
        if not isinstance(document, dict) or key not in document:
            raise InputError(f"{label} 缺少 {key} 清單")
        rows = document[key]
        if rows is None and key == "impacts":
            return []
        if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
            raise InputError(f"{label} 的 {key} 必須是由對照表組成的清單")
        return rows

    def impacts(self):
        path = self.setting("pending_impacts")
        seen = set()
        issues = []
        for row in self.registry(path, "impacts"):
            ident = row.get("id")
            if isinstance(ident, (dict, list)):
                issues.append(f"{relative_label(self.root, path)} 的 id 格式無效")
                continue
            for key in ("id", "source", "target", "created", "status"):
                if not str(row.get(key) or "").strip():
                    issues.append(f"{ident} 缺少 {key}")
            if ident in seen:
                issues.append(f"{ident} 重複")
            seen.add(ident)
            status = row.get("status")
            if status not in ("PENDING", "SYNCHRONIZED", "NO_ACTION", "SUPERSEDED"):
                issues.append(f"{ident} 的 status 無效")
            if status != "PENDING" and not str(row.get("evidence") or "").strip():
                issues.append(f"{ident} 缺少 evidence")
            created = row.get("created")
            if type(created) is not datetime.date and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(created)):
                issues.append(f"{ident} 的 created 日期格式錯誤")
        if self.base:
            old = self.git("show", f"{self.base}:{path}", check=False)
            if old.returncode == 0:
                for row in self.registry(path, "impacts", old.stdout):
                    if "id" not in row or isinstance(row["id"], (dict, list)):
                        raise InputError(f"{relative_label(self.root, path)} 基準版本的 id 無效")
                    if row["id"] not in seen:
                        issues.append(f"已刪除 {row['id']}")
        return issues

    def projects(self):
        registry = self.setting("projects_registry")
        rows = self.registry(registry, "projects")
        modules = configparser.RawConfigParser()
        try:
            with (self.root / ".gitmodules").open(encoding="utf-8") as source:
                modules.read_file(source)
            actual = {modules[s]["path"]: modules[s]["url"]
                      for s in modules.sections() if s.startswith("submodule ")}
        except (KeyError, UnicodeError, configparser.Error):
            raise InputError(".gitmodules 格式錯誤或缺少 path、url") from None
        registered = {}
        for row in rows:
            path = row.get("workspace_path_hint")
            if path:
                url = row.get("canonical_remote")
                if not isinstance(path, str) or not isinstance(url, str):
                    raise InputError(f"{relative_label(self.root, registry)} 的專案路徑或網址無效")
                registered[path] = url

        def normalize(url):
            return url.lower().rstrip("/").removesuffix(".git")

        issues = []
        for path in sorted(actual.keys() | registered.keys()):
            label = relative_label(self.root, path)
            if path not in registered:
                issues.append(f"{label} 未登記")
            elif path not in actual:
                issues.append(f"{label} 缺少 submodule")
            elif normalize(actual[path]) != normalize(registered[path]):
                issues.append(f"{label} 網址不一致")
        return issues

    def indicators(self):
        registry = self.setting("indicator_registry")
        registered = set()
        for row in self.registry(registry, "indicators"):
            path = row.get("unit_path")
            if not isinstance(path, str) or not path.rstrip("/"):
                raise InputError(f"{relative_label(self.root, registry)} 的 unit_path 無效")
            registered.add(path.rstrip("/"))
        actual = {p.relative_to(self.root).as_posix() for p in (self.root / "indicators").glob("*") if p.is_dir()}
        issues = [f"{p} 未登記" for p in sorted(actual - registered)]
        for path in sorted(registered):
            if not (self.root / path).is_dir():
                issues.append(f"{relative_label(self.root, path)} 不存在")
        return issues

    def commands(self):
        issues = []
        for command in self.setting("commands"):
            result = subprocess.run(command, cwd=self.root, shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, errors="replace")
            if result.returncode:
                issues.extend([command, *result.stdout.splitlines()[-20:]])
        return issues


CHECKS = [
    ("共用區塊完整性", Checks.integrity), ("AGENTS 大小", Checks.agents_size),
    ("Memory Bank 大小", Checks.memory_size), ("本機絕對路徑", Checks.home_paths),
    ("secrets", Checks.secrets), ("CLAUDE.md", Checks.claude), ("commit 格式", Checks.commits),
    ("受保護檔案", Checks.protected), ("pending impacts", Checks.impacts),
    ("submodule 登記", Checks.projects), ("指標登記", Checks.indicators), ("指令", Checks.commands),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--base")
    parser.add_argument("--only")
    args = parser.parse_args()
    try:
        root = args.root.resolve()
        prefix = subprocess.run(["git", "rev-parse", "--is-inside-work-tree", "--show-prefix"],
                                cwd=root, capture_output=True)
        lines = prefix.stdout.splitlines()
        if prefix.returncode or lines[:1] != [b"true"]:
            raise InputError("--root 不是 Git repo")
        if any(lines[1:]):
            raise InputError("--root 須為 Git repo 根目錄")
        config = json.loads((root / ".repo-check.json").read_text(encoding="utf-8"))
        if not isinstance(config, dict) or "profile" not in config:
            raise InputError(".repo-check.json 缺少 profile")
        checks = Checks(root, config, args.base if args.base is not None else config.get("base_ref"))
    except InputError as error:
        print(error)
        return 2
    except (ValueError, TypeError):
        print(".repo-check.json 的格式錯誤")
        return 2
    except OSError:
        print("無法開啟 repo、執行 Git 或讀取 .repo-check.json")
        return 2

    passed = failed = skipped = 0
    only = None
    if args.only is not None:
        only = {code.strip() for code in args.only.split(",")}
        valid = {f"C{i:02}" for i in range(1, len(CHECKS) + 1)}
        if only - valid:
            print("--only 包含空白或未知代號：" + "、".join(sorted(only - valid)))
            return 2
    for index, (name, run) in enumerate(CHECKS, 1):
        code = f"C{index:02}"
        if only is not None and code not in only:
            continue
        try:
            issues = run(checks)
        except Skip as reason:
            print(f"[SKIP] {code} {name}：{reason}")
            skipped += 1
            continue
        except InputError as error:
            issues = [str(error)]
        except OSError as error:
            if error.filename:
                path = relative_label(root, error.filename)
                reason = "缺少檔案" if isinstance(error, FileNotFoundError) else "無法讀取"
                issues = [f"{path} {reason}"]
            else:
                issues = [f"檢查時發生未預期的錯誤（{type(error).__name__}），請回報"]
        except Exception as error:
            issues = [f"檢查時發生未預期的錯誤（{type(error).__name__}），請回報"]
        if issues:
            print(f"[FAIL] {code} {name}")
            for detail in issues:
                for line in detail.splitlines():
                    print("  " + line)
            failed += 1
        else:
            print(f"[PASS] {code} {name}")
            passed += 1
    print(f"結果：{passed} 通過、{failed} 失敗、{skipped} 略過")
    return int(failed > 0)


if __name__ == "__main__":
    raise SystemExit(main())
