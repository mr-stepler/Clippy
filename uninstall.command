#!/bin/bash

echo "🗑 Удаление Clippy и всех его данных..."

# 1. Завершение работающих процессов
pkill -f Clippy 2>/dev/null
pkill -f SmartClipboard 2>/dev/null

# 2. Удаление приложения из системы
rm -rf /Applications/Clippy.app 2>/dev/null
rm -rf /Applications/SmartClipboard.app 2>/dev/null

# 3. Очистка временных файлов и данных пользователя (база данных, кэш, конфиги)
rm -f /tmp/clippy.lock 2>/dev/null
rm -f /tmp/smart_clipboard.lock 2>/dev/null
rm -rf ~/Library/Application\ Support/Clippy 2>/dev/null
rm -rf ~/Library/Application\ Support/SmartClipboard 2>/dev/null
rm -rf ~/Library/Caches/Clippy 2>/dev/null
rm -rf ~/Library/Preferences/com.clippy.app.plist 2>/dev/null

# 4. Обновление интерфейса Finder
killall Finder

echo ""
echo "✅ Приложение Clippy и все его следы успешно удалены!"
read -p "Нажмите Enter, чтобы закрыть окно..."