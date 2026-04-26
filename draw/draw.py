"""
小克全域生圖腳本（OpenAI gpt-image-2 + 風格優化版）

用法：
  python draw.py "一隻穿西裝的龍蝦" --style cinematic
  python draw.py "iPhone 15 Pro" --style studio_product --name iphone
  python draw.py "演講海報" --size 2048x2048 --style vintage_poster --name poster
  python draw.py "把背景換成海底" --edit ./photo.jpg --name edited
  python draw.py "加一頂帽子" --edit ./photo.jpg --mask ./mask.png

自動讀取 OPENAI_API_KEY（依序）：
  1. 當前 shell 環境變數
  2. 當前工作目錄的 .env
  3. 使用者 home 的 ~/.openai.env

輸出：
  預設「當前工作目錄/slides/generated/」
  若該目錄不存在 → 建「./generated/」

成本記錄：
  ~/.openai-image-cost.log（每張一行）
"""

import os
import sys
import json
import base64
import argparse
from pathlib import Path
from datetime import datetime

MODEL = "gpt-image-2"
DEFAULT_SIZE = "1024x1024"
DEFAULT_QUALITY = "low"
DEFAULT_FORMAT = "jpeg"
DEFAULT_COMPRESSION = 85
DEFAULT_BACKGROUND = "opaque"
DEFAULT_MODERATION = "auto"
DEFAULT_N = 1

# 可用 size（含 2K / 4K）
VALID_SIZES = [
    "1024x1024",   # 方形
    "1536x1024",   # 橫
    "1024x1536",   # 直
    "2048x2048",   # 方 2K
    "3840x2160",   # 4K 橫
    "2160x3840",   # 4K 直
]

# 官方價格（USD per image，gpt-image-2 2026-04-21 後）
COST_USD = {
    ("low", "1024x1024"): 0.006,
    ("low", "1024x1536"): 0.005,
    ("low", "1536x1024"): 0.005,
    ("low", "2048x2048"): 0.024,   # 估，按 token 比例放大
    ("low", "3840x2160"): 0.045,
    ("low", "2160x3840"): 0.045,
    ("medium", "1024x1024"): 0.053,
    ("medium", "1024x1536"): 0.041,
    ("medium", "1536x1024"): 0.041,
    ("medium", "2048x2048"): 0.212,
    ("medium", "3840x2160"): 0.398,
    ("medium", "2160x3840"): 0.398,
    ("high", "1024x1024"): 0.211,
    ("high", "1024x1536"): 0.165,
    ("high", "1536x1024"): 0.165,
    ("high", "2048x2048"): 0.844,
    ("high", "3840x2160"): 1.580,
    ("high", "2160x3840"): 1.580,
}


