@ECHO OFF
SET SIPPINSTDIR=REPLACE_THIS
SET TERMINFO=c:\usr\share\terminfo
cmd /k "cd %SIPPINSTDIR && mount c:/ / && mode 81,26 && cls && ECHO You can now run sipp by typing 'sipp'"