Habit-Tracker


Sovelluksen toiminnot:

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään tapoja sekä muokkaamaan ja poistamaan lisäämiään tapoja. Myös jo luotoihin tapoihin muut käyttäjät voivat liittyä.
- Käyttäjäsivu näyttää käyttäjän ja muiden lisäämiä tapoja ja omien suorituskertojen määrää.
- Käyttäjä pystyy poistamaan tavan omalta listalta.
- Käyttäjä pystyy löytämään tapoja nimen perusteella.
- Käyttäjä pystyy lisäämään omiin ja muiden käyttäjien tapoihin muistiinpanot ja motivaatiorepliikit.
- Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja eli montako päivää putkeen käyttäjä on suorittanut tapoja. 
- Käyttäjä pystyy valitsemaan ilmoitukselle yhden tai useamman luokittelun: toistuvuuden määrä per viikko ja osaston (urheilu, hyvinvointi, terveys jne.)
- Jos käyttäjä unohtaa merkata, että on suorittanut tavat, hän voi mennä kalenteriin ja merkata jälkeenpäin, milloin tapa oli suoritettu.




Sovelluksen asennus

Ohjeet toimivat macOS- ja Linux-ympäristöissä. Tarkista ensin, että Python ja SQLite ovat käytettävissä:

Mene terminaaliin ja laita:

python3 --version
sqlite3 --version

Kloonaa repositorio ja siirry sen hakemistoon:
git clone https://github.com/sofiasmorodina5/Habit-Tracker.git
cd Habit-Tracker

Luo virtuaaliympäristö ja asenna Flask:
python3 -m venv venv
source venv/bin/activate
python3 -m pip install flask
sqlite3 database.db < schema.sql

Käynnistä sovellus:
flask run

Sovellusta voi käyttää osoitteessa http://127.0.0.1:5000


Sovelluksen testaaminen
Voit luoda vain yhden käyttäjätunnuksen, sillä käyttö onnistuu myös yhdellä käyttäjällä. Jos taas haluat nähdä, miten kaksi käyttäjää vuorovaikuttaa, voit luoda kaksi.

Rekisteröidy ja kirjaudu ensimmäisellä käyttäjällä.
Lisää uusi tapa ja valitse sille halutessaan luokittelu.
Tarkista, että tapa näkyy etusivulla ja että onnistumisilmoitus tulee näkyviin.
Muokkaa lisäämääsi tapaa ja vaihda luokittelua. Tarkista, että muutokset tallentuvat.
Poista tapa ja varmista, että se poistuu listalta.
Yritä lisätä tapa tyhjällä otsikolla. Tavan ei pitäisi muodostua.
Klikkaa tavan otsikkoa ja siirry tavan omalle sivulle.
Klikkaa kalenterin päivää merkitäksesi suorituksen edellis päivänä. Klikkaa uudelleen poistaaksesi merkinnän.
Tarkista, että Streak (putki) ja "Tällä viikolla" -laskuri päivittyvät oikein.
Luo toinen käyttäjä.
Kirjoita kommentti toisen käyttäjän tapaan (tai omaasi) ja tarkista, että se näkyy.
Lisää motivaatiomuistiinpano ja varmista, että se tallentuu ja voit poistaa sen.
Klikkaa "Oma profiili" ja tarkista, että tilastot (suoritukset, paras putki) näkyvät.
Kokeile hakutoimintoa kirjoittamalla hakukenttään osa tavan nimestä.
Kirjaudu ulos ja yritä mennä osoitteeseen /add. Sovelluksen pitäisi ohjata kirjautumissivulle.
Kokeile CSRF-suojausta: poista lomakkeesta piilotettu csrf_token-kenttä ja lähetä lomake. Pitäisi tulla 403-virhe.
Lopuksi voit kirjautua ulos.
