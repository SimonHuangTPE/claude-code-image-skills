---
name: draw
description: OpenAI gpt-image-2 生圖技能（全域可用）— 含 14 種風格 preset、2K 解析度、自動費用記錄。當使用者要求「畫一張」、「生一張圖」、「做一張圖」、「產生圖片」、「畫個封面」、「畫插圖」、「畫示意圖」、「畫分鏡」、「修圖」、「改圖」、「換背景」、「加 logo」等任何 AI 生成或編輯圖像情境時使用。會自動依風格 keyword 套對應 STYLE_PRESETS 包裝 prompt（photorealistic / cinematic / anime / watercolor / flat / 3d_render / pixel_art / line_art / blueprint / isometric / vintage_poster / cyberpunk / studio_product / infographic）。預設 quality=low（NT$0.19/張），存當前資料夾的 generated/ 或 slides/generated/。
---

# 小克生圖技能（gpt-image-2 + 風格優化版）

> 對應 OpenAI 官方 prompting guide（[cookbook](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide)）的 14 種 production 風格自動套用

## 觸發情境

### 生圖（→ draw mode）
- 「畫一張 XX」「生一張圖」「做一張圖」「產生圖片」
- 「畫個封面 / 插圖 / 示意圖 / 分鏡 / 海報」
- 「幫我生圖」「弄張圖」

### 改圖（→ edit mode，需提供 --edit 圖片路徑）
- 「改這張圖」「修圖」「修改圖片」「重新潤色」
- 「把背景換成 XX」「加上 logo」「去除浮水印」「換衣服」
- 「P 圖」「修一下這張」

## 腳本路徑
- macOS/Linux：`~/.claude/skills/draw/draw.py`
- Windows：`C:/Users/<使用者>/.claude/skills/draw/draw.py`

## 使用方式

```bash
python ~/.claude/skills/draw/draw.py "要畫的內容" --style anime --name 檔名前綴
```

### 參數速查

| 參數 | 預設 | 說明 |
|------|------|------|
| `prompt` | （必填）| 要畫什麼 |
| `--style` | 無 | 套 STYLE preset（見下表）|
| `--size` | `1024x1024` | 1024x1024 / 1536x1024 / 1024x1536 / **2048x2048** / **3840x2160** / **2160x3840** |
| `--quality` | `low` | low（NT$0.19）/ medium（NT$1.7）/ high（NT$6.75）/ auto |
| `--format` | `jpeg` | png / jpeg / webp（jpeg/webp 檔小很多）|
| `--compression` | `85` | 0-100，jpeg/webp 用 |
| `--background` | `opaque` | opaque / auto（gpt-image-2 不支援 transparent）|
| `--moderation` | `auto` | auto / low（內部創意較寬鬆）|
| `--n` | 1 | 1-8 張 |
| `--name` | `image` | 檔名前綴 |
| `--outdir` | 自動 | 輸出目錄 |
| `--edit IMAGE_PATH` | 無 | 改圖模式（指定來源圖）|
| `--mask MASK_PATH` | 無 | 遮罩（搭配 --edit，需含 alpha）|

## 14 個 STYLE preset（自動套）

| 客人說 | 套用 `--style` | 自動 quality |
|--------|---------------|-------------|
| 真實照片/寫實/逼真/拍照 | `photorealistic` | high |
| 電影感/cinematic | `cinematic` | medium |
| 動漫/卡通/日漫/吉卜力/宮崎駿風 | `anime` | medium |
| 水彩/插畫/童書風 | `watercolor` | low |
| 扁平/flat/向量/icon 風 | `flat` | low |
| 3D/立體/Octane render | `3d_render` | medium |
| 像素/pixel/8bit/復古遊戲 | `pixel_art` | low |
| 線稿/著色本/技術插圖 | `line_art` | low |
| 藍圖/工程圖/技術圖 | `blueprint` | medium |
| 等角/isometric/SaaS hero | `isometric` | low |
| 復古海報/老海報/60 年代 | `vintage_poster` | high |
| 賽博龐克/cyberpunk/未來城市 | `cyberpunk` | high |
| 商品照/產品圖/電商 | `studio_product` | high |
| 資訊圖/圖解/infographic | `infographic` | medium |

## 範例

```bash
# 純生圖
python ~/.claude/skills/draw/draw.py "一隻穿西裝的龍蝦" --style cinematic

# 商品圖（自動 high quality + studio 設定）
python ~/.claude/skills/draw/draw.py "iPhone 15 Pro 太空黑色" --style studio_product --name iphone

# 2K 海報
python ~/.claude/skills/draw/draw.py "Claude Code 教學海報" --size 2048x2048 --style vintage_poster

# 改圖（局部 mask）
python ~/.claude/skills/draw/draw.py "把背景換成海底" --edit ./photo.jpg --name edited

# 多張變體
python ~/.claude/skills/draw/draw.py "可愛的科技風機器人" --style 3d_render --n 4
```

## 判斷 quality 的優先順序

1. 使用者明確指定 `--quality high` → 用 high
2. 套了 `--style` 且 quality 是預設 → **用 preset 推薦的 quality**（例如 studio_product 自動 high）
3. 都沒指定 → low（省錢）

**原則：高密度文字 / 商品照 / 寫實人像 / 海報 → high；其餘 low/medium**

## 自動費用記錄

每張圖會寫一行到 `~/.openai-image-cost.log`：
```
2026-04-26 14:23:11  $0.006  low  1024x1024  test_iphone_20260426_142311.jpeg
```

要看本月累計：
```bash
grep "^2026-04" ~/.openai-image-cost.log | awk '{sum+=$2} END{printf "Total: $%.3f\n", sum}'
```

## revised_prompt 學習回饋

OpenAI 會自動優化你給的 prompt，腳本會印出 revised 版讓你看 AI 怎麼改：
```
原 prompt: 一隻黑貓
優化後:    A photograph of a sleek black domestic cat with bright green eyes,
           sitting alert on a wooden floor, soft natural window light...
```

幾次後就能學到怎麼下更好的 prompt。

## 錯誤處理
- `403 Organization must be verified` → 到 platform.openai.com/settings/organization/general 做 Individual 驗證
- `401 Invalid API key` → 檢查 `~/.openai.env`
- `429 Rate limit` → 額度用完，到 Billing 儲值
- `400 image too large` → 改圖模式 input image 必須 < 50MB

## 安全
- API Key 在 `~/.openai.env`（不在專案 repo 內，git 不會追）
- 所有生圖在 OpenAI 端，輸出存本機
- mask 必須含 alpha channel（透明區域 = 要修改的範圍）
