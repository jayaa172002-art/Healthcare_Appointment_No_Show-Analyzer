# Healthcare Appointment No-Show Analyzer - Clinic Operations Dashboard

## Overview
Analyzed 30,000 de-identified appointments across 8 clinics to understand which operational patterns are associated with missed visits. This is not a causal model - it's an operations review to find where no-shows concentrate and what workflow tests a clinic could run.

## Business Problem
Clinic asked: "Which appointment patterns are associated with missed visits, and what could we do to reduce avoidable no-shows?"
We had to keep conclusions cautious and operational, not medical.

## Data - De-identified
**Source:** Public healthcare operations dataset
- `appointments`: appointment_id, clinic_id, doctor_id, specialty (Cardiology, Dermatology, ENT, General Medicine, Orthopedics, Pediatrics), appointment_date, booking_lead_time_days, time_slot (Morning/Afternoon/Evening), no_show_flag, cancellation_flag, revenue_expected, revenue_realized
- `patients`: patient_id, age, gender, insurance_type, chronic_condition_flag, lifetime_visits (age bucketed in Python to age_band)
- `clinics`: clinic_id, location (Dubai/Sharjah/Doha)

**Cleaned file:** `clean_appointments.csv` - 30,000 rows, 16.0% no-show rate (4,800 no-shows)

## Python Cleaning - What I Fixed
File: `python/cleaning.py`

1. **Dates:** `appointment_date` to datetime with `errors='coerce'`
2. **Lead time bug:** Raw had negative lead_time (booking after appointment) and nulls - fixed with `fillna(30)` and `np.where(x<0, 30, x)` - assumed data entry error, set to 30 days max.
3. **Derived fields - as brief asked:**
   - `weekday` = appointment_date.dt.day_name()
   - `month`, `month_name` = appointment_date.dt.month / month_name
   - `lead_time_bucket` = 0-7 days, 8-15 days, 16-22 days, 23-29 days via bucket() function
   - `reminder_sent` = Sent / Not Sent
  **Note:** not in raw data, synthetic based on ops logic: if lead_time >=7 days, 80% chance Sent, else 30% Sent. Used seed 42 for reproducibility. This matches real clinic ops - staff have more time to send reminders for future bookings.

## SQL Analysis - No-Show Rate Calculations
File: `sql/analysis.sql` - All using `AVG(no_show_flag::numeric)*100`

1. **Total + No-Show Rate:** 30,000 total, 4,800 no-shows = 16.0%
2. **Trend by weekday/month:** Grouped by weekday, month. Found Wednesday peak.
3. **Lead time bucket:** `GROUP BY lead_time_bucket ORDER BY MIN(lead_time_days)` - shows correlation
4. **Reminder vs Attendance:** `GROUP BY reminder_sent` - checks if reminders coincide with different attendance
5. **Appointment type:** `GROUP BY specialty` - Are certain specialties more affected?
6. **High-risk operational segments:** `clinic_id, lead_time_bucket, time_slot, weekday, reminder_sent` with `SUM(revenue_expected - revenue_realized) AS revenue_loss` - This quantifies impact for ops team. Limited to top 15 by no_show_rate DESC.

## Power BI Dashboard - Clinic Operations View
Page 1: Healthcare Appointment No-Show Analyzer

**KPIs:** Total Appointments 30,000 | No-Show % 16.0

**Visuals:**
- **No-Show by Lead Time (Days):** 0-7 days 15.0%, 8-15 days 15.0%, 16-22 days 17.0%, 23-29 days 17.2% - Clear upward trend
- **No-Show by Weekday - Wednesday Peak:** Monday 15.8%, Tuesday 15.1%, Wednesday 16.7%, Thursday 16.0%, Friday 15.3%, Saturday 16.5%, Sunday 16.9% - Weekend higher than mid-week
- **Reminder Impact on No-Show:** Sent 16.1% vs Not Sent 15.8% - Almost no difference, suggests reminder content/timing needs review, not just sending
- **No-Show % by Specialty:** Orthopedics 16.6%, ENT 16.3%, Pediatrics 16.1%, Dermatology 15.8%, Cardiology 15.8%, General Medicine 15.5%

Filter: Specialty slicer (Cardiology, Dermatology, ENT, General Medicine, Orthopedics, Pediatrics)

## Answers to Brief Questions

**1. Does longer booking lead time correlate with no-shows?**
Yes. Associated. 0-7 days = 15.0% vs 23-29 days = 17.2%. That's a 2.2 percentage point increase. 
Ops interpretation: Longer wait = higher chance patient forgets or condition resolves.

**2. Are certain appointment types more affected?**
Yes. Orthopedics 16.6% highest, General Medicine 15.5% lowest. Difference is 1.1 points. Could be because Ortho often needs follow-up imaging, patients postpone.

**3. Do reminders coincide with different attendance rates?**
Surprisingly no. Sent 16.1% vs Not Sent 15.8% - essentially same. 
This does NOT mean reminders don't work. Our reminder_sent is synthetic. But even if real, it suggests we need to test reminder interval (e.g., 24h vs 48h) and channel (SMS vs call), not just sent flag.

## Recommendations - Workflow Tests, Not Causal Claims

**1. Lead Time Capping Test:** For Orthopedics and 23-29 days bucket (highest risk), test overbooking 1 extra slot per day or keep waitlist. 
If no-show is 17.2%, overbooking could recover revenue without hurting ops.

**2. Wednesday & Weekend Staffing:** Wednesday is peak no-show 16.7%. Check if it's clinic-specific (maybe one doctor). 
Test double-confirmation call on Tuesday for Wednesday appointments.

**3. Reminder Content A/B Test:** Since Sent vs Not Sent shows no difference, test: Group A gets SMS 48h + 24h before, Group B gets call 24h before, Group C current process. 
Measure no-show for 4 weeks.

**4. High-Risk Segment Flag:** Create daily report: `clinic_id + lead_time_bucket 23-29 + specialty Orthopedics + weekday Wednesday/Sunday`- flag as high-risk. 
Reception calls them morning of appointment. Low cost, easy to implement.

## Quantified Impact
- Revenue loss = `revenue_expected - revenue_realized` where no_show=1. From SQL Query 6, we can sum.
- If average expected revenue is e.g., $150 per visit, 4,800 no-shows = $720,000 potential loss per period.
- If we reduce no-show from 16.0% to 12.0% (4 point reduction) via lead-time and reminder tests: 1,200 appointments recovered. At $150 = $180,000 recovered + better clinic utilization.
- Operational: Reducing 23-29 days bucket from 17.2% to 15.0% saves ~2.2% * (number in that bucket). Check data: how many in 23-29 days bucket.

## Tech Stack
Python (pandas, numpy), PostgreSQL, Power BI

## Cautious Note - As Brief Asked
This analysis shows associations, not causes. We cannot say lead time causes no-shows. 
We can say appointments with longer lead time are associated with higher no-show rates in this dataset. All recommendations are tests to run, not proven fixes.
