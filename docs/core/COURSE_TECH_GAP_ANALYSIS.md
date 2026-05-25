# AOI 專案 — 課程技術缺口分析（修訂版）

> 來源：AI 影像辨識工程師特訓班 W1–W7 vs AOI_Defect_Triage_v1 實際專案狀態
> 建立日期：2026-04-29
> 修訂日期：2026-05-25（realigned after PR #7 — canonical phase logic per AOI_MASTER_ROADMAP §14；前次修訂 2026-04-29 對齊 Phase 1-3 狀態 + MASTER_ROADMAP + B_PROJECT_BRIEF）
> 狀態：規劃中，尚未實作

---

## 修訂說明

初版在未完整閱讀專案文件的情況下撰寫。本修訂版根據以下文件對齊：

- `AOI_PROJECT_STATE.md`：Phase 1 完成 (89.28%)、Phase 2 完成 (FastAPI)、Phase 3 已驗證關閉
- `AOI_MASTER_ROADMAP.md`：Phase 4 (LLM defect/evidence explanation，§14 canonical)、Phase 5 (MES Integration)；Batch Inference / Production IO 重新定位為支援性 production-hardening / 未來 serving 能力，非 Phase 4 本體
- `B_PROJECT_BRIEF.md`：YOLO B-project Milestone 1 (mAP50=0.715, 20 epoch)
- `MASTER_ROADMAP §10 Deferred Items`：Docker/K8s、CI/CD、LLM explanation 等明確延後
- `src/train.py`：確認無 augmentation、3 層 CNN、weighted CE、Adam+StepLR

**重要原則**：課程技術建議不覆蓋後續主線 Phase（Phase 4 LLM defect/evidence explanation、Phase 5 MES integration）的 pipeline 規劃。模型改進獨立為 Enhancement Track，並受 DG gating 約束（DG-1..DG-4 穩定 + B8.3 closeout 後才執行），不自動與主線並行。

---

## 現有專案已用到的技術

| 技術 | 課程來源 | 專案位置 | 狀態 |
|------|---------|---------|------|
| Custom CNN (3× Conv-BN-ReLU-MaxPool → FC) | 基礎 DL | `src/train.py` WaferCNN | ✅ Phase 1，test acc 89.28% |
| Inverse-frequency weighted CE | W1 Loss 延伸 | `src/train.py` | ✅ 已實作 |
| YOLOv8n 物件偵測 | W3 YOLO 系列 | `src/b_yolo/train.py` | ✅ B-project，mAP50=0.715 |
| FastAPI /predict endpoint | 自建 | `src/api.py` | ✅ Phase 2 |
| Adam + StepLR(step=7, γ=0.5) | 基礎 DL | `src/train.py` | ✅ 已實作 |
| Locked JSON contract (AOI output) | 自建 | `src/api.py` | ✅ Phase 2 |

### Phase 1 已知弱點（影響改進方向）

| Class | Test Accuracy | 樣本數 | 問題 |
|-------|-------------|--------|------|
| none | 91.52% | 110,701 | OK（dominant class 遮蔽整體數據） |
| Scratch | **31.89%** | 693 | 嚴重不足 — 最急需改善 |
| Loc | **45.31%** | 1,973 | 不足 |
| Center | 59.38% | 832 | 低 |
| Donut | 61.64% | 146 | 低但樣本極少 |
| Edge-Ring | 66.07% | 1,126 | 中等 |
| Edge-Loc | 66.74% | 2,772 | 中等 |

**Val-Test gap**：96.40% → 89.28%，存在過擬合。目前無任何 data augmentation。

---

## Enhancement Track — 課程技術可直接改進 Phase 1 Baseline

> 以下改進不影響後續主線 Phase（Phase 4 LLM explanation 起）的 pipeline 規劃。獨立為 Enhancement Track，但受 DG gating 約束（DG-1..DG-4 穩定 + B8.3 closeout 後才執行），非隨時可執行。

### E1. Data Augmentation（基礎 + CutMix）(W1 延伸)

- **現況**：`src/train.py` transforms 只有 Resize(64) + Normalize(0.5, 0.5)，無任何 augmentation
- **改法**：
  - Step 1：加基礎 augmentation — RandomRotation(90°)、RandomHorizontalFlip、RandomVerticalFlip（wafer map 旋轉對稱，合理操作）
  - Step 2：加 CutMix（W1 延伸）— 混合兩張 wafer map，label 按面積比混合
