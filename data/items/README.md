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

## 中文的來源

中文**優先採用 OECD 臺灣國家版問卷的官方題目文字**（`Chinese Taipei_StQ/IcQ/ScQFLA/TcQ_zh-TW.pdf`
與 `PaQ_zh-TW.pdf`，即臺灣學生當年實際看到的字句）。臺灣版沒有的才由本專案翻譯，並在該題標註
「（本專案翻譯）」。

| 中文來源 | 題數 |
|---|--:|
| OECD 臺灣國家版官方題目 | 1,032 |
| 本專案翻譯 | 48 |
| 尚無中文 | 203 |

**學生問卷 280 題全部有中文**（232 題官方 ＋ 48 題本專案翻譯）。
尚無中文的 203 題集中在家長／學校／教師問卷。

### 為什麼有 108 題對不上代碼

臺灣國家版有時會沿用同一題號但換成不同後綴，代表的其實是**不同的題目**——
例如臺灣版 `PA003Q21JA`（與孩子討論科學相關職業）與國際 Codebook 的 `PA003Q21DA`
（討論科學如何應用在日常生活）並不是同一題。因此本庫**只接受完全相同的代碼**，
不做題號硬套，以免張冠李戴。這 108 題臺灣版自有題號的中文另存於
`00_總表/臺灣版自有題號_未對上國際代碼.csv`。

**〈尖括號〉是 PISA 的在地化佔位符**，各國施測時會替換成當地說法（官方中文版已替換成臺灣用語）。

### 重新產生官方中文

`Chinese Taipei.zip` 在 [PISA 2025 Database](https://www.oecd.org/en/data/datasets/pisa-2025-database.html)
→ National versions → Chinese Taipei，該連結有 Cloudflare 驗證需用瀏覽器下載。放到 `raw/items/` 後：
`python3 build/items_official_zh.py && python3 build/parse_zh_pdf.py && python3 build/items_export.py`

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
