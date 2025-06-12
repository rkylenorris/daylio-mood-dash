DROP TABLE IF EXISTS customMoods; 
DROP TABLE IF EXISTS tags ;
DROP TABLE IF EXISTS dayEntries ;
DROP TABLE IF EXISTS goals ;
DROP TABLE IF EXISTS prefs ;
DROP TABLE IF EXISTS tag_groups ;
DROP TABLE IF EXISTS goalEntries ;
DROP TABLE IF EXISTS calendar ;
DROP TABLE IF EXISTS mood_groups ;
DROP TABLE IF EXISTS entry_tags   ;  
    
    
    
    -- create customMoods table

    CREATE TABLE IF NOT EXISTS customMoods (
        id INTEGER PRIMARY KEY,
        custom_name TEXT,
        mood_value INTEGER,
        mood_group_id INTEGER,
        mood_group_order INTEGER,
        createdAt DATETIME,
        date DATE,
        FOREIGN KEY (mood_group_id) REFERENCES mood_groups(id)
    );


    -- Create tags table

    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY,
        name TEXT,
        createdAt DATETIME,
        `order` INTEGER,
        id_tag_group INTEGER,
        date DATE,
        FOREIGN KEY (id_tag_group) REFERENCES tag_groups(id)
    );


    -- Create dayEntries table

    CREATE TABLE IF NOT EXISTS dayEntries (
        id INTEGER PRIMARY KEY,
        datetime DATETIME,
        mood INTEGER,
        note TEXT,
        note_title TEXT,
        date DATE,
        FOREIGN KEY (mood) REFERENCES customMoods(id)
    );


    -- Create goalEntries table

    CREATE TABLE IF NOT EXISTS goalEntries (
        id INTEGER PRIMARY KEY,
        goalId INTEGER,
        createdAt DATETIME,
        date DATE,
        FOREIGN KEY (goalId) REFERENCES goals(goal_id)
    );


    -- Create goals table

    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY,
        goal_id INTEGER,
        created_at DATETIME,
        id_tag INTEGER,
        end_date DATEIME,
        name TEXT,
        note TEXT,
        date DATE,
        date_end Date,
        FOREIGN KEY (id_tag) REFERENCES tags(id)
    );


    -- Create prefs table

    CREATE TABLE IF NOT EXISTS prefs (
        AUTO_BACKUP_IS_ON BOOLEAN,
        LAST_DAYS_IN_ROWS_NUMBER INTEGER,
        DAYS_IN_ROW_LONGEST_CHAIN INTERGER,
        LAST_ENTRY_CREATION_TIME DATETIME
    );


    -- Create tag_groups table

    CREATE TABLE IF NOT EXISTS tag_groups (
        id INTEGER PRIMARY KEY,
        name TEXT
    );


    -- create calendar table

    CREATE TABLE IF NOT EXISTS calendar (
        TimeStamp DATETIME PRIMARY KEY,
        Date DATE,
        Day INTEGER,
        DayName TEXT,
        Week INTEGER,
        Month INTEGER,
        MonthName TEXT,
        Quarter INTEGER,
        Year INTEGER,
        MonthYear TEXT,
        QuarterYear TEXT,
        IsWeekend BOOLEAN,
        IsWeekday BOOLEAN
    );



    CREATE TABLE IF NOT EXISTS mood_groups (
        id INTEGER PRIMARY KEY,
        name TEXT,
        value INTEGER
   );



    CREATE TABLE entry_tags (
        entry_id INTEGER,
        tag TEXT,
        FOREIGN KEY (entry_id) REFERENCES dayEntries(id)
    );

CREATE TABLE fitbit_sleep (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    duration_milliseconds INTEGER,
    duration_seconds INTEGER,
    duration_minutes INTEGER,
    duration_hours INTEGER,
    duration_hhmmss TEXT,
    sleep_type TEXT,
    start_time TEXT NOT NULL UNIQUE,
    start_time_ymdhm TEXT,
    end_time TEXT,
    end_time_ymdhm TEXT,
    efficiency INTEGER,
    minutes_asleep INTEGER,
    minutes_awake INTEGER,
    main_sleep BOOLEAN,
    deep_sleep_count INTEGER,
    deep_sleep_minutes INTEGER,
    light_sleep_count INTEGER,
    light_sleep_minutes INTEGER,
    rem_sleep_count INTEGER,
    rem_sleep_minutes INTEGER,
    wake_count INTEGER,
    wake_minutes INTEGER,
    asleep_count INTEGER,
    asleep_minutes INTEGER,
    awake_count INTEGER,
    awake_minutes INTEGER,
    restless_count INTEGER,
    restless_minutes INTEGER,
    sleep_log_type TEXT
);