- **預期效果**：Val-Test gap 縮小（96.4%→89.3% 過擬合問題），rare class 泛化提升
- **工作量**：Step 1 約 30 分鐘、Step 2 約 1 小時
- **影響檔案**：`src/train.py`（dataset transforms 區塊）
- **面試加分**：「不只知道要做 augmentation，還知道 wafer map 哪些操作是物理上合理的 — rotation OK 因為晶圓旋轉對稱，color jitter 不適用因為是二值圖」

### E2. Focal Loss (W1 延伸)

- **現況**：`nn.CrossEntropyLoss(weight=class_weights)` — class weight 有幫助但 Scratch 仍只有 31.89%
- **改法**：`focal_loss(alpha=inv_freq, gamma=2.0)` — 額外降低 easy sample 的梯度，讓模型更專注 hard example
- **預期效果**：Scratch / Loc 等 rare class 的 recall 提升（focal loss 對 class imbalance 效果優於單純 weight）
- **工作量**：~30 分鐘，在 `src/train.py` 加一個 loss function
- **影響檔案**：`src/train.py`
- **面試加分**：「weighted CE 是第一步，focal loss 是第二步。YOLO 系列 (W3) 也用 focal loss — 我知道這個 loss 在偵測和分類都適用」

### E3. ResNet Backbone + Transfer Learning (W1)

- **現況**：自建 3 層 CNN（~1.3M params），Scratch 31.89%
- **改法**：`torchvision.models.resnet18(pretrained=True)`，凍結前 3 個 stage，只 fine-tune stage4 + 新 FC 層。input 需從 1-channel 擴展（repeat 3 次或改第一層 conv）
- **預期效果**：test accuracy 92-95%（ResNet skip connection 保留 Scratch 細微紋理特徵）
- **工作量**：~2 小時，改 `src/train.py` model 定義 + 新增 `src/models/resnet_backbone.py`
- **影響檔案**：`src/train.py`、新增 `src/models/resnet_backbone.py`
- **注意**：需驗證 input channel 處理（WM-811K 是 1-channel 灰階 64×64）
- **面試加分**：「知道什麼時候該用 pretrained vs 從頭訓練 — 我的 baseline 是從頭訓練，確認 89% 後才升級到 transfer learning，這是工程紀律」

### E4. Grad-CAM 可解釋性 (W1)

- **現況**：沒有模型解釋機制，無法驗證模型是看缺陷區域還是背景
- **改法**：對 WaferCNN 最後一個 Conv 層做 Grad-CAM，可視化 class activation
- **預期效果**：不提升 accuracy，但能 debug Scratch 31.89% 的根因（模型可能看了 background noise 而非 scratch pattern）
- **工作量**：~1 小時，新增 `src/explainability.py`
- **影響檔案**：新增 `src/explainability.py`，不動 `src/train.py`
- **面試加分**：「AOI 業界面試必問 — 你怎麼知道模型在看對的地方？我有 Grad-CAM 可以直接展示」

### E5. Optuna 超參數搜尋 (W1)

- **現況**：固定 lr=1e-3、batch=64、epoch=20、StepLR(7, 0.5) — 未做過搜尋
- **改法**：用 Optuna (W1 有教 Bayesian Optimization + TPE) 搜尋 lr / batch / scheduler / dropout
- **預期效果**：在同一架構下可能提升 1-3%，更重要的是找到最佳 focal loss γ 值
- **工作量**：~2 小時
- **影響檔案**：新增 `src/hparam_search.py`
- **面試加分**：「不只是跑一組參數就算了，我做過系統性搜尋」

---

## Expansion Track — 課程技術擴展新能力

### X1. Multi-label Classification (W1/W3)

- **現況**：single-label softmax（一片 wafer 只歸一類）
- **改法**：sigmoid BCE 取代 softmax CE，允許一片 wafer 同時有 Scratch + Edge-loc
- **預期效果**：更貼近工廠現實（一片 wafer 可能有多種缺陷模式重疊）
- **工作量**：~1.5 小時，改 loss + 評估指標 (per-class AP, mAP)
- **影響檔案**：`src/train.py`（loss 定義 + metrics）、`src/evaluate.py`
- **注意**：WM-811K 原始標註是 single-label，需要確認是否有 multi-label 的 ground truth
- **面試加分**：「我知道現場一片 wafer 不會只有一種缺陷 — W3 YOLO 的 multi-label 機制 (sigmoid per class) 我也熟」

