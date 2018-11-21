@REM App Studio
@REM
@REM Copyright (c) twigkit.com
@REM
@REM NOTICE: All information contained herein is, and remains the property
@REM of App Studio and its suppliers, if any.
@REM The intellectual and technical concepts contained herein are PROPRIETARY
@REM to App Studio and its suppliers and may be covered by U.S. and Foreign Patents,
@REM patents in process, and are protected by trade secret or COPYRIGHT LAW.
@REM Dissemination of this information or reproduction of this material
@REM is strictly FORBIDDEN unless prior written permission is obtained
@REM from TwigKit.
@REM
@REM This software is distributed in the hope that it will be useful,
@REM but WITHOUT ANY WARRANTY; without even the implied warranty of
@REM MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
@REM
@REM All Rights Reserved.
@REM ----------------------------------------------------------------------------

@REM Copyright (c) 2009-2016 App Studio.  All rights reserved.

@echo off

@REM ----------------------------------------------------------------------------
@REM Check this is a valid project
@REM ----------------------------------------------------------------------------

@REM if [ ! -f ./pom.xml ]; then
@REM	echo ""
@REM    echo "Could not find project pom.xml file, are you sure the current directory is a App Studio project?"
@REM    echo ""
@REM    exit 1
@REM fi

@REM ----------------------------------------------------------------------------
@REM Set environment variables
@REM ----------------------------------------------------------------------------

set BASEDIR=.
set TWIGKIT_PID_DIR=%BASEDIR%/logs
set TWIGKIT_LOGS_DIR=%BASEDIR%/logs
set MVNCMD=%BASEDIR%/bin/mvnw.cmd
set SETTINGS=%BASEDIR%/bin/settings.xml
set START_TIMEOUT=120
set START_MESSAGE_TEXT="start.txt"

set TWIGKIT_PORT=8080

@REM ----------------------------------------------------------------------------
@REM Check which command is invoked
@REM ----------------------------------------------------------------------------

IF NOT [%1] == [] (
  set SCRIPT_CMD=%1
) ELSE (
  CALL :print_usage
  EXIT /B 0
)

IF %1==-help (
  CALL :print_usage
  EXIT /B 0
)

@REM verify the command given is supported
IF NOT "%SCRIPT_CMD%" == "stop" IF NOT "%SCRIPT_CMD%" == "start" IF NOT "%SCRIPT_CMD%" == "package" IF NOT "%SCRIPT_CMD%" == "dist" (
  CALL :print_usage "" "%SCRIPT_CMD% is not a valid command!"
  EXIT /B 1
)

IF [%2] == [-help] (
  CALL :print_usage %SCRIPT_CMD%
  EXIT /B 0
)

@REM Run in foreground (default is to run in the background)
set FG="false"
set noprompt=false
set TWIGKIT_OPTS=

goto set_script_cmd

@REM Only allow the command to be the first argument, assume start if not supplied
:parse_args
set "arg=%~1"
set "firstTwo=%arg:~0,2%"
IF "%SCRIPT_CMD%"=="" set SCRIPT_CMD=start
IF [%1]==[] goto process_script_cmd
IF "%1"=="-help" call :print_usage
IF "%1"=="-usage" call :print_usage
IF "%1"=="/?" call :print_usage
IF "%1"=="-f" goto set_foreground_mode
IF "%1"=="-foreground" goto set_foreground_mode
IF "%1"=="-V" goto set_verbose
IF "%1"=="-verbose" goto set_verbose
IF "%1"=="-m" goto set_memory
IF "%1"=="-memory" goto set_memory
IF "%1"=="-p" goto set_port
IF "%1"=="-port" goto set_port
IF "%1"=="-t" goto set_timeout
IF "%1"=="-timeout" goto set_timeout
IF "%1"=="-all" goto set_stop_all
IF "%1"=="--production" goto set_production_mode
IF "%firstTwo%"=="-D" goto set_passthru
IF NOT "%1"=="" goto invalid_cmd_line
goto invalid_cmd_line

:set_script_cmd
set SCRIPT_CMD=%1
SHIFT
goto parse_args

:set_foreground_mode
set FG=1
SHIFT
goto parse_args

:set_verbose
set verbose=1
set "PASS_TO_RUN_EXAMPLE=--verbose !PASS_TO_RUN_EXAMPLE!"
SHIFT
goto parse_args

