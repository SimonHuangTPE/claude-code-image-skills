"""
小克批次變體生圖（OpenAI gpt-image-2）

用法：
  python draw_batch.py "穿太空服的橘色貓咪太空人" --vary pose --n 4 --style anime
  python draw_batch.py "黑色陶瓷馬克杯" --vary angle --n 4 --style studio_product
  python draw_batch.py "穿西裝的龍蝦" --custom "drinking coffee, riding skateboard, programming, conducting orchestra" --style cinematic
  python draw_batch.py "金髮藍眼少女" --vary expression --n 4 --reference

模式：
  獨立生成（預設）：每張帶完整主體描述，便宜、稍有飄移
  --reference：第一張獨立生，後續用 edit + 第一張當 reference，一致性高、貴 2-4x

輸出：
  generated/batch_<timestamp>_<name>/
    01_<vary>_<value>.jpeg
    02_<vary>_<value>.jpeg
    ...
    _summary.md
"""

import os
import sys
import json
import base64
import random
import argparse
from pathlib import Path
from datetime import datetime

MODEL = "gpt-image-2"
DEFAULT_SIZE = "1024x1024"
DEFAULT_QUALITY = "low"
DEFAULT_FORMAT = "jpeg"
DEFAULT_N = 4

# 8 個變體軸（每軸 8 個值，隨需求隨機抽 N 個）
VARIATION_AXES = {
    "pose": [
        "standing confidently",
        "sitting cross-legged",
        "running forward dynamically",
        "jumping mid-air with energy",
        "dancing joyfully",
        "sleeping peacefully curled up",
        "in fighting stance ready to strike",
        "walking thoughtfully",
    ],
    "scene": [
        "in a misty pine forest",
        "on a busy neon-lit city street at night",
        "on a tropical beach at sunset",
        "atop a snowy mountain peak",
        "in a sand dune desert under the stars",
        "inside a cozy wooden cafe interior",
        "in an ancient library with tall bookshelves",
        "on a futuristic spaceship bridge",
    ],
    "angle": [
        "front view, centered composition",
        "left side profile view",
        "back view from behind",
        "three-quarter view from front-right",
        "top-down view looking straight down",
        "low-angle view looking up dramatically",
        "aerial view from above",
        "close-up macro detail shot",
    ],
    "expression": [
        "smiling warmly with bright eyes",
        "serious thoughtful expression",
        "surprised with wide eyes and open mouth",
        "deep in thoughtful concentration",
        "laughing joyfully head tilted back",
        "sad with quiet tears",
        "angry with furrowed brow",
        "peaceful serene closed eyes",
    ],
    "outfit": [
        "wearing casual streetwear",
        "wearing formal black business suit",
        "wearing sporty athletic gear",
        "wearing thick winter coat with fur trim",
        "wearing flowy summer dress",
        "wearing traditional cultural attire",
        "wearing futuristic armor",
        "wearing comfortable cotton pajamas",
    ],
    "time": [
        "at dawn with first golden light",
        "in bright morning sunlight",
        "at high noon under direct sun",
        "in warm afternoon light",
        "at dusk with purple-orange sky",
        "at night under street lamps",
        "at midnight with full moon",
        "during golden hour with rich glow",
    ],
    "weather": [
        "on a clear sunny day",
        "in heavy rain with puddles",
        "during a snowstorm with falling flakes",
        "in dense morning fog",
        "during a dramatic thunderstorm",
        "under overcast cloudy sky",
        "in strong wind with hair blowing",
        "with a rainbow after rain",
    ],
    "mood": [
        "with a peaceful serene atmosphere",
        "with dramatic intense atmosphere",
        "with mysterious shadowy atmosphere",
        "with joyful vibrant energy",
        "with melancholy quiet feeling",
        "with high-energy dynamic feel",
        "with nostalgic warm vintage feel",
        "with surreal dreamlike quality",
    ],
}


def load_env():
    for p in [Path.cwd() / ".env", Path.home() / ".openai.env"]:
        if not p.exists():
            continue
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


# 直接用 draw skill 的 STYLE_PRESETS（不重複定義）
def load_style_presets():
    """從同 user 的 draw skill 載入 STYLE_PRESETS"""
    draw_path = Path.home() / ".claude/skills/draw/draw.py"
    if not draw_path.exists():
        return {}
    try:
        ns = {}
        exec(draw_path.read_text(encoding="utf-8"), ns)
        return ns.get("STYLE_PRESETS", {})
    except Exception as e:
        print(f"⚠️ 無法載入 draw skill 的 STYLE_PRESETS: {e}", file=sys.stderr)
        return {}


STYLE_PRESETS = load_style_presets()


def pick_variations(axis: str, n: int, custom: str | None):
    """選 N 個變體值。custom 優先（逗號分隔字串），否則從 VARIATION_AXES 抽"""
    if custom:
        items = [s.strip() for s in custom.split(",") if s.strip()]
        return items[:n] if len(items) >= n else items
    if axis not in VARIATION_AXES:
        raise ValueError(f"未知變體軸 '{axis}'，可選：{list(VARIATION_AXES.keys())}")
    pool = VARIATION_AXES[axis]
    if n <= len(pool):
        # 取前 N 個（保持順序穩定，方便重現）
        return pool[:n]
    return pool + random.choices(pool, k=n - len(pool))


def build_prompt(subject: str, variation: str, style: str | None):
    """組合：style wrap + subject + variation"""
    body = f"{subject}, {variation}"
    if style and style in STYLE_PRESETS:
        return STYLE_PRESETS[style]["wrap"].format(S=body)
    return body


def slug(s: str, n=20):
    """變體值 → 檔名片段"""
    keep = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    s = "".join(c if c in keep else "_" for c in s.replace(" ", "_"))
    return s[:n]


