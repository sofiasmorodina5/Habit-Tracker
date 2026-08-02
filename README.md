# Habit Tracker

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään sovellukseen tapoja. Lisäksi käyttäjä pystyy muokkaamaan ja poistamaan lisäämiään tapoja.
- Käyttäjä näkee sovellukseen lisätyt tavat. Käyttäjä näkee sekä itse lisäämänsä että muiden käyttäjien lisäämät tavat.
- Käyttäjä pystyy etsimään tapoja hakusanalla tai muulla perusteella. Käyttäjä pystyy hakemaan sekä itse lisäämiään että muiden käyttäjien lisäämiä tapoja.
- Sovelluksessa on käyttäjäsivut, jotka näyttävät jokaisesta käyttäjästä tilastoja ja käyttäjän lisäämät tavat.
- Tietokohteille on valittavissa useampia luokitteluja, jotka on tallennettu tietokantaan. Käyttäjä voi valita jokaisen luokittelun kohdalla yhden useasta vaihtoehdosta. Luokittelut ovat esimerkikisi: viikon päivät, jolloin kysyinen tapa pitäisi suorittaa, tai kertojen määrä per päivä/viikko/kuukausi, jolloin tietty tapa pitäisi suorittaa.
- Sovelluksessa pääasiallisen tavoite on omien "habittien seuranta", lisäksi toissijainen tietokohde on ilmoittautuminen ja osallistuminen muiden käyttäjiin luomiin tapoihin. Tämä täydentää pääasiallista tietokohdetta. Käyttäjä pystyy lisäämään toissijaisia tapoja omiin ja muiden käyttäjien tapoihin.

Asennus ja Käynnistys
Mene terminaaliin ja kirjoita:

git clone https://github.com/sofiasmorodina5/Habit-Tracker.git
cd Habit-Tracker
python3 -m venv venv
source venv/bin/activate  
pip install -r requirements.txt
sqlite3 database.db < schema.sql
flask run

Sitten mene selaimeen ja kirjoita: 
http://127.0.0.1:5000

Rekisteröidy ensin ja sitten kirjaudu sovelluksen sisään. Sen jälkeen voit käyttää sovellusta.
