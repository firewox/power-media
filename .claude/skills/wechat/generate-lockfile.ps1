$ErrorActionPreference = 'Stop'

$SkillRoot = $PSScriptRoot
Set-Location -LiteralPath $SkillRoot

npm.cmd shrinkwrap
