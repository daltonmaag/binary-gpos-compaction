Get-ChildItem ..\google-fonts\ofl\* | ForEach-Object -Parallel { poetry run python -m gpos_compaction (ls $_\*.ttf) > $_\results.csv }
