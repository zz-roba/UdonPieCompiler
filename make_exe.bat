pyinstaller udon_compiler.spec
copy /Y	 udon_funcs_data.py dist\udon_funcs_data.py
copy /Y	 README.md dist\README.md
xcopy /Y tools dist\
powershell compress-archive -Force dist UdonPie_release.zip
