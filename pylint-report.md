# Pylint-raportti

Sovelluksen lopullinen Python-koodi tarkastettiin Pylintin versiolla 4.0.7
komennolla:

```bash
python3 -m pylint *.py
```

Pylint antoi seuraavan palautteen:

```text
************* Module app
app.py:1:0: C0114: Missing module docstring (missing-module-docstring)
app.py:28:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:47:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:87:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:107:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:113:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:140:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:173:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:209:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:260:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:272:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:294:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:306:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:323:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:338:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:356:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:367:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:385:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:396:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:435:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:465:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:470:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module comment
comment.py:1:0: C0114: Missing module docstring (missing-module-docstring)
comment.py:3:0: C0116: Missing function or method docstring (missing-function-docstring)
comment.py:13:0: C0116: Missing function or method docstring (missing-function-docstring)
comment.py:19:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module config
config.py:1:0: C0114: Missing module docstring (missing-module-docstring)
************* Module db
db.py:1:0: C0114: Missing module docstring (missing-module-docstring)
db.py:5:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:11:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:18:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:25:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module habit
habit.py:1:0: C0114: Missing module docstring (missing-module-docstring)
habit.py:5:0: C0116: Missing function or method docstring (missing-function-docstring)
habit.py:9:0: C0116: Missing function or method docstring (missing-function-docstring)
habit.py:22:0: C0116: Missing function or method docstring (missing-function-docstring)
habit.py:34:0: C0116: Missing function or method docstring (missing-function-docstring)
habit.py:52:0: C0116: Missing function or method docstring (missing-function-docstring)
habit.py:61:0: C0116: Missing function or method docstring (missing-function-docstring)
habit.py:68:0: C0116: Missing function or method docstring (missing-function-docstring)
habit.py:74:0: C0116: Missing function or method docstring (missing-function-docstring)
habit.py:80:0: C0116: Missing function or method docstring (missing-function-docstring)
habit.py:86:0: C0116: Missing function or method docstring (missing-function-docstring)
habit.py:98:0: C0116: Missing function or method docstring (missing-function-docstring)
habit.py:104:0: C0116: Missing function or method docstring (missing-function-docstring)
habit.py:107:0: C0116: Missing function or method docstring (missing-function-docstring)
habit.py:114:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module log
log.py:1:0: C0114: Missing module docstring (missing-module-docstring)
log.py:5:0: C0116: Missing function or method docstring (missing-function-docstring)
log.py:12:0: C0116: Missing function or method docstring (missing-function-docstring)
log.py:19:0: C0116: Missing function or method docstring (missing-function-docstring)
log.py:33:0: C0116: Missing function or method docstring (missing-function-docstring)
log.py:51:0: C0116: Missing function or method docstring (missing-function-docstring)
log.py:62:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module note
note.py:1:0: C0114: Missing module docstring (missing-module-docstring)
note.py:3:0: C0116: Missing function or method docstring (missing-function-docstring)
note.py:13:0: C0116: Missing function or method docstring (missing-function-docstring)
note.py:19:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module participant
participant.py:1:0: C0114: Missing module docstring (missing-module-docstring)
participant.py:3:0: C0116: Missing function or method docstring (missing-function-docstring)
participant.py:11:0: C0116: Missing function or method docstring (missing-function-docstring)
participant.py:18:0: C0116: Missing function or method docstring (missing-function-docstring)
participant.py:24:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module seed
seed.py:1:0: C0114: Missing module docstring (missing-module-docstring)
seed.py:19:0: C0116: Missing function or method docstring (missing-function-docstring)
seed.py:29:0: C0116: Missing function or method docstring (missing-function-docstring)
seed.py:34:0: C0116: Missing function or method docstring (missing-function-docstring)
seed.py:46:0: C0116: Missing function or method docstring (missing-function-docstring)
seed.py:54:0: C0116: Missing function or method docstring (missing-function-docstring)
seed.py:62:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module user
user.py:1:0: C0114: Missing module docstring (missing-module-docstring)
user.py:3:0: C0116: Missing function or method docstring (missing-function-docstring)
user.py:9:0: C0116: Missing function or method docstring (missing-function-docstring)
user.py:15:0: C0116: Missing function or method docstring (missing-function-docstring)
user.py:21:0: C0116: Missing function or method docstring (missing-function-docstring)
user.py:28:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module utils
utils.py:1:0: C0114: Missing module docstring (missing-module-docstring)
utils.py:4:0: C0116: Missing function or method docstring (missing-function-docstring)
utils.py:9:0: C0116: Missing function or method docstring (missing-function-docstring)

------------------------------------------------------------------
Your code has been rated at 8.44/10 (previous run: 8.32/10, +0.13)
```

 Docstring-ilmoitukset

Kaikki Pylintin ilmoitukset ovat tyyppiä `missing-module-docstring` tai
`missing-function-docstring`. Ne tarkoittavat, että moduulien ja funktioiden
alussa ei ole docstring-kuvauksia.

Docstringejä ei lisätty, koska niitä ei edellytetä tällä kurssilla. Sovelluksen
moduulit ovat melko lyhyitä, ja funktioiden nimet sekä niiden vastuut on pyritty
pitämään selkeinä (esimerkiksi `add_habit`, `delete_comment`, `get_week_dates`),
joten lyhyet docstringit lähinnä toistaisivat koodista jo ilmenevän asian. Kaikki
muut Pylintin aiemmin osoittamat rakenteelliset huomautukset korjattiin ennen
tämän lopullisen raportin tekemistä.
