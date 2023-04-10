Implementační dokumentace k 1. úloze do IPP 2022/2023 <br>
Jméno a příjmení: Patrik Gáfrik <br>
Login: xgafri00

### Úvod
Implementácia skriptu `parse.php` v jazyku PHP 8.1. Skript načíta zo štandardného vstupu kód v jazyku `IPPcode23`, vykoná lexikálnu a syntaktickú kontrolu kódu a na štandardný výstup vypíše XML reprezentáciu kódu určenú pre spracovanie interpretom.
<br/>

### Popis riešenia
Skript načítava vstupný kód riadok po riadku vo while cykle pomocou funkcie `fgets`. Pokiaľ sa v načítanom riadku nachádza komentár, odstráni ho pomocou funkcie `removeComment` a taktiež sa z riadku odstránia biele znaky na začiatku a na konci a odstráni sa znak '\n' pomocou funkcií `trim` a `str_replace`.
Potom sa riadok rozdelí na pole tokenov (podľa separátoru " " alebo "\t") pomocou funkcie `tokenizeLine`. Táto funkcia vráti pole tokenov, ktoré sa ukladá do premennej `$tokens`. Po načítaní prvého riadku sa skontroluje prítomnosť hlavičky pomocou `preg_match`, čo je vstavaná funkcia na kontrolu zhody reťazca s regulárnym výrazom.
V prípade, že táto funkcia vráti hodnotu true, do globálnej premennej `$xml` sa zapíše koreňový element `program` s príslušným atribútom `langauge`. Ak funkcia vráti false, program sa ukončí s chybovým kódom 21. Pri načítaní ďaľších riadkov sa preskočí kontrola hlavičky a zavolá sa funkcia `codeParse`, ktorá berie na vstup pole tokenov `$tokens`.
Táto funkcia sa podľa názvu inštrukcie (`$tokens[0]`) rozhodne, akú akciu vykoná. Inštrukcie sú rozdelené podľa počtu a typu povinných argumentov. Pre výpis XML reprezentácie kódu sa
používa knižnica `XMLWriter`. Globálna premenná `$xml` je objekt triedy `XMLWriter` a využíva metódy pre zápis XML elementov. Elementy pre inštrukcie a argumenty zapisujeme do `$xml` pomocou funkcií `writeInstruction`, `writeVar`, `writeSymb`, `writeLabel`, `writeType`. U každej inštrukcií sa najprv skontroluje počet argumentov, v prípade, že je chybný, program sa 
ukončí s chybovým kódom 23. Pre syntaktickú kontrolu argumentov slúžia funkcie `checkVar`, `checkSymb`, `checkLabel`, `checkType`, ktoré porovnajú zhodu argumentu s regulárnym výrazom podľa popisu jazyka. V prípade, že aspoň jedna z týchto funkcií vráti false, program sa ukončí s chybovým kódom 23.

### Spustenie skriptu
Skript je možné spustiť príkazom:
```
php8.1 parse.php [options] <filename
```
kde `filename` je názov zdrojového súboru IPPcode23