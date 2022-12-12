# install.packages("openxlsx")


library(jsonlite) 
library(data.table) 
library(httr) 
library(plyr) 
library(dplyr) 
library(stringr) 
library(tidyr) 
library(odbc) 
require(DBI) 
library(openxlsx) 


isEmpty <- function(x) { 
  return(length(x)==0) 
} 


# #Check if you have required package 
# packages = c('jsonlite','data.table','httr','plyr','dplyr','stringr','tidyr','odbc','DBI','openxlsx') 
#  
# #Now load or install packages 
# package.check <- lapply( 
#   packages, 
#   FUN = function(x) { 
#     if (!require(x, character.only = TRUE)) { 
#       install.packages(x, repo='http://cran.rstudio.com/') 
#       library(x, character.only = TRUE) 
#     } 
#   } 
# ) 



#--- prevent numbers from exporting in scientific notation 
options(scipen=999) 


# #---set proxy env 
# proxyURLhttp <- ""  
# proxyURLhttps <- ""  
# Sys.setenv(http_proxy = proxyURLhttp, https_proxy = proxyURLhttps)  


#--- Credentials 
strUser <- 'admin' 
strToken <- '' 


#---TEST RELATED RECORDS---connet to ODATA link and extract into data frame 
#URL <- '' 

#------URLs below have been tested and works--------- 
URLPre <- 'aiqprdeauxnat001.australiaeast.cloudapp.azure.com:8080/xnat-web-1.8.5/xapi' 


URL <- paste0(URLPre, '/access/admin/projects') 

encodeURL <- URLencode(URL) 
get_raw_query <- httr::GET(encodeURL,authenticate(strUser, strToken, "basic"))
querytest <- content(get_raw_query, as ="raw") 
chartest <- rawToChar(querytest) 
Encoding(chartest) <- "UTF-8" 
jsontest <- fromJSON(chartest) 
dfItems <- flatten(as.data.frame(jsontest)) 
# view(dfItems) 
# view(colnames(dfItems)) 
# write.xlsx(dfItems,'')