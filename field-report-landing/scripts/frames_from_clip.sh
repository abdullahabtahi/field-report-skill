#!/usr/bin/env bash
# Cut a generated clip into graded WebP frames for a scroll-scrubbed canvas sequence.
#
# usage: frames_from_clip.sh INPUT.mp4 OUTDIR [options]
#   --every N      keep every Nth frame            (default 3)
#   --crop W:H:X:Y crop before scaling, ffmpeg crop syntax (default: none)
#                  e.g. 1000:1080:460:0 keeps the centre of a 1920x1080 clip
#   --width PX     scale to this width, height follows (default 800)
#   --sat S        saturation multiplier, 1 = unchanged (default 0.7)
#   --black B      lift the black point to this level 0..1; cuts bloom haze (default 0.06)
#   --quality Q    cwebp quality (default 62)
#   --prefix P     file name prefix (default f_)
#
# Why these defaults: the first build used every 3rd frame, saturation 0.7 and a lifted black point, then
# cwebp -q 62. Its exact black-point value was not recorded, so 0.06 is a starting point: compare the first
# frames with your hero artwork and adjust --sat and --black until glow is gone and the signal colour survives.
set -euo pipefail

if [ $# -lt 2 ]; then sed -n '2,19p' "$0"; exit 2; fi
IN="$1"; OUT="$2"; shift 2
EVERY=3; CROP=""; WIDTH=800; SAT=0.7; BLACK=0.06; Q=62; PREFIX="f_"
while [ $# -gt 0 ]; do
  case "$1" in
    --every) EVERY="$2"; shift 2 ;;
    --crop) CROP="$2"; shift 2 ;;
    --width) WIDTH="$2"; shift 2 ;;
    --sat) SAT="$2"; shift 2 ;;
    --black) BLACK="$2"; shift 2 ;;
    --quality) Q="$2"; shift 2 ;;
    --prefix) PREFIX="$2"; shift 2 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

for tool in ffmpeg cwebp; do
  command -v "$tool" >/dev/null || { echo "$tool is required" >&2; exit 1; }
done
[ -f "$IN" ] || { echo "no such file: $IN" >&2; exit 1; }

mkdir -p "$OUT"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

VF="select='not(mod(n\,${EVERY}))'"
[ -n "$CROP" ] && VF="${VF},crop=${CROP}"
VF="${VF},scale=${WIDTH}:-2:flags=lanczos,hue=s=${SAT},colorlevels=rimin=${BLACK}:gimin=${BLACK}:bimin=${BLACK}"

ffmpeg -v error -y -i "$IN" -vf "$VF" -fps_mode vfr "$TMP/%04d.png"

i=0
for f in "$TMP"/*.png; do
  i=$((i + 1))
  cwebp -quiet -q "$Q" "$f" -o "$OUT/$(printf '%s%03d' "$PREFIX" "$i").webp"
done
echo "wrote $i frames to $OUT"
