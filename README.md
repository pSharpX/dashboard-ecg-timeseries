# [A large scale 12-lead electrocardiogram database for arrhythmia study](https://physionet.org/content/ecg-arrhythmia/1.0.0/)

**Authors:** Jianwei Zheng, Hangyuan Guo, Huimin Chu  
**Published:** Aug. 24, 2022  
**Version:** 1.0.0  

---

## Cite

**Zheng, J., Guo, H., & Chu, H. (2022).** *A large scale 12-lead electrocardiogram database for arrhythmia study (version 1.0.0)*. PhysioNet. RRID: SCR_007345. https://doi.org/10.13026/wgex-er52  

**Original publication to also cite:**  
Zheng, J., Chu, H., Struppa, D., Zhang, J., Yacoub, S. M., El-Askary, H., Chang, A., Ehwerhemuepha, L., Abudayyeh, I., Barrett, A. S., Fu, G., Yao, H., Li, D., Guo, H., & Rakovski, C. (2020). *Optimal Multi-Stage Arrhythmia Classification Approach*. *Scientific Reports*, 10.  

**Standard citation for PhysioNet:**  
Goldberger, A., Amaral, L., Glass, L., Hausdorff, J., Ivanov, P. C., Mark, R., … & Stanley, H. E. (2000). *PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research resource for complex physiologic signals*. *Circulation* [Online], 101(23), e215–e220. RRID: SCR_007345.  
---

## Contents

- Abstract  
- Background  
- Methods  
- Data Description  
- Usage Notes   
- References
- Files
---

## Abstract

This newly inaugurated research database for 12-lead electrocardiogram (ECG) signals was created under the auspices of Chapman University, Shaoxing People’s Hospital (Shaoxing Hospital Zhejiang University School of Medicine), and Ningbo First Hospital. It aims to enable the scientific community in conducting new studies on arrhythmia and other cardiovascular conditions. Certain types of arrhythmias, such as atrial fibrillation, have a pronounced negative impact on public health, quality of life, and medical expenditures. As a non-invasive test, ECG is a major and vital diagnostic tool for detecting these conditions. This practice, however, generates large amounts of data, the analysis of which requires considerable time and effort by human experts. Modern machine learning and statistical tools can be trained on high quality, large data to achieve exceptional levels of automated diagnostic accuracy. Thus, we collected and disseminated this novel database that contains 12-lead ECGs of 45,152 patients with a 500 Hz sampling rate that features multiple common rhythms and additional cardiovascular conditions, all labeled by professional experts. The dataset can be used to design, compare, and fine-tune new and classical statistical and machine learning techniques in studies focused on arrhythmia and other cardiovascular conditions.

---

## Background

An ECG is a graph depicting voltage with respect to time that reflects the electrical activities of cardiac muscle depolarization followed by repolarization during each heartbeat[1]. The ECG graph of a normal beat consists of a sequence of waves, a P-wave presenting the atrial depolarization process, a QRS complex denoting the ventricular depolarization process, and a T-wave representing the ventricular repolarization. Other portions of the signal include the PR, ST, and QT intervals. Arrhythmias represent a family of cardiac conditions characterized by irregularities in the rate or rhythm of heartbeats. There are several dozen such classes with various distinct manifestations, such as sinus bradycardia (SB), atrial tachycardia (AT), premature ventricular contraction (PVC), and other irregular rhythms with missing or distorted wave segments and intervals. The most common and pernicious arrhythmia type is atrial fibrillation (AFIB). It is associated with a significant increase in the risk of severe cardiac dysfunction and stroke.

