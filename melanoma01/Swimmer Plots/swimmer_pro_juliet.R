library("readxl")
library("swimplot")
library("ggplot2")
library("jsonlite") 
library("rjson")
library("reshape2")
library("openxlsx") 
library("xlsx")

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


# Find Total Treatment Length
df_master_data[ , 'overall_start'] <- NA
df_master_data[ , 'overall_end'] <- NA
for(i in 1:length(df_master_data$patients)) {
  if (length(df_master_data$patients[[i]]$treatments) > 0) {
    start_date <- df_master_data$patients[[i]]$treatments[[1]]$treatmentStartDate
    end_date <- df_master_data$patients[[i]]$treatments[[1]]$treatmentEndDate
    for (j in 1:length(df_master_data$patients[[i]]$treatments)) {
      if (df_master_data$patients[[i]]$treatments[[j]]$treatmentType == "immunotherapy") {
        if (df_master_data$patients[[i]]$treatments[[j]]$treatmentStartDate < start_date | start_date == "") {
          start_date <- df_master_data$patients[[i]]$treatments[[j]]$treatmentStartDate
        }
        if (df_master_data$patients[[i]]$treatments[[j]]$treatmentEndDate > end_date | end_date == "") {
          end_date <- df_master_data$patients[[i]]$treatments[[j]]$treatmentEndDate
        }
      }
    }
    df_master_data[i,]$overall_start <- start_date
    df_master_data[i,]$overall_end <- end_date
  }
}

#filter out data without treatment start or end date
df_master_data <- subset(df_master_data, df_master_data$overall_end != "" & df_master_data$overall_start != "")

#order by total treatment length
df_master_data$total_treatment_length <- as.numeric(difftime(as.Date(df_master_data$overall_end),as.Date(df_master_data$overall_start), units = "days"))
df_master_data <- df_master_data[order(-as.numeric(df_master_data$total_treatment_length)),]


#Define which rows of patients to see here
df_master_data <- df_master_data[1:50,]


#Process Scan Data
im_data <- data.frame(matrix(ncol = 3, nrow = 0))
x <- c("ID", "Action", "Time")
colnames(im_data) <- x


for(i in 1:length(df_master_data$patients)) {
  if (length(df_master_data$patients[[i]]$scans) > 0) {
    for (j in 1:length(df_master_data$patients[[i]]$scans)) {
      if (df_master_data$patients[[i]]$scans[[j]]$scanModality == "PET/CT") {
        im_data[nrow(im_data) + 1,] = c(df_master_data$patients[[i]]$PID,"image",df_master_data$patients[[i]]$scans[[j]]$dateOfScan)
      }
    }
  }
}


#Process Death data
death_data <- data.frame(matrix(ncol = 3, nrow = 0))
x <- c("ID", "Action", "Time")
colnames(death_data) <- x

for(i in 1:length(df_master_data$patients)) {
  if (df_master_data$patients[[i]]$dateOfDeath != "") {
    death_data[nrow(death_data) + 1,] = c(df_master_data$patients[[i]]$PID,"death",df_master_data$patients[[i]]$dateOfDeath)
  }
}


#Combine Action data
im_data <- rbind(im_data,death_data)



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
treatment_data <- subset(treatment_data, treatment_data$Start_Time != "" & treatment_data$End_Time != "")
treatment_data <- treatment_data[order(as.numeric(treatment_data$ID), as.Date(treatment_data$Start_Time)),]

treatment_data[ , 'note'] <- NA

for (i in 1:nrow(treatment_data)) {
  if (i != nrow(treatment_data)) {
    if (treatment_data[i,]$ID == treatment_data[i+1,]$ID) {
      if (as.Date(treatment_data[i,]$End_Time) < as.Date(treatment_data[i+1,]$Start_Time)) {
        treatment_data[i,]$note <- "Gap"
        treatment_data[nrow(treatment_data) + 1,] = c(treatment_data[i,]$End_Time
                                                      ,treatment_data[i+1,]$Start_Time
                                                      ,"Off"
                                                      ,treatment_data[i,]$ID
                                                      ,"Filled_Gap")
      } else if (as.Date(treatment_data[i,]$End_Time) == as.Date(treatment_data[i+1,]$Start_Time)) {
        treatment_data[i,]$note <- "Continuous"
      } else if (as.Date(treatment_data[i,]$End_Time) > as.Date(treatment_data[i+1,]$Start_Time)) {
        treatment_data[i,]$note <- "Overlap"
      }
    } else {
      treatment_data[i,]$note <- "Last"
    }
  } else {
    treatment_data[i,]$note <- "Last"
  }
}

treatment_data <- treatment_data[order(as.numeric(treatment_data$ID), as.Date(treatment_data$Start_Time)),]


#Process adverse event Data
ir_data <- data.frame(matrix(ncol = 4, nrow = 0))
x <- c("ID", "Site", "Time", "Grade")
colnames(ir_data) <- x

