# Claude Code Image Skills

Two image-generation skills for Claude Code, powered by OpenAI **gpt-image-2** (released 2026-04-21).

> 在 Claude Code 對話裡一句話生圖／批次生圖，自動套用官方 cookbook 推薦的風格化 prompt。

## ✨ 內建功能

| Skill | 用途 | 觸發詞 |
|-------|------|--------|
| [`draw`](./draw) | 單張生圖 / 改圖（14 種風格 preset、2K 解析度、自動費用記錄）| 「畫一張」「生一張圖」「修圖」「改背景」 |
| [`draw-batch`](./draw-batch) | 同主體 / 同角色多張變體（pose / scene / angle / expression / outfit / time / weather / mood）| 「角色設定圖」「同產品多視角」「mood board」「分鏡圖」「8 連發」 |

---

## 🚀 安裝（一次設定全域可用）

### 1. OpenAI 帳號準備（手動）

| 步驟 | 連結 |
|------|------|
| ① 註冊 + 儲值 ≥ US$5 | [Billing](https://platform.openai.com/account/billing) |
| ② 組織 Individual 驗證（**必做**，否則 403）| [Verifications](https://platform.openai.com/settings/organization/general) |
| ③ 取 API Key | [API keys](https://platform.openai.com/api-keys) |

### 2. 安裝 SDK + 寫 Key

```bash
pip install openai --break-system-packages
echo "OPENAI_API_KEY=sk-..." > ~/.openai.env
chmod 600 ~/.openai.env
```

### 3. Clone Skills 到 `~/.claude/skills/`

```bash
mkdir -p ~/.claude/skills
cd ~/.claude/skills
git clone https://github.com/SimonHuangTPE/claude-code-image-skills.git tmp
mv tmp/draw .
mv tmp/draw-batch .
rm -rf tmp
```

開新的 Claude Code 對話，輸入「畫一隻黑貓」即可測試。

---

## 💰 費用速查（gpt-image-2 官方價）

| Quality | 1024×1024 | 2048×2048 | 3840×2160 |
|---------|-----------|-----------|-----------|
| low     | $0.006 / NT$0.19 | $0.024 / NT$0.77 | $0.045 / NT$1.4 |
| medium  | $0.053 / NT$1.7  | $0.212 / NT$6.8  | $0.398 / NT$13 |
| high    | $0.211 / NT$6.8  | $0.844 / NT$27   | $1.580 / NT$51 |

每張會記錄到 `~/.openai-image-cost.log`。

---

## 🎨 STYLE Presets（draw skill 內建 14 種）

| 風格 keyword | preset | 推薦 quality |
|-------------|--------|-------------|
| 真實照片 / 寫實 / 拍照 | `photorealistic` | high |
| 電影感 / cinematic | `cinematic` | medium |
| 動漫 / 吉卜力 / 宮崎駿 | `anime` | medium |
| 水彩 / 童書插畫 | `watercolor` | low |
| 扁平 / 向量 / icon | `flat` | low |
| 3D / Octane render | `3d_render` | medium |
| 像素 / 8bit / 復古遊戲 | `pixel_art` | low |
| 線稿 / 著色本 | `line_art` | low |
| 藍圖 / 工程圖 | `blueprint` | medium |
| 等角 / SaaS hero | `isometric` | low |
| 復古海報 / 60 年代 | `vintage_poster` | high |
| 賽博龐克 | `cyberpunk` | high |
| 商品照 / 電商 | `studio_product` | high |
| 資訊圖 / infographic | `infographic` | medium |

---

## 🔁 batch 變體軸（draw-batch skill 內建 8 種）

| `--vary` | 變體值範例 |
|---------|-----------|
| `pose` | standing / sitting / running / jumping / dancing / sleeping / fighting / walking |
| `scene` | forest / city / beach / mountain / desert / cafe / library / spaceship |
| `angle` | front / side / back / three-quarter / top-down / low-angle / aerial / macro |
| `expression` | smiling / serious / surprised / thoughtful / laughing / crying / angry / peaceful |
| `outfit` | casual / formal / sporty / winter / summer / traditional / armor / pajamas |
| `time` | dawn / morning / noon / afternoon / dusk / night / midnight / golden hour |
| `weather` | sunny / rainy / snowy / foggy / stormy / cloudy / windy / rainbow |
| `mood` | peaceful / dramatic / mysterious / joyful / melancholy / energetic / nostalgic / surreal |

或用 `--custom "list1,list2,list3"` 自訂。

---

## 📚 對 Claude Code 直接說話即可

| 你說 | Claude 自動跑的指令 |
|------|-------------------|
| 「畫一隻穿西裝的龍蝦」 | `draw.py "穿西裝的龍蝦" --style cinematic` |
| 「iPhone 商品照」 | `draw.py "iPhone 15 Pro" --style studio_product` |
| 「Claude 安裝流程圖」 | `draw.py "Claude Code 安裝步驟" --style infographic` |
| 「畫個太空貓 4 個動作」 | `draw_batch.py "太空貓" --vary pose --n 4 --style anime` |
| 「黑馬克杯 4 個視角」 | `draw_batch.py "黑色陶瓷馬克杯" --vary angle --n 4 --style studio_product` |
| 「同小屋一日六時」 | `draw_batch.py "山中小屋" --vary time --n 6 --style watercolor` |

---

## 🔧 進階參數

`draw`：完整參數見 [draw/SKILL.md](./draw/SKILL.md)

`draw-batch`：含 `--reference` 模式（第一張當 reference image，後續 edit 確保角色一致），詳見 [draw-batch/SKILL.md](./draw-batch/SKILL.md)

---

## 🔗 官方資源

- [OpenAI 官方 prompting guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide)
- [gpt-image-2 release](https://community.openai.com/t/introducing-gpt-image-2-available-today-in-the-api-and-codex/1379479)
- [API reference](https://developers.openai.com/api/docs/guides/image-generation)
- [社群 prompt 範例庫](https://github.com/EvoLinkAI/awesome-gpt-image-2-prompts)

---

## 📝 License

MIT — 自由 fork 修改。

## 致敬

優化參考自 [@MathRuffian 的 EP11 懶人包](https://github.com/mathruffian-dot/claude-code-lazy-packs)，補完官方 prompting guide 14 風格 + 批次變體 + 2K 解析度 + 費用追蹤。
