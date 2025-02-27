# MyProductivityApp

A web app based on the Dash package that is setup to allow tracking desired types of activities in your everyday life. Along with logging sessions, be it exercise, reading, technical courses,  this provides a convenient way of logging, checking your progress (with regards to flexible targets) and visualising this in insightful ways.

## Quick set-up

The app makes use of in particular two data sources; ideally these are databases or cloud based storage files (e.g. an AWS S3 bucket). For convience, and since it is just fine when running the program locally, these have by default been set up as two csv files. These CSV files are populated with dummy data corresponding to the types of activities hard-coded into the app. This is to see the format these should be in, when starting to use the app, these CSV files should be cleared, so you can start afresh. A helper script is also included to streamline the creation of the goals csv.

When using the program it should be easy amend the types of activities to match what you are indeed interested in tracking, although digging into the code must be expected. Maybe in the future, the selection of activities / gropus / labels will be defined outside of the code or maybe directly through the web app.

# Future work

Some future work is planned, including
* integration with external APIs, for instance the Strava API and maybe some Garmin API
* automation/integration of configuration into the application itself reducing the need to mess with the code
