library("readxl")
library("swimplot")
library("ggplot2")
library("jsonlite") 
library("rjson")
library("reshape2")
library("openxlsx") 
library("xlsx")
library("lubridate")

#Load Raw data
# setwd("C:\\Users\\strah\\OneDrive\\Namizje\\Melanoma\\Prospective\\")
# setwd("\\\\uniwa.uwa.edu.au\\userhome\\staff3\\00105493\\My Documents\\AIQ\\01. Development\\R\\Swimmer")
setwd("\\\\uniwa.uwa.edu.au\\userhome\\staff3\\00105493\\My Documents\\AIQ\\01. Development\\australia-aiq-data-development\\melanoma01")

master_data <- fromJSON(file="file.json")
# df_master_data <- flatten(as.data.frame(master_data$patients)) 

df_master_data <- data.frame(matrix(ncol = 1, nrow = length(master_data$patients)))
x <- c("patients")
colnames(df_master_data) <- x


df_master_data$patients <- master_data$patients



# Remove patient without immunotherapy
df_master_data[ , 'immuno'] <- NA

for(i in 1:length(df_master_data$patients)) {
  count <- 0
  if (length(df_master_data$patients[[i]]$treatments) > 0) {
    for (j in 1:length(df_master_data$patients[[i]]$treatments)) {
      if (df_master_data$patients[[i]]$treatments[[j]]$treatmentType == "immunotherapy") {
        count <- count + 1
      }
    }
  } 
  if (count == 0) {
    df_master_data[i,]$immuno <- "No"
  } else {
    df_master_data[i,]$immuno <- "Yes"
  }
}


df_master_data <- subset(df_master_data, df_master_data$immuno == "Yes")


# # Find Total Treatment Length
# df_master_data[ , 'overall_start'] <- NA
# df_master_data[ , 'overall_end'] <- NA
# for(i in 1:length(df_master_data$patients)) {
#   if (length(df_master_data$patients[[i]]$treatments) > 0) {
#     start_date <- df_master_data$patients[[i]]$treatments[[1]]$treatmentStartDate
#     end_date <- df_master_data$patients[[i]]$treatments[[1]]$treatmentEndDate
#     for (j in 1:length(df_master_data$patients[[i]]$treatments)) {
#       if (df_master_data$patients[[i]]$treatments[[j]]$treatmentType == "immunotherapy") {
#         if (df_master_data$patients[[i]]$treatments[[j]]$treatmentStartDate < start_date | start_date == "") {
#           start_date <- df_master_data$patients[[i]]$treatments[[j]]$treatmentStartDate
#         }
#         if (df_master_data$patients[[i]]$treatments[[j]]$treatmentEndDate > end_date | end_date == "") {
#           end_date <- df_master_data$patients[[i]]$treatments[[j]]$treatmentEndDate
#         }
#       }
#     }
#     df_master_data[i,]$overall_start <- start_date
#     df_master_data[i,]$overall_end <- end_date
#   }
# }

# #filter out data without treatment start or end date
# df_master_data <- subset(df_master_data, df_master_data$overall_end != "" & df_master_data$overall_start != "")

# #order by total treatment length
# df_master_data$total_treatment_length <- as.numeric(difftime(as.Date(df_master_data$overall_end),as.Date(df_master_data$overall_start), units = "days"))
# df_master_data <- df_master_data[order(-as.numeric(df_master_data$total_treatment_length)),]


#Define which rows of patients to see here
# df_master_data <- df_master_data[1:50,]


#Process Scan Data
im_data <- data.frame(matrix(ncol = 4, nrow = 0))
x <- c("ID", "Action", "Time","Provider")
colnames(im_data) <- x


for(i in 1:length(df_master_data$patients)) {
  if (length(df_master_data$patients[[i]]$scans) > 0) {
    for (j in 1:length(df_master_data$patients[[i]]$scans)) {
      if (df_master_data$patients[[i]]$scans[[j]]$scanModality == "PET/CT") {
        im_data[nrow(im_data) + 1,] = c(df_master_data$patients[[i]]$PID
                                      ,"image"
                                      ,df_master_data$patients[[i]]$scans[[j]]$dateOfScan
                                      ,df_master_data$patients[[i]]$scans[[j]]$scanProvider)
                  
      }
    }
  }
}


