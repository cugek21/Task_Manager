"""
zadani_1.py: čtvrtý projekt do Engeto Tester s Pythonem

author: Radek Jíša
email: radek.jisa@gmail.com
"""

ukoly = []

def hlavni_menu() -> int:
    '''
    Zobrazí hlavní menu a vyžádá si volbu uživatele.
    '''
    print(
        '\nSprávce úkolů - Hlavní menu\n'
        '1. Přidat nový úkol\n'
        '2. Zobrazit všechny úkoly\n'
        '3. Odstranit úkol\n'
        '4. Konec programu\n'
        )

    volba = input('Vyberte možnost (1-4): ').strip()

    if volba.isdigit() and int(volba) in range(1, 5):
        return int(volba)
    else:
        print('Neplatná volba. Zadejte číslo mezi 1 a 4.')
        return hlavni_menu()

def pridat_ukol() -> None:
    '''
    Vyžádá si od uživatele název a popis úkolu a přidá jej do seznamu úkolů.
    '''
    nazev = input('Zadejte název úkolu: ').strip()
    popis = input('Zadejte popis úkolu: ').strip()
    if nazev and popis:
        ukol = {
            'Nazev': nazev,
            'Popis': popis,
        }
        ukoly.append(ukol)
        print(f'Úkol {nazev} byl úspěšně přidán.')
    else:
        print('Pole název a popis úkolu nesmí být prázdné.')
        return pridat_ukol()

def zobrazit_ukoly() -> None:
    '''
    Vypíše seznam všech aktuálně uložených úkolů.
    '''
    if not ukoly:
        print('Žádné úkoly nebyly přidány.')
    else:
        print('\nSeznam úkolů:')
        for index, ukol in enumerate(ukoly, start=1):
            print(f"{index}. Název: {ukol['Nazev']}, Popis: {ukol['Popis']}")

def odstranit_ukol() -> None:
    '''
    Zobrazí seznam úkolů a umožní uživateli vybrat úkol k odstranění.
    '''
    zobrazit_ukoly()
    vyber_ukolu = input('Zadejte číslo úkolu, který chcete odstranit: ').strip()

    if vyber_ukolu.isdigit() and 1 <= int(vyber_ukolu) <= len(ukoly):
        odstraneny_ukol = ukoly.pop(int(vyber_ukolu) - 1)
        print(f"Úkol {odstraneny_ukol['Nazev']} byl úspěšně odstraněn.")
    else:
        print('Neplatná volba. Zadejte číslo úkolu, který chcete odstranit.')
        return odstranit_ukol()

def main() -> None:
    '''
    Hlavní smyčka programu. Zobrazuje hlavní menu a reaguje na uživatelské volby.
    '''
    while True:
        volba = hlavni_menu()
        if volba == 1:
            pridat_ukol()
        elif volba == 2:
            zobrazit_ukoly()
        elif volba == 3:
            odstranit_ukol()
        elif volba == 4:
            print('Konec programu')
            break

if __name__ == '__main__':
    main()
