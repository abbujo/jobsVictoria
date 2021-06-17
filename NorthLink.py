import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as plt
import os
    
my_path = os.getcwd()
#####################################################################
################# PHASE 1: DATA PREPROCESSING ####################### 
#####################################################################
def data_processing(df_cleanedReport,df_otherActivities,df_participantActivities,df_participantByProject):
  # Reading the Other Activities file
  df_otherActivities.drop(['Project Start Date','Salutation','First Name','Last Name','Status','Participant Activity Ref','Activity Cease Date','Activity Commence Date','Account Name: Account Name','Opportunity Name','Project End Date'], axis = 1, inplace = True)
  # Dropping all the Fitted for work type activities and Other activities whose comment does not have referred or passport to work
  for index, row in df_otherActivities.iterrows():
    if row['Type']=="Other":
      if str(row['Comments']).lower().find("referred")<0 and str(row['Comments']).lower().find("passport to work")<0:
        df_otherActivities = df_otherActivities.drop([index], axis=0)
    if row['Type']=="Fitted for Work":
      df_otherActivities = df_otherActivities.drop([index], axis=0)
  for index, row in df_otherActivities.iterrows():
    if row['Type']=="Other":
      if str(row['Comments']).lower().find("referred")<0:
        df_otherActivities.at[index,'Type']= "Post employment"
      else:
        df_otherActivities.at[index,'Type']= "Referred"
  # Dropping comments column altogether
  df_otherActivities.drop(['Comments'], axis = 1, inplace = True)

  # removing unwanted fields
  df_participantByProject.drop(['Other Demographics','Salutation','First Name','Last Name','Finish Date','Account Name: Account Name','Opportunity Name'], axis = 1, inplace = True)


  # removing unwanted fields
  df_participantActivities.drop(['Activity Status','Project Start Date','Project End Date','Salutation','First Name','Last Name','Status','Employer Name','Contact Name','Contact Phone','Job Title','Participant Activity Ref','Activity Commence Date','Placement Claim: Claim Ref #','Contact Email','Opportunity Name','Outcome Claim: Claim Ref #'], axis = 1, inplace = True)
  df_participantActivities = df_participantActivities.rename(columns={"Type": "Outcome Type"})

  # Data Integration
  # Merging Both the activities files
  df_all = pd.merge(df_otherActivities,df_participantActivities,on="Code",how="outer")
  df_all['Employment Hours Per Week'] = df_all['Employment Hours Per Week'].fillna(0)
  df_all['Weeks Employed'] = df_all['Weeks Employed'].fillna(0)
  df_all['Occupation Code: Occupation'] = df_all['Occupation Code: Occupation'].fillna("NA")	
  df_all['Industry Code: Class'] = df_all['Industry Code: Class'].fillna("NA")
  df_all['Outcome Type'] = df_all['Outcome Type'].fillna("Unemployed")
  df_all['Placement Status'] = df_all['Placement Status'].fillna("NA")
  df_all['Outcome Status'] = df_all['Outcome Status'].fillna("NA")
  # All Activities file after merging the two files


  # Integrating all the data
  df_unionAll = pd.merge(df_participantByProject,df_all,on="Code",how="outer")
  # Removing all those without activities
  df_unionAll['Activity Cease Date'] = df_unionAll['Activity Cease Date'].fillna(df_unionAll['Registration Date'])
  df_unionAll = df_unionAll.dropna()
  df_unionAll = df_unionAll.drop_duplicates()
  df_unionAll["Days_to_Employ"]= pd.to_datetime(df_unionAll['Activity Cease Date'])-pd.to_datetime(df_unionAll['Registration Date'])
  df_unionAll['Days_to_Employ'] = df_unionAll['Days_to_Employ'].astype(str).str.replace(" days", '')
  ################# Final File after data cleaning and reduction #################

  #####################################################################
  ############# PHASE 2: ACTIVITY BASED DATA ANALYSIS ################# 
  #####################################################################

  # analysis 1 - Activity Frequency
  type_dataframe = df_unionAll[['Type']]
  type_dataframe=type_dataframe.groupby(by='Type').size().reset_index(name="Frequency")
  type_dataframe.plot(kind="pie",y="Frequency",labels=type_dataframe['Type'], figsize=(10,10), radius=0.5, autopct='%.2f')
  plt.tight_layout()
  plt.title('Activity Frequency Chart')
  plt.savefig(my_path + '/static/img/analysis1.png')
  plt.cla()
  # analysis 2 - Activity Outcome Frequency
  type_outcome_dataframe = df_unionAll[['Type', 'Outcome Type']]
  type_outcome_dataframe_frequency = type_outcome_dataframe.groupby(['Type', 'Outcome Type']).size().reset_index(name="Frequency")

  # Plotting Analysis 2
  type_outcome_dataframe_frequency.pivot('Type', 'Outcome Type', 'Frequency').plot(figsize=(10,10),kind='bar')
  plt.tight_layout()
  plt.subplots_adjust(left=None, bottom=0.176, right=None, top=0.97, wspace=None, hspace=None)
  plt.xticks(rotation=30,horizontalalignment="right")
  plt.title('Activity vs Outcome Count Graph')
  plt.savefig(my_path + '/static/img/analysis2.png')
  plt.cla()