for(i in 1:length(df_master_data$patients)) {
  if (length(df_master_data$patients[[i]]$adverseEvents) > 0) {
    for (j in 1:length(df_master_data$patients[[i]]$adverseEvents)) {
      ir_data[nrow(ir_data) + 1,] = c(df_master_data$patients[[i]]$PID
                                      ,"Toxicity"
                                      ,df_master_data$patients[[i]]$adverseEvents[[j]]$aeStartDate
                                      ,df_master_data$patients[[i]]$adverseEvents[[j]]$adverseEventGrade
                                      )
      
    }
  }
}

# ir_data_Error <- subset(ir_data, ir_data$Time == "")
# write.xlsx(ir_data_Error,'\\\\uniwa.uwa.edu.au\\userhome\\staff3\\00105493\\My Documents\\AIQ\\01. Development\\R\\Swimmer\\AE_NO_DATES.xlsx')
ir_data <- subset(ir_data, ir_data$Time != "")



#Normalise Timeline
patient_list <- unique(c(unique(im_data$ID),unique(treatment_data$ID),unique(ir_data$ID)))
for (i in 1:length(patient_list)) {
  min_time <- min(as.Date(treatment_data[treatment_data$ID == patient_list[i],]$Start_Time))
  im_data[im_data$ID == patient_list[i], 'Norm_Time'] <- as.numeric(difftime(as.Date(im_data[im_data$ID == patient_list[i],]$Time),min_time, units = "days"))
  treatment_data[treatment_data$ID == patient_list[i], 'Norm_Time'] <- as.numeric(difftime(as.Date(treatment_data[treatment_data$ID == patient_list[i],]$End_Time),min_time, units = "days"))
  ir_data[ir_data$ID == patient_list[i], 'Norm_Time'] <- as.numeric(difftime(as.Date(ir_data[ir_data$ID == patient_list[i],]$Time),min_time, units = "days"))
}


all_treatment <- treatment_data[,c("Norm_Time", "arm", "ID")]
colnames(all_treatment)[which(names(all_treatment) == "Norm_Time")] <- "Time"
im_data <- im_data[,c("ID", "Action", "Norm_Time")]
colnames(im_data)[which(names(im_data) == "Norm_Time")] <- "Time"
ir_data <- ir_data[,c("ID", "Site", "Norm_Time", "Grade")]
colnames(ir_data)[which(names(ir_data) == "Norm_Time")] <- "Time"




#Plot Swimmer Plot
arm_plot<-swimmer_plot(df=all_treatment, 
             id="ID", 
             end="Time",
             name_fill="arm",
             col="black",
             alpha=0.75,
             width=.9)


AE_plot<-arm_plot + swimmer_points(df_points=im_data,
                                   id='ID',
                                   time='Time',
                                   name_shape ='Action',
                                   size=2.5,
                                   fill='black',
                                   col='black')



AE_P2<- AE_plot + swimmer_points(df_points= ir_data,
                    id='ID',
                    time='Time',
                    name_shape = 'Site',
                    size=1,
                    name_col="Grade",
                    stroke=1.5)


AE_P2<-AE_P2 + 
  scale_color_manual(name="Treatment"
                     ,values=c("nivolumab"="#e28743", "ipilumimab and nivolumab" ="#e41a1c","ipilumimab"='#722d80',"off"="#868686","pembrolizumab"="#377eb8")) +
  scale_fill_manual(name="Treatment"
                    ,values=c("nivolumab"="#e28743", "ipilumimab and nivolumab" ="#e41a1c","ipilumimab"='#722d80',"off"="#868686","pembrolizumab"="#377eb8")) +
  scale_shape_manual(name="Action"
                     ,values=c(image=18, death=16, Toxicity=6)
                     ,breaks=c('image','death', 'Toxicity')
                     ,labels=c('PET/CT','Death','Other Toxicity'))+
  scale_color_manual(name="Grade",values=c("Grade 1"="#006400", "Grade 2"="#ffff00", "Grade 3" ="#ffa500","Grade 4"='#ff1493'))

windows();AE_P2 + 
  theme(panel.grid.major.y = element_line(colour="grey", size=0.1,linetype = 1)) + 
  scale_y_continuous(name = "Time since treatment start (days)"
                           ,breaks = seq(-3500,4500,by=500)
                           ,limits = c(-3500,4500)
                           )



# #DQ Check

# #Load Raw data
# setwd("\\\\uniwa.uwa.edu.au\\userhome\\staff3\\00105493\\My Documents\\AIQ\\australia-aiq-data-development\\melanoma01")

# master_data <- fromJSON(file="file.json")
# # df_master_data <- flatten(as.data.frame(master_data$patients)) 

# df_master_data <- data.frame(matrix(ncol = 1, nrow = length(master_data$patients)))
# x <- c("patients")
# colnames(df_master_data) <- x

# df_master_data$patients <- master_data$patients


# #Patients with no treatment data
# patient_id_without_treatments <- c()
# for (i in 1:nrow(df_master_data)){
#   if (length(df_master_data$patients[[i]]$treatments) == 0) {
#     patient_id_without_treatments <- c(patient_id_without_treatments,df_master_data$patients[[i]]$PID)
#   }
# }
# df_patient_id_without_treatments <- data.frame(patient_id_without_treatments)


