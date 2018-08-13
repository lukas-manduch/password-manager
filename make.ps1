param($lint = $false, $interpreter = "python.exe" )

write-host "Using interpreter $interpreter"

$Script:ErrorActionPreference = "Continue"

$args = @('-m', 'unittest', 'discover', '-s', 'src', '-p', '*_test.py')

& $interpreter $args 2>&1 | % { "$_" }

if ($lint -eq $false -or $LASTEXITCODE -ne 0)
{
    exit $LASTEXITCODE
}

Get-ChildItem "src" -File -Filter "*.py" |
ForEach-Object {
    write-output($_.FullName)
    & $interpreter "-m", "pylint", $_.FullName 2>&1 | % { "$_" }
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    & $interpreter "-m", "mypy", $_.FullName 2>&1 | % { "$_" }
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

exit $LASTEXITCODE
