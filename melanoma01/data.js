const fs = require("fs");
const readline = require("readline");
const CSV = require('csv-string');
var currentPatient = "";
var patient;

async function processLineByLine() {
  const fileStream = fs.createReadStream("CBBioMelanoma-AllFieldsMD_DATA_LABELS_2022-06-07_Sample 60 patients.csv"); //input file define
  var jsonOutput = new Object();
  jsonOutput.patients = [];
  var lineNumber = 0;

  const rl = readline.createInterface({
    input: fileStream,
    crlfDelay: Infinity
  });

  for await (const line of rl) {
    // Process the line from the file
    lineNumber++;
    
    // Ignore the header
    if (lineNumber == 1) {
        // Do nothing
        continue;
    }

    var columnValues = CSV.parse(line)[0];
    var pid = columnValues[0];

    if (currentPatient != pid) {

        // If there is a patient add the current patient to the output
        if (patient) {
            jsonOutput.patients.push(patient);
        }

        // There is a new patient to process
        patient = new Object();
        currentPatient = pid;
        
        // Get the info for the patient
        patient.PID = pid; // PID
        patient.dateOfBirth = columnValues[3]; // "Date of birth"
        patient.age = columnValues[4]; // "Age (years)"
        patient.sex = columnValues[5]; // sex
        patient.cancerType = columnValues[181]; // "Cancer Type"
        patient.histologicalSubtype = columnValues[182]; // "Histological subtype"
        patient.otherHistologicalSubtype = columnValues[183]; // "Specify other histological subtype"
        patient.dateOfDeath = columnValues[184]; // "Date of Death"
        patient.wasDeathCancerTypeRelated = columnValues[185]; // "Was death [cancertype] related?"
        patient.primaryLocation = columnValues[186]; // "Primary location"
        patient.primaryLocationKnown = columnValues[187]; // "Primary location?"
        patient.melanomaTStage = columnValues[188]; // "Melanoma - T stage"
        patient.melanomaNStage = columnValues[189]; // "Melanoma - N stage"
        patient.melanomaMStage = columnValues[190]; // "Melanoma - M stage"
        patient.melanomaMStageValue = columnValues[191]; // "M-stage: 0 or 1 ?"
        patient.otherMalignancyHistory = columnValues[192]; // "Other malignancy history"
        patient.otherConditions = columnValues[193]; // "Other (specify)"
        patient.pastMedicalHistory = columnValues[194]; // "Past medical history"
        patient.notes = columnValues[195]; // Notes
        patient.complete = columnValues[196]; // Complete?

        patient.scans = [];
        patient.treatments = [];
        patient.adverseEvents = [];

    } else {

        // The current line still has information for the current patient but it's not a new patient line

        // Get the scans
        if ((columnValues[1] == "Scans") && columnValues[6]) {
            patient.scans.push(processScan(columnValues, 6));
        }
        if ((columnValues[1] == "Scans") && columnValues[18]) {
            patient.scans.push(processScan(columnValues, 18));
        }
        if ((columnValues[1] == "Scans") && columnValues[30]) {
            patient.scans.push(processScan(columnValues, 30));
        }
        if ((columnValues[1] == "Scans") && columnValues[42]) {
            patient.scans.push(processScan(columnValues, 42));
        }
        if ((columnValues[1] == "Scans") && columnValues[54]) {
            patient.scans.push(processScan(columnValues, 54));
        }
        if ((columnValues[1] == "Scans") && columnValues[66]) {
            patient.scans.push(processScan(columnValues, 66));
        }
        if ((columnValues[1] == "Scans") && columnValues[78]) {
            patient.scans.push(processScan(columnValues, 78));
        }
        if ((columnValues[1] == "Scans") && columnValues[90]) {
            patient.scans.push(processScan(columnValues, 90));
        }
        if ((columnValues[1] == "Scans") && columnValues[102]) {
            patient.scans.push(processScan(columnValues, 102));
        }
        if ((columnValues[1] == "Scans") && columnValues[114]) {
            patient.scans.push(processScan(columnValues, 114));
        }

        // Get the treatments
        if ((columnValues[1] == "Treatments") && columnValues[127]) {
            patient.treatments.push(processTreatment(columnValues, 127));
        }
        // Get the Adverse Events
        if ((columnValues[1] == "Adverse Events") && columnValues[197]) {
            patient.adverseEvents.push(processAdverseEvent(columnValues, 197));
        }
    }
  }

  // Add the last patient
  jsonOutput.patients.push(patient);

  fs.writeFile("patients_output.json", JSON.stringify(jsonOutput, null, 2), (error) => { // output file define
    if (error) {
      throw error;
    }
  });
}

