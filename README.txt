# Bio-727
Goal: to produce a functioning prototype of a web-based software tool for handling molecular biology data.

MSC BIOINFORMATICS
SOFTWARE DEVELOPMENT GROUP PROJECT 2025

Directory structure:
.
├── README.txt
├── app.py
├── associations.tsv
├── uniprot_data.tsv
├── genetics.db.py
├── static
│   ├── api.js
│   ├── charts.js
│   ├── main.js
│   ├── styles.css
│   └── ui.js
└── templates
    ├── gene.html
    ├── index.html
    ├── population.html
    └── results.html

Database schema visualisation (genetics.db.py):
+-------------------+           +-------------------+
|  associations     |           |  uniprot_data     |
+-------------------+           +-------------------+
| varId             |           | gene_name         |
| alignment         |           | mapped_gene_id (FK)--> gene.gene_id
| alt               |           | uniprot_url       |
| ancestry          |           | uniprot_id        |
| beta              |           +-------------------+
| chromosome        |
| clumpEnd          |           +-------------------+       +-------------------+       +-------------------+
| clumpStart        |           |      gene         |       |    population     |       |       snp         |
| dataset           |           +-------------------+       +-------------------+       +-------------------+
| inMetaTypes       |           | gene_id (PK)      |<------| population_id (PK)|       | snp_id (PK)       |
| leadSNP           |           | gene_name         |       | population_name   |       | snp_name          |
| n                 |           | functional_term   |       | sampling_location |       | chromosome        |
| pValue            |           +-------------------+       +-------------------+       | start_position    |
| phenotype         |                                                                   | end_position      |
| position          |                                                                   | p_value           |
| posteriorProbability|         +-------------------------------+                       | mapped_gene_id (FK)--> gene.gene_id
| reference         |           | snp_population_selection_stats|                       +-------------------+
| source            |           +-------------------------------+
| stdErr            |           | snp_id (FK) -------------------> snp.snp_id
| clump             |           | population_id (FK) ------------> population.population_id
| dbSNP             |           | allele_freq                   |
| consequence       |           | selection_statistic_1         |
| nearest           |           | selection_statistic_2         |
| minorAllele       |           +-------------------------------+
| maf               |
| af                |
+-------------------+