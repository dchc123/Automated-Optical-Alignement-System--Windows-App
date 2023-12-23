@echo off


REM Functions are defined in the order they are executed in

REM permission check
:check_permissions
    REM from https://stackoverflow.com/questions/4051883/batch-script-how-to-check-for-admin-rights#11995662
    echo Detecting administrative permissions...

    net session >nul 2>&1
    if %errorLevel% == 0 (
        echo Administrative permissions confirmed.
        call:check_python_command
    ) else (
        echo FAILURE: Current permissions inadequate. Please run as an Adminstrator
        cmd /k
    )
    goto:eof

:check_python_command
    REM check python installation and install it if necessary
    echo ----------------------------------------------------------------
    echo Detecting python commands
    python -V > temp.txt 2>&1
    if ERRORLEVEL 9009 (
        echo python command does not exist
        call:check_py_command
    ) else (
        setlocal EnableDelayedExpansion
        for /f "tokens=2" %%g in (temp.txt) do (
            set val=%%g
        )
        echo Python !val! detected
        if "!val:~0,3!"=="3.6" (
            echo Correct version of Python is installed
            call:add_env_variables
        ) else (
            echo WARNING: Another version of Python is already installed
            call:check_py_command
        )
    )
    del temp.txt
    goto:eof

:check_py_command
    REM check python installation and install it if necessary
    echo ----------------------------------------------------------------
    echo Detecting py commands
    py -3.6 -V > nul 2>&1
    if errorlevel 1 (
        echo py -3.6 command does not exist
        call:install_python
        call:add_env_variables
    ) else (
        echo Correct version of Python is installed
        call:add_env_variables
    )
    del temp.txt
    goto:eof

REM install python
:install_python
    echo ----------------------------------------------------------------
    echo Installing Python 3.6.4...
    setlocal DisableDelayedExpansion
    "%~dp0\Utilities\python-3.6.4.exe" /quiet InstallAllUsers=1 SimpleInstall=1 Include_test=0 TargetDir=C:\Python36
    goto:eof

REM permission check; exit if missing permission
:add_env_variables
    echo ----------------------------------------------------------------
    REM from https://stackoverflow.com/questions/5491383/find-out-whether-an-environment-variable-contains-a-substring
    REM from https://stackoverflow.com/a/41850533
    REM https://stackoverflow.com/a/6362922
    echo Checking environment variables...

    FOR /F "tokens=* USEBACKQ" %%F IN (`py -3.6 -c "import sys; pydir = str(sys.executable).replace(""python.exe"",""""); print(pydir)"`) DO (
    SET pydir=%%F
    )
    set pyscriptdir=%pydir%Scripts

    ECHO Python 3.6 Directory: %pydir%
    ECHO Python 3.6 Scripts Directory: %pyscriptdir%

    echo.%PATH%|findstr %pydir% >nul 2>&1
    if not errorlevel 1 (
       echo Python36 directory is already in environment variables
    ) else (
        echo Adding Python36 to environment variables
        for /F "usebackq skip=2 tokens=2*" %%A IN (`reg query "HKEY_CURRENT_USER\Environment" /v Path`) do (reg add "HKEY_CURRENT_USER\Environment" /f /v Path /t REG_SZ /d "%%B";%pydir%;)
        setx /M USERNAME %USERNAME%
        call:reload_env_variables
    )

    echo.%PATH%|findstr %pyscriptdir% >nul 2>&1
    if not errorlevel 1 (
       echo Python36 Scripts directory is already in environment variables
    ) else (
        echo Adding Python36 Scripts to environment variables
        for /F "usebackq skip=2 tokens=2*" %%A IN (`reg query "HKEY_CURRENT_USER\Environment" /v Path`) do (reg add "HKEY_CURRENT_USER\Environment" /f /v Path /t REG_SZ /d "%%B";%pyscriptdir%;)
        setx /M USERNAME %USERNAME%
        call:reload_env_variables
    )

    call:install_libs

    goto:eof

REM reload environment variables after adding them
:reload_env_variables
    echo ----------------------------------------------------------------
    REM from https://stackoverflow.com/questions/39856234/how-can-i-refresh-the-path-environment-variable-in-a-batch-script
    echo Refreshing PATH from registry
    :: Get System PATH
    for /f "tokens=3*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path') do set syspath=%%A%%B

    :: Get User Path
    for /f "tokens=3*" %%A in ('reg query "HKCU\Environment" /v Path') do set userpath=%%A%%B

    :: Set Refreshed Path
    set PATH=%userpath%;%syspath%

    echo Refreshed PATH
    goto:eof

:install_libs
    echo ----------------------------------------------------------------
    echo Installing python libraries...this may take some time
    if "%PYTHONHOME%"=="" (
        echo No PYTHONHOME environment variable detected
    ) else (
        echo PYTHONHOME environment variable detected. Temporarily setting to empty.
        set pythonhomeexists=True
        set PYTHONHOME=
    )
    setlocal DisableDelayedExpansion
    pip3.6 install -r "%~dp0\Utilities\python_libs.txt" > "%~dp0\Utilities\setup_log.txt" 2>&1
    call:uninstall_libs

:uninstall_libs
    echo ----------------------------------------------------------------
    echo Uninstalling conflicting libraries
    setlocal DisableDelayedExpansion
    pip3.6 uninstall -r "%~dp0\Utilities\python_remove_libs.txt" > "%~dp0\Utilities\setup_log.txt" 2>&1
    call:ipython_config

:ipython_config
    echo ----------------------------------------------------------------
    echo Creating IPython configuration file
    %pyscriptdir%\ipython3 profile create
    setlocal DisableDelayedExpansion
    py "%~dp0\Utilities\ipython_config.py" "C:\Users\%USERNAME%\.ipython\profile_default\ipython_config.py"
    call:completed_notification

:completed_notification
    echo ----------------------------------------------------------------
    if "%pythonhomeexists%"=="" (
        py -c "import ctypes; ctypes.windll.user32.MessageBoxW(0, 'CLI setup completed', 'CLI Setup', 0)"
    ) else (
        py -c "import ctypes; ctypes.windll.user32.MessageBoxW(0, 'CLI setup completed. \n\nPYTHONHOME environment variable detected. It is recommended to remove this variable.', 'CLI Setup', 0)"
    )
    cmd /k