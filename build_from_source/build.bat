@echo off

cd..

python -m venv venv

call venv\Scripts\activate

pip install -r requirements.txt

call deactivate

python -m PyInstaller --paths venv\lib\site-packages --icon=build_from_source\resources\logo.ico --noconsole --runtime-hook=build_from_source\resources\use_lib.py ToMaChess.py

python -m PyInstaller --clean -y ToMaChess.spec

rmdir /s /q venv

rmdir /s /q build

del ToMaChess.spec

mkdir "dist/ToMaChess/lib"

for %%F in ("dist\ToMaChess\*") do (
	set "excludeFile="
	for %%E in (
		dist\ToMaChess\base_library.zip
		dist\ToMaChess\pyside6.abi3.dll
		dist\ToMaChess\python3.dll
		dist\ToMaChess\python311.dll
		dist\ToMaChess\python312.dll
		dist\ToMaChess\Qt6Core.dll
		dist\ToMaChess\Qt6Gui.dll
		dist\ToMaChess\Qt6Widgets.dll
		dist\ToMaChess\shiboken6.abi3.dll
		dist\ToMaChess\ToMaChess.exe
                dist\ToMaChess\MSVCP140.dll
                dist\ToMaChess\MSVCP140_1.dll
                dist\ToMaChess\MSVCP140_2.dll
                dist\ToMaChess\VCRUNTIME140.dll
                dist\ToMaChess\VCRUNTIME140_1.dll
	) do (
		if "%%F" == "%%E" (
                        attrib +h %%F
			set "excludeFile=true"
		)
	)
	if not defined excludeFile (
		move %%F "dist/ToMaChess/lib"
	)
)

for /D %%F in ("dist\ToMaChess\*") do (
	set "excludeFile="
	for %%E in (
		dist\ToMaChess\lib
		dist\ToMaChess\PIL
		dist\ToMaChess\PySide6
		dist\ToMaChess\shiboken6
	) do (
		if "%%F" == "%%E" (
                        attrib +h %%F
			set "excludeFile=true"
		)
	)
	if not defined excludeFile (
		move %%F "dist/ToMaChess/lib"
	)
)

attrib -h "dist/ToMaChess/ToMaChess.exe"

for %%F in (
	bbp
	certificates
	images
	locales
	styles
) do (
	xcopy "%%F" "dist/ToMaChess/%%F" /E /I /H /K /Y
)

xcopy "LICENSE" "dist/ToMaChess"

xcopy /s "build_from_source/include_files" "dist/ToMaChess"

move "dist/ToMaChess" "build_from_source/"

rd "dist"

echo.
echo Executable built successfully!
echo.

pause
