# Scrapcar — monitor ofert samochodowych

Automat sprawdza automarket.pl i findcar.pl wg filtrow zdefiniowanych w
`configs/*.yaml` i wysyla powiadomienia na Telegram / ntfy.sh, gdy pojawi
sie nowa oferta. Oferty, ktore znikaja z wynikow (sprzedane / juz
niepasujace), sa automatycznie usuwane ze stanu.

## Dodawanie nowego monitora

1. Skopiuj `configs/_przyklad.yaml` pod nowa nazwa, np. `configs/moje-bmw.yaml`.
2. Ustaw filtry recznie na automarket.pl / findcar.pl, skopiuj parametry
   z paska adresu do sekcji `filters` w pliku.
3. Commit + push (albo rece odpal `python generate_readme.py`, zeby od razu
   zobaczyc nowa sekcje ponizej).

Kazdy plik w `configs/` to niezalezny monitor - moze sledzic automarket,
findcar, albo obie strony naraz. Nic wiecej nie trzeba zmieniac w kodzie.

## Reczne uruchomienie

```
pip install -r requirements.txt
python run.py                        # wszystkie monitory
python run.py --only arteon-benzyna  # tylko wybrany monitor
python run.py --report-first-run     # zglos od razu wszystkie oferty jako nowe
python generate_readme.py            # odswiez linki ponizej
```

## Historia uruchomien / logi

https://github.com/Maciek-Jasinski/Scrapcar/actions

## Aktualne monitory

<!-- MONITORS:START -->

### VW Arteon benzyna od 2022, do 70 tys km

- [Szukaj na Automarket](https://automarket.pl/samochody/uzywane/wszystkie/volkswagen/arteon?production_year=2022-*&course=*-70000&fuel_type=PB&sort_by=popular&power=180-300)
- [Szukaj na FindCar](https://findcar.pl/znajdz-samochod?makes=volkswagen&models=arteon&conditions=vehicle_used&fuelTypes=petrol&yearMin=2022&mileageMax=70000&size=45&powerMin=180&powerMax=300)

Zapisany stan (co skrypt aktualnie "wie"):
- [Automarket](https://github.com/Maciek-Jasinski/Scrapcar/blob/main/state/arteon-benzyna__automarket.json)
- [FindCar](https://github.com/Maciek-Jasinski/Scrapcar/blob/main/state/arteon-benzyna__findcar.json)

### Multi-marka hybryda/PB, automat, hatchback/sedan

- [Szukaj na Automarket](https://automarket.pl/samochody/uzywane/wszystkie/skoda,toyota,alfa-romeo,audi,bmw,kia,land-rover,lexus,mazda,mercedes-benz,volkswagen,volvo?warranty_protection=1&fuel_type=Hybryda,PB&gearbox_type=Automatyczna&body_style=Hatchback,Sedan&course=*-55537&engine_capacity=1490-*&power=150-*&installment=*-2060&production_year=2022-*&sort_by=popular)
- [Szukaj na FindCar](https://findcar.pl/znajdz-samochod?conditions=vehicle_used&fuelTypes=petrol,hybrid_hev&priceMax=120000&yearMin=2022&mileageMax=50000&mileageMin=6000&capacityMin=1400&powerMin=150&makes=volkswagen,toyota,skoda,alfa-romeo,jaguar,kia,lexus,mazda,mercedes-benz,volvo&transmissionTypes=automatic&bodyTypes=liftback,compact,sedan&size=45)

Zapisany stan (co skrypt aktualnie "wie"):
- [Automarket](https://github.com/Maciek-Jasinski/Scrapcar/blob/main/state/multi-marka-hybryda-pb__automarket.json)
- [FindCar](https://github.com/Maciek-Jasinski/Scrapcar/blob/main/state/multi-marka-hybryda-pb__findcar.json)

<!-- MONITORS:END -->

(Jesli link do pliku stanu pokazuje 404 - plik jeszcze nie istnieje, bo
workflow sie jeszcze nie uruchomil. Odpal recznie w zakladce
**Actions → Run workflow**, a po chwili plik sie pojawi.)
