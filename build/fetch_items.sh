#!/usr/bin/env bash
# 重新下載 PISA 2025 題庫原始檔
set -euo pipefail
cd "$(dirname "$0")/../raw/items" 2>/dev/null || { mkdir -p "$(dirname "$0")/../raw/items"; cd "$(dirname "$0")/../raw/items"; }
echo "→ PISA 2025 Codebook（題目原文與選項）"
curl -fsSL -o PISA2025_Codebook.xlsx "https://webfs.oecd.org/pisa2022/2025/PISA2025_Codebook.xlsx"
echo "→ 官方英文學生問卷 PDF"
curl -fsSL -o student_questionnaire_en.pdf \
  "https://www.oecd.org/content/dam/oecd/en/data/datasets/pisa/pisa-2025-datasets/questionnaires/STUDENT%20QUESTIONNAIRE%20PISA%202025.pdf"
echo "→ 臺灣中文家長問卷 PDF"
curl -fsSL -o parent_questionnaire_zhTW.pdf \
  "https://www.oecd.org/content/dam/oecd/en/data/datasets/pisa/pisa-2025-datasets/national-versions-pisa-2025-datasets/pb_versions/PaQ_zh-TW_FINAL_21-02-2025.pdf"
echo
echo "完成。中文學生問卷（Chinese Taipei.zip）有 Cloudflare 驗證，需手動下載："
echo "  https://www.oecd.org/en/data/datasets/pisa-2025-database.html → National versions → Chinese Taipei"
echo "下載後放進 raw/items/ 再執行： python3 build/items_official_zh.py"
