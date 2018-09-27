param($lint = $false,
      $interpreter = "python.exe",
      $filematch = "." )

write-host "Using interpreter $interpreter"

$Script:ErrorActionPreference = "Continue"

$args = @('-m', 'unittest', 'discover', '-s', 'src', '-p', '*_test.py')

& $interpreter $args 2>&1 | % { "$_" }

if ($lint -eq $false -or $LASTEXITCODE -ne 0)
{
    exit $LASTEXITCODE
}

# Iterate all src
Get-ChildItem "src" -File -Filter "*.py" |
Where Name -CMatch $filematch |
ForEach-Object     {
        write-output($_.FullName)
        Write-Output("")
        Write-Output("PYLINT")
        & $interpreter "-m", "pylint", $_.FullName 2>&1

        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }


        Write-Output("MYPY")

        & $interpreter "-m", "mypy", $_.FullName 2>&1

        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
        Write-Output("---------------------------------------")

        Write-Output("PYFLAKES")
        & $interpreter "-m", "pyflakes", $_.FullName 2>&1

        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }

        Write-Output("***************************************")
        Write-Output("***************************************")
    }

exit 0
