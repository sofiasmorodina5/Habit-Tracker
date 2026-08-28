<h1>Habit-Tracker</h1>


<h2>Sovelluksen toiminnot:</h2>

## Sovelluksen toiminnot

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään uusia tapoja sekä muokkaamaan ja poistamaan lisäämiään tapoja.
- Käyttäjä näkee kaikki sovellukseen lisätyt tavat etusivulla.
- Käyttäjä pystyy hakemaan tapoja otsikon tai luokittelun perusteella.
- Käyttäjäsivu näyttää tilastoja (suorituskertojen määrä, paras putki) ja käyttäjän lisäämät tavat.
- Käyttäjä pystyy valitsemaan tavalle luokittelun (urheilu, hyvinvointi, terveys, oppiminen, työ, harrastus) ja vaikeustason (helppo, neutraali, vaativa).
- Käyttäjä pystyy merkitsemään suorituksia kalenterista klikkaamalla päivää.
- Streak (putki) laskee, montako päivää putkeen käyttäjä on suorittanut tiettyä tapaa.
- Streak katkeaa, jos käyttäjä jättää yhdenkin päivän merkkaamatta.
- Käyttäjä voi merkitä suorituksen jälkeenpäin kalenterista, jos on unohtanut merkitä sen aiemmin.
- Käyttäjä voi osallistua muiden käyttäjien luomiin tapoihin painamalla "Osallistu"-nappia.
- Vain tavan omistaja ja osallistujat voivat lisätä kommentteja ja motivaatiomuistiinpanoja.
- Tavan luoja ei näy osallistujien määrässä.
- Käyttäjä voi jättää motivaatiorepliikkejä ja kommentteja muiden tapoihin.
- Kommentit ja muistiinpanot ovat enintään 30 merkkiä pitkiä, ja sovellus estää fyysisesti kirjoittamasta enempää.
- Sovellus estää tyhjien kommenttien ja muistiinpanojen lähettämisen.
- Käyttäjä voi poistaa omat kommenttinsa ja muistiinpanonsa.
- Käyttäjä voi poistua osallistumasta tapaan "Poistu"-napilla.



<h2>Sovelluksen asennus</h2>

Ohjeet toimivat macOS- ja Linux-ympäristöissä. Tarkista ensin, että Python ja SQLite ovat käytettävissä:

<h3>Mene terminaaliin ja laita:</h3>

```bash
python3 --version

sqlite3 --version
```

<h3>Kloonaa repositorio ja siirry sen hakemistoon:</h3>

```bash
git clone https://github.com/sofiasmorodina5/Habit-Tracker.git

cd Habit-Tracker
```

<h3>Luo virtuaaliympäristö ja asenna Flask:</h3>

```bash
python3 -m venv venv

source venv/bin/activate

python3 -m pip install flask

sqlite3 database.db < schema.sql
```

<h3>Käynnistä sovellus:</h3>

```bash
flask run
```


<h3>Sovellusta voi käyttää osoitteessa:</h3>

```bash
http://127.0.0.1:5000
```



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

10.Kirjoita kommentti toisen käyttäjän tapaan  ja tarkista, että se näkyy.

11.Lisää motivaatiomuistiinpano ja varmista, että se tallentuu ja voit poistaa sen.

12.Klikkaa "Oma profiili" ja tarkista, että tilastot (suoritukset, paras putki) näkyvät.

13.Kokeile hakutoimintoa kirjoittamalla hakukenttään osa tavan nimestä.

14.Lopuksi voit kirjautua ulos.
