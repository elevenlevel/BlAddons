@echo off
REM Путь к Blender.exe
set BLENDER_PATH="C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"

REM Корневая папка репозитория
set REPO_DIR="D:\__Repositories\BlAddons\Extensions"

REM Переход в папку репозитория (для удобства работы с архивами)
pushd %REPO_DIR%

REM Архивация каждой папки в корне REPO_DIR
for /D %%F in (*) do (
    REM Проверяем, что нет архивов с таким именем
    if not exist "%%F.zip" (
        REM Создание ZIP архива из папки %%F
        powershell.exe -Command "Compress-Archive -Path '%%F\*' -DestinationPath '%%F.zip' -Force"
    )
)

REM Возврат в исходную директорию
popd

REM Генерация index.json командой Blender
%BLENDER_PATH% --command extension server-generate --repo-dir=%REPO_DIR%

pause