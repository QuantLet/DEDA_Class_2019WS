install.packages("data.table")
install.packages("eurostat")
library(data.table)
library(eurostat)

## settings ##
setwd("~/rev_forecast") # set working directory

Sys.setenv(LANG = "en") # set environment language to English
Sys.setlocale("LC_TIME", "en_US.UTF-8") # set timestamp language to English
## ##

## search eurostat ##
energy_data <- data.table(search_eurostat("energy", type = "all"))
setkey(energy_data, title)
View(energy_data)

eurostat_datasets <- lapply(energy_data[!type %in% "folder"]$code, function(x) data.table(get_eurostat(x, time_format = "raw")))
names(eurostat_datasets) <- energy_data[!type %in% "folder"]$title

eurostat_datasets <- rbindlist(eurostat_datasets, fill = TRUE, idcol = "dataset")