# ───────────────────────────────────────────────────────
# STYLE PRESETS — 基於 OpenAI cookbook prompting guide
# ───────────────────────────────────────────────────────
STYLE_PRESETS = {
    "photorealistic": {
        "wrap": ("A photorealistic photograph of {S}. Realistic skin texture, "
                 "fabric wear, accurate proportions. Shot on 50mm lens, natural "
                 "soft lighting, shallow depth of field, eye-level perspective. "
                 "No watermark, no text overlay."),
        "quality": "high",
    },
    "cinematic": {
        "wrap": ("A cinematic still of {S}. Anamorphic widescreen, golden hour "
                 "rim lighting, atmospheric haze, color-graded teal and orange, "
                 "shallow depth of field, dramatic composition."),
        "quality": "medium",
    },
    "anime": {
        "wrap": ("Anime illustration of {S}. Studio Ghibli-inspired hand-painted "
                 "style, soft cel shading, expressive eyes, vibrant warm color "
                 "palette, detailed background."),
        "quality": "medium",
    },
    "watercolor": {
        "wrap": ("Watercolor painting of {S}. Soft outlines, warm earthy colors, "
                 "hand-painted look, paper texture visible, gentle washes, "
                 "suitable for children's book illustration."),
        "quality": "low",
    },
    "flat": {
        "wrap": ("Flat vector illustration of {S}. Clean geometric shapes, "
                 "limited color palette, no shadows or gradients, minimalist "
                 "composition, suitable for UI / infographic."),
        "quality": "low",
    },
    "3d_render": {
        "wrap": ("3D rendered scene of {S}. Octane render quality, studio "
                 "lighting, realistic materials and reflections, soft shadows, "
                 "isometric or eye-level perspective."),
        "quality": "medium",
    },
    "pixel_art": {
        "wrap": ("Pixel art of {S}. 16-bit retro game aesthetic, limited color "
                 "palette, sharp pixel edges, no anti-aliasing, suitable for "
                 "retro game sprite."),
        "quality": "low",
    },
    "line_art": {
        "wrap": ("Black-and-white line drawing of {S}. Clean continuous lines, "
                 "no shading, minimalist style, suitable for coloring book or "
                 "technical illustration."),
        "quality": "low",
    },
    "blueprint": {
        "wrap": ("Technical blueprint of {S}. White lines on blue background, "
                 "dimension labels, top/side/front orthographic views, "
                 "engineering drawing style."),
        "quality": "medium",
    },
    "isometric": {
        "wrap": ("Isometric illustration of {S}. 30-degree axonometric view, "
                 "clean geometric shapes, soft pastel color palette, minimal "
                 "shadows, suitable for tech/SaaS hero image."),
        "quality": "low",
    },
    "vintage_poster": {
        "wrap": ("Vintage 1960s poster of {S}. Limited color palette (cream, "
                 "orange, deep red, navy), bold serif typography, halftone "
                 "print texture, retro design."),
        "quality": "high",
    },
    "cyberpunk": {
        "wrap": ("Cyberpunk scene featuring {S}. Neon lights, rain-soaked "
                 "streets, holographic billboards, deep purple-pink-teal "
                 "palette, dystopian atmosphere."),
        "quality": "high",
    },
    "studio_product": {
        "wrap": ("Premium product photograph of {S}. Studio lighting, white "
                 "seamless background, clean shadows, sharp focus on product "
                 "details, suitable for e-commerce. No watermarks, no logos "
                 "added."),
        "quality": "high",
    },
    "infographic": {
        "wrap": ("Infographic showing {S}. Flat design, consistent icon style, "
                 "clear typography, organized grid layout. Include ONLY the "
                 "text shown verbatim, no extra labels, no watermarks."),
        "quality": "medium",
    },
}


def load_env_from_file(path: Path):
    if not path.exists():
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_env():
    load_env_from_file(Path.cwd() / ".env")
    load_env_from_file(Path.home() / ".openai.env")


def resolve_outdir(user_outdir):
    if user_outdir:
        return Path(user_outdir)
    cwd = Path.cwd()
    slides_dir = cwd / "slides"
    if slides_dir.exists():
        return slides_dir / "generated"
    return cwd / "generated"


def apply_style(prompt: str, style: str | None):
    """套 STYLE preset 包裝 prompt + 推薦 quality。回傳 (final_prompt, suggested_quality)"""
    if not style or style not in STYLE_PRESETS:
        return prompt, None
    preset = STYLE_PRESETS[style]
    return preset["wrap"].format(S=prompt), preset.get("quality")


def log_cost(quality, size, n, files):
    """寫成本到 ~/.openai-image-cost.log"""
    cost_per = COST_USD.get((quality, size), 0.0)
    total = cost_per * n
    log_path = Path.home() / ".openai-image-cost.log"
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        for fp in files:
            f.write(f"{stamp}  ${cost_per:.4f}  {quality:6s}  {size:11s}  {fp.name}\n")
    print(f"💰 本次費用：${total:.4f} USD ≈ NT${total*32:.2f}（累計記在 {log_path}）",
          file=sys.stderr)


def _save_results(result, name, n, outdir, ext):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved = []
    for i, item in enumerate(result.data):
        suffix = f"_{i + 1}" if n > 1 else ""
        out_path = outdir / f"{name}_{stamp}{suffix}.{ext}"
        png_bytes = base64.b64decode(item.b64_json)
        out_path.write_bytes(png_bytes)
        saved.append(out_path)
        print(f"  [OK] {out_path}")
    # revised_prompt 印出
    if hasattr(result.data[0], "revised_prompt") and result.data[0].revised_prompt:
        print(f"\n💡 OpenAI 優化後 prompt：\n   {result.data[0].revised_prompt[:300]}",
              file=sys.stderr)
    return saved


