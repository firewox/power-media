@echo off
setlocal
set "SKILL_ROOT=%~dp0"
cd /d "%SKILL_ROOT%"
npm.cmd shrinkwrap
