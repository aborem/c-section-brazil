# C-Section Prevalence Rations in Brazil
_Arthur Borem, PHP 1100, Fall 2019_

This short program uses data from SINASC (DATASUS) to identify prevalence ratios of c-sections within key demographics 
(race, education and location, although only race and education are used for the analysis). The results are fitted to a
Poisson regression to measure the significance of the demographics on the determination of a c-section.


## File Descriptions
`sinasc_data.py` does the key analysis described above. The raw findings are located in `findings/` and the code used to 
convert the results from `json` encoded data to a latex table format (for the final report) can be found in 
`latex_table_converter.py`.

## Resources Used
[Cesarean section on demand: a population-based study in Southern Brazil](http://www.scielo.br/pdf/rbsmi/v17n1/1519-3829-rbsmi-17-01-0099.pdf)
used for project inspiration.

[An Illustrated Guide to the Poisson Regression Model](https://towardsdatascience.com/an-illustrated-guide-to-the-poisson-regression-model-50cccba15958)
used for data analysis guidance.i

## Required Libraries
```
pandas
statsmodels
json
pysus
patsy
```
