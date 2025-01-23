# Bio-727
produce a functioning prototype of a web-based software tool for handling molecular biology data..

MSC BIOINFORMATICS
SOFTWARE DEVELOPMENT GROUP PROJECT 2025
Rationale
The overall aim of this module is to give you the experience of working together within a team to
produce a functioning prototype of a web-based software tool for handling molecular biology data.
The project starts with the release of this briefing document, with an online session held shortly
after. Before this session you should connect with your teammates, study this document, think about
how you might go about tackling the project, and assemble a list of questions that would help you
clarify what you need to do and how you are going to do it. The project finishes with a
demonstration of your final prototypes and a presentation during which each student will explain
their contribution to the project. During the project, tutorials will be held weekly and help on
specific topics provided as necessary. Information on team membership, schedule of tutorials, and
time slots are available separately on QMplus.
Motivation
Type 2 Diabetes (T2D) is a cardiovascular genetic disease affecting roughly half a billion people
worldwide. According to the NHS, in 2021-2022 almost 250,000 adults in England were diagnosed
with T2D. Genetic susceptibility to T2D varies across ancestries with some populations
experiencing a higher incidence rate. For instance, south Asians develop T2D early in life despite
having a normal body mass index (BMI).
In a recent study, scientists at the Wolfson Institute of Population Health used ancestry-corrected
polygenic scores to understand the genetic basis of T2D susceptibility in a cohort of British
Pakistani and British Bangladeshi individuals (Hodgson et al. 2024), part of the Genes & Health
study (https://www.genesandhealth.org/). Researchers found that earlier onset of T2D in this cohort
is associated with molecular pathways involved in insulin deficiency and lipodystrophy.
Interestingly, the same researchers have previously suggested that one T2D-associated gene
involved with glucose homeostasis displays signatures of positive selection in south Asians (Dupuis
et al. 2023).
This finding is in line with the hypothesis that some common disease-associated variants may have
been maintained in the population through the action of past natural selection, and that their effect
on the carriers shifted from (weakly) beneficial to deleterious due to environmental or lifestyle
changes (Di Rienzo 2006), as, for instance, reported for T2D-incidence in Inuit (Moltke et al. 2014).
Therefore, the identification of variants under positive selection in contemporary populations can
serve as a strategy to detect functional genetic polymorphisms to be then screened for association
with disease (Werren et al. 2021). Several summary statistics are typically calculated to detect
genomic signals of positive selection, generally on levels of genetic or haplotype diversity (e.g.
Pavlidis & Alachiotis 2017).
Scientists are now interested in assessing any overlap between genetic variants associated with T2D
and signals of positive selection in south Asians, to either validate or confute the hypothesis of
evolution shaping predisposition to cardiovascular diseases, and to identify potentially novel targets
for further functional experiments. To interpret the mapping of the evolutionary genetic basis of
T2D, it is necessary to develop a web browser that leverages upon genomic, functional, and clinical
information available nowadays. This is the goal of your group project.
Software requirements
The aim of your project is to build a web application that can retrieve information on single
nucleotide polymorphisms (SNPs) associated with T2D and integrate them with population
genomic and functional data. The web application should also be capable to produce informative
plots and analyses in this regard. The web application should return results which are presented in a
manner that will help answer biological questions.
Specifically, the web application should satisfy the following requirements:
1. The user should be able to retrieve SNP information on T2D-associated variants given either its
name (e.g. rs value), genomic coordinates (chromosome, start and end), and mapped gene name (if
any). The web application should be able to handle queries that do not return any value.
2. The application should return the following information for each query: SNP name(s), genomic
position(s) (its location), p-value(s) from the association test (if available), mapped gene(s) (if any),
at least two summary statistics of positive selection calculated for at least two south Asian
populations.
3. If mapped gene(s) are returned, the user should be able to select one single gene of interest, and
the web application should return at least one functional or ontology term associated with it in a
new page.
4. If multiple SNPs are returned, the user should be able to select the population(s) of interest, and
the web application should return some descriptive information on selected population(s) (e.g. on
their geographical sampling locations) and a plot visualising the chosen summary statistics of
positive selection across the genomic region of interest. The user should also be able to download a
text file with reported values of summary statistics for the region of interest and their average and
standard deviation.
There are some important practical considerations.
1. You can focus on one or more phenotypes related to T2D, either by aggregating or separating
them.
2. We do not require the web application to retrieve information on all SNPs, but only on the ones
you found to be associated with your phenotype(s) of interest.
3. As it is hard to find numerous SNPs associated with T2D in south Asians specifically, the web
application can present disease-SNPs reported for any ancestry. However, the chosen summary
statistics to detect positive selection should be calculated for south Asian populations specifically.
4. You are free to choose the south Asian populations of interest for the analysis of positive
selection. It will be positively acknowledged if your web application is easy to be extended to
further populations and summary statistics.
5. For the specific task of providing summary statistics of positive selection, we ask you to calculate
them from genomic data yourself, instead of relying on precomputed tables from genome browsers.
However, using precalculate values from studies (e.g. Speidel et al. 2019) is acceptable as long as at
least one summary statistics is calculated from genomic data by yourself.
6. We ask you to use SQL to complete this assignment, although you may be able to fulfill the
software requirements without it. SQL is often requested by employers. We also require each team
to develop their code for this project on GitHub.
Justify all the choices you made on phenotypes, populations, summary statistics, and functional
information (and any other variable) in your documentation.
Available resources
You are free to find and use the most relevant data sets and software for your project. However, we
can suggest some resources you may wish, or not, to consider. You can decide to follow or not these
suggestions.
For retrieving genetic association data, either the GWAS catalog at www.ebi.ac.uk/gwas or the T2D
Knowledge Portal https://t2d.hugeamp.org could be suitable resources. Alternatively, you can also
retrieve data from publications (e.g. Vujkovic et al. 2020) or genome browsers (e.g. UCSC Genome
Browser, Ensembl).
Summary statistics of genetic or haplotype diversity (or else) can be calculated from population
genomic data. To this aim you may wish to consider the International Genome Samples Resource
database (https://www.internationalgenome.org/). It is your responsibility to find suitable software
to process genomic data and calculate chosen summary statistics.
Functional information on genes can be accessed as gene ontology terms (https://geneontology.org/)
or pathways (e.g. KEGG pathway database), or by aggregating clinical relevance of SNPs within
the gene through, for instance, SIFT, Polyphen, or CADD scores.
References
(please do let us know if you can’t access some of the references)
Di Rienzo 2006 https://doi.org/10.1016/j.gde.2006.10.002
Dupuis et al. 2023 https://www.medrxiv.org/content/10.1101/2023.05.04.23289501v1
Hodgson et al. 2024 https://www.nature.com/articles/s41591-024-03317-8
Moltke et al. 2014 https://www.nature.com/articles/nature13425
Pavlidis & Alachiotis 2017 https://doi.org/10.1186/s40709-017-0064-0
Speidel et al. 2019 https://zenodo.org/records/3234689
Vujkovic et al. 2020 https://www.nature.com/articles/s41588-020-0637-y
Werren et al. 2021 https://doi.org/10.1007/s00439-020-02206-7
How to begin the project
Successful completion of this project requires a combination of technical skill, good organisation,
logical thinking, web-based research and, most importantly, team work. Your first task is to work
with your team to do the following:
1. Ensure that you understand the software requirements and sketch out some kind of architecture
for the software (i.e. what components are needed and how they should interact).
2. Determine which data and technologies you need to produce the software.
3. Find out enough about the data and technologies so that you can approximate how long the
different parts of project will take, and who in your team is best suited to complete them.
4. Agree on the optimal way of working together to complete the project.
5. Identify any specific new skills that need to be learned by team members.
6. Produce a development plan (e.g. Gantt chart) for the duration of the project, detailing the various
tasks and who will be responsible for them.
We recommend that the software architecture and development plan should be presented at the first
tutorial. Provided that the development plan is acceptable, you will then embark on this plan to
develop the software.
Getting the most out of the tutorials
To make the most of the tutorials you need to be organised. Before the tutorial prepare to give a
brief summary of what your group has been working on, ideally using slides or a demo if helpful,
and be sure to arrive in good time. Think in advance about the questions you want to ask and the
advice you need.
Getting help and advice between tutorials
Please post any questions to the QMplus discussion forum for this module. This will be monitored
every weekday until the end of the project. To avoid giving away your team’s best ideas, be careful
about what exactly you post.