### X2. ViT 對比實驗 (W1)

- **現況**：只有 CNN
- **改法**：`timm` 的 ViT-tiny pretrained，與 CNN / ResNet 做 accuracy 對比
- **預期效果**：64×64 小圖上 ViT 可能不如 CNN（W1 筆記提到 ViT 在小資料集需要 2-4x 計算資源），但實驗數據本身有面試價值
- **工作量**：~2 小時
- **影響檔案**：新增 `src/models/vit_baseline.py`
- **面試加分**：「Transformer 在小圖效果不一定好 — 我跑過實驗知道差多少，這是工程判斷力」

### X3. U-Net 缺陷區域分割 (W2)

- **現況**：只有 wafer-level 分類，不知道缺陷具體在哪個區域
- **改法**：用 WM-811K wafer map 作為 pseudo-label 訓練 U-Net，用 mIoU (W2 核心指標) 評估
- **預期效果**：從「這片 wafer 有 Scratch」→「Scratch pattern 集中在 edge zone」
- **工作量**：~4 小時（含 pseudo-label 生成 + U-Net 訓練）
- **影響檔案**：新增 `src/models/unet_segmentation.py`、`src/prepare_segmentation_data.py`
- **與 B-project 關係**：B-project YOLO 做 bbox 偵測（camera layer），U-Net 做 pixel 分割（wafer map layer）— 不同資料層、互補不衝突
- **面試加分**：「分類 + 偵測 + 分割 三層能力我都有 — 對應 W1 + W3 + W2 的課程脈絡」

---

## Advanced Track — 需要額外資料或算力

### V1. CycleGAN / CyEDA 跨機台 Domain Adaptation (W6)

- **現況**：所有資料來自 WM-811K 單一資料集
- **課程技術**：CyEDA (W6) 用 blending mask + cycle-object edge consistency，不需 paired data，FID 優於 CycleGAN
- **改法**：如果有不同 AOI 機台的影像，用 CyEDA 做風格轉換讓模型跨機台不用重訓
- **預期效果**：解決半導體業真實的 domain shift 問題
- **前提**：需要不同機台的 AOI 影像（目前沒有）
- **面試加分**：「我知道 domain shift 在半導體是真實問題 — CyEDA 比 CycleGAN 更穩定因為有 edge consistency loss 防止 steganography」

### V2. Stable Diffusion + ControlNet 合成稀缺缺陷 (W7)

- **現況**：Scratch 只有 693 筆，直接導致 test accuracy 31.89%
- **課程技術**：ControlNet (W7) 用 zero convolution 加控制條件，可以用邊緣圖引導生成
- **改法**：以 Scratch 的 wafer map 邊緣為 ControlNet 條件，生成更多 Scratch 訓練樣本
- **預期效果**：rare class 從 693 → 3000+ 筆，Scratch accuracy 從 31.89% → 60%+
- **工作量**：~4 小時，需要 GPU
- **前提**：需要驗證生成樣本的品質（FID / IS 指標，W6 有教）
- **面試加分**：「用生成式 AI 解 class imbalance — 這不是單純的 oversampling，是 condition-guided generation」

### V3. DreamBooth / Textual Inversion 小樣本學習 (W7)

- **現況**：新缺陷類型需要重新收集大量資料 + 重訓整個模型
- **課程技術**：DreamBooth 用 3-5 張照片 + rare-token identifier + prior preservation loss；Textual Inversion 只學一個 embedding vector
- **改法**：從 3-5 張新缺陷樣本學習新類型，不需重訓整個模型
- **預期效果**：新缺陷類型上線時間從「數週」→「1 天」
- **工作量**：~3 小時，需要 GPU
- **面試加分**：「客戶說有新缺陷類型，我一天內可以加進系統 — 用 DreamBooth 不是重訓整個 pipeline」

---

## 與現有 Phase 規劃的對應關係

