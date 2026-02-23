#!/bin/bash

if [ "$#" -lt 3 ]; then
  echo "エラー: 引数が不足しています。" >&2
  echo "使い方: $0 Correct|Mistake 単語1 [単語2...] YYYY-MM-DD" >&2
  exit 1
fi

MODE="$1"
DATE="${@: -1}"
WORDS=("${@:2:$#-2}")
SEARCH_DIR="." 

if [ "$MODE" != "Correct" ] && [ "$MODE" != "Mistake" ]; then
  echo "エラー: 最初の引数は 'Correct' または 'Mistake' である必要があります。" >&2
  echo "使い方: $0 Correct|Mistake 単語1 [単語2...] YYYY-MM-DD" >&2
  exit 1
fi

# --- メイン処理 ---
echo "処理を開始します (モード: $MODE)..."
for word in "${WORDS[@]}"; do
  echo "------------------------------------"
  echo "検索中: \"$word\""

  # 検索文字列を含むファイルを特定
  TARGET_FILE=$(grep -rl "$word" "$SEARCH_DIR" | head -n 1)

  if [ -n "$TARGET_FILE" ]; then
    echo "✅ ファイルを特定: $TARGET_FILE"
    
    TMP_FILE=$(mktemp)

    if [ "$MODE" == "Correct" ]; then
      # 1列目が単語と一致する行を探し、4, 5列目を日付で更新、6列目を+1する
      awk -F, -v OFS=, -v w="$word" -v d="$DATE" '{
        if ($1 == w) {
          $4 = d;
          $5 = d;
          $6 = $6 + 1;
        }
        print $0;
      }' "$TARGET_FILE" > "$TMP_FILE"
      echo "\"$word\": last_seen, last_correctを更新し、correct_numをインクリメントしました。"

    elif [ "$MODE" == "Mistake" ]; then
      # 1列目が単語と一致する行を探し、4列目を日付で更新、6列目を0にする
      awk -F, -v OFS=, -v w="$word" -v d="$DATE" '{
        if ($1 == w) {
          $4 = d;
          $6 = 0;
        }
        print $0;
      }' "$TARGET_FILE" > "$TMP_FILE"
      echo "\"$word\": last_seenを更新し、correct_numを0にリセットしました。"
    fi
    
    mv "$TMP_FILE" "$TARGET_FILE"

  else
    echo "❌ \"$word\" を含むファイルが見つかりませんでした。スキップします。"
  fi
done

echo "Done"
