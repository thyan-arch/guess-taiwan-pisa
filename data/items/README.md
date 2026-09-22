# PISA 2025 題庫（中英對照）

PISA 2025 學生、家長、學校、教師問卷的**完整題項**，以及認知測驗的題組清單。
每題附代碼、題幹、題目原文、選項量尺；其中被 OECD 正式分析的題目另附
**臺灣 vs OECD 的逐選項作答百分比**。

- 施測年：PISA 2025（2026-09-08 公布結果）
- 題項總數：**1,283**（學生 280、ICT 93、家長 196、學校 352、教師 362）
- 認知測驗題組：**226 組**

## 資料夾

| 資料夾 | 內容 |
|---|---|
| `00_總表/` | `問卷題庫_全部.csv`（Excel 可開）、`.json`、`衍生指數清單.csv` |
| `01_學生問卷/` | 依主題分檔的 Markdown ＋ `_總表.csv` |
| `02_ICT數位素養問卷/` | 同上 |
| `03_家長問卷/` | 同上 |
| `04_學校問卷/` | 同上 |
| `05_教師問卷/` | 同上 |
| `06_認知測驗/` | `認知測驗題組清單.csv` |

每個主題的 `.md` 檔包含：題幹（中／英）、選項量尺（中／英）、逐題（中文、英文原文、變項代碼），
以及該題的臺灣與 OECD 逐選項百分比對照表。

## 中文的來源與界線

- **中文為本專案翻譯，不是 OECD 官方譯本。** 已翻譯 390 題：全部 280 題學生問卷，
  加上其他問卷中 110 題有對應構念（＝實際被 OECD 分析使用）的題目。
- 其餘 893 題（家長／學校／教師問卷中偏行政性的題目）目前只有英文原文。
- **〈尖括號〉是 PISA 的在地化佔位符**，各國施測時會替換成當地說法。
  例如 `〈學校科學課〉`＝該國學制中對應的自然科課程名稱。

### 要官方中文版問卷

OECD 的臺灣版問卷在 `Chinese Taipei.zip`（[PISA 2025 Database](https://www.oecd.org/en/data/datasets/pisa-2025-database.html)
→ National versions → Chinese Taipei）。該連結有 Cloudflare 人機驗證，需要用瀏覽器手動下載。
下載後放到 `raw/items/`，執行 `python3 build/items_official_zh.py` 會列出裡面的中文題本並解壓到
`raw/items/zh_official/`。

## 判讀注意

1. 百分比是**有效作答的百分比**，已排除未作答與跳答。
2. 「對應構念」取自該題在 PISA 2025 Results (Volume I) Annex B 中所屬表格的標題；
   同一題組的題目一律歸為同一構念。
3. 部分題組（例如科學自我效能 ST129）在 Volume I 沒有對應表，可能要等 Volume II（預計 2026-12-01）。
4. **認知測驗的題目內容 OECD 不公開**，只有少數釋出樣題。`06_認知測驗/` 提供的是題組名稱、
   小題編號與領域，可用來了解測驗涵蓋的情境範圍，但沒有題目文字。
5. 臺灣在 OECD 表中名稱為 Chinese Taipei，非 OECD 會員，OECD 平均不含臺灣。

## 來源

- 題目原文與選項：OECD, *PISA 2025 Codebook*（`raw/items/PISA2025_Codebook.xlsx`）
- 臺灣與 OECD 百分比：OECD, *PISA 2025 Results (Volume I)* Annex B
- 官方英文問卷 PDF：`raw/items/student_questionnaire_en.pdf`

重建：`python3 build/items_bank.py && python3 build/items_export.py`
