Implementační dokumentace k 2. úloze do IPP 2022/2023 <br>
Jméno a příjmení: Patrik Gáfrik <br>
Login: xgafri00

### Úvod
Implementácia skriptu interpret.py v jazyku Python 3.10. Skript načíta vstupnú XML reprezentáciu kódu v jazyku IPPcode23, skontroluje správnosť XML štruktúry, vykoná syntaktickú analýzu programu a interpretuje jednotlivé inštrukcie IPPcode23 podľa popisu sémantiky v zadaní projektu.

### Popis objektovo-orientovaného návrhu
Pri objektovo-orientovanom návrhu som sa rozhodol program rozdeliť na triedy:
 - **class Interpret** -> implementuje statické metódy pre spracovanie argumentov, načítanie vstupného súboru, 											kontrolu štruktúry XML a spracovanie inštrukcií pre interpretáciu
 - **class Instruction** -> reprezentuje XML element pre inštrukciu, implementuje metódy pre interpretáciu konkrétnej inštrukcie
 - **class FrameModel** -> reprezentuje pamäťový model programu, implementuje rámce pre ukladanie premenných a triedne metódy pre manipuláciu s premennými
 - **class Var** -> reprezentuje argument inštrukcie typu premenná
 - **class Symb** -> reprezentuje argument inštrukcie typu konštanta
 - **class Label** -> reprezentuje návestie

### Popis riešenia
#### Spracovanie XML štruktúry
Pre spracovanie XML štruktúry som využil knižnicu **ElementTree** pomocou ktorej zo vstupného XML súboru vytvorím stromovú štruktúru XML elementov (metóda **load_xml()** v triede Interpret).

#### Interpretácia inštrukcií
Interpretácia inštrukcií začína volaním metódy **Interpret.interpret()**, ktorá najskôr skontroluje správnosť XML štruktúry (prítomnosť správnych tagov a atribútov v elementoch, obmedzenia u atribútu order). Potom začne prechádzať jednotlivé inštrukcie v strome elementov cez for cyklus a pre každú inštrukciu vytvorí instanciu triedy **Instruction** a následne na túto instanciu zavolá metódu **Instruction.process_instruction()**. Pri vytváraní instancií triedy **Instruction** sa na jednotlivé argumenty inštrukcie zavolá metóda **Instruction.get_type()** ktorá podľa atribútu **type** rozhodne o aký typ argumentu ide a podľa toho vytvorí instanciu príslušnej triedy (**Var,** **Symb** alebo **Label**). Instanciu tejto triedy potom uloží do poľa **args**. Metóda **Instruction.process_instruction()** je implementovaná ako match-case, ktorý podľa atribútu **opcode** rozhodne ktorá inštrukcia sa bude interpretovať a podľa toho zavolá metódu ktorá implementuje príslušnú inštrukciu (riadky 430-590) .

#### Práca s pamäťovým modelom
Pamäťový model je implementovaný ako sada troch python dictionaries (globálny, lokálny, dočasný rámec) a jeden zásobník pre ukladanie rámcov. Pre pridanie premennej do rámca (inštrukcia **DEFVAR**) slúži metóda **FrameModel.add_to_frame()** ktorá najskôr zistí typ rámca z názvu premennej pomocou metódy **FrameModel.get_frame()** a potom pridá premennú do rámca ako key v dictionary **rámec[názov_premennej]**. Pre inicializaciu premennej (inštrukcia **MOVE**) sa zavolá metóda **FrameModel.init_var()** ktorá do premennej uloží hodnotu v prípade premennej ako **rámec_l_hodnoty[názov_premennej] = rámec_r_hodnoty[názov_premennej]** a v prípade konštanty ako **rámec_l_hodnoty[názov_premennej] = konštanta**. Pri inštrukcií **CREATEFRAME** sa dočasný rámec **FrameModel.TF** inicializuje na prázdny dictionary. Pri inštrukcií **PUSHFRAME** sa zásobník rámcov **FrameModel.stack** pridá dočasný rámec **FrameModel.TF** (v prípade, že už bol vytvorený, inak chyba 55). Pri inštrukcií **POPFRAME** sa zo zásobníku rámcov odstráni vrcholový rámec a uloží sa do dočasného rámca **FrameModel.TF**. Lokálny rámec **FrameModel.LF** je vždy inicializovaný na vrcholový rámec na zásobníku rámcov.


### Spustenie skriptu
Skript je možné spustiť príkazom:

`python3 interpret.py --source=[SOURCE_FILE] --input=[INPUT_FILE]` <br>
**SOURCE_FILE** je vstupný súbor s XML reprezentáciou programu <br>
**INPUT_FILE** súbor so vstupmi pre inštrukciu READ

### Class diagram v UML
![Class diagram](class_diagram_interpret.drawio.png)

