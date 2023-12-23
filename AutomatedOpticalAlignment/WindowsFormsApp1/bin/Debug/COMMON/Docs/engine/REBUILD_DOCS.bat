@echo off
echo Rebuilding documentation

echo ----------------------------------------------------------------
echo Deleting auto-generated '.rst' files
del ..\source\COMMON*.rst

echo ----------------------------------------------------------------
echo Deleting existing build
rmdir "..\build\html" /s /q
REM rmdir "build\latex" /s /q

echo ----------------------------------------------------------------
echo Generating new '.rst' files
sphinx-apidoc -f -e -M -T -o ..\source %~dp0..\..

echo ----------------------------------------------------------------
echo Post process RST files
py post_process_rst.py ..\source

echo ----------------------------------------------------------------
echo Rebuilding HTML docs
call make html

REM echo ----------------------------------------------------------------
REM echo Rebuilding PDF primitives
REM call engine\make latex
REM cd build\latex
REM pdflatex.exe CLIUserDoc.tex

REM echo ----------------------------------------------------------------
REM echo Updating SVN status for html folder
REM py svn_operations.py ..\build

echo ----------------------------------------------------------------
pause
@echo on