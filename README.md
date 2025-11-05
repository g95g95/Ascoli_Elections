# Simulatore elettorale di Ascoli Piceno

Questo repository contiene una simulazione Monte Carlo dell'elezione del sindaco di Ascoli Piceno. Il modello recepisce
il sistema elettorale italiano per i comuni sopra i 15.000 abitanti, utilizza i risultati ufficiali del 2019 pubblicati da
Eligendo e sfrutta una catena di Markov per modellare i flussi di voto fra primo turno e ballottaggio.

## Dati di partenza

| Candidato               | Coalizione              | Voti 1° turno | % 1° turno | Voti 2° turno | % 2° turno |
|-------------------------|-------------------------|---------------|------------|---------------|------------|
| Marco Fioravanti        | Centrodestra            | 14.170        | 37,47 %    | 16.199        | 59,31 %    |
| Piero Celani            | Civiche di centro       | 12.288        | 32,48 %    | 11.101        | 40,69 %    |
| Francesco Ameli         | Centrosinistra          | 8.850         | 23,38 %    | —             | —          |
| Gianluca Vecchi         | Movimento 5 Stelle      | 1.985         | 5,25 %     | —             | —          |
| Domenico Stallone       | Civiche                 | 533           | 1,41 %     | —             | —          |

* Totale schede valide 1° turno: 37.826
* Totale schede valide ballottaggio: 27.270
* Astensione 1° turno: 37,9 % degli aventi diritto
* Astensione ballottaggio: 56,5 % degli aventi diritto

I dati sono stati ricavati dalla piattaforma ufficiale del Ministero dell'Interno (Eligendo) e sono riportati nel modulo
[`ascoli_elections/data.py`](ascoli_elections/data.py).

## Modello probabilistico

La dinamica del primo turno è modellata con una distribuzione Dirichlet-Multinomiale. Se $\boldsymbol{p}$ è il vettore
delle quote di voto per i $K$ candidati e $\boldsymbol{\alpha}$ il parametro di concentrazione, estraiamo

$$
\boldsymbol{p} \sim \mathrm{Dirichlet}(\boldsymbol{\alpha}), \qquad
\boldsymbol{v} \mid \boldsymbol{p} \sim \mathrm{Multinomiale}(N, \boldsymbol{p})
$$

dove $N$ è il numero di schede valide. Il parametro di concentrazione $\kappa$ è controllabile da linea di comando e
viene scalato sulle percentuali storiche $\hat{p}_i$ tramite $\alpha_i = \kappa \hat{p}_i$.
Nell'implementazione ci limitiamo a campionare $\boldsymbol{p}$, sufficiente a determinare l'esito del turno in termini di quote percentuali.

Il trattamento dell'astensione al primo turno è affidato ad una perturbazione gaussiana

$$
A^{(1)} \sim \max\Bigl(0, \min\bigl(0{,}9, \mathcal{N}(\hat{a}_1, \sigma_a^2)\bigr)\Bigr)
$$

dove $\hat{a}_1$ è l'astensione osservata nel 2019 e $\sigma_a$ un parametro di volatilità (default 0,02).

### Regole elettorali

* Vince al primo turno il candidato che supera il 50 % dei voti validi.
* In caso contrario accedono al ballottaggio i due candidati con più voti.

### Catena di Markov per il ballottaggio

La catena di Markov agisce sul vettore di probabilità
$\boldsymbol{q}^{(1)} = (p_1, \dots, p_K, a_1)$ composto dalle quote del primo turno e dall'astensione. La matrice di
transizione $\mathbf{T}$ restituisce la distribuzione post riallineamento

$$
\boldsymbol{q}^{(2)} = \boldsymbol{q}^{(1)} \mathbf{T}.
$$

La calibrazione avviene miscelando la preferenza del gruppo di origine con il risultato storico del ballottaggio
$\boldsymbol{r}$. Se indichiamo con $\boldsymbol{e}_i$ il vettore unitario del gruppo $i$ e con $\lambda$ il
parametro di elasticità, ogni riga di $\mathbf{T}$ è costruita come

