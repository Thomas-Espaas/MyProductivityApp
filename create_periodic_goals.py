import pandas as pd

if __name__ == '__main__':
    """
    This script can be run to create period goals for the dashboard. It has been set up to make it easy
    to add based on pre-specified time intervals; weekly, bi-weekly, tri-weekly and monthly
    """


    # "Identifier level" should be 0 for grand totals, 1 for activity groups (exercise/culture...), 2 for activities
    # (climbing, reading, industry research, ...) and 3 for activity highlights (board climbing, bench press,
    # non-fiction, ...). "Identifier" is then what ever identifier is relevant to the condition (e.g. climbing,
    # strength, ...). Condition type is currently just "Count" which is meant to evaluate the number of sessions.
    # Planning to add functionality for "Duration" which shall then evaluate the total time of relevant sessions.
    # Label allows to provide a name that can be printed on the dashboard
    period_goals_df = pd.DataFrame(
        columns=['Start date', 'End date', 'Label', 'Identifier level', 'Identifier', 'Condition type', 'Quantity']
    )

    """
    Weekly goals here
    """
    start = pd.Timestamp('2025-01-06')  # We start at the first monday of the year
    stop = pd.Timestamp('2025-01-12')

    # stop will be updated every iteration of the while loop until it reaches the target
    while stop.year != 2026:

        # Do things here

        period_goals_df.loc[period_goals_df.shape[0]] = {'Start date': start,
                                                         'End date': stop,
                                                         'Label': 'Reading',
                                                         'Identifier level': 2,
                                                         'Identifier': 'Reading',
                                                         'Condition type': 'Count',
                                                         'Quantity': 2}  # LinedIn/Finn advert review

        start = start + pd.Timedelta(days=7)
        stop = stop + pd.Timedelta(days=7)


    """
    Two-weekly goals here
    """
    start = pd.Timestamp('2025-01-06')
    stop = pd.Timestamp('2025-01-19')

    while stop.year != 2026:

        # Do things here
        period_goals_df.loc[period_goals_df.shape[0]] = {'Start date': start,
                                                         'End date': stop,
                                                         'Label': 'Climbing',
                                                         'Identifier level': 2,
                                                         'Identifier': 'Climbing',
                                                         'Condition type': 'Count',
                                                         'Quantity': 2}

        period_goals_df.loc[period_goals_df.shape[0]] = {'Start date': start,
                                                         'End date': stop,
                                                         'Label': 'Running',
                                                         'Identifier level': 2,
                                                         'Identifier': 'Running',
                                                         'Condition type': 'Count',
                                                         'Quantity': 1}

        period_goals_df.loc[period_goals_df.shape[0]] = {'Start date': start,
                                                         'End date': stop,
                                                         'Label': 'Strength',
                                                         'Identifier level': 2,
                                                         'Identifier': 'Strength',
                                                         'Condition type': 'Count',
                                                         'Quantity': 1}

        period_goals_df.loc[period_goals_df.shape[0]] = {'Start date': start,
                                                         'End date': stop,
                                                         'Label': 'Technical skills',
                                                         'Identifier level': 2,
                                                         'Identifier': 'Technical skills',
                                                         'Condition type': 'Count',
                                                         'Quantity': 1}

        period_goals_df.loc[period_goals_df.shape[0]] = {'Start date': start,
                                                         'End date': stop,
                                                         'Label': 'Languages',
                                                         'Identifier level': 2,
                                                         'Identifier': 'Languages',
                                                         'Condition type': 'Count',
                                                         'Quantity': 1}

        start = start + pd.Timedelta(days=14)
        stop = stop + pd.Timedelta(days=14)

    """
       Two-weekly goals here
       """
    start = pd.Timestamp('2025-01-06')
    stop = pd.Timestamp('2025-01-26')

    while stop.year != 2026:
        # Do things here

        period_goals_df.loc[period_goals_df.shape[0]] = {'Start date': start,
                                                         'End date': stop,
                                                         'Label': 'Lead climbing',
                                                         'Identifier level': 3,
                                                         'Identifier': 'Lead climbing',
                                                         'Condition type': 'Count',
                                                         'Quantity': 1}

        period_goals_df.loc[period_goals_df.shape[0]] = {'Start date': start,
                                                         'End date': stop,
                                                         'Label': 'Intervals',
                                                         'Identifier level': 3,
                                                         'Identifier': 'Intervals',
                                                         'Condition type': 'Count',
                                                         'Quantity': 1}

        start = start + pd.Timedelta(days=21)
        stop = stop + pd.Timedelta(days=21)

    """
    Monthly goals here
    """
    start = pd.Timestamp('2025-01-01')
    stop = start + pd.tseries.offsets.MonthEnd(0)

    while stop.year != 2026:

        # Do things here

        period_goals_df.loc[period_goals_df.shape[0]] = {'Start date': start,
                                                         'End date': stop,
                                                         'Label': 'Bench',
                                                         'Identifier level': 3,
                                                         'Identifier': 'Bench press',
                                                         'Condition type': 'Count',
                                                         'Quantity': 1}

        period_goals_df.loc[period_goals_df.shape[0]] = {'Start date': start,
                                                         'End date': stop,
                                                         'Label': 'Squats',
                                                         'Identifier level': 3,
                                                         'Identifier': 'Squats',
                                                         'Condition type': 'Count',
                                                         'Quantity': 1}

        period_goals_df.loc[period_goals_df.shape[0]] = {'Start date': start,
                                                         'End date': stop,
                                                         'Label': 'Deadlifts',
                                                         'Identifier level': 3,
                                                         'Identifier': 'Deadlifts',
                                                         'Condition type': 'Count',
                                                         'Quantity': 1}

        # Need some extra logic to account for months with 28/29/30/31 days
        start = stop + pd.Timedelta(days=1)
        stop = start + pd.tseries.offsets.MonthEnd(0)

    print(period_goals_df)

    period_goals_df.to_csv('Period_goals.csv')

