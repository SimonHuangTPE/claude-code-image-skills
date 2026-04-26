---
name: draw-batch
description: OpenAI gpt-image-2 批次變體生圖 — 鎖定同主體/角色/風格，自動產生多張變體（不同動作、場景、視角、表情、服裝、時間、天氣、心情）。當使用者要求「畫一組角色設定圖」、「同角色多動作」、「同產品多視角」、「mood board」、「分鏡圖」、「同場景不同時間」、「character sheet」、「多張變體」、「8 連發」、「畫一系列」等需要批次生成相關圖像時使用。內建 8 種變體軸（pose/scene/angle/expression/outfit/time/weather/mood）+ 自訂變體列表，會輸出整理好的資料夾含 `_summary.md` 對照表。
---

# 批次變體生圖（draw-batch）

> 適用：character sheet、product sheet、mood board、storyboard、season variants

## 觸發情境

- 「同角色多動作 / 多表情 / 多服裝」
- 「畫一組 character sheet / 角色設定圖 / 角色三視圖」
- 「產品多視角 / 多顏色 / 多場景」
- 「mood board」「氛圍板」
- 「分鏡圖 4 格 / 8 格」
- 「同場景不同時間 / 不同天氣」
- 「畫一系列 XX」「連發 8 張」「批次變體」

## 腳本路徑

`~/.claude/skills/draw-batch/draw_batch.py`

## 使用方式

```bash
python ~/.claude/skills/draw-batch/draw_batch.py "主體描述" \
  --style 風格 \
  --vary 變體軸 \
  --n 變體數量 \
  --name 檔名前綴
```

### 參數速查

| 參數 | 預設 | 說明 |
|------|------|------|
| `prompt` | 必填 | 主體描述（會在所有變體中保持一致）|
| `--vary` | `pose` | 變體軸（見下表）或自訂 list |
| `--n` | 4 | 變體數量（1-8）|
| `--style` | 無 | 風格（沿用 draw skill 的 14 個 preset）|
| `--size` | `1024x1024` | 同 draw skill |
| `--quality` | `low` | 批次預設 low 省錢；高品質 character sheet 用 medium |
| `--reference` | False | 用第一張當 reference image，後續用 edit 模式（一致性更高，較貴）|
| `--custom` | 無 | 自訂變體 list，逗號分隔，覆蓋 --vary |
| `--name` | `batch` | 檔名前綴 |

## 內建 8 個變體軸

| `--vary` | 變體內容（隨機抽 N 個）|
|---------|---------------------|
| `pose` | standing / sitting / running / jumping / dancing / sleeping / fighting / walking |
| `scene` | forest / city street / beach / mountain / desert / cafe interior / library / spaceship |
| `angle` | front view / side view / back view / three-quarter view / top-down view / low-angle / aerial |
| `expression` | smiling / serious / surprised / thoughtful / laughing / crying / angry / peaceful |
| `outfit` | casual / formal suit / sporty / winter coat / summer dress / traditional / armor / pajamas |
| `time` | dawn / morning / noon / afternoon / dusk / night / midnight / golden hour |
| `weather` | sunny / rainy / snowy / foggy / stormy / cloudy / windy / rainbow after rain |
| `mood` | peaceful / dramatic / mysterious / joyful / melancholy / energetic / nostalgic / surreal |

## 範例

### 角色設定圖（同角色 4 個動作）
```bash
python draw_batch.py "穿太空服的橘色貓咪太空人" \
  --vary pose --n 4 --style anime --name astrocat
```

→ 4 張：standing / running / sitting / jumping，全部都是同一隻橘貓太空人。

### 產品多視角（電商常用）
```bash
python draw_batch.py "黑色陶瓷馬克杯 上面印 4wheels 字樣" \
  --vary angle --n 4 --style studio_product --name mug
```

→ 4 張：front / side / three-quarter / top-down 視角。

### 同場景不同時間（mood board）
```bash
python draw_batch.py "山中小屋與杉樹" \
  --vary time --n 6 --style watercolor --name cabin
```

→ 6 張：dawn / morning / noon / dusk / night / golden hour。

### 自訂變體列表
```bash
python draw_batch.py "穿西裝的龍蝦" \
  --custom "drinking coffee, riding skateboard, conducting orchestra, programming on laptop" \
  --style cinematic --name lobster
```

→ 4 張：每張對應 custom 列的一個動作。

### 一致性優先（用第一張當 reference）
```bash
python draw_batch.py "金髮藍眼少女 戴貓耳朵 紅色洋裝" \
  --vary expression --n 4 --reference --name girl
```

→ 第一張 generate，後 3 張用 edit + 第一張當 reference，臉部更一致。
（成本約 4 倍，因為 edit 也算生圖；用於需要嚴格角色一致時）

## 輸出結構

```
generated/batch_<timestamp>_<name>/
  ├── 01_<vary>_<value>.jpeg    # 例：01_pose_standing.jpeg
  ├── 02_<vary>_<value>.jpeg
  ├── ...
  └── _summary.md               # 列出每張的完整 prompt + 費用
```

`_summary.md` 範例：
```markdown
# Batch: astrocat (2026-04-26 14:23)

主體：穿太空服的橘色貓咪太空人
風格：anime
變體軸：pose × 4

## 01_pose_standing.jpeg
Prompt: ... standing ...
Cost: $0.006

## 02_pose_running.jpeg
Prompt: ... running ...
Cost: $0.006
...

**總費用：$0.024 ≈ NT$0.77**
```

## 一致性策略

1. **預設模式（獨立生成）**：每張 prompt 都帶完整主體描述，靠 prompt 自身保持一致
   - 優：快、便宜（n × low quality）
   - 缺：細節（臉、配件、顏色）可能輕微飄移

2. **`--reference` 模式（reference-based）**：第一張獨立生，之後每張用 edit 模式 + 第一張當 reference
   - 優：角色臉部、服裝細節高度一致
   - 缺：成本約 2-4 倍（edit 比 generate 貴）
   - 用於：character sheet、需要嚴格角色一致的多動作圖

## 費用預估（low quality 1024x1024）

| n | 獨立模式 | reference 模式 |
|---|---------|--------------|
| 4 | $0.024 ≈ NT$0.77 | $0.06 ≈ NT$2 |
| 8 | $0.048 ≈ NT$1.5 | $0.12 ≈ NT$4 |

medium quality × 8 ≈ NT$13；high × 8 ≈ NT$54。

## AI 判斷該用哪個變體軸

| 客人說 | 用 `--vary` |
|--------|------------|
| 多動作 / character sheet / 角色設定 | `pose` |
| 多表情 / 表情包 | `expression` |
| 多服裝 / 換衣服 | `outfit` |
| 多視角 / 三視圖 / 多角度 / 商品多角度 | `angle` |
| 多場景 / 多地點 | `scene` |
| 不同時間 / 一日變化 | `time` |
| 不同天氣 / 季節 | `weather` |
| mood board / 氛圍 / 心情變化 | `mood` |

不確定問客人，或預設 `pose`。