# #Process Death data
# death_data <- data.frame(matrix(ncol = 3, nrow = 0))
# x <- c("ID", "Action", "Time")
# colnames(death_data) <- x

# for(i in 1:length(df_master_data$patients)) {
#   if (df_master_data$patients[[i]]$dateOfDeath != "") {
#     death_data[nrow(death_data) + 1,] = c(df_master_data$patients[[i]]$PID,"death",df_master_data$patients[[i]]$dateOfDeath)
#   }
# }


# #Combine Action data
# im_data <- rbind(im_data,death_data)



#Process Treatment Data
treatment_data <- data.frame(matrix(ncol = 4, nrow = 0))
x <- c("Start_Time", "End_Time", "arm", "ID")
colnames(treatment_data) <- x

for(i in 1:length(df_master_data$patients)) {
  if (length(df_master_data$patients[[i]]$treatments) > 0) {
    for (j in 1:length(df_master_data$patients[[i]]$treatments)) {
      if (df_master_data$patients[[i]]$treatments[[j]]$treatmentType == "immunotherapy") {
        treatment_data[nrow(treatment_data) + 1,] = c(df_master_data$patients[[i]]$treatments[[j]]$treatmentStartDate
                                                      ,df_master_data$patients[[i]]$treatments[[j]]$treatmentEndDate
                                                      ,df_master_data$patients[[i]]$treatments[[j]]$regimen
                                                      ,df_master_data$patients[[i]]$PID)
      }
    }
  }
}


# treatment_data_error <- subset(treatment_data, treatment_data$Start_Time == "" | treatment_data$End_Time == "")
# treatment_data <- subset(treatment_data, treatment_data$Start_Time != "" & treatment_data$End_Time != "")
treatment_data <- treatment_data[order(as.numeric(treatment_data$ID), as.Date(treatment_data$Start_Time)),]

# treatment_data[ , 'note'] <- NA

# for (i in 1:nrow(treatment_data)) {
#   if (i != nrow(treatment_data)) {
#     if (treatment_data[i,]$ID == treatment_data[i+1,]$ID) {
#       if (as.Date(treatment_data[i,]$End_Time) < as.Date(treatment_data[i+1,]$Start_Time)) {
#         treatment_data[i,]$note <- "Gap"
#         treatment_data[nrow(treatment_data) + 1,] = c(treatment_data[i,]$End_Time
#                                                       ,treatment_data[i+1,]$Start_Time
#                                                       ,"Off"
#                                                       ,treatment_data[i,]$ID
#                                                       ,"Filled_Gap")
#       } else if (as.Date(treatment_data[i,]$End_Time) == as.Date(treatment_data[i+1,]$Start_Time)) {
#         treatment_data[i,]$note <- "Continuous"
#       } else if (as.Date(treatment_data[i,]$End_Time) > as.Date(treatment_data[i+1,]$Start_Time)) {
#         treatment_data[i,]$note <- "Overlap"
#       }
#     } else {
#       treatment_data[i,]$note <- "Last"
#     }
#   } else {
#     treatment_data[i,]$note <- "Last"
#   }
# }

# treatment_data <- treatment_data[order(as.numeric(treatment_data$ID), as.Date(treatment_data$Start_Time)),]


#Process adverse event Data
ir_data <- data.frame(matrix(ncol = 4, nrow = 0))
x <- c("ID", "Site", "Time", "Grade")
colnames(ir_data) <- x