```
現有 Phase 結構（canonical — 見 AOI_MASTER_ROADMAP §5 + §14；以下僅引用，不重新定義）：
  Phase 1: CNN Baseline           ✅ 完成 (89.28%)
  Phase 2: FastAPI Service        ✅ 完成
  Phase 3: Detection Feasibility  ✅ 已驗證關閉（WM-811K 不適合偵測）
  Phase 4: LLM defect/evidence explanation   → 規劃中（Stage 2 優先，§14 canonical）
  Phase 5: AOI → MES Integration             → 規劃中（gated：需 MES sidecar spec）
  （Batch Inference + Production IO：支援性 production-hardening / 未來 serving 能力，非獨立 Phase 本體）

Enhancement Track（不佔 Phase 編號；受 DG gating）：
  E1-E5: 改善 Phase 1 baseline accuracy
         → gated：DG-1..DG-4 穩定 + B8.3 closeout 後才執行
         → 改善後的模型供後續 serving / batch inference（支援性能力）使用

Expansion Track（視需要插入；同受 DG gating）：
  X1-X3: 擴展新能力（multi-label / ViT / U-Net）
         → 建議在主線 pipeline 穩定後再啟動
         → X3 (U-Net) 產出可供 RAG / decision layer 做 evidence（見 MASTER_ROADMAP §5/§14）

Advanced Track（需要額外資源）：
  V1-V3: 跨機台適應 / 合成資料 / 小樣本學習
         → 長期規劃，視資料和算力決定
```

### 與 B-project 的關係

B-project（YOLO camera layer）有獨立的 Milestone 結構，本 gap analysis 不介入：

- B-project Milestone 1 近完成（B6 predict.py JSON validation 待做）
- B-project 用 Roboflow Wafer Defect v2 資料集（7 classes），與 WM-811K 不同
- 課程 W3 YOLO 技術已在 B-project 使用
- X3 (U-Net) 在 wafer map layer，B-project 在 camera layer — 互補不衝突

### §10 Deferred Items（尊重既有決定，不建議提前）

以下項目在 `MASTER_ROADMAP §10` 明確延後，本 gap analysis 不重複建議：

- Docker / Kubernetes 部署
- CI/CD pipeline
- Vector DB、MES event bus、production DB schema

（註：LLM defect/evidence explanation 已不在此 deferred 列 — post-PR #7 為 Phase 4 canonical、Stage 2 優先，見 MASTER_ROADMAP §14；本 gap analysis 不介入其 pipeline 設計。）

---

## 實作建議順序

```
Enhancement Track（gated：DG-1..DG-4 穩定 + B8.3 closeout 後才執行；以下為解除 gate 後的建議順序）：
  Step 1: E1 (augmentation) + E2 (focal loss)
          → 最小工作量（~1.5 hr），直接改善 rare class
          → 預期 Scratch 31.89% → 50%+

  Step 2: E3 (ResNet backbone)
          → 架構升級（~2 hr）
          → 預期 overall 89.28% → 93%+

  Step 3: E4 (Grad-CAM)
          → 驗證 Step 1-2 的改善是否「看對地方」（~1 hr）

  Step 4: E5 (Optuna)
          → 最佳化超參數（~2 hr）
          → 在最終架構上做一次系統搜尋

Expansion Track（主線 pipeline 穩定後；同受 DG gating）：
  Step 5: X1 (multi-label) or X2 (ViT 對比)
          → 視面試需求選擇
          → 預計各 ~2 hr

  Step 6: X3 (U-Net segmentation)
          → 新增 pixel-level 能力（~4 hr）

Advanced Track（視資源）：
  Step 7+: V1-V3
```

---

## 面試講法（修訂版）

> 「Phase 1 的 CNN baseline test accuracy 89.28%，但 rare class 表現不好 — Scratch 只有 31.89%、Loc 45.31%。我分析過根因：一是沒有做 data augmentation 導致過擬合（Val 96.4% vs Test 89.3%），二是 weighted CE 不夠強，需要 focal loss 聚焦 hard sample。下一步是加 augmentation + focal loss + ResNet pretrained backbone，預期整體拉到 93%+。同時用 Grad-CAM 驗證模型是看缺陷區域而不是背景 — 這是 AOI 面試必答題。更遠期包括 U-Net 像素級分割、CycleGAN 跨機台 domain adaptation、以及用 Stable Diffusion ControlNet 生成稀缺缺陷樣本 — 這些都是課程學到的技術，我已經規劃好怎麼整合，而且不影響後續主線 Phase（Phase 4 LLM explanation / Phase 5 MES integration）的 pipeline 開發，Enhancement 工作則受 DG gating 約束。」