def draw(prompt, size, quality, fmt, compression, background, moderation, n, name, outdir):
    from openai import OpenAI
    if not os.getenv("OPENAI_API_KEY"):
        print("錯誤：找不到 OPENAI_API_KEY", file=sys.stderr)
        sys.exit(1)
    outdir.mkdir(parents=True, exist_ok=True)
    client = OpenAI()
    print(f"畫圖中（{MODEL}, size={size}, quality={quality}, fmt={fmt}, n={n}） -> {outdir}",
          file=sys.stderr)
    kwargs = dict(
        model=MODEL, prompt=prompt, size=size, quality=quality, n=n,
        output_format=fmt, background=background, moderation=moderation,
    )
    if fmt in ("jpeg", "webp"):
        kwargs["output_compression"] = compression
    result = client.images.generate(**kwargs)
    saved = _save_results(result, name, n, outdir, fmt)
    log_cost(quality, size, n, saved)
    return saved


def edit(prompt, image_path, mask_path, size, quality, fmt, compression, n, name, outdir):
    from openai import OpenAI
    if not os.getenv("OPENAI_API_KEY"):
        print("錯誤：找不到 OPENAI_API_KEY", file=sys.stderr)
        sys.exit(1)
    if not image_path.exists():
        print(f"錯誤：找不到來源圖片 {image_path}", file=sys.stderr)
        sys.exit(1)
    # 大小檢查
    size_mb = image_path.stat().st_size / 1024 / 1024
    if size_mb > 50:
        print(f"錯誤：來源圖 {size_mb:.1f}MB 超過 50MB 上限", file=sys.stderr)
        sys.exit(1)
    outdir.mkdir(parents=True, exist_ok=True)
    client = OpenAI()
    mode = "遮罩改圖" if mask_path else "全圖改圖"
    print(f"改圖中（{mode}, {MODEL}, size={size}, quality={quality}） -> {outdir}",
          file=sys.stderr)
    kwargs = dict(
        model=MODEL, image=open(image_path, "rb"),
        prompt=prompt, size=size, quality=quality, n=n,
    )
    if mask_path:
        if not mask_path.exists():
            print(f"錯誤：找不到遮罩圖片 {mask_path}", file=sys.stderr)
            sys.exit(1)
        kwargs["mask"] = open(mask_path, "rb")
    result = client.images.edit(**kwargs)
    saved = _save_results(result, name, n, outdir, fmt)
    log_cost(quality, size, n, saved)
    return saved


def main():
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", nargs="+")
    parser.add_argument("--style", default=None, choices=list(STYLE_PRESETS.keys()))
    parser.add_argument("--edit", default=None)
    parser.add_argument("--mask", default=None)
    parser.add_argument("--size", default=DEFAULT_SIZE, choices=VALID_SIZES)
    parser.add_argument("--quality", default=DEFAULT_QUALITY,
                        choices=["low", "medium", "high", "auto"])
    parser.add_argument("--format", default=DEFAULT_FORMAT,
                        choices=["png", "jpeg", "webp"])
    parser.add_argument("--compression", type=int, default=DEFAULT_COMPRESSION)
    parser.add_argument("--background", default=DEFAULT_BACKGROUND,
                        choices=["opaque", "auto"])
    parser.add_argument("--moderation", default=DEFAULT_MODERATION,
                        choices=["auto", "low"])
    parser.add_argument("--n", type=int, default=DEFAULT_N)
    parser.add_argument("--name", default="image")
    parser.add_argument("--outdir", default=None)
    args = parser.parse_args()

    raw_prompt = " ".join(args.prompt)
    final_prompt, suggested_q = apply_style(raw_prompt, args.style)

    # quality 決策：明確指定 > preset 推薦 > 預設
    quality = args.quality
    if args.quality == DEFAULT_QUALITY and suggested_q:
        quality = suggested_q
        print(f"🎨 套用 STYLE='{args.style}' → 自動 quality={quality}", file=sys.stderr)

    if args.style:
        print(f"📝 風格化 prompt：{final_prompt[:200]}...", file=sys.stderr)

    outdir = resolve_outdir(args.outdir)

    if args.edit:
        edit(final_prompt, Path(args.edit), Path(args.mask) if args.mask else None,
             args.size, quality, args.format, args.compression, args.n, args.name, outdir)
    else:
        draw(final_prompt, args.size, quality, args.format, args.compression,
             args.background, args.moderation, args.n, args.name, outdir)


if __name__ == "__main__":
    main()
