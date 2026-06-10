#!/bin/bash
# 영상만 있는 연도의 wmv에서 장면 스틸컷 추출 → photos/<연도>/stills_<영상명>_NNN.jpg
# 장면 전환 감지(>0.35) 기준, 영상당 최대 40장
set -u
WS="$(cd "$(dirname "$0")/../.." && pwd)"
for y in 1991 1992 1993 1996 1997 1998 2003; do
  find "$WS/photos/$y" -iname "*.wmv" ! -name "._*" | while IFS= read -r src; do
    name=$(basename "$src" | sed 's/\.[Ww][Mm][Vv]$//' | tr ' ' '_' | cut -c1-40)
    out="$WS/photos/$y"
    # 이미 추출했으면 스킵
    ls "$out"/still_"$name"_*.jpg >/dev/null 2>&1 && { echo "SKIP $y/$name"; continue; }
    ffmpeg -nostdin -hide_banner -loglevel error -i "$src" \
      -vf "select='gt(scene,0.35)',scale=1280:-2" -vsync vfr -frames:v 40 -q:v 3 \
      "$out/still_${name}_%03d.jpg" && echo "DONE $y/$name" || echo "FAIL $y/$name"
  done
done
echo "STILLS FINISHED"
