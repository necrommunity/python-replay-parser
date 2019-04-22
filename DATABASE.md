# Database Schema 

## **run** 

Each row represents a single replay file

> id: int, primary key, autoincrements
> > The unique ID for each run in the database

> version: int
> > The version of the replay file

> amplified: bool
> > Designates if this has the Amplified DLC in Early Access

> amplified_full: bool
> > Designates if this has the Amplified DLC after full release

> folder: text
> > The folder path to the replay

> file: text
> > The file name of the replay

> hash: int
> > A unique hash based off of folder, file and character of the run

> run_date: int
> > The date of when the run happened

> f_run_date: text
> > The run date in a pretty format for display

> run_type: int
> > The type of run that the replay represents

> f_fun_type: text
> > The type of run in a pretty format for display

> run_time: int
> > The length of the run in milliseconds

> f_run_time: text
> > The length of the run formatted as the end screen output

> seed: int
> > The integer representation of the seed

> songs: int
> > How many songs were played throughout the run

> players: int
> > How many characters were played in the run, irrelavent because I did not code in co-op 

> char1: int
> > The character for player 1

> f_char1: text
> > The character for player 1, formatted for display

> char2: int
> > The character for player 2

> f_char2: text
> > The character for player 2, formatted for display

> win: bool
> > Designates if the run was completed or not

> killed_by: int
> > What you were killed by, not currently implemented

> f_killed_by: text
> > What you were killed by, formatted for display

> key_presses: int
> > The number of keys pressed throughout a run

> score: int
> > The score the run achieved

> imported_date: int
> > The date the run was imported

## **bugged** 
Each row represents data for a bugged run

> id: int, primary key, autoincremented
> > The unique ID of each bugged run

> run_id: int, references run(id)
> > A reference to the run's id in the run table

> bugged_reason: text
> > The reason the run was bugged

> bugged_data: text
> > The raw data behind the bugged run

## **tag** 
Each row represents a specific tag -- not currently implemented

> id: int, primary key, autoincremented
> > The unique ID of each tag

> name: text
> > The name of each tag

> color: text
> > The color of each tag

## **run_tag** 
Each row represents the tag of the a run in the run table -- not currently implemented

> id: int, primary key, autoincremented
> > The unique ID of each run's tag

> run_id: int, references run(id)
> > The run's ID from the run table

> tag_id: int, references tag(id)
> > The tag's ID from the tag table