processLineByLine();

function processScan(columnValues, startColumn) {
    var scan = new Object();
    scan.dateOfScan = columnValues[startColumn]; // "Date of scan"
    scan.scanModality = columnValues[startColumn+1]; // "Scan modality"
    scan.scanId = columnValues[startColumn+2]; // "Scan ID / IMPAX No."
    scan.scanProvider = columnValues[startColumn+3]; // "Scan provider"
    scan.otherScanProvider = columnValues[startColumn+4]; // "Specify other scan provider"
    scan.scanOutcome = columnValues[startColumn+5]; // "Scan outcome"
    scan.sitesOfPDSkinSubcutaneousLymphNodes = columnValues[startColumn+6]; // "Site(s) of PD (choice=Skin, subcutaneous, or lymph nodes)"
    scan.sitesOfPDLung = columnValues[startColumn+7]; // "Site(s) of PD (choice=Lung)"
    scan.sitesOfPDOtherVisceralSites = columnValues[startColumn+8]; // "Site(s) of PD (choice=Other visceral sites)"
    scan.sitesOfPDBrain = columnValues[startColumn+9]; // "Site(s) of PD (choice=Brain)"
    scan.furtherComments = columnValues[startColumn+10]; // "Further comments"
    if (startColumn != 114) {
        scan.uploadScanReport = columnValues[startColumn+11]; // "Upload scan report"
    } else {
        scan.commentsAboutIMPAXScanSummaryFile = columnValues[startColumn+11]; // "Upload scan report"
        scan.scanComplete = columnValues[startColumn+12]; // "Upload scan report"
    }
    return scan;
}