for(i in 1:length(df_master_data$patients)) {
  if (length(df_master_data$patients[[i]]$adverseEvents) > 0) {
    for (j in 1:length(df_master_data$patients[[i]]$adverseEvents)) {
      ir_data[nrow(ir_data) + 1,] = c(df_master_data$patients[[i]]$PID
                                      ,df_master_data$patients[[i]]$adverseEvents[[j]]$CTCAE
                                      ,df_master_data$patients[[i]]$adverseEvents[[j]]$aeStartDate
                                      ,df_master_data$patients[[i]]$adverseEvents[[j]]$adverseEventGrade
                                      )
      
    }
  }
}

# ir_data_Error <- subset(ir_data, ir_data$Time == "")
# write.xlsx(ir_data_Error,'\\\\uniwa.uwa.edu.au\\userhome\\staff3\\00105493\\My Documents\\AIQ\\01. Development\\R\\Swimmer\\AE_NO_DATES.xlsx')
ir_data <- subset(ir_data, ir_data$Time != "")


#get all Pre scans after immuno & one Post scan for each AE after immuno & one scan before immuno
for (i in 1:nrow(ir_data)) {
  im_data_per <- subset(im_data, im_data$ID == ir_data$ID[i] & im_data$Action == "image")
  im_data_per <- im_data_per[order(as.Date(im_data_per$Time)),]
  treatment_data_per <- subset(treatment_data, treatment_data$ID == ir_data$ID[i])
  treatment_data_per <- treatment_data_per[order(as.Date(treatment_data_per$Start_Time),decreasing = TRUE),]

  if (nrow(treatment_data_per) > 0) {
    for (j in 1:nrow(treatment_data_per)) {
      if (ir_data$Time[i] >= treatment_data_per$Start_Time[j]){
        ir_data[i,"immuno_start"] <- treatment_data_per$Start_Time[j]
        ir_data[i,"immuno_end"] <- treatment_data_per$End_Time[j]
        ir_data[i,"immuno_type"] <- treatment_data_per$arm[j]
        isafter <- "Yes"
        break
      }
    }
  }
  if (isafter == "Yes") {
    if (nrow(im_data_per) > 0) {
      scans <- c()
      post_scans <- c()
      for (j in 1:nrow(im_data_per)) {
        #Get all scans after immuno start and before AE
        if (im_data_per$Time[j] <= ir_data$Time[i] & im_data_per$Time[j] >= ir_data$immuno_start[i]) {
          scans <- append(scans, format(as.Date(im_data_per$Time[j]), "%d/%m/%Y"))
        } 
        #Get the scan right before immuno
        if (j != nrow(im_data_per)) {
          if (im_data_per$Time[j] <= ir_data$immuno_start[i] & im_data_per$Time[j + 1] >= ir_data$immuno_start[i]) {
            ir_data[i,"pre_immuno"] <- im_data_per$Time[j]
            # next
          }
        }
        # #Get scan right after AE
        # if (j != nrow(im_data_per)) {
        #   if (im_data_per$Time[j] <= ir_data$Time[i] & im_data_per$Time[j + 1] >= ir_data$Time[i]) {
        #     ir_data[i,"post_scan"] <- im_data_per$Time[j + 1]
        #     break
        #   }
        # }
        
        #Get scan right after immuno end
        if (j != nrow(im_data_per)) {
          if (im_data_per$Time[j] <= ir_data$immuno_end[i] & im_data_per$Time[j + 1] >= ir_data$immuno_end[i]) {
            ir_data[i,"last_scan"] <- im_data_per$Time[j + 1]
            break
          }
        }


        #Get all scans after AE and before immuno end 
        if (im_data_per$Time[j] > ir_data$Time[i] & im_data_per$Time[j] <= ir_data$immuno_end[i]) {
          post_scans <- append(post_scans, format(as.Date(im_data_per$Time[j]), "%d/%m/%Y"))
        }

        # if (j != nrow(im_data_per)) {
        #     if (im_data_per$Time[j] <= ir_data$Time[i] & im_data_per$Time[j + 1] >= ir_data$Time[i]) {
        #       ir_data[i,"pre_scan_1"] <- im_data_per$Time[j]
        #       ir_data[i,"post_scan"] <- im_data_per$Time[j + 1]
        #       if (j >= 3) {
        #         ir_data[i,"pre_scan_2"] <- im_data_per$Time[j - 1]
        #         ir_data[i,"pre_scan_3"] <- im_data_per$Time[j - 2]
        #       }
        #       if (j >= 2) {
        #         ir_data[i,"pre_scan_2"] <- im_data_per$Time[j - 1]
        #       }
        #       break
        #   }
        # }
      }
      ir_data[i,"pre_scan"] <- paste(scans, collapse = ', ')
      ir_data[i,"post_scan"] <- paste(post_scans, collapse = ', ')
    }
  }
  isafter <- "No"
}
ir_data <- ir_data[order(as.numeric(ir_data$ID),as.Date(ir_data$Time)),]
ir_data$Time <- format(as.Date(ir_data$Time), "%d/%m/%Y")
ir_data$immuno_start <- format(as.Date(ir_data$immuno_start), "%d/%m/%Y")
ir_data$immuno_end <- format(as.Date(ir_data$immuno_end), "%d/%m/%Y")
ir_data$last_scan <- format(as.Date(ir_data$last_scan), "%d/%m/%Y")
ir_data$pre_immuno <- format(as.Date(ir_data$pre_immuno), "%d/%m/%Y")

