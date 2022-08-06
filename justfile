set dotenv-load
version := `poetry version -s --no-ansi`
release := "v"+ version

default:
    @just --list

publish:
    echo {{version}}
    echo {{release}}
    gh release create {{release}}

test:
    @pytest