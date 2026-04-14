# B 專案資料集策略更新 — 2026-04-13

## 背景：為什麼需要更新

B 專案原始計畫（`B_PROJECT_BRIEF.md`）以 DAGM 2007 為主資料集，MVTec AD transistor subset 為 semiconductor anchor。經過深度搜尋和技術審查後，發現了更適合的資料集選項，同時也釐清了三條可行的技術路線。

---

## 一、新發現：真實 Wafer Defect 影像資料集

### ★ 主力候選：Roboflow Wafer Defect Instance Segmentation

- **連結**: https://universe.roboflow.com/wafer-irhuv/wafer-defect-rv1vx
- **影像數量**: 4,532 張
- **類型**: 真實 wafer die 光學影像（非 wafer map、非鋼材、非合成）
- **標註**: Instance segmentation（polygon mask），可直接轉 bbox
- **缺陷類別（7 類）**:
  - Block Etch
  - Coating Bad
  - Particle
  - PIQ Particle
  - PO Contamination
  - Scratch
  - SEZ Burnt
- **授權**: CC BY 4.0（免費商用）
- **格式匯出**: Roboflow 支援一鍵匯出 YOLOv8 detection / segmentation 格式
- **為什麼適合 B 專案**: 缺陷類別直接對應半導體製程 AOI 場景（Particle、Scratch、Contamination 等），4,532 張足以支撐正式 YOLO 訓練

### 補充資料集

| 資料集 | 連結 | 影像數 | 類別 | 用途 |
|--------|------|--------|------|------|
| Wafer Defect Detection | https://universe.roboflow.com/wafer-semiconductor/wafer-defect-detection-bbdhl | 760 | crease, scratch | 擴充 scratch 樣本 |
| Wafer4 | https://universe.roboflow.com/defect-efc9c/wafer4 | 327 | particle, scratch, other | 擴充 particle 樣本 |

---

## 二、三條技術路線（互補不互斥）

### 路線 1：Proxy Dataset → YOLO Pipeline

- **做法**: 用真實/proxy 影像資料集訓練 YOLO detection model
- **目前最佳選擇**: Roboflow Wafer Defect（4,532 張真實 wafer）
- **之前的選擇**: DAGM 2007（合成紋理）、NEU-DET（鋼材表面）
- **學理支撐**: cross-domain defect detection 文獻廣泛
- **優點**: 最快啟動、pipeline 立即可跑
- **限制**: 若用 proxy（非 wafer）資料，domain gap 會影響真實場景效果

### 路線 2：Synthetic Data Generation → YOLO

- **做法**: 用 Blender 3D 或 Stable Diffusion 合成 wafer 缺陷影像
- **學理支撐**:
  - Springer 2026 論文：Blender 合成 wafer scratch 影像，YOLOv8 直接在真實影像測試達 F1 > 0.96
  - 連結: https://link.springer.com/article/10.1007/s41060-026-01034-8
  - YOLO-SD（Springer 2024）：Stable Diffusion + ControlNet 生成 few-shot 缺陷影像
  - 連結: https://link.springer.com/article/10.1007/s13042-024-02175-7
  - AnomalyDiffusion（AAAI 2024）：few-shot anomaly image generator，開源
  - 連結: https://github.com/sjtuplayer/anomalydiffusion
- **優點**: domain gap 最小、可控制缺陷類型和數量
- **限制**: 需投入時間建 3D/生成 pipeline

### 路線 3：Vision Foundation Model（VFM）+ 少量 Fine-tune

- **做法**: 用 DINOv2 / CLIP 等通用視覺 backbone，少量真實影像 fine-tune
- **學理支撐**:
  - NVIDIA 官方技術文章：NV-DINOv2 → domain adaptation → fine-tune，準確率 93.84% → 98.51%
  - 連結: https://developer.nvidia.com/blog/optimizing-semiconductor-defect-classification-with-generative-ai-and-vision-foundation-models/
- **優點**: 最穩、最符合業界趨勢、不依賴特定 proxy dataset
- **限制**: 需要少量真實影像才能發揮最大效果

### 三條路線的關係

三條路線不是「選一條」，而是疊在不同層級：

```
┌─────────────────────────────────────┐
│ 應用層：YOLO → JSON → MES           │ ← 做一次，不用改
├─────────────────────────────────────┤
│ 資料層：Roboflow Wafer（現在）       │ ← 可換成 synthetic 或真實 AOI
├─────────────────────────────────────┤
│ 底層：COCO pre-trained backbone      │ ← 可換成 DINOv2 / VFM
└─────────────────────────────────────┘
```

每層可獨立升級，不影響其他層。

---

## 三、更新後的資料集排序

### B 專案

| 優先級 | 資料集 | 定位 | 理由 |
|--------|--------|------|------|
| **主力** | Roboflow Wafer Defect Seg（4,532 張） | 真實 wafer，7 類缺陷，instance seg | 真實半導體影像 + bbox/mask + YOLO 格式直接匯出 |
| **補充** | Roboflow Wafer Detection（760 張）+ Wafer4（327 張） | 擴充 scratch/particle 樣本 | 同為真實 wafer 影像 |
| **對照實驗** | NEU-DET（1,800 張） | cross-domain 對照組 | 驗證跨域 transfer 效果 |
| **方法驗證** | DAGM 2007 | 合成紋理 baseline | 保留做 ablation / 方法驗證 |

