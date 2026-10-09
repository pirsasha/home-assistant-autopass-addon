# Чек-лист релиза Autopass

История изменений для Home Assistant — это файл **`autopass/CHANGELOG.md`**: именно
его Supervisor показывает пользователю в окне обновления add-on. Корневой
`CHANGELOG.md` должен содержать ту же историю (он используется для просмотра в
репозитории).

## Обязательный порядок

1. **Сначала changelog, потом версия.** В source-репозитории приложения
   (`pirsasha/home-assistant-autopass`) выходит release-заметка в `CHANGELOG.md`.
2. **Синхронизировать оба changelog этого репозитория** до изменения версии:

   ```
   python scripts/check_changelog.py --sync-from <путь к source CHANGELOG.md>
   ```

   Для Home Assistant допустимо сократить технические формулировки, но смысл
   каждой версии сохраняется и новые версии не выдумываются.
3. **Только после этого** поднять `version` в `autopass/config.yaml`.
   Поле `image: ghcr.io/pirsasha/{arch}-autopass` не меняется.
4. **Собрать и опубликовать образы** для обеих платформ (локальный Docker Buildx,
   без GitHub Actions):
   `ghcr.io/pirsasha/amd64-autopass:<версия>` и `ghcr.io/pirsasha/aarch64-autopass:<версия>`,
   плюс `latest` у обоих. Проверить платформы и совпадение digest у `latest` и версии.
5. **Проверить, что changelog и версия согласованы:**

   ```
   python scripts/check_changelog.py
   ```

   Проверка обязана завершиться `OK`. Она падает, если в `autopass/CHANGELOG.md`
   или `CHANGELOG.md` нет заголовка текущей версии из `autopass/config.yaml` или
   если файлы разошлись.
6. **Закоммитить и запушить** store-репозиторий без force.
7. **Ничего не применять на production автоматически** — обновление add-on
   устанавливает пользователь/администратор вручную.

## Почему это важно

Ранее `autopass/CHANGELOG.md` отставал (последняя версия 0.19.9), поэтому в окне
обновления Home Assistant не были видны изменения 0.19.10–0.19.50. Проверка
`scripts/check_changelog.py` не даёт повторить эту ситуацию.