function processTreatment(columnValues, startColumn) {
    var treatment = new Object();
    treatment.treatmentType = columnValues[startColumn]; 
    treatment.lineOfSystemTreatment = columnValues[startColumn+1]; 
    treatment.regimen = columnValues[startColumn+2]; 
    treatment.specificChemotherapy = columnValues[startColumn+3]; 
    treatment.specificClinicalTrial = columnValues[startColumn+4]; 
    treatment.specificOtherTreatmentType = columnValues[startColumn+5]; 
    treatment.treatmentStartDate = columnValues[startColumn+6]; 
    treatment.ageAtStartOfTreatment = columnValues[startColumn+7]; 
    treatment.treatmentEndDate = columnValues[startColumn+8]; 
    treatment.locationOfRadiation = columnValues[startColumn+9]; 
    treatment.typeOfRadiation = columnValues[startColumn+10]; 
    treatment.typeOfSurgery = columnValues[startColumn+11]; 
    treatment.noteAboutSurgery = columnValues[startColumn+12]; 
    treatment.LDHAtStartOfTreatment = columnValues[startColumn+13]; 
    treatment.LDGDate = columnValues[startColumn+14]; 
    treatment.LDHTestNormalRangeLowerLimit = columnValues[startColumn+15]; 
    treatment.LDHTestNormalRangeUpperLimit = columnValues[startColumn+16]; 
    treatment.LDHRangeUnits = columnValues[startColumn+17]; 
    treatment.LDHIsXUpperLimitOfNormal = columnValues[startColumn+18]; 
    treatment.whiteBloodCellCount = columnValues[startColumn+19]; 
    treatment.neutrophilCount = columnValues[startColumn+20]; 
    treatment.lymphocyteCount = columnValues[startColumn+21]; 
    treatment.immunosuppressiveNote = columnValues[startColumn+22]; 
    treatment.ECOGStatusAtStartOfTreatment = columnValues[startColumn+23]; 
    treatment.numberOfCycles = columnValues[startColumn+24]; 
    treatment.dateNumberOfCyclesEntered = columnValues[startColumn+25]; 
    treatment.firstResponse = columnValues[startColumn+26]; 
    treatment.dateOfFirstResponse = columnValues[startColumn+27]; 
    treatment.bestResponse = columnValues[startColumn+28]; 
    treatment.dateOfBestResponse = columnValues[startColumn+29]; 
    treatment.timeToBestResponse = columnValues[startColumn+30]; 
    treatment.progressionOfDisease = columnValues[startColumn+31]; 
    treatment.dateOfPD = columnValues[startColumn+32]; 
    treatment.toxicity = columnValues[startColumn+33]; 
    treatment.reasonStopped = columnValues[startColumn+34]; 
    treatment.otherReasonStopped = columnValues[startColumn+35]; 
    treatment.radiationDuringTreatment = columnValues[startColumn+36]; 
    treatment.locationOfRadiationDuringTreatmentOtherThanBrain = columnValues[startColumn+37]; 
    treatment.anatomicalLocationOfRadiationDuringTreatment = columnValues[startColumn+38]; 
    treatment.dateOfRadiation = columnValues[startColumn+39]; 
    treatment.surgeryDuringTreatment = columnValues[startColumn+40]; 
    treatment.surgeryDuringTreamentNote = columnValues[startColumn+41]; 
    treatment.dateOfSurgeryDuringTreatment = columnValues[startColumn+42]; 
    treatment.didPatientHaveRadiationPriorToTreatment = columnValues[startColumn+43]; 
    treatment.anatomicalLocationForRadiationBeforeThisTreatment = columnValues[startColumn+44]; 
    treatment.locationOfRadiationBeforeCurrentTreatment = columnValues[startColumn+45]; 
    treatment.dateOfRadiationPriorToTreatment = columnValues[startColumn+46]; 
    treatment.didPatientHaveSurgeryPriorToTreatment = columnValues[startColumn+47]; 
    treatment.surgeryPriorToTreatment = columnValues[startColumn+48]; 
    treatment.dateOfSurgeryPriorToTreatment = columnValues[startColumn+49]; 
    treatment.antibioticsEitherDuringUpToTwoWeeksBeforeTreatment = columnValues[startColumn+50]; 
    treatment.antibioticsOralOrIntravenous = columnValues[startColumn+51]; 
    treatment.otherMedications = columnValues[startColumn+52]; 
    treatment.UMRNNotes = columnValues[startColumn+53]; 
    return treatment;
}