### A 專案（不變）

| 資料集 | 定位 |
|--------|------|
| WM-811K | wafer-level pattern classification |

---

## 四、對 B_PROJECT_BRIEF.md 的影響

### 需要更新的部分

1. **§2 "Why DAGM 2007 as the primary dataset"**
   - DAGM 2007 降為對照 / 方法驗證集
   - 主力改為 Roboflow Wafer Defect Instance Segmentation
   - 理由：找到了真實 wafer defect 影像資料集，不再需要以合成紋理做主力

2. **§3 "Why MVTec AD — transistor subset"**
   - MVTec transistor 作為 semiconductor anchor 的角色被 Roboflow Wafer Defect 取代
   - Roboflow 資料集本身就是真實半導體影像，不需要額外的 realism anchor

3. **§5 "First milestone — YOLO baseline on DAGM 2007"**
   - 改為 YOLO baseline on Roboflow Wafer Defect
   - `prepare_dagm.py` 需要對應的 `prepare_roboflow_wafer.py`
   - `dataset.yaml` 的 class names 從 class1-10 改為 7 類真實缺陷名稱

### 不需要改的部分

- §1 Project positioning — 不變
- §4 A → B JSON contract — 不變（JSON schema 與資料集無關）
- §5 的 pipeline 結構 — 不變（train → eval → predict → JSON）
- 所有 milestone 的 definition of done — 結構不變，只換資料集名稱

---

## 五、現有程式碼影響評估

| 檔案 | 影響 | 說明 |
|------|------|------|
| `src/b_yolo/prepare_dagm.py` | 需新增對應腳本 | 新增 `prepare_roboflow_wafer.py`，Roboflow 可直接匯出 YOLO 格式，轉換邏輯更簡單 |
| `src/b_yolo/train.py` | 改動極小 | 只需改 `DEFAULT_DATA` 指向新的 `dataset.yaml` |
| `src/b_yolo/predict.py` | 不需要改 | 輸出 JSON 格式與資料集無關 |
| `src/api.py` | 不需要改 | Phase 2 API 與資料集無關 |
| `docs/core/B_PROJECT_BRIEF.md` | 需更新 §2, §3, §5 | 資料集選擇理由更新 |

---

## 六、面試 / 報告定位建議

### 可以說

> 公開的半導體 AOI 影像資料集極度稀缺，大部分 FAB 資料是 proprietary。我在 Roboflow Universe 上找到一個 4,532 張真實 wafer die 影像的 instance segmentation 資料集，包含 7 類半導體製程常見缺陷（Particle、Scratch、Contamination 等）。我以此作為主訓練集建立 YOLO detection pipeline，同時保留 DAGM 2007 和 NEU-DET 做 cross-domain 對照實驗。Pipeline 設計上，資料層和模型層解耦，未來有真實 AOI 影像或 synthetic data 時，只需替換 data folder，不用重建 pipeline。這個分層設計參考了 NVIDIA 推薦的 VFM → domain adaptation → fine-tune workflow。

### 不要說

- ❌ 「我用鋼材資料集訓練 wafer AOI model」
- ❌ 「我的 model 可以直接部署到產線」
- ❌ 「DAGM 2007 是半導體資料集」

---

## 七、關鍵參考資料

| 資源 | 連結 | 用途 |
|------|------|------|
| Roboflow Wafer Defect Seg（主力） | https://universe.roboflow.com/wafer-irhuv/wafer-defect-rv1vx | B 專案主訓練集 |
| Roboflow Wafer Detection | https://universe.roboflow.com/wafer-semiconductor/wafer-defect-detection-bbdhl | 補充資料 |
| Roboflow Wafer4 | https://universe.roboflow.com/defect-efc9c/wafer4 | 補充資料 |
| NEU-DET（Kaggle） | https://www.kaggle.com/datasets/kaustubhdikshit/neu-surface-defect-database | 對照實驗 |
| DAGM 2007 | 原 B_PROJECT_BRIEF.md 已有連結 | 方法驗證 |
| Springer 2026: Synthetic Wafer + YOLO | https://link.springer.com/article/10.1007/s41060-026-01034-8 | 未來路線參考 |
| NVIDIA VFM Semiconductor Workflow | https://developer.nvidia.com/blog/optimizing-semiconductor-defect-classification-with-generative-ai-and-vision-foundation-models/ | 底層架構參考 |
| YOLO-SD（Stable Diffusion） | https://link.springer.com/article/10.1007/s13042-024-02175-7 | Synthetic augmentation 參考 |
| AnomalyDiffusion（AAAI 2024） | https://github.com/sjtuplayer/anomalydiffusion | Few-shot defect generation |
| Awesome Few-Shot Defect Image Gen | https://github.com/bcmi/Awesome-Few-Shot-Defect-Image-Generation | 綜合參考 |
