#!/bin/bash

read -p "커밋 메시지: " msg

git fetch origin main
git pull origin main --rebase   # 🔹 리모트 변경 위에 내 커밋 재적용
git add .
git commit -m "$msg"
git push origin main
