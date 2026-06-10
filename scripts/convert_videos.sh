#!/bin/bash
# photos/<연도>/*.wmv → YouTube 업로드용 mp4 일괄 변환
# 사용법: bash convert_videos.sh
# 출력: 40th_website/video_out/<연도>_<원본이름>.mp4 (gitignore됨)
# 이미 변환된 파일은 건너뛴다 (중단 후 재실행 안전)
set -u
WS="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$WS/40th_website/video_out"
mkdir -p "$OUT"

find "$WS/photos" -iname "*.wmv" ! -name "._*" | sort | while IFS= read -r src; do
  year=$(basename "$(dirname "$src")")
  name=$(basename "$src" | sed 's/\.[Ww][Mm][Vv]$//')
  dst="$OUT/${year}_${name}.mp4"
  if [ -s "$dst" ]; then echo "SKIP: $dst"; continue; fi
  echo "CONVERT: $src"
  # H.264 + AAC, 원본 해상도 유지, 업로드용 적정 화질 (CRF 20)
  ffmpeg -nostdin -hide_banner -loglevel error -y -i "$src" \
    -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
    -c:a aac -b:a 160k -movflags +faststart "$dst" \
    && echo "DONE: $dst" || { echo "FAIL: $src"; rm -f "$dst"; }
done
echo "ALL FINISHED"
