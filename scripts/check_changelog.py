#!/usr/bin/env python3
"""Проверка changelog'ов store-репозитория для Home Assistant.

Supervisor показывает пользователю `autopass/CHANGELOG.md`, поэтому он обязан
содержать заголовок текущей версии из `autopass/config.yaml`. Корневой
`CHANGELOG.md` должен совпадать с ним, иначе заметки о релизе расходятся.

Использование:
    python scripts/check_changelog.py                  # проверка (код 1 при ошибке)
    python scripts/check_changelog.py --sync-from PATH # записать оба файла из source

`--sync-from` копирует source CHANGELOG (pirsasha/home-assistant-autopass) в оба
файла store-репозитория — так addon changelog не отстаёт от истории приложения.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "autopass" / "config.yaml"
ROOT_CHANGELOG = ROOT / "CHANGELOG.md"
ADDON_CHANGELOG = ROOT / "autopass" / "CHANGELOG.md"
HEADING = re.compile(r"^## (\S+)\s*$", re.M)


def current_version() -> str:
    text = CONFIG.read_text(encoding="utf-8")
    match = re.search(r'^version:\s*"?([^"\s]+)"?\s*$', text, flags=re.M)
    if not match:
        raise SystemExit(f"в {CONFIG} не найдено поле version")
    return match.group(1)


def headings(path: Path) -> list[str]:
    return HEADING.findall(path.read_text(encoding="utf-8"))


def sync(source: Path) -> int:
    text = source.read_text(encoding="utf-8")
    if not text.startswith("# История изменений"):
        raise SystemExit(f"{source}: ожидается заголовок «# История изменений»")
    if not HEADING.search(text):
        raise SystemExit(f"{source}: не найдено ни одной версии")
    payload = text.rstrip("\n") + "\n"
    for path in (ROOT_CHANGELOG, ADDON_CHANGELOG):
        path.write_text(payload, encoding="utf-8")
        print(f"обновлён {path.relative_to(ROOT)} ({len(HEADING.findall(payload))} версий)")
    return 0


def check() -> int:
    version = current_version()
    problems: list[str] = []
    root_versions = headings(ROOT_CHANGELOG)
    addon_versions = headings(ADDON_CHANGELOG)

    print(f"версия в autopass/config.yaml: {version}")
    for name, versions in (("CHANGELOG.md", root_versions),
                           ("autopass/CHANGELOG.md", addon_versions)):
        if not versions:
            problems.append(f"{name}: не найдено ни одного заголовка «## <версия>»")
            continue
        print(f"{name}: последняя версия {versions[0]}, всего {len(versions)}")
        if versions[0] != version:
            problems.append(
                f"{name}: последняя версия {versions[0]}, а в config.yaml {version} — "
                "заметки о релизе для Home Assistant не обновлены"
            )
        if version not in versions:
            problems.append(f"{name}: нет раздела «## {version}»")

    if root_versions != addon_versions:
        only_root = [item for item in root_versions if item not in addon_versions]
        only_addon = [item for item in addon_versions if item not in root_versions]
        problems.append(
            "CHANGELOG.md и autopass/CHANGELOG.md расходятся"
            + (f"; только в корневом: {only_root}" if only_root else "")
            + (f"; только в addon: {only_addon}" if only_addon else "")
            + ("; порядок версий различается" if not only_root and not only_addon else "")
        )

    if problems:
        print()
        for problem in problems:
            print(f"ОШИБКА: {problem}")
        print()
        print("Порядок релиза: сначала обновить source CHANGELOG приложения, затем")
        print("`python scripts/check_changelog.py --sync-from <source CHANGELOG.md>`, и")
        print("только после этого менять version в autopass/config.yaml.")
        return 1

    print()
    print("OK: changelog для Home Assistant содержит текущую версию, файлы синхронны")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sync-from", type=Path, default=None,
                        help="source CHANGELOG.md приложения: записать оба файла store")
    args = parser.parse_args()
    if args.sync_from is not None:
        return sync(args.sync_from)
    return check()


if __name__ == "__main__":
    sys.exit(main())
