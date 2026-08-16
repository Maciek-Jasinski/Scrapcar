# Scrapcar — monitor ofert samochodowych

Automat sprawdza automarket.pl i findcar.pl wg poniższych filtrów i wysyła
powiadomienia na Telegram, gdy pojawi się nowa oferta. Oferty, które znikają
z wyników (sprzedane / już niepasujące), są automatycznie usuwane z JSON-a.

## Podgląd wyników na żywo w przeglądarce

- **Automarket** (bezpośredni link do wyszukiwania z aktualnymi filtrami):
  https://automarket.pl/samochody/uzywane/wszystkie/skoda,toyota,alfa-romeo,audi,bmw,kia,land-rover,lexus,mazda,mercedes-benz,volkswagen,volvo?warranty_protection=1&fuel_type=Hybryda,PB&gearbox_type=Automatyczna&body_style=Hatchback,Sedan&course=*-55537&engine_capacity=1490-*&power=150-*&installment=*-3285&installment_cash=*-120000&production_year=2022-*&sort_by=popular

- **FindCar** (bezpośredni link do wyszukiwania z aktualnymi filtrami):
  https://findcar.pl/znajdz-samochod?conditions=vehicle_used&fuelTypes=petrol,hybrid_hev&priceMax=120000&yearMin=2022&mileageMax=50000&mileageMin=6000&capacityMin=1400&powerMin=150&makes=volkswagen,toyota,skoda,alfa-romeo,jaguar,kia,lexus,mazda,mercedes-benz,volvo&transmissionTypes=automatic&bodyTypes=liftback,compact&size=45

## Podgląd zapisanego stanu (co skrypt aktualnie "wie")

- automarket_seen_offers.json:
  https://github.com/Maciek-Jasinski/Scrapcar/blob/main/automarket_seen_offers.json

- findcar_seen_offers.json:
  https://github.com/Maciek-Jasinski/Scrapcar/blob/main/findcar_seen_offers.json

(Jeśli link do pliku pokazuje 404 - plik jeszcze nie istnieje, bo workflow
się jeszcze nie uruchomił / nie zdążył zacommitować. Odpal ręcznie w zakładce
**Actions → Run workflow**, a po chwili plik się pojawi.)

## Historia uruchomień / logi

https://github.com/Maciek-Jasinski/Scrapcar/actions

## Zmiana filtrów

Filtry są zaszyte w słowniku `FILTERS` na górze każdego pliku:
- `automarket_scraper.py`
- `findcar_scraper.py`

Zmieniasz tam wartości -> commit -> przy najbliższym uruchomieniu (albo
ręcznym "Run workflow") zaczną obowiązywać nowe kryteria.
