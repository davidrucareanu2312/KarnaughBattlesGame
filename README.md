Karnaugh Warriors - README
1. Descriere

Karnaugh Warriors este incercarea noastra de a face materia de Proiectare 
Logica puțin mai usor de inteles (si mai fun). Este un joc 2D top-down RPG, 
scris in Python, care pune jucatorul in pielea unui student ce trebuie să 
supravietuiasca unei sesiuni de examene.

Actiunea are loc intr-un fake campus poli, unde "bosii" sunt cea mai random 
grupare de personaje/personalitati: My Talking Tom (tutorial), Obama 
(chiar el), Descartes, Joseph Joestar (pentru cei care cunosc) si, bineinteles,
 cu ocazia sarbatorilor l-am adaugat si pe Fuego. Gameplay-ul alterneaza 
intre explorare si batalii turn-based, unde armele sunt cunostintele de 
proiectare logica si minimizari Karnaugh.

2. Repository

Codul sursa complet si istoricul commit-urilor se afla aici:

    Link repository: https://github.com/davidrucareanu2312/KarnaughBattlesGame

3. Tehnologii și Arhitectură

    Limbaj: Python 3.11

    Engine Grafic: pygame (Community Edition 2.6.1) – 
    folosit pentru randare, gestionarea window-ului de la joc si a input-ului.

    Stocare Date: Fisiere .json – am pus toata configuratia bosilor (dialog, 
    viata) in fisiere separate, ca sa putem modifica gameplayul fara sa intram 
    in codul sursa.

    Audio: pygame.mixer – pentru gestionarea melodiei de fundal in ultimul
     battle.

Structura Codului: Jocul ruleaza pe un State Machine simplu (Intro -> Title 
-> Game -> Cutscene -> Battle). Am folosit OOP pentru a separa logica hartii 
(MapLoader) de logica jucatorului (Player) și a bataliilor (Battle).

4. Instrucțiuni

Dependente necesare rularii jocului: biblioteca pygame

Rularea aplicatiei: python -m game.main din radacina proiectului

pip install pygame

Start Joc: Rulează fișierul principal:
Bash

    python main.py

5. Contribuții Individuale

Suntem o echipa de 2 membri si am incercat sa impartim task-urile in 1.
Functionalitatea efectiva a mapului, a interactiunilor, a miscarii pe harta, 
2. Boss battles, dialog in battle si crearea diagramelor Karnaugh.

    Nasta Alexandra - Functionalitate map, interactiuni, miscare

        In primul rand, am implementat sistemul de deplasare si coliziuni. 
 Am folosit o masca de biti (bitmask) generata din imaginea hartii 
 (campus_mask.png - facuta manual in GIMP), astfel incat playerul sa nu poata 
merge pe conturul clădirilor sau pe masini etc. Am creat design-ul campus
maskului, imaginea cu harta propriu zisa fiind de pe internet si am plasat
NPC-urile si zonele de trigger pentru bosi. Am implementat logica prin care
muzica se schimba dinamic doar atunci cand il batem pe Fuego, folosind 
trigger-ele din MapLoader.
        
        In al doilea rand, m-am ocupat de Game Loop si de gestionarea starilor 
(explore state -> fight state si invers) si astfel, apasand tasta "E" 
pe o cladire, ajungem intr-un boss battle pe care il putem incepe 
(sau nu) in functie de starea bossului anterior celui pe care incercam 
acum sa il batem. In "main.py" se gestioneaza tranzitiile (functionand 
pe baza unei masini cu stari finite), starile fiind: STATE_INTRO, 
STATE_GAME, STATE_BOSS_SEQ si STATE_BATTLE. Astfel, jocul stie cand sa 
 randeze harta/interfata de lupta.
        
        Fisierul "camera.py" exista pentru a permite urmarirea personajului 
odata cu miscarea sa pe harta. Aceasta a fost o decizie pe care am luat-o mai 
tarziu, inainte sa dau primul push, frustrarea fiind faptul ca harta era mult 
prea mare ca sa incapa intr-un window si ori trebuia sa impart in 4 harti mai 
mici, window-sized si sa fac tranzitia de la una la alta cand ajung in
 extremitati, ori sa folosesc acest sistem de urmarire pentru personaj.In 
 "camera.py" se calculeaza un offset bazat pe pozitia curenta a playerului, 
 centrandu-l constant pe ecran. Camera nu poate iesi in afara limitelor
  imaginii de fundal. 

    Rucareanu David Mihai - Sistemul de lupta, Save states, configurari pentru 
    lupte

        - Logica principala de desfasurare a luptelor, tranzitiile intre faze, 
 ce au loc pe baza configurarilor
        din json-urile din configs/Karnaugh ce contin informatii despre: 
reprezentarea phase-urilor, contributia la scor, voice line-urile bossilor, 
sprite-ul necesar + randarea luptelor pe baza informatiilor obtinute din config 
file-uri
        - Logica de completare/minimizare a diagramelor Karnaugh(principala 
        caracteristica a luptelor)
        - Tipuri diferite de bossi
        - Logica de Save Stateuri: incarcarea unei sesiuni a jocului pe baza 
informatiilor retinute in json-urile din configs/SaveStates, abilitatea de a 
incarca sau a sterge un SaveState

6. Dificultăți Întâmpinate

    Din unblocked (alb) ajungea pe blocked (negru), si nu se mai putea misca
playerul.
   Uneori jucătorul rămânea blocat în pereți dacă se mișca 
prea repede. Asadar, am implementat o functie is_walkable care verifica 
viitoarea pozitie a jucatorului inainte de a-l muta efectiv. Daca viitoarea 
pozitie atinge un pixel negru pe masca de coliziune, miscarea este anulata.

    Respawn-ul in urma unei lupta:
        Dupa terminarea unei lupte, uneori, se apleca metoda de gasire a unei
 pozitii corecte si punea caracterul acolo, dar din pacare, se intampla
 cateodata ca pozitia sa fie doar aproape buna si dupa ce ieseam din lupte, 
 ramaneam blocati. A fost de ajuns sa retinem coordonatile inainte de lupta 
 si sa incarcam asa dupa.

    
    Selectia corecta de grupuri de celule la Karnaugh:
        La selectia unui grup de celule in lupte, acceptarea sa la enter nu 
era mereu ok, gen uneori imi lua drept corecte grupari in forma de L dar nu 
lua drept corecte grupari de 4 cu wrap-around. A trebuit sa fie adaugata o 
metoda separata de verificare a validitatii unui grup, care sa se asigure ca
 grupul de celule selectate e corect pe baza dimensinuii sale, continulului 
 sau, si a codificarii in cod Gray.
