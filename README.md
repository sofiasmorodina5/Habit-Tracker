<h1>Habit-Tracker</h1>


<h2>Sovelluksen toiminnot:</h2>

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään tapoja sekä muokkaamaan ja poistamaan lisäämiään tapoja. Myös jo luotoihin tapoihin muut käyttäjät voivat liittyä.
- Käyttäjäsivu näyttää käyttäjän ja muiden lisäämiä tapoja ja omien suorituskertojen määrää.
- Käyttäjä pystyy poistamaan tavan omalta listalta.
- Käyttäjä pystyy löytämään tapoja nimen perusteella.
- Käyttäjä pystyy lisäämään omiin ja muiden käyttäjien tapoihin muistiinpanot ja motivaatiorepliikit.
- Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja eli montako päivää putkeen käyttäjä on suorittanut tapoja. 
- Käyttäjä pystyy valitsemaan ilmoitukselle yhden tai useamman luokittelun: toistuvuuden määrä per viikko ja osaston (urheilu, hyvinvointi, terveys jne.)
- Jos käyttäjä unohtaa merkata, että on suorittanut tavat, hän voi mennä kalenteriin ja merkata jälkeenpäin, milloin tapa oli suoritettu.




<h2>Sovelluksen asennus</h2>

Ohjeet toimivat macOS- ja Linux-ympäristöissä. Tarkista ensin, että Python ja SQLite ovat käytettävissä:

<h3>Mene terminaaliin ja laita:</h3>

python3 --version

sqlite3 --version


<h3>Kloonaa repositorio ja siirry sen hakemistoon:</h3>


git clone https://github.com/sofiasmorodina5/Habit-Tracker.git

cd Habit-Tracker


<h3>Luo virtuaaliympäristö ja asenna Flask:</h3>

python3 -m venv venv

source venv/bin/activate

python3 -m pip install flask

sqlite3 database.db < schema.sql


<h3>Käynnistä sovellus:</h3>

flask run

Sovellusta voi käyttää osoitteessa http://127.0.0.1:5000




<h2>Sovelluksen testaaminen</h2>

Voit luoda vain yhden käyttäjätunnuksen, sillä käyttö onnistuu myös yhdellä käyttäjällä. Jos taas haluat nähdä, miten kaksi käyttäjää vuorovaikuttaa, voit luoda kaksi.

1.Rekisteröidy ja kirjaudu ensimmäisellä käyttäjällä.

2.Lisää uusi tapa ja valitse sille halutessaan luokittelu.

3.Tarkista, että tapa näkyy etusivulla ja että onnistumisilmoitus tulee näkyviin.

3.Muokkaa lisäämääsi tapaa ja vaihda luokittelua. Tarkista, että muutokset tallentuvat.

4.Poista tapa ja varmista, että se poistuu listalta.

5.Yritä lisätä tapa tyhjällä otsikolla. Tavan ei pitäisi muodostua.

6.Klikkaa tavan otsikkoa ja siirry tavan omalle sivulle.

7.Klikkaa kalenterin päivää merkitäksesi suorituksen edellis päivänä. Klikkaa uudelleen poistaaksesi merkinnän.

8.Tarkista, että Streak (putki) ja "Tällä viikolla" -laskuri päivittyvät oikein.

9.Luo toinen käyttäjä.

10.Kirjoita kommentti toisen käyttäjän tapaan (tai omaasi) ja tarkista, että se näkyy.

11.Lisää motivaatiomuistiinpano ja varmista, että se tallentuu ja voit poistaa sen.

12.Klikkaa "Oma profiili" ja tarkista, että tilastot (suoritukset, paras putki) näkyvät.

13.Kokeile hakutoimintoa kirjoittamalla hakukenttään osa tavan nimestä.

14.Kirjaudu ulos ja yritä mennä osoitteeseen /add. Sovelluksen pitäisi ohjata kirjautumissivulle.

15.Kokeile CSRF-suojausta: poista lomakkeesta piilotettu csrf_token-kenttä ja lähetä lomake. Pitäisi tulla 403-virhe.

16.Lopuksi voit kirjautua ulos.
