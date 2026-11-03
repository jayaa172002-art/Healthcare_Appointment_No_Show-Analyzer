-- 1. Total appointments and N0 show rate
SELECT COUNT(*) AS total_appointments,
SUM(no_show_flag) AS no_shows,
ROUND(AVG(NO_show_flag::numeric)*100,2) AS no_show_rate_pct
FROM appointments;

-- 2. Trend by weekday/month
SELECT weekday,
COUNT(*) AS total,
ROUND(AVG(no_show_flag::numeric)*100,2) AS no_show_rate
FROM appointments
GROUP BY weekday;

SELECT month, month_name,
COUNT(*) AS total,
ROUND(AVG(no_show_flag::numeric)*100,2) AS no_show_rate
FROM appointments
GROUP BY month, month_name
ORDER BY month;


--3. Lead_time_bucket
SELECT lead_time_bucket,
COUNT(*) AS total,
ROUND(AVG(no_show_flag)*100,2) AS no_show_percent
FROM appointments
GROUP BY lead_time_bucket
ORDER BY MIN(lead_time_days);


--4. Remainer vs Attendance
SELECT reminder_sent,
COUNT(*) AS total,
ROUND(AVG(no_show_flag::numeric)*100,2) AS no_show_rate
FROM appointments
GROUP BY reminder_sent;


--5. Appointment
--Are certain appointment types more affected?
SELECT appointment_time_slot AS appointment_type,
COUNT(*) AS total,
ROUND(AVG(no_show_flag::numeric)*100,2) AS no_show_rate
FROM appointments
GROUP BY appointment_time_slot
ORDER BY no_show_rate DESC;

--6. High-risk operational segments
SELECT clinic_id, lead_time_bucket, appointment_time_slot, weekday, reminder_sent,
COUNT(*) AS total,
ROUND(AVG(no_show_flag::numeric)*100,2) AS no_show_rate,
SUM(revenue_expected - revenue_realized) AS revenue_loss
FROM appointments
GROUP BY clinic_id, lead_time_bucket, appointment_time_slot, weekday, reminder_sent
ORDER BY no_show_rate DESC
LIMIT 15;


