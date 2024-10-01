#!/bin/bash

# Чтение текущей версии
version=$(cat version.txt)

# Разбиение версии на компоненты
IFS='.' read -ra ADDR <<< "$version"
major="${ADDR[0]}"
minor="${ADDR[1]}"
patch="${ADDR[2]}"

# Инкрементирование patch версии
patch=$((patch + 1))

# Сборка новой версии
new_version="$major.$minor.$patch"

# Запись новой версии в файл
echo $new_version > version.txt

# Добавление изменений в Git
git add version.txt
git commit -m "Bump version to $new_version"