According to the current screening and diagnostic practices, either cardiologists or physicians review ECG data, establish the correct diagnosis, and begin implementing subsequent treatment plans such as medication regime and radiofrequency catheter ablation. However, the demand for high accuracy automatic heart condition diagnoses has recently increased sharply in parallel with the public health policy of implementing wider screening procedures and the adoption of ECG-enabled wearable devices. Such classification methods require large-size data that contain all prevalent types of conditions for algorithm training purposes. For instance, this database was used to train a supervised machine learning algorithm to classify four major rhythms[[2](https://www.nature.com/articles/s41598-020-59821-7)].

---

## Methods

All of the data was acquired in five stages. First, each subject underwent a 12-lead resting ECG test that was taken over a period of 10 seconds. The data was stored into the GE MUSE ECG system. Second, a licensed physician labeled the rhythm and other cardiac conditions. Another licensed physician performed a secondary validation. If there was a disagreement, a senior physician intervened and made a final decision. There are labels of each subject’s rhythm and other conditions such as PVC, right bundle branch block (RBBB), left bundle branch block (LBBB), and atrial premature beat (APB). These additional conditions were applied to the entire sample rather than to specified beats in the 10-second reading. The final diagnoses were stored in the MUSE ECG system as well. Third, ECG data and diagnostic information were exported from the GE MUSE system to XML files that were encoded with a specific naming conversion defined by General Electric (GE). Fourthly, we developed a converting tool to extract ECG data and diagnostic information from the XML file and transfer them to CSV format. In doing so, we referred to the work of Maarten J.B. van Ettinger[[3](https://sourceforge.net/projects/ecgtoolkit-cs/)]. Finally, the CSV files were converted to WFDB format.

---

## Data Description

This database consists of 45,152 patient ECGs. The number of volts per A/D bit is 4.88, and A/D converter had 32-bit resolution. The amplitude unit was microvolt. The upper limit was 32,767, and the lower limit was −32,768. The institutional review board of Shaoxing People’s Hospital and Ningbo First Hospital approved this study, granted the waiver application to obtain informed consent, and allowed the data to be shared publicly after de-identification.

### CSV Format Data
Initially, the part of this database (10,646 patient) was shared at figshare[4] and it consists of four parts: raw ECG data, denoised ECG data, diagnoses file, and attributes dictionary file. For each subject, the raw ECG data was saved as a single CSV file, and all denoised ECG data were saved under the same name CSV file, but in a different file folder. Also, each CSV file mentioned above contains 5000 rows and 12 columns with header names presenting the ECG lead. These CSV files are named by unique IDs. These IDs were also saved in the diagnostics file with the attributes name FileName. The diagnoses file contains all the diagnoses information for each subject including filename, rhythm, other conditions, patient age, gender, and other ECG summary attributes (acquired from GE MUSE system).

### WFDB Format Data
Finally, we moved the data shared at Firgshare to Physionet repository and increased the ECG recording size to 45,152. In addition, the ECG recording format was changed to WFDB format. In the WFDB-format every ECG is represented by a tuple of two files, a mat-file containing the binary raw data and a corresponding header file with the same name and hea-extension. The head file contained annotation information including lead configuration, age, gender, and SNOMED CT code. The file ConditionNames_SNOMED-CT.xlsx presented the mapping between original letter labels and SNOMED CT code. The above settings are designed to keep consistency with other databases used for the PhysioNet/Computing in Cardiology Challenge 2021[[5](https://physionetchallenges.org/2021/)].

---

## Usage Notes

All recordings are organized in two levels folder directory under the WFDBRecords folder. The first level directory contains 46 folders and each one has 10 subfolders. Each subfolder contains 100 ECG recorders and each recorder consists of a header file (.hea) and a data file (.mat). In the data collection stage, we recommend the C# ECG Toolkit that is an open-source software to convert, view and print electrocardiograms [[3](https://sourceforge.net/projects/ecgtoolkit-cs/)]. We suggest the use of Matlab or Python to carry out the denoising step of the analysis. In the feature extraction step, BioSPPy [[6](https://github.com/PIA-Group/BioSPPy/)] is recommended to extract general ECG summary features such as QRS count, R wave location, etc. The source code of the converter tool that transfers ECG data files from XML format to CSV format can be found at the Github repository [[7](https://github.com/zheng120/ECGConverter)], which contains binary executable files, source code, and a user manual. Both the MATLAB [[8](https://www.mathworks.com/)] and Python version programs for ECG noise reduction are available at the Github repository[[9](https://github.com/zheng120/ECGDenoisingTool)].

---

## References

1. Zheng, J., Zhang, J., Danioko, S., Yao, H., Guo, H., & Rakovski, C. (2020). *A 12-lead electrocardiogram database for arrhythmia research covering more than 10,000 patients*. *Scientific Data*, 7(1), 48. https://doi.org/10.1038/s41597-020-0386-x  
2. Zheng, J., Chu, H., Struppa, D., et al. *Optimal Multi-Stage Arrhythmia Classification Approach*. *Scientific Reports*, 10, 2898 (2020). https://doi.org/10.1038/s41598-020-59821-7  
3. https://sourceforge.net/projects/ecgtoolkit-cs/ (accessed [8-10-2022])  
4. https://doi.org/10.6084/m9.figshare.c.4560497.v2  
5. physionetchallenges.org/2021/  
6. https://github.com/PIA-Group/BioSPPy/ (accessed [8-10-2022])  
7. https://github.com/zheng120/ECGConverter (accessed [8-10-2022])  
8. https://www.mathworks.com/ (accessed [8-10-2022])  
9. https://github.com/zheng120/ECGDenoisingTool (accessed [8-10-2022])

---

## Files

Total uncompressed size: 5.1 GB.

### Access the files
- [Download the ZIP file](https://physionet.org/content/ecg-arrhythmia/get-zip/1.0.0/) (2.3 GB)
- Download the files using your terminal: `wget -r -N -c -np https://physionet.org/files/ecg-arrhythmia/1.0.0/`
- Download the files using AWS command line tools: `aws s3 sync --no-sign-request s3://physionet-open/ecg-arrhythmia/1.0.0/ DESTINATION`
