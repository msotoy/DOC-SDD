#!/usr/bin/env bash
# Valida que cada SKILL.md del catálogo tenga el frontmatter requerido
# y que el nombre de carpeta cumpla la convención (minúsculas, guiones).
set -euo pipefail

errors=0

while IFS= read -r -d '' skill_file; do
  dir=$(dirname "$skill_file")
  folder_name=$(basename "$dir")

  frontmatter=$(awk '/^---$/{c++; next} c==1' "$skill_file")

  name=$(echo "$frontmatter" | grep -E '^name:' | sed -E 's/^name:[[:space:]]*//' | tr -d "'\"")
  description=$(echo "$frontmatter" | grep -E '^description:' | sed -E 's/^description:[[:space:]]*//')

  if [[ -z "$name" ]]; then
    echo "❌ $skill_file: falta 'name' en el frontmatter"
    errors=$((errors + 1))
  elif [[ "$name" != "$folder_name" ]]; then
    echo "❌ $skill_file: 'name' ($name) no coincide con el nombre de carpeta ($folder_name)"
    errors=$((errors + 1))
  fi

  if [[ -z "$description" ]]; then
    echo "❌ $skill_file: falta 'description' en el frontmatter"
    errors=$((errors + 1))
  fi

  if [[ ! "$folder_name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
    echo "❌ $dir: el nombre de carpeta debe ser minúsculas y guiones"
    errors=$((errors + 1))
  fi

done < <(find domains -name 'SKILL.md' -print0)

if [[ $errors -gt 0 ]]; then
  echo ""
  echo "$errors problema(s) encontrado(s)."
  exit 1
fi

echo "✅ Todas las skills son válidas."
