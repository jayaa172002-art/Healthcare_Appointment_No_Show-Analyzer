import pandas as pd
from sqlalchemy import create_engine

# change password
engine = create_engine('postgresql://postgres:840991@localhost:5432/healthcare_no_show_db')

# Load cleaned data
appointments = pd.read_csv('data/clean_appointments.csv')
print("Appointments:", appointments.shape)
appointments.to_sql('appointments', engine, if_exists='replace', index=False)
    
patients = pd.read_csv('data/patients.csv')
print("Patients:", patients.shape)
patients.to_sql('patients', engine, if_exists='replace', index=False)

clinics = pd.read_csv('data/clinics.csv')
print("Clinics:", clinics.shape)
clinics.to_sql('clinics', engine, if_exists='replace', index=False)

print("All 3 tables loaded in postgres")