# #Patient with treatment data but without immuno
# patient_id_without_immuno <- c()
# for(i in 1:length(df_master_data$patients)) {
#   if (length(df_master_data$patients[[i]]$treatments) > 0) {
#     count <- 0
#     for (j in 1:length(df_master_data$patients[[i]]$treatments)) {
#       if (df_master_data$patients[[i]]$treatments[[j]]$treatmentType == "immunotherapy") {
#         count <- count + 1
#       }
#     }
#     if (count == 0) {
#       patient_id_without_immuno <- c(patient_id_without_immuno,df_master_data$patients[[i]]$PID)
#     }
#   } 
# }
# df_patient_id_without_immuno <- data.frame(patient_id_without_immuno)


# #Treatment without start or end date (Immuno Only)
# df_patient_with_no_treatment_start_end <- data.frame(matrix(ncol = 2, nrow = 0))
# x <- c("ID", "regimen")
# colnames(df_patient_with_no_treatment_start_end) <- x
# for (i in 1:nrow(df_master_data)) {
#   if (length(df_master_data$patients[[i]]$treatments) > 0) {
#     for (j in 1:length(df_master_data$patients[[i]]$treatments)) {
#       if (df_master_data$patients[[i]]$treatments[[j]]$treatmentType == "immunotherapy") {
#         if (df_master_data$patients[[i]]$treatments[[j]]$treatmentStartDate == "" | df_master_data$patients[[i]]$treatments[[j]]$treatmentEndDate == "") {
#           df_patient_with_no_treatment_start_end[nrow(df_patient_with_no_treatment_start_end) + 1,] = c(df_master_data$patients[[i]]$PID,df_master_data$patients[[i]]$treatments[[j]]$regimen)
#         }
#       }
#     }
#   }
# }


# #Adverse events without date
# df_adverse_events_no_date <- data.frame(matrix(ncol = 3, nrow = 0))
# x <- c("ID", "Grade", "CTCAE")
# colnames(df_adverse_events_no_date) <- x
# for (i in 1:nrow(df_master_data)) {
#   if (length(df_master_data$patients[[i]]$adverseEvents) > 0) {
#     for (j in 1:length(df_master_data$patients[[i]]$adverseEvents)) {
#       if (df_master_data$patients[[i]]$adverseEvents[[j]]$aeStartDate == "") {
#         df_adverse_events_no_date[nrow(df_adverse_events_no_date) + 1,] = c(df_master_data$patients[[i]]$PID,df_master_data$patients[[i]]$adverseEvents[[j]]$adverseEventGrade,df_master_data$patients[[i]]$adverseEvents[[j]]$CTCAE)
#       }
#     }
#   }
# }

# # write.xlsx(df_patient_id_without_treatments,file = '\\\\uniwa.uwa.edu.au\\userhome\\staff3\\00105493\\My Documents\\AIQ\\01. Development\\R\\Swimmer\\error_data_Swimmer.xlsx',sheetName="patient_without_treatments")
# # write.xlsx(df_patient_id_without_immuno,file = '\\\\uniwa.uwa.edu.au\\userhome\\staff3\\00105493\\My Documents\\AIQ\\01. Development\\R\\Swimmer\\error_data_Swimmer.xlsx',sheetName="patient_without_immuno")
# # write.xlsx(df_patient_with_no_treatment_start_end,file = '\\\\uniwa.uwa.edu.au\\userhome\\staff3\\00105493\\My Documents\\AIQ\\01. Development\\R\\Swimmer\\error_data_Swimmer.xlsx',sheetName="patient_no_start_end")
# # write.xlsx(df_adverse_events_no_date,file = '\\\\uniwa.uwa.edu.au\\userhome\\staff3\\00105493\\My Documents\\AIQ\\01. Development\\R\\Swimmer\\error_data_Swimmer.xlsx',sheetName="adverse_events_no_date")


# wb = createWorkbook()

# sheet = xlsx :: createSheet(wb, sheetName = as.character("patient_without_treatments"))
# addDataFrame(df_patient_id_without_treatments, sheet=sheet, startColumn=1, row.names=FALSE)

# sheet = createSheet(wb, sheetName = as.character("patient_without_immuno"))
# addDataFrame(df_patient_id_without_immuno, sheet=sheet, startColumn=1, row.names=FALSE)

# sheet = createSheet(wb, sheetName = as.character("patient_no_start_end"))
# addDataFrame(df_patient_with_no_treatment_start_end, sheet=sheet, startColumn=1, row.names=FALSE)

# sheet = createSheet(wb, sheetName = as.character("adverse_events_no_date"))
# addDataFrame(df_adverse_events_no_date, sheet=sheet, startColumn=1, row.names=FALSE)

# saveWorkbook(wb, "\\\\uniwa.uwa.edu.au\\userhome\\staff3\\00105493\\My Documents\\AIQ\\01. Development\\R\\Swimmer\\error_data_Swimmer.xlsx")