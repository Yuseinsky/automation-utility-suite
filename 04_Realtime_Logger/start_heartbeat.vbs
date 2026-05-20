Set WshShell = CreateObject("WScript.Shell")
' 0 represents hidden window, False means don't wait for execution.
' Please replace the path below with your absolute path to sys_heartbeat.py
WshShell.Run "pythonw.exe ""C:\path\to\your\Wantedly_Portfolio\04_Realtime_Logger\sys_heartbeat.py""", 0, False