# Analysis 3
  cat_dict = {"Full Time":"Employed", "Part Time":"Employed", "Unemployed": "Unemployed"}
  type_outcome_dataframe['Outcome'] = (type_outcome_dataframe['Outcome Type'].str.extract(fr"\b({'|'.join(cat_dict.keys())})\b")[0].map(cat_dict))


  # type_outcome_dataframe['Outcome'] = np.where((type_outcome_dataframe['Outcome Type'] =="Part time") ||(type_outcome_dataframe['Outcome Type'] =="Full time")) 
  type_outcome_dataframe.drop(['Outcome Type'], axis = 1, inplace = True)
  type_outcome_dataframe = type_outcome_dataframe.groupby(['Type', 'Outcome']).size().reset_index(name="Frequency")

  type_outcome_dataframe.pivot('Type', 'Outcome', 'Frequency').plot(figsize=(10,10),kind='bar')
  plt.tight_layout()
  plt.subplots_adjust(left=None, bottom=0.176, right=None, top=0.97, wspace=None, hspace=None)
  plt.xticks(rotation=30,horizontalalignment="right")
  plt.title('Activity vs Outcome Count Consolidated Graph')
  plt.savefig(my_path + '/static/img/analysis3.png')
  plt.cla()
  # Analysis 4
  industry_outcome_dataframe = df_unionAll[['Industry Code: Class', 'Outcome Type']]
  for index, row in industry_outcome_dataframe.iterrows():
    if row['Industry Code: Class']=="NA":
      industry_outcome_dataframe = industry_outcome_dataframe.drop([index], axis=0)
  industry_outcome_dataframe['Outcome'] = (industry_outcome_dataframe['Outcome Type'].str.extract(fr"\b({'|'.join(cat_dict.keys())})\b")[0].map(cat_dict))

  industry_outcome_dataframe.drop(['Outcome Type'], axis = 1, inplace = True)
  industry_outcome_dataframe = industry_outcome_dataframe.groupby(['Industry Code: Class', 'Outcome']).size().reset_index(name="Frequency")
  industry_outcome_dataframe = industry_outcome_dataframe.nlargest(10,'Frequency')
  industry_outcome_dataframe.pivot('Industry Code: Class', 'Outcome', 'Frequency').plot(figsize=(10,10),kind='bar')
  plt.tight_layout()
  plt.subplots_adjust(left=None, bottom=0.176, right=None, top=0.97, wspace=None, hspace=None)
  plt.xticks(rotation=30,horizontalalignment="right")
  plt.title('Industry vs Outcome Count Consolidated Graph')
  plt.savefig(my_path + '/static/img/analysis4.png')
  plt.cla()
  # Analysis 5
  df_cleanedReport.drop(['First Name','Last Name','Email','Comments','Status','Preferred Occupation','Previous Occupation',], axis = 1, inplace = True)
  df_cleanedReport['Age'].plot(kind='box', vert=False, figsize=(10, 10))
  plt.tight_layout()
  plt.subplots_adjust(left=None, bottom=0.176, right=None, top=0.97, wspace=None, hspace=None)
  plt.xticks(np.arange(min(df_cleanedReport['Age'])-5, max(df_cleanedReport['Age'])+5, 5.0))
  plt.title("Boxplot Analysis for Age")
  plt.savefig(my_path + '/static/img/analysis5.png')
  plt.cla()

  # Analysis 6
  suburb_analysis_df = df_cleanedReport[['Suburb']]
  suburb_analysis_df_frequency = suburb_analysis_df.groupby(['Suburb']).size().reset_index(name="Frequency")
  newData = suburb_analysis_df_frequency.nlargest(10,'Frequency')
  maxValue = newData['Frequency'].max()
  newData.plot(figsize=(10,10),kind='barh').set_yticklabels(newData['Suburb'])
  plt.tight_layout()
  plt.xlim(0,maxValue+10)
  plt.subplots_adjust(left=None, bottom=0.176, right=None, top=0.97, wspace=None, hspace=None)
  plt.xticks(rotation=30,horizontalalignment="right")
  plt.title(r"Top 10 Suburbs from where participant's register")
  plt.savefig(my_path + '/static/img/analysis6.png')
  plt.cla()

  # Analysis 7
  demographic_analysis_df = df_unionAll[['Primary Demographic']]
  demographic_analysis_frequency = demographic_analysis_df.groupby(['Primary Demographic']).size().reset_index(name="Frequency")
  newData = demographic_analysis_frequency.nlargest(10,'Frequency')
  maxValue = newData['Frequency'].max()
  newData.plot(figsize=(10,10),kind='barh').set_yticklabels(newData['Primary Demographic'])
  plt.tight_layout()
  plt.xlim(0,maxValue+10)
  plt.subplots_adjust(left=None, bottom=0.176, right=None, top=0.97, wspace=None, hspace=None)
  plt.xticks(rotation=30,horizontalalignment="right")
  plt.title(r"Top 10 Primary Demographic of participant's")
  plt.savefig(my_path + '/static/img/analysis7.png')
  plt.cla()

  # Analysis 8
  main_language_analysis_df = df_unionAll[['Main Language']]
  main_language_analysis_frequency = main_language_analysis_df.groupby(['Main Language']).size().reset_index(name="Frequency")
  for index, row in main_language_analysis_frequency.iterrows():
    if row['Main Language']=="English":
      main_language_analysis_frequency = main_language_analysis_frequency.drop([index], axis=0)
  newData = main_language_analysis_frequency.nlargest(10,'Frequency')
  maxValue = newData['Frequency'].max()
  newData.plot(figsize=(10,10),kind='barh').set_yticklabels(newData['Main Language'])
  plt.tight_layout()
  plt.xlim(0,maxValue+10)
  plt.subplots_adjust(left=None, bottom=0.176, right=None, top=0.97, wspace=None, hspace=None)
  plt.xticks(rotation=30,horizontalalignment="right")
  plt.title(r"Top 10 Main Language of participant's")
  plt.savefig(my_path + '/static/img/analysis8.png')
  plt.cla()

  # Analysis 9
  birth_country_analysis_df = df_unionAll[['Country of Birth']]
  birth_country_analysis_frequency = birth_country_analysis_df.groupby(['Country of Birth']).size().reset_index(name="Frequency")
  for index, row in birth_country_analysis_frequency.iterrows():
    if row['Country of Birth']=="Australia":
      birth_country_analysis_frequency = birth_country_analysis_frequency.drop([index], axis=0)
  newData = birth_country_analysis_frequency.nlargest(10,'Frequency')
  maxValue = newData['Frequency'].max()
  newData.plot(figsize=(10,10),kind='barh').set_yticklabels(newData['Country of Birth'])
  plt.tight_layout()
  plt.xlim(0,maxValue+10)
  plt.subplots_adjust(left=None, bottom=0.176, right=None, top=0.97, wspace=None, hspace=None)
  plt.xticks(rotation=30,horizontalalignment="right")
  plt.title(r"Top 10 Country of Birth of participant's")
  plt.savefig(my_path + '/static/img/analysis9.png')
  plt.cla()

  # Analysis 10 and 11
  days_to_employ_analysis_df = df_unionAll[['Industry Code: Class','Days_to_Employ']]
  for index, row in days_to_employ_analysis_df.iterrows():
      if row['Industry Code: Class']=="NA" or row['Days_to_Employ']=="0":
        days_to_employ_analysis_df = days_to_employ_analysis_df.drop([index], axis=0)
  days_to_employ_analysis_df['Days_to_Employ'] = pd.to_numeric(days_to_employ_analysis_df['Days_to_Employ'])
  newDF = pd.DataFrame(days_to_employ_analysis_df.groupby('Industry Code: Class').mean())
  newDF['Industry Code: Class'] = newDF.index
  newDF = newDF[['Industry Code: Class','Days_to_Employ']]
  newData1 = newDF.nlargest(10,'Days_to_Employ')
  newData2 = newDF.nsmallest(10,'Days_to_Employ')


  newData1.plot(figsize=(10,10),kind='barh').set_yticklabels(newData1['Industry Code: Class'])
  plt.tight_layout()
  plt.subplots_adjust(left=None, bottom=0.176, right=None, top=0.97, wspace=None, hspace=None)
  plt.xticks(rotation=30,horizontalalignment="right")
  plt.title('Industry Code that take most days for placement (Mean)')
  plt.savefig(my_path + '/static/img/analysis10.png')
  plt.cla()

  newData2.plot(figsize=(10,10),kind='barh').set_yticklabels(newData2['Industry Code: Class'])
  plt.tight_layout()
  plt.subplots_adjust(left=None, bottom=0.176, right=None, top=0.97, wspace=None, hspace=None)
  plt.xticks(rotation=30,horizontalalignment="right")
  plt.title('Industry Code that take least days for placement (Mean)')
  plt.savefig(my_path + '/static/img/analysis11.png')
  plt.cla()


  file_list=[df_all,df_unionAll,type_dataframe,type_outcome_dataframe_frequency,type_outcome_dataframe,industry_outcome_dataframe,suburb_analysis_df_frequency,demographic_analysis_frequency,main_language_analysis_frequency,birth_country_analysis_frequency,days_to_employ_analysis_df]
  name_list=[  'PHASE_1_All_Activities_NORTHlink_Jobs_VIC.csv',
  'PHASE_1_Processed_Data_NORTHlink_Jobs_VIC.csv',
  'PHASE_2_Analysis_1_Activity_vs_Frequency.csv',
  'PHASE_2_Analysis_2_Activity_Outcome_Frequency.csv',
  'PHASE_2_Analysis_3_Activity_Outcome_Consolidated.csv',
  'PHASE_2_Analysis_4_Industry_Outcome_Consolidated.csv',
  'PHASE_2_Analysis_6_Suburb_Analysis.csv',
  "PHASE_2_Analysis_7_Demographic_Analysis.csv",
  "PHASE_2_Analysis_7_main_language_Analysis.csv",
  "PHASE_2_Analysis_7_birth_country_Analysis.csv",
  "PHASE_2_Analysis_7_Days_to_employ.csv"]

  val ={'files': file_list, 'names':name_list }

  return val