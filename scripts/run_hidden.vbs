Set WshShell = CreateObject("WScript.Shell")
strScriptPath = WScript.ScriptFullName
strScriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(strScriptPath)
strBatPath = strScriptDir & "\start_bot.bat"
WshShell.Run "cmd.exe /c """ & strBatPath & """", 0, False
