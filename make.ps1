param($lint = $false)

$Script:ErrorActionPreference = "Continue"

$interpreter = get-command python | Select-Object -ExpandProperty Source  
#Write-Host "Using interpreter $interpreter"
$args = @('-m', 'unittest', 'discover', '-s', 'src', '-p', '*_test.py')

& $interpreter $args 2>&1 | % { "$_" }

if ($lint -eq $false -or $LASTEXITCODE -ne 0)
{
    exit $LASTEXITCODE
}

Get-ChildItem "src" -File -Filter "*.py" |
ForEach-Object {
    &"python" "-m", "pylint", $_.FullName 2>&1 | % { "$_" }
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

exit $LASTEXITCODE