:set_memory
set "arg=%~2"
IF "%arg%"=="" (
  set SCRIPT_ERROR=Memory setting is required!
  goto invalid_cmd_line
)
set firstChar=%arg:~0,1%
IF "%firstChar%"=="-" (
  set SCRIPT_ERROR=Expected memory setting but found %2 instead!
  goto invalid_cmd_line
)
set SOLR_HEAP=%~2
set "PASS_TO_RUN_EXAMPLE=-m %~2 !PASS_TO_RUN_EXAMPLE!"
SHIFT
SHIFT
goto parse_args

:set_port
set "arg=%~2"
IF "%arg%"=="" (
  set SCRIPT_ERROR=Port is required!
  goto invalid_cmd_line
)
set firstChar=%arg:~0,1%
IF "%firstChar%"=="-" (
  set SCRIPT_ERROR=Expected port but found %2 instead!
  goto invalid_cmd_line
)

set TWIGKIT_PORT=%~2
set "PASS_TO_RUN_EXAMPLE=-p %~2 !PASS_TO_RUN_EXAMPLE!"
SHIFT
SHIFT
goto parse_args

:set_stop_all
set STOP_ALL=1
SHIFT
goto parse_args

:set_production_mode
set "PRODUCTION_MODE=-Dlucidworks.app.mode=production"
set "TWIGKIT_OPTS=%TWIGKIT_OPTS% %PRODUCTION_MODE%"
SHIFT
goto parse_args

:set_passthru
set "PASSTHRU=%~1=%~2"
IF NOT "%SOLR_OPTS%"=="" (
  set "SOLR_OPTS=%SOLR_OPTS% %PASSTHRU%"
) ELSE (
  set "SOLR_OPTS=%PASSTHRU%"
)
set "PASS_TO_RUN_EXAMPLE=%PASSTHRU% !PASS_TO_RUN_EXAMPLE!"
SHIFT
SHIFT
goto parse_args

:invalid_cmd_line
@echo.
IF "!SCRIPT_ERROR!"=="" (
  @echo Invalid command-line option: %1
) ELSE (
  @echo ERROR: !SCRIPT_ERROR!
)
@echo.
call :print_usage

@REM ----------------------------------------------------------------------------
@REM Now run the command
@REM ----------------------------------------------------------------------------


@REM ############# start/stop/build logic below here ################

@REM Perform the requested command after processing args
:process_script_cmd
IF "%verbose%"=="1" (
  CALL :safe_echo "Using Java: %JAVA%"
  "%JAVA%" -version
  @echo.
)

set /a STOP_PORT=%TWIGKIT_PORT%-1000

