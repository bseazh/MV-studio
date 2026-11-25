#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在用户指定的目标文件夹里建好 MV 项目骨架。

用法:
    python3 新建项目.py <目标目录> <项目名> [--模式 手动|自动]

会创建 <目标目录>/mv-<项目名>/ 下的全套目录、进度.json、全部提示词.md，
并把本 skill 的参考文件和使用说明复制进项目。
"""

import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

DIRS = [
    "模板",
    "0-立项",
    "1-情节",
    "2-歌词",
    "3-画风",
    "4-人物",
    "5-场景",
    "6-道具",
    "7-分镜",
    "8-视频",
    "复制粘贴",
    "素材/人物",
    "素材/场景",
    "素材/道具",
    "素材/分镜",
    "素材/视频",
    "素材/调用记录",
]


def slugify(name: str) -> str:
    """保留中文，空格和路径分隔符换成连字符。"""
    name = re.sub(r'[\s/\\:*?"<>|]+', "-", name.strip())
    return re.sub(r"-{2,}", "-", name).strip("-") or "未命名"


def main() -> int:
    args = [a for a in sys.argv[1:]]
    if len(args) < 2:
        print(__doc__)
        return 1

    mode = "手动"
    if "--模式" in args:
        i = args.index("--模式")
        if i + 1 < len(args) and args[i + 1] in ("手动", "自动"):
            mode = args[i + 1]
        args = args[:i] + args[i + 2:]

    target = Path(args[0]).expanduser().resolve()
    project_name = args[1]

    if not target.is_dir():
        print(f"目标目录不存在: {target}")
        print("请先确认用户要把项目放在哪里，不要自行创建。")
        return 1

    root = target / f"mv-{slugify(project_name)}"
    if (root / "进度.json").exists():
        print(f"项目已存在: {root}")
        print("请改为读取它的 进度.json 续做，不要覆盖。")
        return 1

    for d in DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)

    skill_root = Path(__file__).resolve().parent.parent
    refs = skill_root / "references"
    if refs.is_dir():
        for f in sorted(refs.glob("*.md")):
            shutil.copy2(f, root / "模板" / f.name)
    guide = skill_root / "使用说明.md"
    if guide.is_file():
        shutil.copy2(guide, root / "使用说明.md")

    state = {
        "项目": project_name,
        "创建时间": datetime.now().isoformat(timespec="seconds"),
        "mode": mode,
        "画布": "",
        "stage": 1,
        "当前阶段": "故事情节方向",
        "brief": "",
        "参数确认单": {
            "总时长": "",
            "分段": "",
            "歌词行数": "",
            "语言人声": "",
            "宫格": "",
            "人物数": "",
            "场景数": "",
            "道具数": 1,
        },
        "情节": None,
        "歌词": None,
        "画风": None,
        "人物": [],
        "场景": [],
        "道具": [],
        "分段": [],
    }
    (root / "进度.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    (root / "全部提示词.md").write_text(
        f"# {project_name} · 全套提示词\n\n"
        "| 阶段 | 对象 | 提示词 | 复制包 | 产出图 | 状态 |\n"
        "|---|---|---|---|---|---|\n"
        "| 情节 | — | — | — | — | ⬜ 未开始 |\n",
        encoding="utf-8",
    )
    (root / "素材" / "调用记录" / ".keep").write_text("", encoding="utf-8")

    print(f"项目已创建: {root}")
    print(f"模式: {mode}")
    for d in DIRS:
        print(f"  {d}/")
    print("\n当前阶段: 1 · 故事情节方向")
    print("下一步: 读 references/01-情节.md，给用户三个情节方向选。")
    print("提醒: 参数确认单应已在阶段 0 核对过，把结果填进 进度.json。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