$$
\mathbf{T}_{i,\cdot} = (1-\lambda) \boldsymbol{e}_{f(i)} + \lambda \boldsymbol{r},
$$

dove $f(i)$ è il finalista preferito dal gruppo $i$ (di norma il proprio candidato, o quello maggiormente vicino
politicamente). Il parametro $\lambda$ controlla la convergenza verso il ballottaggio 2019: $\lambda=0$ significa che
ogni blocco resta monolitico, $\lambda=1$ significa allineamento immediato a $\boldsymbol{r}$.

Dopo l'applicazione della catena di Markov la distribuzione viene normalizzata sulle colonne dei finalisti per ottenere una stima
$\tilde{p}$ delle loro quote al ballottaggio. Per modellare la variabilità di breve periodo adottiamo una distribuzione Beta:

$$
\tilde{p}_1 \sim \mathrm{Beta}(\lambda\tilde{p}_1,\, \lambda(1-\tilde{p}_1))
$$

Il parametro $\lambda$ corrisponde a ``runoff_strength`` e rappresenta la dimensione campionaria efficace della disputa di secondo turno.

## Struttura del codice

```
Ascoli_Elections/
├── ascoli_elections/
│   ├── __init__.py
│   ├── data.py
│   ├── markov.py
│   └── simulation.py
├── Electoral.py
└── README.md
```

* `data.py` contiene i dati ufficiali e le costanti principali.
* `markov.py` implementa la classe `TransitionMatrix` e la funzione `calibrate_runoff_transition`.
* `simulation.py` definisce `MonteCarloElection`, che combina Dirichlet, catena di Markov e perturbazioni Beta per il ballottaggio.
* `Electoral.py` fornisce un'interfaccia a riga di comando.

## Utilizzo

```bash
python Electoral.py --draws 20000 --concentration 8000 --abstention-volatility 0.015 --runoff-strength 800
```

Output di esempio:

```
Parametri utilizzati:
  draws: 20000
  concentration: 8000.0
  abstention_volatility: 0.015
  runoff_elasticity: 0.2
  runoff_strength: 800.0

Frequenze di vittoria:
  Marco Fioravanti          : 66.21%
  Piero Celani              : 33.79%
  Francesco Ameli           :  0.00%
  Gianluca Vecchi           :  0.00%
  Domenico Stallone         :  0.00%
```

Le frequenze sono stime Monte Carlo della probabilità di vittoria in base alle assunzioni indicate. Il numero di
simulazioni (``--draws``) determina la precisione statistica, mentre ``--concentration`` controlla la dispersione della
Dirichlet.

Il parametro ``--runoff-strength`` controlla invece quanto rumore viene aggiunto al secondo turno: valori elevati rendono il risultato più concentrato attorno alla previsione storica, valori bassi consentono scenari più volatili.

## Ottimizzazione e performance

* Le operazioni numeriche usano solo il modulo standard `random` (campionamento Gamma/Beta) per garantire portabilità senza dipendenze esterne.
* La catena di Markov viene precalcolata all'inizializzazione del simulatore, evitando ricostruzioni ripetute durante le iterazioni.
* L'uso combinato di Dirichlet e Beta mantiene una complessità $\mathcal{O}(K)$ per simulazione e permette di controllare con precisione la volatilità.

## Riproducibilità

Il modello non imposta un seed fisso per lasciare l'utente libero di cambiare scenario. Per riprodurre un esperimento
specifico è sufficiente impostare la variabile d'ambiente ``NP_RANDOM_SEED`` prima dell'esecuzione o richiamare la libreria
in modo personalizzato.

## Possibili estensioni

1. Modellare la ripartizione dei seggi del consiglio comunale con la maggioranza garantita al sindaco eletto.
2. Introdurre scenari contrafattuali modificando le quote di partenza o inserendo nuovi candidati.
3. Integrare sondaggi o serie storiche multiple per aggiornare i parametri della Dirichlet con approccio bayesiano.