IF "%SCRIPT_CMD%" == "start" (
  @REM see if App Studio is already running
  set TWIGKIT_PID=twigkit_pid_by_port "%TWIGKIT_PORT%"`

  @REM IF "%TWIGKIT_PID%" == [] (
    @REM not found using the pid file ... but use ps to ensure not found
    @REM set TWIGKIT_PID=`ps auxww | grep start\.jar | grep -w $TWIGKIT_PORT | grep -v grep | awk '{print $2}' | sort -r`
  @REM )

  @REM IF NOT "%TWIGKIT_PID%" == "" (
  @REM  echo.
  @REM  echo  Port %TWIGKIT_PORT% is already being used by another process (pid: %TWIGKIT_PID%)
  @REM	echo.
  @REM	echo  Please choose a different port using the -p option.
  @REM  EXIT /B 1
  @REM )
  CALL :launch_twigkit "%FG%" "%ADDITIONAL_CMD_OPTS%"
  EXIT /B 0
)
IF "%SCRIPT_CMD%" == "package" (
  CALL :build_twigkit
  EXIT /B 0
)
IF "%SCRIPT_CMD%" == "dist" (
  CALL :build_twigkit_standalone
  EXIT /B 0
) ELSE (
  CALL :find_and_stop_twigkit
  EXIT /B 0
)

IF "%SCRIPT_CMD%" == "stop" (
  @REM already stopped, script is done.
  EXIT /B 0
)

@REM JAVA_MEM_OPTS=()
@REM if [ -z "$SOLR_HEAP" ] && [ -n "$SOLR_JAVA_MEM" ]; then
@REM   JAVA_MEM_OPTS=($SOLR_JAVA_MEM)
@REM else
@REM   SOLR_HEAP="${SOLR_HEAP:-512m}"
@REM   JAVA_MEM_OPTS=("-Xms$SOLR_HEAP" "-Xmx$SOLR_HEAP")
@REM fi

@REM function print_start_message() {
@REM   cat $START_MESSAGE_TEXT
@REM }

@REM ----------------------------------------------------------------------------
@REM Define functions
@REM ----------------------------------------------------------------------------


@REM Usage instructions
:print_usage
  set CMD=%1
  set ERROR_MSG=%2

  IF DEFINED "%ERROR_MSG%" (
	echo.
    echo ERROR: %ERROR_MSG%
  )

  IF [%1]==[] (
    echo.
    echo Usage: app-studio.bat COMMAND OPTIONS
    echo        where COMMAND is one of: start, stop, package, dist
    echo.
    echo   Allows you to build and run App Studio applications easily from the command line.
    echo.
    echo   Standalone server example [start App Studio running in the background on port 8080]:
    echo.
    echo     app-studio.bat start -p 8080
    echo.
    echo.
    echo Pass -help after any COMMAND to see command-specific usage information,
    echo   such as:    app-studio.bat start -help or app-studio.bat stop -help
    echo.
	EXIT /B 0
  )
  IF %CMD%==start (
    echo.
    echo Usage: app-studio.bat %CMD% [-f] [-p port] [-m memory] [-t timeout] [-V]
    echo.
    echo   -f            Start App Studio in foreground; default starts App Studio in the background
    echo                   and sends stdout / stderr to app-studio-PORT-console.log
    echo.
    echo   -p [port]     Specify the port to start the App Studio web server on; default is 8080.
    echo.
    echo   -m [memory]   Sets the min [-Xms] and max [-Xmx] heap size for the JVM, such as: -m 4g
    echo                   results in: -Xms4g -Xmx4g; by default, this script sets the heap size to 512m
    echo.
    echo   -t [timeout]  Sets the startup timeout in seconds [defaults to %START_TIMEOUT%]
    echo.
    echo   -V            Verbose messages from this script
    echo.
    echo.  --production  Start App in production mode
    echo.
  )
  IF %CMD%==stop (
    echo.
    echo Usage: app-studio.bat %CMD% [-p port] [-V]
    echo.
    echo   -p [port]     Specify the port the App Studio HTTP listener is bound to
    echo.
    echo.
  )
  IF %CMD%==package (
    echo.
    echo Usage: app-studio.bat %CMD%
    echo.
    echo   NOTE: This command will build a new WAR file with App Studio and place it in .\dist
    echo.
  )
  IF %CMD%==dist (
    echo.
    echo. Usage: app-studio.bat %CMD%
    echo.
    echo.  NOTE: This command will build a self-contained application and place it in .\dist\${project.name}-standalone\
    echo.
  )
EXIT /B 0

@REM Used to show the script is still alive when waiting on work to complete
@REM function spinner() {
@REM   local pid=$1
@REM   local delay=0.5
@REM   local spinstr='|/-\'
@REM   while [ "$(ps aux | awk '{print $2}' | grep -w $pid)" ]; do
@REM       local temp=${spinstr#?}
@REM       printf " [%c]  " "$spinstr"
@REM       local spinstr=$temp${spinstr%"$temp"}
@REM       sleep $delay
@REM       printf "\b\b\b\b\b\b"
@REM   done
@REM   printf "    \b\b\b\b"
@REM }

:find_and_stop_twigkit
  @REM see if App Studio is already running
  @REM set TWIGKIT_PID=`twigkit_pid_by_port "%TWIGKIT_PORT%"`
  @REM IF "%TWIGKIT_PID%" == [] (
    @REM not found using the pid file ... but use ps to ensure not found
  @REM set TWIGKIT_PID=`ps auxww | grep start\.jar | grep -w %TWIGKIT_PORT% | grep -v grep | awk '{print $2}' | sort -r`
  )
  @REM IF "%TWIGKIT_PID%" == [] (
    call :stop_twigkit "%TWIGKIT_PORT%" "%STOP_KEY%" "%TWIGKIT_PID%"
  @REM )
  @REM IF "%SCRIPT_CMD%" == "stop" (
  @REM    echo No process found for App Studio node running on port %TWIGKIT_PORT%
  @REM    EXIT /B 1
  @REM )
EXIT /B 0

@REM tries to gracefully stop App Studio using the Jetty
@REM stop command and if that fails, then uses kill -9
:stop_twigkit
  set TWIGKIT_PORT=%1
  set /a STOP_PORT=%TWIGKIT_PORT%-1000
  set STOP_KEY=%2
  set TWIGKIT_PID=%3

  IF NOT [%3] == [] (
    echo Sending stop command to App Studio running on port %TWIGKIT_PORT% ...
    CALL %MVNCMD% jetty:stop -Dtwigkit.http.stop.port=%STOP_PORT%
	echo App Studio stop command executed succesfully. If App Studio still appears to be running it may be necessary to manually kill the Java process.
    @REM (sleep 5) &
    @REM spinner $!
    @REM rm -f "%TWIGKIT_PID_DIR%/twigkit-%TWIGKIT_PORT%.pid"
  ) ELSE (
    echo No App Studio nodes found to stop.
    EXIT /B 0
  )

  @REM CHECK_PID=`ps auxww | awk '{print $2}' | grep -w $TWIGKIT_PID | sort -r | tr -d ' '`
  @REM if [ "$CHECK_PID" != "" ]; then
  @REM   echo "App Studio process $TWIGKIT_PID is still running; forcefully killing it now."
  @REM   kill -9 $TWIGKIT_PID
  @REM   echo "Killed process $TWIGKIT_PID"
  @REM   rm -f "$TWIGKIT_PID_DIR/twigkit-$TWIGKIT_PORT.pid"
  @REM   sleep 1
  @REM else
  @REM   echo "App Studio process stopped gracefully"
  @REM fi

  @REM CHECK_PID=`ps auxww | awk '{print $2}' | grep -w $TWIGKIT_PID | sort -r | tr -d ' '`
  @REM if [ "$CHECK_PID" != "" ]; then
  @REM   echo "ERROR: Failed to kill previous App Studio Java process $TWIGKIT_PID ... script fails."
  @REM   exit 1
  @REM fi
EXIT /B 0

@REM build the deployable App Studio artifact
:build_twigkit
  CALL "%MVNCMD%" clean package --settings "%SETTINGS%"
EXIT /B 0

@REM build the deployable App Studio artifact as a standalone service
:build_twigkit_standalone
  CALL "%MVNCMD%" clean package -Pstandalone --settings "%SETTINGS%"
EXIT /B 0

@REM Launches App Studio in foreground/background depending on parameters
:launch_twigkit
  @REM goto print_start_message

  set run_in_foreground=%1
  set stop_port="%STOP_PORT%"

  @REM set GC_TUNE=($GC_TUNE)

  IF NOT EXIST "%BASEDIR%/bin/mvnw.cmd" (
    echo.
    echo ERROR: mvnw.cmd file not found in %BASEDIR%/bin!
    EXIT /B 0
  )

  if not exist "%TWIGKIT_LOGS_DIR%" mkdir "%TWIGKIT_LOGS_DIR%"
  if not exist "%TWIGKIT_PID_DIR%" mkdir "%TWIGKIT_PID_DIR%"

  IF %FG%==1 (
    echo.
    echo Starting App Studio on port %TWIGKIT_PORT%
	@echo on
    CALL %MVNCMD% jetty:run --settings %SETTINGS% %TWIGKIT_OPTS% -Dtwigkit.http.port=%TWIGKIT_PORT% -Dtwigkit.http.stop.port=%STOP_PORT% -Dtwigkit.conf.overlay=file://src/dev/resources/conf -Dtwigkit.conf.watch=false
	@REM removed live config reload (-Dtwigkit.conf.watch=true) due to bug when used on Windows
  ) ELSE (
    @REM run in the background
    start /b cmd /c CALL %MVNCMD% jetty:run --settings %SETTINGS% %TWIGKIT_OPTS% -Dtwigkit.http.port=%TWIGKIT_PORT% -Dtwigkit.http.stop.port=%STOP_PORT% -Dtwigkit.conf.watch=false -Dtwigkit.conf.overlay=file://src/dev/resources/conf %SOLR_OPTS%>"%TWIGKIT_LOGS_DIR%/app-studio-%TWIGKIT_PORT%-console.log" 2>&1
	@REM removed live config reload (-Dtwigkit.conf.watch=true) due to bug when used on Windows

	@REM for /F "TOKENS=1,2,*" %%a in ('tasklist /FI "IMAGENAME eq java.exe"') do set TWIGKIT_PID=%%b
	echo.
	echo Please wait while App Studio loads...
	ping localhost -n 1 -w 45000 > nul
	echo Started App Studio server on port %TWIGKIT_PORT%. Have fun!
	start "" http://localhost:%TWIGKIT_PORT%
    echo.
  )
EXIT /B 0
