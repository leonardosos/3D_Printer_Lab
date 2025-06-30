# Riunione Iniziale del Progetto IoT

## MICROSERVIZI

Devono essere semplici, senza introdurre tool esterni complicati.

È sufficiente definire chiaramente le responsabilità: anche un'architettura "grezza" va bene, purché sia funzionale.

**Comunicazione doppia tra microservizi:**

- Può essere implementata con un sidecar, ma questo dettaglio va solo accennato nella presentazione.
- All'interno del codice, si può gestire tutto nello stesso servizio/classe.

(Usare file di configurazione per tutte le impostazioni, evitando hardcoded.)

## ARCHITETTURA

Deve essere scomposta in componenti chiari e ciascuno deve avere una responsabilità ben definita.

Deve risultare modulare, facilmente scalabile e leggibile.

## GUI (Interfaccia Grafica)

Deve essere stilizzata in modo semplice.

Evitare CSS complessi e meccanismi di comunicazione strani o opachi che complicano l'integrazione. (può chiedere come avviene la comunicazione tra frontend e backend)

## TOPIC E ARCHITETTURA MODULARE

L'architettura deve permettere di vedere chiaramente i componenti e supportare la scalabilità automatica delle operazioni in base all'aumento dei device.

Evitare valori hardcoded, ad esempio trattare i topic tramite ID dinamici.

## CLASS DIAGRAM

Consigliato creare un diagramma delle classi per ogni microservizio principale:

- Deve contenere attributi e metodi principali.
- Per microservizi piccoli o molto semplici, può essere generico o anche evitato.
- L'importante è che siano chiare le responsabilità delle classi, la loro composizione/decomposizione, e i rapporti d'uso (chi usa cosa, dove e come).

## SUGGERIMENTI FINALI

Prima di fare codice definire per ogni classe e microservizio:

- Strutture dati utilizzate
- Interfacce di comunicazione
- Tipi di sanity check
- Metodi delle classi principali
