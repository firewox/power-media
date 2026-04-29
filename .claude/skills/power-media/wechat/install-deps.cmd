@echo off
setlocal
set "SKILL_ROOT=%~dp0"
npm.cmd install --prefix "%SKILL_ROOT%"
