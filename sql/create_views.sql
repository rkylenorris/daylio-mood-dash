DROP VIEW IF EXISTS v_activity_summary ;
DROP VIEW IF EXISTS v_entry_details ;
DROP VIEW IF EXISTS v_daily_avgs ;
DROP VIEW IF EXISTS v_sleep_summary ;
DROP VIEW IF EXISTS v_sleep_trend ;
DROP VIEW IF EXISTS v_goal_summary ;
DROP VIEW IF EXISTS v_goal_calendar ;
DROP VIEW IF EXISTS v_goal_progress_by_month ;


CREATE VIEW v_activity_summary AS
WITH ranked_activities AS (
    SELECT
        tg.name AS [group],
        t.name AS [activity],
        COUNT(t.name) AS [count],
        ROW_NUMBER() OVER (
            PARTITION BY tg.name
            ORDER BY COUNT(t.name) DESC
        ) AS rank
    FROM dayEntries AS de
    LEFT JOIN entry_tags AS et ON de.id = et.entry_id
    LEFT JOIN tags AS t ON et.tag = t.id
    LEFT JOIN tag_groups AS tg ON t.id_tag_group = tg.id
    WHERE date(de.date) > date('now', '-90 days')
    GROUP BY tg.name, t.name
)
SELECT [group], activity, [count]
FROM ranked_activities
WHERE rank <= 10
ORDER BY [group], [count] DESC;


CREATE VIEW v_entry_details
AS
SELECT
        de.date as day
        ,de.datetime as entry_datetime
        ,de.id as entry_id
        ,de.mood as mood_id
        ,cm.custom_name as mood_name
        ,cm.mood_group_id as mood_group
        ,cm.mood_value as mood_value
        ,mg.name as mood_group_name
    FROM dayEntries as de
    join customMoods as cm on de.mood = cm.id
    join mood_groups as mg on cm.mood_group_id = mg.id
    where date(de.date) > date('now', '-90 days')
    order by de.date, de.datetime;

CREATE VIEW v_daily_avgs
AS
Select
day,
round(avg(mood_value),2) as avg_mood_value
FROM
   ( SELECT
       day
    ,mood_value
    FROM v_entry_details)
group by day
order by day desc;


CREATE VIEW v_sleep_summary
AS
SELECT
    t.name as [sleep_status],
    COUNT(t.name) AS [count]
FROM dayEntries AS de
LEFT JOIN entry_tags as et on de.id = et.entry_id
LEFT JOIN tags AS t ON et.tag = t.id
LEFT JOIN tag_groups AS tg ON t.id_tag_group = tg.id
where date(de.date) > date('now', '-90 days')
AND tg.name = 'Sleep'
group by t.name;

CREATE VIEW v_sleep_trend
AS
SELECT
    de.date as [day],
    t.name as [sleep_status],
    CASE
        WHEN t.name = 'good sleep' then 3
        WHEN t.name = 'medium sleep' then 2
        when t.name = 'bad sleep' then 1
        else 0
    END AS [value]
FROM dayEntries AS de
LEFT JOIN entry_tags as et on de.id = et.entry_id
LEFT JOIN tags AS t ON et.tag = t.id
where  t.id in (75, 76, 77, 152)
and date(de.date) > date('now', '-90 days')
group by de.date, t.name;

CREATE VIEW v_goal_summary AS
SELECT
    g.goal_id,
    g.name AS goal_name,
    g.note AS goal_note,
    tg.name AS tag_group,
    t.name AS tag_name,
    g.created_at AS goal_start,
    COALESCE(g.date_end, g.end_date) AS goal_end,
    COUNT(ge.id) AS times_completed,
    MIN(ge.date) AS first_checkin,
    MAX(ge.date) AS last_checkin
FROM goals g
LEFT JOIN tags t ON g.id_tag = t.id
LEFT JOIN tag_groups tg ON t.id_tag_group = tg.id
LEFT JOIN goalEntries ge ON g.goal_id = ge.goalId
GROUP BY g.goal_id
ORDER BY times_completed DESC, goal_start;


CREATE VIEW v_goal_calendar AS
SELECT
    g.goal_id,
    g.name AS goal_name,
    cal.Date AS calendar_day,
    CASE WHEN ge.id IS NOT NULL THEN 1 ELSE 0 END AS goal_completed
FROM goals g
JOIN calendar cal ON cal.Date BETWEEN DATE(g.created_at) AND COALESCE(g.date_end, g.end_date, DATE('now'))
LEFT JOIN goalEntries ge ON g.goal_id = ge.goalId AND ge.date = cal.Date
ORDER BY g.goal_id, cal.Date;


CREATE VIEW v_goal_progress_by_month AS
SELECT
    g.goal_id,
    g.name AS goal_name,
    cal.MonthYear,
    COUNT(ge.id) AS completions
FROM goals g
JOIN goalEntries ge ON g.goal_id = ge.goalId
JOIN calendar cal ON cal.Date = ge.date
GROUP BY g.goal_id, cal.MonthYear
ORDER BY g.goal_id, cal.MonthYear;

CREATE VIEW v_sleep_main_per_day AS
SELECT 
    [date],
    duration_hours,
    CASE
        WHEN duration_hours <= 2 THEN 0
        WHEN duration_hours <= 4 THEN 1
        WHEN duration_hours <= 6 THEN 2
        WHEN duration_hours <= 8 THEN 3
        ELSE 4
    END AS sleep_quality_score,
    
    CASE
        WHEN duration_hours <= 2 THEN 'Very Poor'
        WHEN duration_hours <= 4 THEN 'Poor'
        WHEN duration_hours <= 6 THEN 'Fair'
        WHEN duration_hours <= 8 THEN 'Good'
        ELSE 'Excellent'
    END AS sleep_quality_label
FROM fitbit_sleep
WHERE sleep_type != 'nap'
  AND (
      date, duration_minutes
  ) IN (
      SELECT date, MAX(duration_minutes)
      FROM fitbit_sleep
      WHERE sleep_type != 'nap'
      GROUP BY date
  );

