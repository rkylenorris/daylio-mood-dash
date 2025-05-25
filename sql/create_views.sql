DROP VIEW IF EXISTS v_activity_summary ;
DROP VIEW IF EXISTS v_entry_details ;
DROP VIEW IF EXISTS v_daily_avgs ;
DROP VIEW IF EXISTS v_sleep_summary ;
DROP VIEW IF EXISTS v_sleep_trend ;


CREATE VIEW v_activity_summary
AS
SELECT
    tg.name as [group],
    t.name as [activity],
    COUNT(t.name) AS [count]
FROM dayEntries AS de
LEFT JOIN entry_tags as et on de.id = et.entry_id
LEFT JOIN tags AS t ON et.tag = t.id
LEFT JOIN tag_groups AS tg ON t.id_tag_group = tg.id
where date(de.date) > date('now', '-90 days')
group by tg.name, t.name
having count > 0
order by count desc, [group]
limit 20;

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