def generate_one(client, prompt, size, quality, fmt, name_idx, vary_label, outdir):
    print(f"  [{name_idx}] {vary_label} ...", file=sys.stderr)
    result = client.images.generate(
        model=MODEL, prompt=prompt, size=size, quality=quality, n=1,
        output_format=fmt,
    )
    item = result.data[0]
    out_path = outdir / f"{name_idx:02d}_{slug(vary_label)}.{fmt}"
    out_path.write_bytes(base64.b64decode(item.b64_json))
    revised = getattr(item, "revised_prompt", "") or ""
    return out_path, revised


def edit_one(client, ref_path, prompt, size, quality, fmt, name_idx, vary_label, outdir):
    print(f"  [{name_idx}] {vary_label} (edit ref={ref_path.name}) ...", file=sys.stderr)
    result = client.images.edit(
        model=MODEL, image=open(ref_path, "rb"),
        prompt=prompt, size=size, quality=quality, n=1,
    )
    item = result.data[0]
    out_path = outdir / f"{name_idx:02d}_{slug(vary_label)}.{fmt}"
    out_path.write_bytes(base64.b64decode(item.b64_json))
    return out_path, ""


# 簡易成本估算（同 draw skill）
COST_USD = {
    ("low", "1024x1024"): 0.006,
    ("low", "1024x1536"): 0.005,
    ("low", "1536x1024"): 0.005,
    ("medium", "1024x1024"): 0.053,
    ("high", "1024x1024"): 0.211,
}


def main():
    load_env()
    if not os.getenv("OPENAI_API_KEY"):
        print("錯誤：找不到 OPENAI_API_KEY", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", nargs="+", help="主體描述")
    parser.add_argument("--vary", default="pose", choices=list(VARIATION_AXES.keys()))
    parser.add_argument("--custom", default=None,
                        help="自訂變體 list，逗號分隔，會覆蓋 --vary")
    parser.add_argument("--n", type=int, default=DEFAULT_N)
    parser.add_argument("--style", default=None,
                        choices=list(STYLE_PRESETS.keys()) if STYLE_PRESETS else None)
    parser.add_argument("--size", default=DEFAULT_SIZE)
    parser.add_argument("--quality", default=DEFAULT_QUALITY,
                        choices=["low", "medium", "high", "auto"])
    parser.add_argument("--format", default=DEFAULT_FORMAT,
                        choices=["png", "jpeg", "webp"])
    parser.add_argument("--reference", action="store_true",
                        help="第一張當 ref，後續用 edit 模式（一致性更高，貴 2-4x）")
    parser.add_argument("--name", default="batch")
    parser.add_argument("--outdir", default=None)
    args = parser.parse_args()

    subject = " ".join(args.prompt)
    n = max(1, min(args.n, 8))
    variations = pick_variations(args.vary, n, args.custom)
    actual_n = len(variations)

    # 建輸出資料夾
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cwd = Path.cwd()
    base = Path(args.outdir) if args.outdir else (
        (cwd / "slides" / "generated") if (cwd / "slides").exists() else (cwd / "generated")
    )
    outdir = base / f"batch_{stamp}_{args.name}"
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"📁 輸出：{outdir}", file=sys.stderr)
    print(f"🎯 主體：{subject}", file=sys.stderr)
    print(f"🔀 變體：{args.vary if not args.custom else 'custom'} × {actual_n}", file=sys.stderr)
    if args.style:
        print(f"🎨 風格：{args.style}", file=sys.stderr)
    print(f"💰 預估費用：${COST_USD.get((args.quality, args.size), 0) * actual_n:.4f} USD", file=sys.stderr)
    print("", file=sys.stderr)

    from openai import OpenAI
    client = OpenAI()

    summary = [
        f"# Batch: {args.name} ({datetime.now():%Y-%m-%d %H:%M})\n",
        f"主體：{subject}\n",
        f"風格：{args.style or '(無)'}\n",
        f"變體軸：{args.vary if not args.custom else 'custom'} × {actual_n}\n",
        f"模式：{'reference (edit)' if args.reference else '獨立生成'}\n",
        "",
    ]

    ref_path = None
    total_cost = 0.0
    for idx, var in enumerate(variations, start=1):
        prompt = build_prompt(subject, var, args.style)
        try:
            if args.reference and idx > 1 and ref_path:
                out_path, revised = edit_one(
                    client, ref_path, prompt, args.size, args.quality,
                    args.format, idx, var, outdir,
                )
            else:
                out_path, revised = generate_one(
                    client, prompt, args.size, args.quality, args.format,
                    idx, var, outdir,
                )
                if args.reference and idx == 1:
                    ref_path = out_path
            cost = COST_USD.get((args.quality, args.size), 0)
            total_cost += cost
            summary += [
                f"## {out_path.name}",
                f"**變體**: {var}",
                f"**Prompt**: {prompt}",
                f"**Cost**: ${cost:.4f}",
                f"**Revised**: {revised[:200]}" if revised else "",
                "",
            ]
        except Exception as e:
            print(f"  ❌ {idx} 失敗: {e}", file=sys.stderr)
            summary.append(f"## {idx:02d}_{slug(var)}\n❌ 失敗：{e}\n")

    summary.append(f"\n**總費用：${total_cost:.4f} USD ≈ NT${total_cost*32:.2f}**\n")
    (outdir / "_summary.md").write_text("\n".join(summary), encoding="utf-8")

    print(f"\n✅ 完成 {actual_n} 張，總費用 ${total_cost:.4f}", file=sys.stderr)
    print(f"📋 摘要：{outdir / '_summary.md'}", file=sys.stderr)


if __name__ == "__main__":
    main()
