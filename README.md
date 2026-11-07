# Intel RealSense SR305: acquisizione RGB e profondità

Esempi Python per attività didattiche con la camera **Intel RealSense SR305**. Gli script mostrano in tempo reale l'immagine a colori e la mappa di profondità e permettono di confrontare l'acquisizione originale con l'allineamento del colore alla profondità.

Materiale a cura di [luca-polito](https://github.com/luca-polito).

## Gli script

| Script | Funzionalità |
| --- | --- |
| [`rs_basic_example.py`](rs_basic_example.py) | Acquisisce e visualizza i frame RGB e di profondità nelle rispettive coordinate originali. Non esegue allineamento geometrico. |
| [`rs_align_example.py`](rs_align_example.py) | Allinea il frame RGB alla griglia del sensore di profondità tramite `rs.align(rs.stream.depth)`, prima della visualizzazione. |

Entrambi gli script:

- acquisiscono profondità a **640 × 480, 30 fps**, in formato `z16`, e colore a **640 × 480, 30 fps**, in formato `bgr8`;
- tentano di abilitare l'esposizione automatica RGB, se il sensore la supporta;
- visualizzano il colore a sinistra e la profondità colorizzata a destra nella finestra `RealSense`;
- usano `rs.colorizer()` con palette **Jet** RealSense e equalizzazione dell'istogramma per il contrasto automatico;
- arrestano la pipeline nel blocco `finally` quando l'esecuzione termina.

Nella palette Jet RealSense le distanze crescono dal **blu**, attraverso ciano e giallo, fino al **rosso scuro**. I pixel senza una misura di profondità valida sono neri. Con l'equalizzazione attiva, l'associazione tra distanza e colore si adatta alla distribuzione delle profondità del frame: un colore non rappresenta una distanza fissa in metri.

### Che cosa cambia con l'allineamento

I sensori RGB e di profondità hanno punti di vista e parametri ottici diversi. Anche quando le immagini hanno la stessa risoluzione, lo stesso pixel `(x, y)` può rappresentare punti diversi della scena.

In `rs_align_example.py`, `rs.align(rs.stream.depth)` usa la calibrazione della camera e le misure di profondità per riproiettare il colore nelle coordinate della profondità. La profondità mantiene la propria griglia; il colore viene adattato a quella griglia. Dove mancano misure valide o il punto non è visibile al sensore RGB, il colore allineato può presentare aree nere o artefatti, soprattutto lungo i bordi degli oggetti.

Nel programma base, l'eventuale `cv2.resize()` serve solo ad affiancare immagini di dimensioni diverse: non realizza questo allineamento.

## Ambiente e dipendenze

Versioni rilevate nell'ambiente locale `realsenseSR305-viewer` su Windows:

| Componente | Versione | Utilizzo |
| --- | --- | --- |
| Python | **3.9.25** | Interprete |
| `pyrealsense2` | **2.50.0.3812** | Accesso alla camera, acquisizione, esposizione, colorizzazione e allineamento |
| `numpy` | **2.0.1** | Conversione dei frame in array e affiancamento delle immagini |
| `opencv-python` | **4.11.0.86** | Finestre, visualizzazione, conversione RGB/BGR e ridimensionamento |

I pacchetti Python sono elencati in [`requirements.txt`](requirements.txt).

**Usare Python 3.9 a 64 bit** per riprodurre questo ambiente: la versione indicata di `pyrealsense2` dispone di un pacchetto Windows per Python 3.9, ma non per Python 3.10. Usare **`opencv-python`**, con supporto grafico; la variante `opencv-python-headless` non può aprire la finestra del viewer.

## Installazione con Conda

Occorrono una SR305 collegata e riconosciuta da Windows, l'accesso alla camera consentito alle applicazioni desktop e Conda disponibile nell'Anaconda Prompt. Chiudere eventuali altri programmi che stanno usando la camera.

Scaricare il repository da GitHub tramite **Code → Download ZIP** ed estrarlo, oppure clonarlo con Git. Aprire Anaconda Prompt nella cartella che contiene gli script e `requirements.txt`, quindi eseguire:

```bat
conda create -n realsenseSR305-viewer python=3.9.25 pip
conda activate realsenseSR305-viewer
python -m pip install -r requirements.txt
```

L'ambiente separato permette di mantenere altri progetti con dipendenze diverse, incluse eventuali installazioni headless di OpenCV.

In VS Code selezionare **Python: Select Interpreter** dalla palette comandi e scegliere l'interprete dell'ambiente `realsenseSR305-viewer`.

## Esecuzione

Con l'ambiente attivo, dalla cartella del progetto eseguire uno script alla volta:

```bat
python rs_basic_example.py
```

oppure:

```bat
python rs_align_example.py
```

Attendere qualche secondo per l'adattamento dell'esposizione automatica. Per interrompere lo script, premere **Ctrl+C nel terminale**. Gli script attuali non implementano un comando di uscita con `q` o `Esc`.

## Problemi comuni

| Problema | Controllo suggerito |
| --- | --- |
| Errore OpenCV «The function is not implemented» su `namedWindow` | Verificare di usare l'interprete corretto e `opencv-python`, senza la variante headless nello stesso ambiente. |
| `No matching distribution found` per `pyrealsense2==2.50.0.3812` | Controllare con `python --version` di usare Python 3.9 e un interprete a 64 bit. |
| Camera non rilevata o accesso negato | Controllare collegamento USB, riconoscimento del dispositivo, permessi della camera in Windows e altri programmi che potrebbero utilizzarla. |
| Immagine RGB scura | Attendere l'adattamento automatico e controllare l'illuminazione e gli eventuali messaggi sull'esposizione nel terminale. |

## Riferimenti e provenienza

Gli script derivano dagli esempi Python del progetto [librealsense](https://github.com/realsenseai/librealsense), adattati per questi esempi didattici. Le intestazioni originali riportano copyright RealSense e licenza Apache 2.0.

- [Esempi Python librealsense](https://github.com/realsenseai/librealsense/tree/v2.50.0/wrappers/python/examples)
- [Pacchetti di pyrealsense2 2.50.0.3812](https://pypi.org/project/pyrealsense2/2.50.0.3812/#files)
- [Licenza Apache 2.0 del progetto originale](https://github.com/realsenseai/librealsense/blob/v2.50.0/LICENSE)