# ir_data$Time <- as.Date(ir_data$Time)
# ir_data$Time <- format(ir_data$Time, "%d/%m/%Y")
write.xlsx(ir_data,'\\\\uniwa.uwa.edu.au\\userhome\\staff3\\00105493\\My Documents\\AIQ\\01. Development\\australia-aiq-data-development\\melanoma01\\ad_im_reference_complete_timeline.xlsx')
# write.xlsx(ir_data,'\\\\uniwa.uwa.edu.au\\userhome\\staff3\\00105493\\My Documents\\AIQ\\01. Development\\australia-aiq-data-development\\melanoma01\\all_ir.xlsx')


#get one Pre & one Post scan for each immunotherapy
treatment_data <- subset(treatment_data, treatment_data$arm != "Off")
for (i in 1:nrow(treatment_data)) {
    im_data_per <- subset(im_data, im_data$ID == treatment_data$ID[i] & im_data$Action == "image")
    im_data_per <- im_data_per[order(as.Date(im_data_per$Time)),]
    if (nrow(im_data_per) > 0) {
      for (j in 1:nrow(im_data_per)) {
        if (j != nrow(im_data_per)) {
          if (im_data_per$Time[j] <= treatment_data$Start_Time[i] & im_data_per$Time[j + 1] >= treatment_data$Start_Time[i]) {
              treatment_data[i,"pre_scan"] <- im_data_per$Time[j]
              treatment_data[i,"post_scan"] <- im_data_per$Time[j + 1]
              treatment_data[i,"pre_scan_provider"] <- im_data_per$Provider[j]
              treatment_data[i,"post_scan_provider"] <- im_data_per$Provider[j + 1]
              break
          }
        }
      }
    }
}
treatment_data <- treatment_data[order(as.numeric(treatment_data$ID),as.Date(treatment_data$Start_Time)),]
treatment_data$Start_Time <- format(as.Date(treatment_data$Start_Time), "%d/%m/%Y")
treatment_data$End_Time <- format(as.Date(treatment_data$End_Time), "%d/%m/%Y")
treatment_data$pre_scan <- format(as.Date(treatment_data$pre_scan), "%d/%m/%Y")
treatment_data$post_scan <- format(as.Date(treatment_data$post_scan), "%d/%m/%Y")
treatment_data <- treatment_data[,c("ID", "Start_Time", "End_Time", "arm", "pre_scan", "post_scan","pre_scan_provider","post_scan_provider")]

write.xlsx(treatment_data,'\\\\uniwa.uwa.edu.au\\userhome\\staff3\\00105493\\My Documents\\AIQ\\01. Development\\australia-aiq-data-development\\melanoma01\\immuno_im_reference.xlsx')
