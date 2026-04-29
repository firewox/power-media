$ErrorActionPreference = 'Stop'

$SkillRoot = $PSScriptRoot
Set-Location -LiteralPath $SkillRoot

npm.cmd install --prefix $SkillRoot
