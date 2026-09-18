#!/usr/bin/env bash
# 重新下載所有 OECD 原始資料表（raw/ 未納入版控，見 README）
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p raw && cd raw

echo "→ PISA 2025 Volume I，Annex B1 各章（stat.link）"
i=1
for c in 9i7u4g mrq53f k68msa 68stqn 6gtbnx 5eaxdr xmra2f h3z8b1; do
  curl -fsSL -o "b1_${i}_2025.xlsx" "https://stat.link/$c"; i=$((i+1))
done
curl -fsSL -o ch2_2025.xlsx "https://stat.link/xgs41b"

echo "→ PISA 2015 Volume I，Annex B1 各章（DOI StatLink）"
i=2
for d in 888933433171 888933433183 888933433195 888933433203 888933433214 888933433226; do
  url=$(curl -sI "https://doi.org/10.1787/$d" | tr -d '\r' | awk '/^location:/{print $2}')
  curl -fsSL -o "pisa2015_ch${i}.xlsx" "$url"; i=$((i+1))
done

echo "→ PISA 2006 Volume 2: Data，各章（DOI StatLink）"
for pair in "ch2:142056138443" "ch3:142102278412" "ch4:142104560611" "ch5:142127877152" "ch6:142183565744"; do
  n=${pair%%:*}; d=${pair##*:}
  url=$(curl -sI "https://doi.org/10.1787/$d" | tr -d '\r' | awk '/^location:/{print $2}')
  curl -fsSL -o "pisa2006_${n}.xls" "$url"
done

echo "→ 報告 PDF（僅供查證，非必要）"
curl -fsSL -o pisa2015_vol1.pdf "https://www.oecd.org/content/dam/oecd/en/publications/reports/2016/12/pisa-2015-results-volume-i_g1g7397c/9789264266490-en.pdf" || true
curl -fsSL -o pisa2006_vol1.pdf "https://www.oecd.org/content/dam/oecd/en/publications/reports/2007/12/pisa-2006_g1gh866e/9789264040014-en.pdf" || true

echo "完成。接著執行： python3 build/extract.py && python3 build/web_data.py && python3 build/trend_data.py && python3 build/make_site.py"
