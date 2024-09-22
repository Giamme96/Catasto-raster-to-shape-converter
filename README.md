# Catasto-raster-to-shape-converter [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue)](https://www.linkedin.com/in/gian-maria-lunghi-24376b163/)

Il catasto è finalmente diventato vettoriale? No.

## Indice

- [Introduzione](#introduzione)
- [Progetto](#progetto)
- [Installazione](#installazione)
- [Licenza](#licenza)
- [Disclaimer](#disclaimer)

## Introduzione

Questo progetto offre una soluzione semplice ed efficace per ottenere shape a partire dal WMS raster dell'agenzia delle entrate.  
Un grande limite dei raster è l'impossibilità di sfruttare i dati sottostanti per analisi geospaziali, quali sovrapposizione di layer (ormai spesso e volentieri interrogabili), overlap o calcoli geometrici.  
Convertendo in vettoriale le shape desiderate, è possibile rappresentare sui software GIS un oggetto che sia particella e/o fabbricati.  

Come si presenta il servizio di WMS  


![wms_catasto](https://github.com/user-attachments/assets/9b421ef1-02c3-42fb-bece-c328b6286c1a)


## Progetto

### Come usarlo
1. Fornisci un bounding box (bbox) come input e gli estremi catastali.
2. Viene chiamato il servizio WMS per scaricare l'immagine alla massima risoluzione possibile in rapporto al bbox.
3. L'immagine non georeferenziata viene riproiettata e trasformata in vettoriale.
4. Vengono escluse tutte le shape che sono parziali e non inerenti agli estremi catastali in input.
5. Viene esportato in Excel il dataframe di tutte le shape estratte, oltre che in pickle e shape file.

### Procedimento

1. Immagine satellitare d'esempio  
   ![satellite](https://github.com/user-attachments/assets/eee01ac9-5640-406f-90c1-6f158fd84232)

3. Immagine raster del catasto (Geoportale Cartografico Catastale)  
   ![wms_catasto](https://github.com/user-attachments/assets/77f795b6-4875-4607-b81f-961f8e9546a3)

4. Vettoriale estratto  
  ![vettoriale](https://github.com/user-attachments/assets/11ba8d88-03c9-467f-aebe-1809df638217)

5. Confronto WMS vs vettoriale  
   ![sovrapposizione](https://github.com/user-attachments/assets/ae40c48b-c367-4aea-b160-a4e40e8a1582)


### Alcune info interessanti su shape vettoriali
- **Scalabilità**: Le shape vettoriali possono essere facilmente scalate senza perdita di qualità.
- **Interattività**: Permettono una visualizzazione interattiva in GIS e altre applicazioni.
- **Analisi Dati**: Facilita operazioni di analisi spaziale, come la sovrapposizione con altri layer.
- **Archiviazione Efficiente**: Occupano meno spazio rispetto ai raster per la rappresentazione di geometrie.

## Installazione

Passaggi per installare il progetto:

- Clone del repo
- Install delle dependencies

```bash
pip install -r requirements.txt
```

## Licenza

Questo progetto è distribuito sotto la licenza MIT. Vedi il file [LICENSE](LICENSE) per ulteriori dettagli.

## Disclaimer

Il codice e la documentazione presenti in questo repository sono forniti esclusivamente a scopo informativo e documentale. Questo progetto non è destinato all'uso commerciale, né garantiamo che sia adatto per qualsiasi specifico utilizzo commerciale. Gli autori non si assumono alcuna responsabilità per eventuali danni diretti o indiretti derivanti dall'uso di questo codice.

Utilizzando il codice presente in questo repository, accetti che:

1. **Nessuna Garanzia**: Il codice è fornito "così com'è", senza garanzia di alcun tipo, espressa o implicita, incluse, ma non limitate a, le garanzie di commerciabilità, idoneità per un particolare scopo e non violazione. Gli autori non garantiscono che il codice sia privo di errori o che funzionerà in modo ininterrotto.

2. **Uso a Proprio Rischio**: L'uso del codice è interamente a tuo rischio. Gli autori non saranno responsabili per eventuali reclami, danni, perdite o altre responsabilità, sia in un'azione di contratto, torto o altro, derivanti da, o in connessione con il codice o l'uso o altri rapporti nel codice.

3. **Scopo Informativo**: Questo progetto è inteso solo per fini educativi e di documentazione. Non è stato sottoposto a controlli rigorosi di sicurezza, quindi non dovrebbe essere utilizzato in ambienti di produzione o per scopi sensibili. Gli autori non garantiscono che il codice sia adatto per qualsiasi specifico utilizzo, né che rispetti normative o requisiti legali applicabili.

4. **Nessun Supporto Ufficiale**: Gli autori non sono obbligati a fornire supporto, aggiornamenti, correzioni di bug o nuove funzionalità per questo progetto. Qualsiasi supporto fornito sarà a totale discrezione degli autori.

Si prega di leggere e comprendere completamente questi termini prima di utilizzare il codice. Se non si è d'accordo con questi termini, si prega di non utilizzare il codice.

Per ulteriori domande, contatta [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue)](https://www.linkedin.com/in/gian-maria-lunghi-24376b163/)
