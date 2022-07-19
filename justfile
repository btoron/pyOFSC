
version := `poetry version -s --no-ansi`
release := "v"+ version

publish:
    echo {{version}}
    echo {{release}}
    gh release create {{release}}