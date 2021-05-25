Get-ChildItem ..\google-fonts\ofl\* | ForEach-Object -Parallel { poetry run python -m gpos_compression_by_tetris (ls $_\*.ttf) > $_\results.csv }
