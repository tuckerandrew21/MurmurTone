Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\tucke\Repositories\voice-typer"
WshShell.Run """C:\Users\tucke\Repositories\voice-typer\venv\Scripts\pythonw.exe"" murmurtone.py", 0, False
