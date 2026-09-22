TABLE_SCHEMA_DESCRIPTION = """
Table: classes
Contains one row per course section (group) offered at the university.

Columns:
- course_code (text): course identifier code, e.g. "056"
- group_number (text): section/group number for the course, e.g. "01"
- course_name (text): Persian course name, e.g. "آمار و احتمال مهندسی"
- total_units (integer): number of credit units
- practical_units (integer): number of practical/lab credit units
- capacity (integer): total seats available in the section
- waiting_list (integer): current waitlist count
- teacher_name (text): instructor's name in Persian
- has_theory (boolean): whether this section has a lecture session
- theory_day (text): Persian day of week for lecture, e.g. "یکشنبه" (Sunday), "دوشنبه" (Monday), "سه‌شنبه" (Tuesday)
- theory_start_time / theory_end_time (integer): lecture hour, 24h format, whole hours only (e.g. 8 means 8:00)
- theory_location (text): lecture room number, e.g. "611"
- has_practical / practical_day / practical_start_time / practical_end_time / practical_location: same pattern for practical (lab) sessions
- has_exercise / exercise_day / exercise_start_time / exercise_end_time / exercise_location: same pattern for exercise/tutorial sessions
- has_exam (boolean): whether this section has a final exam
- exam_date (text): exam date in Jalali calendar format "YYYY.MM.DD", e.g. "1405.10.23"
- exam_start_time / exam_end_time (text): exam time range in "HH:MM" format (unlike theory/practical/exercise times, these are strings, not integers)
- description (text): free-text notes about the section
- emergency_drop_allowed (boolean): whether emergency withdrawal is allowed for this section

Notes for query generation:
- Each course_code can have multiple rows (multiple groups/sections) — always consider group_number when a user asks about a specific section.
- Day names are in Persian; match them exactly as stored, don't translate.
- theory/practical/exercise times are integer hours (e.g. 8, 14) — compare as numbers, not strings.
- exam_start_time and exam_end_time are "HH:MM" strings — use string comparison or LIKE for these, not numeric comparison.
"""