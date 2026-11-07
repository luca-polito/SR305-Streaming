# Intel RealSense SR305: acquisizione RGB e profondità

Esempi Python per attività didattiche con la camera **Intel RealSense SR305**. Il progetto comprende due viewer live, per confrontare l'acquisizione originale con l'allineamento del colore alla profondità, e un viewer per riprodurre registrazioni RealSense `.bag`. Tutti mostrano l'immagine a colori e la mappa di profondità affiancate.

Materiale a cura di [luca-polito](https://github.com/luca-polito).

## Gli script

| Script | Funzionalità |
| --- | --- |
| [`rs_live_basic_example.py`](rs_live_basic_example.py) | Acquisisce e visualizza i frame RGB e di profondità nelle rispettive coordinate originali. Non esegue allineamento geometrico. |
| [`rs_live_align_example.py`](rs_live_align_example.py) | Allinea il frame RGB alla griglia del sensore di profondità tramite `rs.align(rs.stream.depth)`, prima della visualizzazione. |
| [`rs_recorded_sequence_basic_example.py`](rs_recorded_sequence_basic_example.py) | Riproduce una registrazione RealSense `.bag`, mostrando colore e profondità affiancati senza allineamento geometrico. |

Entrambi gli script live:

- acquisiscono profondità a **640 × 480, 30 fps**, in formato `z16`, e colore a **640 × 480, 30 fps**, in formato `bgr8`;
- tentano di abilitare l'esposizione automatica RGB, se il sensore la supporta;
- visualizzano il colore a sinistra e la profondità colorizzata a destra nella finestra `RealSense`;
- usano `rs.colorizer()` con palette **Jet** RealSense e equalizzazione dell'istogramma per il contrasto automatico;
- arrestano la pipeline nel blocco `finally` quando l'esecuzione termina.

Nella palette Jet RealSense le distanze crescono dal **blu**, attraverso ciano e giallo, fino al **rosso scuro**. I pixel senza una misura di profondità valida sono neri. Con l'equalizzazione attiva, l'associazione tra distanza e colore si adatta alla distribuzione delle profondità del frame: un colore non rappresenta una distanza fissa in metri.

### Che cosa cambia con l'allineamento

I sensori RGB e di profondità hanno punti di vista e parametri ottici diversi. Anche quando le immagini hanno la stessa risoluzione, lo stesso pixel `(x, y)` può rappresentare punti diversi della scena.

In `rs_live_align_example.py`, `rs.align(rs.stream.depth)` usa la calibrazione della camera e le misure di profondità per riproiettare il colore nelle coordinate della profondità. La profondità mantiene la propria griglia; il colore viene adattato a quella griglia. Dove mancano misure valide o il punto non è visibile al sensore RGB, il colore allineato può presentare aree nere o artefatti, soprattutto lungo i bordi degli oggetti.

Nei programmi base, live e da registrazione, l'eventuale `cv2.resize()` serve solo ad affiancare immagini di dimensioni diverse: non realizza questo allineamento.

## Ambiente e dipendenze

Versioni rilevate nell'ambiente locale `realsenseSR305-viewer` su Windows:

| Componente | Versione | Utilizzo |
| --- | --- | --- |
| Python | **3.9.25** | Interprete |
| `pyrealsense2` | **2.50.0.3812** | Accesso alla camera, acquisizione, riproduzione `.bag`, esposizione, colorizzazione e allineamento |
| `numpy` | **2.0.1** | Conversione dei frame in array e affiancamento delle immagini |
| `opencv-python` | **4.11.0.86** | Finestre, visualizzazione, conversione RGB/BGR e ridimensionamento |

I pacchetti Python sono elencati in [`requirements.txt`](requirements.txt).

Tutti e tre gli script usano le stesse dipendenze. Il viewer da registrazione utilizza anche `argparse` e `pathlib`, inclusi nella libreria standard Python: non richiedono installazioni aggiuntive.

**Usare Python 3.9 a 64 bit** per riprodurre questo ambiente: la versione indicata di `pyrealsense2` dispone di un pacchetto Windows per Python 3.9, ma non per Python 3.10. Usare **`opencv-python`**, con supporto grafico; la variante `opencv-python-headless` non può aprire la finestra del viewer.

### OpenCV con finestre proprie o con PyQt

Gli esempi di questo repository visualizzano le immagini con `cv2.namedWindow()` e `cv2.imshow()`, quindi richiedono **`opencv-python`**.

Per un'applicazione la cui interfaccia è gestita da **PyQt**, è invece consigliato **`opencv-python-headless`**: OpenCV elabora le immagini, mentre PyQt le visualizza tramite `QImage`, `QPixmap` e widget. La variante headless esclude le dipendenze grafiche di OpenCV e può evitare conflitti con quelle dell'interfaccia. Un conflitto tra OpenCV con supporto grafico e PyQt non è automatico: dipende dalla piattaforma e dalla compilazione di OpenCV.

| Come vengono visualizzate le immagini | Pacchetto consigliato |
| --- | --- |
| Finestre OpenCV con `cv2.imshow()` e `cv2.namedWindow()` | `opencv-python` |
| Interfaccia gestita da PyQt, senza finestre OpenCV | `opencv-python-headless` |

Installare **una sola variante OpenCV per ambiente**: `opencv-python` e `opencv-python-headless` forniscono entrambe il modulo `cv2` e non devono essere installate insieme. Per mantenere sia questi esempi sia un progetto PyQt con headless, usare ambienti separati. Vedere la [documentazione del pacchetto OpenCV](https://pypi.org/project/opencv-python/).

## Installazione con Conda

Per l'installazione occorre Conda disponibile nell'Anaconda Prompt. Per gli esempi live servono inoltre una SR305 collegata e riconosciuta da Windows e l'accesso alla camera consentito alle applicazioni desktop. Chiudere eventuali altri programmi che stanno usando la camera. Per il viewer da registrazione basta un file RealSense `.bag` locale con entrambi i flussi RGB e profondità.

Scaricare il repository da GitHub tramite **Code → Download ZIP** ed estrarlo, oppure clonarlo con Git. Aprire Anaconda Prompt nella cartella che contiene gli script e `requirements.txt`, quindi eseguire:

```bat
conda create -n realsenseSR305-viewer python=3.9.25 pip
conda activate realsenseSR305-viewer
python -m pip install -r requirements.txt
```

L'ambiente separato permette di mantenere altri progetti con dipendenze diverse, incluse eventuali installazioni headless di OpenCV.

In VS Code selezionare **Python: Select Interpreter** dalla palette comandi e scegliere l'interprete dell'ambiente `realsenseSR305-viewer`.

## Esecuzione

### Streaming live

Con l'ambiente attivo, dalla cartella del progetto eseguire uno script alla volta:

```bat
python rs_live_basic_example.py
```

oppure:

```bat
python rs_live_align_example.py
```

Attendere qualche secondo per l'adattamento dell'esposizione automatica. Per interrompere lo script, premere **Ctrl+C nel terminale**. I due script live non implementano un comando di uscita con `q` o `Esc`.

### Riproduzione di una registrazione

Il terzo script richiede un file **RealSense `.bag` contenente sia colore sia profondità**. Un normale video `.mp4` o `.avi` non contiene i flussi RealSense necessari. Per riprodurre il file non serve collegare la camera.

Passare il percorso tra virgolette, ad esempio:

```bat
python rs_recorded_sequence_basic_example.py "C:\registrazioni\sequenza.bag"
```

Oppure avviare lo script senza argomenti e inserire il percorso quando richiesto:

```bat
python rs_recorded_sequence_basic_example.py
```

In questo caso incollare il percorso nel terminale e premere **Invio**. Il testo passato a `input()` nel codice è solo il messaggio della richiesta: non occorre modificarlo per scegliere il file. I percorsi relativi sono risolti rispetto alla cartella da cui si avvia il comando.

Per file su Google Drive per desktop, renderli disponibili offline e attendere il download completo, oppure copiarli sul disco locale. Passare un percorso del filesystem, non un link web di condivisione. Il repository contiene gli script; ciascuno deve procurarsi separatamente la registrazione da riprodurre.

La riproduzione usa risoluzioni e frequenze registrate e termina alla fine del file, senza ricominciare. Il colore è mostrato a sinistra, la profondità con la stessa palette Jet degli esempi live a destra. L'esposizione è quella della registrazione. In questo script è possibile uscire con **q**, **Esc** o chiudendo la finestra.

## Problemi comuni

| Problema | Controllo suggerito |
| --- | --- |
| Errore OpenCV «The function is not implemented» su `namedWindow` | Verificare di usare l'interprete corretto e `opencv-python`, senza la variante headless nello stesso ambiente. |
| `No matching distribution found` per `pyrealsense2==2.50.0.3812` | Controllare con `python --version` di usare Python 3.9 e un interprete a 64 bit. |
| Camera non rilevata o accesso negato | Controllare collegamento USB, riconoscimento del dispositivo, permessi della camera in Windows e altri programmi che potrebbero utilizzarla. |
| Immagine RGB scura | Attendere l'adattamento automatico e controllare l'illuminazione e gli eventuali messaggi sull'esposizione nel terminale. |
| `Recording file not found` | Verificare il percorso del `.bag`; usare le virgolette nel comando se contiene spazi e assicurarsi che il file sia scaricato sul PC. |
| Il programma mostra la richiesta del percorso e sembra fermo | Incollare il percorso e premere Invio, oppure passarlo direttamente come argomento del comando. |
| Impossibile avviare la riproduzione `.bag` | Verificare che il file sia una registrazione RealSense leggibile con entrambi i flussi colore e profondità. |

## Riferimenti e provenienza

Gli script derivano dagli esempi Python del progetto [librealsense](https://github.com/realsenseai/librealsense), adattati per questi esempi didattici. Le intestazioni originali riportano copyright RealSense e licenza Apache 2.0.

- [Esempi Python librealsense](https://github.com/realsenseai/librealsense/tree/v2.50.0/wrappers/python/examples)
- [Pacchetti di pyrealsense2 2.50.0.3812](https://pypi.org/project/pyrealsense2/2.50.0.3812/#files)
- [Licenza Apache 2.0 del progetto originale](https://github.com/realsenseai/librealsense/blob/v2.50.0/LICENSE)