function processAdverseEvent(columnValues, startColumn) {
    var adverseEvent = new Object();
    adverseEvent.adverseEventGrade = columnValues[startColumn]; 
    adverseEvent.CTCAE = columnValues[startColumn+1]; 
    adverseEvent.aeStartDateKnown = columnValues[startColumn+2]; 
    adverseEvent.aeStartDate = columnValues[startColumn+3]; 
    adverseEvent.isAEImmuneRelated = columnValues[startColumn+4]; 
    adverseEvent.wasPatientHospitalisedForToxicity = columnValues[startColumn+5]; 
    adverseEvent.lengthOfHospitalStay = columnValues[startColumn+6]; 
    adverseEvent.treatmentGivenInHospitalForAEIVCorticoSteroids = columnValues[startColumn+7]; 
    adverseEvent.treatmentGivenInHospitalForAEOralCorticoSteroids = columnValues[startColumn+8]; 
    adverseEvent.treatmentGivenInHospitalForAEIVAndOralCorticoSteroids = columnValues[startColumn+9]; 
    adverseEvent.treatmentGivenInHospitalForAEInfliximab = columnValues[startColumn+10]; 
    adverseEvent.treatmentGivenInHospitalForAEMycophenolateMofetil = columnValues[startColumn+11]; 
    adverseEvent.treatmentGivenInHospitalForAECyclosporine = columnValues[startColumn+12]; 
    adverseEvent.treatmentGivenInHospitalForAEOther = columnValues[startColumn+13]; 
    adverseEvent.treatmentGivenInHospitalForNotes = columnValues[startColumn+14]; 
    adverseEvent.wasPatientAdmittedForAToxicityOtherThanThisToxicity = columnValues[startColumn+15]; 
    adverseEvent.didPatientReceiveTreatmentForThisSpecificAEDuringHospitalisation = columnValues[startColumn+16]; 
    adverseEvent.durationOfTreatmentDuringHospitalisation = columnValues[startColumn+17]; 
    adverseEvent.commentsRegardingTreatmentsInHospital = columnValues[startColumn+18]; 
    adverseEvent.outpatientTreatmentGivenForAECorticoSteroids = columnValues[startColumn+19]; 
    adverseEvent.outpatientTreatmentGivenForAETopicalCorticoSteroids = columnValues[startColumn+20]; 
    adverseEvent.outpatientTreatmentGivenForAEEndocrineReplacement = columnValues[startColumn+21]; 
    adverseEvent.outpatientTreatmentGivenForAEMycophenolateMofetil = columnValues[startColumn+22]; 
    adverseEvent.outpatientTreatmentGivenForAETacrolimus = columnValues[startColumn+23]; 
    adverseEvent.outpatientTreatmentGivenForAECyclophosphamide = columnValues[startColumn+24]; 
    adverseEvent.outpatientTreatmentGivenForAEInfliximab = columnValues[startColumn+25]; 
    adverseEvent.outpatientTreatmentGivenForAEVedolizumab = columnValues[startColumn+26]; 
    adverseEvent.outpatientTreatmentGivenForAEOther = columnValues[startColumn+27]; 
    adverseEvent.administrationOfCorticoSteroids = columnValues[startColumn+28]; 
    adverseEvent.specifyOtherAdministrationOfCorticoSteroids = columnValues[startColumn+29]; 
    adverseEvent.wasTherapyContinuedAsPerTheUsualTimeline = columnValues[startColumn+30]; 
    adverseEvent.dateStopTherapy = columnValues[startColumn+31]; 
    adverseEvent.durationOfTreatmentBreakIfKnown = columnValues[startColumn+32]; 
    adverseEvent.wasPatientRechallengedWithTheSameTherapy = columnValues[startColumn+33]; 
    adverseEvent.dateOfRechallengeTherapy = columnValues[startColumn+34]; 
    adverseEvent.toxicityGradeAtRechallenge = columnValues[startColumn+35]; 
    adverseEvent.flareOfToxicity = columnValues[startColumn+36]; 
    adverseEvent.commentsOnFlareOfToxicity = columnValues[startColumn+37]; 
    adverseEvent.otherAESecondaryToRechallenge = columnValues[startColumn+38]; 
    adverseEvent.wasPatientGivenADifferentTherapyFollowingAE = columnValues[startColumn+39]; 
    adverseEvent.aeOutcome = columnValues[startColumn+40]; 
    adverseEvent.didPatientDieSecondaryToThisAE = columnValues[startColumn+41]; 
    adverseEvent.aeOutcomeOngoing = columnValues[startColumn+42]; 
    adverseEvent.gradeOfOngoingAE = columnValues[startColumn+43]; 
    adverseEvent.dateOfResolutionIfKnown = columnValues[startColumn+44]; 
    adverseEvent.ifStopDateNoOfWeeksEitherSideOfSelectedDate = columnValues[startColumn+45]; 
    adverseEvent.aeComments = columnValues[startColumn+46]; 
    adverseEvent.aeComplete = columnValues[startColumn+47]; 
    return adverseEvent;
}
