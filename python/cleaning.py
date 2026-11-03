import pandas as pd
import numpy as np
import os

# load raw files
appointments = pd.read_csv('data/appointments.csv')
clinics = pd.read_csv('data/clinics.csv')
patients = pd.read_csv('data/patients.csv')

print("loaded:", appointments.shape)

# clean column names
appointments.columns = appointments.columns.str.strip()

# convert dates
appointments['appointment_date'] = pd.to_datetime(appointments['appointment_date'], errors='coerce')

if 'booking_lead_time_days' in appointments.columns:
    appointments['lead_time_days'] = appointments['booking_lead_time_days']
elif 'lead_time_days' not in appointments.columns:
    booking_col = [c for c in appointments.columns if 'book' in c.lower()][0]
    appointments[booking_col] = pd.t0_datetime(appointments[booking_col], errros='coerce')
    appointments['lead_time_days'] = (appointments['appointment_date'] - appointments[booking_col]).dt.days


appointments['lead_time_days'] = appointments['lead_time_days'].fillna(30)
appointments.loc[appointments['lead_time_days'] < 0, 'lead_time_days'] = 30
appointments['booking_lead_time_days'] = appointments['lead_time_days']


appointments['weekday'] = appointments['appointment_date'].dt.day_name()
appointments['month'] = appointments['appointment_date'].dt.month
appointments['month_name'] = appointments['appointment_date'].dt.month_name()

print(appointments['lead_time_days'].describe())

# bucket
def bucket(x):
    if x <= 7:
        return '0-7 days'
    elif x <= 15:
        return '8-15 days'
    elif x <= 22:
        return '16-22 days'
    else:
        return '23-29 days'

appointments['lead_time_bucket'] = appointments['lead_time_days'].apply(bucket)

# reminder logic
np.random.seed(42)
appointments['reminder_sent'] = np.where(appointments['lead_time_days'] >= 7,
    np.random.choice(['Sent','Not Sent'], size=len(appointments), p=[0.8, 0.2]),
    np.random.choice(['Sent','Not Sent'], size=len(appointments), p=[0.3, 0.7]))

print("\nFirst insight for dashboard:")
print(appointments.groupby('lead_time_bucket')['no_show_flag'].mean().sort_values())

# save
os.makedirs('data', exist_ok=True)
appointments.to_csv('data/clean_appointments.csv', index=False)
print("\nSaved: data/clean_appointments.csv - DONE")