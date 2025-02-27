from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.colors import DEFAULT_PLOTLY_COLORS
import datetime as dt
import pandas as pd
import ast

# Initialising the dash app, with the SLATE theme to get a nice dark mode layout
app = Dash(external_stylesheets=[dbc.themes.SLATE])

# Layout for the dash app
app.layout = dbc.Container(children=[
    # Title
    html.H1(children='My Productivity Dashboard', style={'textAlign': 'center', 'margin': '3vh'}),
    # First main row, one block for logging activities, one block for viewing activity log and a final block for
    # viewing period goals
    dbc.Row(children=[dbc.Col(children=[html.H2('Log new activity',
                                                className="d-flex justify-content-center align-items-center"),
                                        dbc.Row(children=[dbc.Col('Session date'),
                                                          dbc.Col(children=dcc.DatePickerSingle(display_format='DD/MM/YYYY',
                                                                                                id='Session-calendar'))]),
                                        dbc.Row(children=[dbc.Col('Activity type'),
                                                          dbc.Col(dbc.Select(id='Activity-type-select',
                                                                             options=[
                                                                                 {'label': 'Exercise', 'value': 'Exercise'},
                                                                                 {'label': 'Self-development', 'value':'Technical'},
                                                                                 {'label': 'Culture', 'value': 'Culture'}],
                                                                             # Setting the start value to Exercise
                                                                             value='Exercise',
                                                                             size='sm'))]),
                                        dbc.Row(children=[dbc.Col('Activity subtype'),
                                                          # The subactivity options will be set in a callback
                                                          dbc.Col(dbc.Select(id='Subactivity-type-select',
                                                                             size='sm'))]),
                                        # The highlights will also be set in a callback
                                        dbc.Row(children=[dbc.Checklist(id='Activity-highlights')]),
                                        dbc.Row(dbc.Col(dbc.Textarea(placeholder='Session notes here...',
                                                                     id='Session-notes'),
                                                        #style={'height': '15vh'}
                                                        )
                                                ),
                                        dbc.Row(children=dbc.Col(dbc.Button('Save session',
                                                                            id='Session-save-button'),
                                                                 className="d-grid"))
                                        ],
                              width=4,
                              ),
                      # Block for visualising the logged activities
                      dbc.Col(children=[html.H2('My log')],
                              id='Log-col',
                              width=4,
                              style={'height': '100%',
                                     'overflow-y': 'auto'}),
                      # Block for viewing active, past and future periodic goals
                      dbc.Col(children=[html.H2('My goals', className="d-flex justify-content-center align-items-center"),
                                        dbc.Row(children=[dbc.Col(children=[dbc.RadioItems(options=[
                                            {"label": "Past", "value": 'past'},
                                            {"label": "Active", "value": 'active'},
                                            {"label": "Future", "value": 'future'}],
                                            id="goal-period-selector",
                                            className="btn-group",
                                            inputClassName="btn-check",
                                            labelClassName="btn btn-outline-primary",
                                            labelCheckedClassName="active",
                                            style={"width": "100%"},  # Full width for container
                                            labelStyle={'width': '100%'},
                                            value='active')],
                                            className='radioGroupCol')]),
                                        dbc.Row(children=[dbc.Col('Target activity', style={"font-weight": "bold"}),
                                                          dbc.Col('Start date', style={"font-weight": "bold"}),
                                                          dbc.Col('End date', style={"font-weight": "bold"}),
                                                          dbc.Col('Progress', style={"font-weight": "bold"})]),
                                        dbc.Row(dbc.Col(id='goals-log'))],
                              id='Active-goals-col',
                              style={'height': '100%',
                                     'overflow-y': 'auto'}),
                      # Dummy col used to initiate callback chains when saving a new session
                      dbc.Col(id='Temp-log-initiator',
                              style={'display': 'none'},
                              width=0)],
            style={'height': '45vh'}
            ),
    # Dropwdown menu for selecting labels for the visualisations. Number in the value is to indiciate the "level" at
    # which the label is (activity, subacitivity, etc - 0 for grand total)
    dbc.Row(children=[dbc.Col(dcc.Dropdown([{'label': 'Total', 'value': 'Total0'},
                                            {'label': 'Exercise', 'value': 'Exercise1'},
                                            {'label': 'Self-development', 'value': 'Technical1'},
                                            {'label': 'Culture', 'value': 'Culture1'},
                                            {'label': 'Climbing', 'value': 'Climbing2'},
                                            {'label': 'Running', 'value': 'Running2'},
                                            {'label': 'Strength', 'value': 'Strength2'},
                                            {'label': 'Cross-country skiing', 'value': 'Cross-country skiing2'},
                                            {'label': 'Cycling', 'value': 'Cycling2'},
                                            {'label': 'Technical skills', 'value': 'Technical skills2'},
                                            {'label': 'Reading', 'value': 'Reading2'},
                                            {'label': 'Languages', 'value': 'Languages2'}],
                                           ['Climbing2', 'Running2', 'Strength2'],
                                           multi=True,
                                           id='timeseries-selection-dropdown'))],
            style={'margin-top': '5vh'}),
    dbc.Row(children=[dbc.Col(children=[dcc.Graph(id='timeseries-graph')], width=6),
                      dbc.Col(children=[dcc.Graph(id='goal-reaching-graph')], width=6)],
            id='graph-row',
            style={'height': '35vh', 'padding': '0', 'margin': '0', 'margin-bottom': '15vh'}
            ),
    dcc.Location(id='date-picker-updater', refresh=False)
], fluid=True
)

@app.callback(Output('Session-calendar', 'date'),
              Input('date-picker-updater', 'pathname'))
def update_calendar_date(_):
    return dt.date.today()

@app.callback(
    Output('goal-reaching-graph', 'figure'),
    Input('Log-col', 'children'), Input('timeseries-selection-dropdown', 'value')
)
def plot_goals_graph(_, selection):
    """
    Callback function for updating the figure visualising the satisfaction of periodic goals.  Using the log col as
    an input means that this will be updated everytime a new activity is logged

    """
    # Start by reading in data files
    my_goals_df = pd.read_csv('Period_goals.csv', index_col=0)
    my_sessions_df = pd.read_csv('Session_log.csv', index_col=0)

    # Convert time columns to datetime objects
    my_goals_df['Start date'] = pd.to_datetime(my_goals_df['Start date'])
    my_goals_df['End date'] = pd.to_datetime(my_goals_df['End date'])

    # Create a new column "Satisfied" initiated to False that will be updated to indicate whether a particular goals
    # was satisfied
    my_goals_df['Satisfied'] = False
    my_goals_df['Satisfied'] = my_goals_df['Satisfied'].astype(bool)

    my_sessions_df['Date'] = pd.to_datetime(my_sessions_df['Date'])
    # The keywords were populated as a list, when reading in the CSV file again we have to translate a list-like string
    # back to an actual list
    my_sessions_df['Keywords'] = my_sessions_df['Keywords'].apply(
        lambda x: ast.literal_eval(x) if pd.notnull(x) else [])

    my_sessions_df.sort_values('Date', ascending=False, inplace=True)

    date_list = pd.date_range(start='2025-01-01', end=pd.Timestamp.today())
    categories = selection # selection is list of values from the dropdown menu

    counter_lists = {}

    # We loop through all the goals in the dataframe, and evaluate the ones where the end date has already passed
    # Condition type so far only allows 'Count', so we then check the sessions dataframe to see if the target quantity
    # of sessions has been logged within the specified date range. The "Satisfied" column for the goal is then
    # updated
    for index, row in my_goals_df.iterrows():
        if pd.Timestamp.today().normalize() >= row['End date']:
            if row['Condition type'] == 'Count':
                if row['Identifier level'] == 0:
                    pass
                elif row['Identifier level'] == 1:
                    relevant_df = my_sessions_df.loc[((my_sessions_df['Date'] >= row['Start date']) &
                                                     (my_sessions_df['Date'] <= row['End date']) &
                                                     (my_sessions_df['Activity group'] == row['Identifier']))]

                    active_count = relevant_df.shape[0]
                    target = row['Quantity']
                    if active_count >= target:
                        my_goals_df.at[index, 'Satisfied'] = True
                elif row['Identifier level'] == 2:
                    relevant_df = my_sessions_df.loc[((my_sessions_df['Date'] >= row['Start date']) &
                                                     (my_sessions_df['Date'] <= row['End date']) &
                                                     (my_sessions_df['Activity name'] == row['Identifier']))]

                    active_count = relevant_df.shape[0]
                    target = row['Quantity']
                    if active_count >= target:
                        my_goals_df.at[index, 'Satisfied'] = True
                elif row['Identifier level'] == 3:
                    # For the highlights, since these are lists we use DataFrame.apply() with a lambda function to see
                    # if the specific identifier is in this list
                    relevant_df = my_sessions_df.loc[((my_sessions_df['Date'] >= row['Start date']) &
                                                     (my_sessions_df['Date'] <= row['End date']) &
                                                     (my_sessions_df['Keywords'].apply(
                                                         lambda x: row['Identifier'] in x if isinstance(x,
                                                                                                        list) else False)))]

                    active_count = relevant_df.shape[0]
                    target = row['Quantity']
                    if active_count >= target:
                        my_goals_df.at[index, 'Satisfied'] = True
        #print(my_goals_df.iloc[index])

    # For plotting cumulative fractions of completed goals we then count satisfied and not satisfied goals. Slightly
    # different logic is needed for categories at different levels (0 being grand total, 1 being activity, 2 being
    # sub-activity, etc.)
    for category in categories:
        if category[-1] == '0':
            counter_lists[category[:-1]] = [my_goals_df.loc[my_goals_df['End date'] <= date].shape[0] for date in date_list]
            counter_lists[category[:-1] + ' - satisfied'] = [my_goals_df.loc[((my_goals_df['End date'] <= date) &
                                                                              (my_goals_df['Satisfied']))].shape[0] for date in date_list]
            counter_lists[category[:-1] + ' - not satisfied'] = [my_goals_df.loc[((my_goals_df['End date'] <= date) &
                                                                                  (~my_goals_df['Satisfied']))].shape[0] for date in date_list]

        elif category[-1] == '1':
            counter_lists[category[:-1]] = [my_goals_df.loc[((my_goals_df['End date'] <= date) &
                                                             my_goals_df['Identifier'] == category[:-1])].shape[0]
                                            for date in date_list]
            counter_lists[category[:-1] + ' - satisfied'] = [
                my_goals_df.loc[((my_goals_df['End date'] <= date) &
                                 (my_goals_df['Satisfied']) &
                                 (my_goals_df['Identifier'] == category[:-1]))].shape[0] for date in date_list]
            counter_lists[category[:-1] + ' - not satisfied'] = [
                my_goals_df.loc[((my_goals_df['End date'] <= date) &
                                 (~my_goals_df['Satisfied']) &
                                 (my_goals_df['Identifier'] == category[:-1]))].shape[0] for date in date_list]
        elif category[-1] == '2':
            counter_lists[category[:-1]] = [my_goals_df.loc[((my_goals_df['End date'] <= date) &
                                                             (my_goals_df['Identifier'] == category[:-1]))].shape[0]
                                            for date in date_list]
            counter_lists[category[:-1] + ' - satisfied'] = [
                my_goals_df.loc[((my_goals_df['End date'] <= date) &
                                 (my_goals_df['Satisfied']) &
                                 (my_goals_df['Identifier'] == category[:-1]))].shape[0] for date in date_list]
            counter_lists[category[:-1] + ' - not satisfied'] = [
                my_goals_df.loc[((my_goals_df['End date'] <= date) &
                                 (~my_goals_df['Satisfied']) &
                                 (my_goals_df['Identifier'] == category[:-1]))].shape[0] for date in date_list]

    # We now return the figure
    figure_to_return = go.Figure()

    for category in categories:
        counter_lists[category[:-1] + ' - fraction'] = [1.0 if target == 0 else done / target for done, target in
                                                        zip(counter_lists[category[:-1] + ' - satisfied'],
                                                            counter_lists[category[:-1]])]
        figure_to_return.add_trace(
            go.Scatter(y=counter_lists[category[:-1] + ' - fraction'], x=date_list, name=category[:-1]))
        #figure_to_return.add_trace(go.Scatter(y=counter_lists[category[:-1]], x=date_list, name=category[:-1] + ' - target'))
        #figure_to_return.add_trace(go.Scatter(y=counter_lists[category[:-1] + ' - satisfied'], x=date_list, name=category[:-1] + ' - satisfied'))
        #figure_to_return.add_trace(go.Scatter(y=counter_lists[category[:-1] + ' - not satisfied'], x=date_list, name=category[:-1] + ' - not satisfied'))

    figure_to_return.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),  # Left, Right, Top, Bottom
        xaxis_title="Date",
        yaxis_title="Goal count",
        # plot_bgcolor="#343a40",  # Dark background
        paper_bgcolor="#272b30",
        font=dict(color="#f8f9fa"),
        yaxis_range=[-0.1, 1.1],
        legend=dict(
            x=0.05,  # Horizontal position (0: left, 1: right)
            y=0.95,  # Vertical position (0: bottom, 1: top)
            xanchor='left',  # Align legend box's right side at x
            yanchor='top',  # Align legend box's top side at y
            bgcolor='#343a40',  # Optional: Semi-transparent white background
        )
    )

    return figure_to_return

@app.callback(Output('goals-log', 'children'),
              Input('Log-col', 'children'), Input('goal-period-selector', 'value'))
def goal_log_update(_, period):
    """
    Function to update the log of goals, especially in case new activities are logged or if the user switches between
    past, active and future goals

    """
    list_to_return = []

    my_goals_df = pd.read_csv('Period_goals.csv', index_col=0)
    my_session_df = pd.read_csv('Session_log.csv', index_col=0)

    my_goals_df['Start date'] = pd.to_datetime(my_goals_df['Start date'])
    my_goals_df['End date'] = pd.to_datetime(my_goals_df['End date'])

    my_session_df['Date'] = pd.to_datetime(my_session_df['Date'])

    my_session_df['Keywords'] = my_session_df['Keywords'].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])

    today = pd.Timestamp.today().normalize()

    # We want to save dbc.Row() elements with the identifier name (maybe this should be a separate label actually),
    # the date range and an indication of goal progress. Typically this is something like #achieved / #target
    for index, row in my_goals_df.sort_values('End date').iterrows():
        if ((period == 'active' and row['Start date'] <= today <= row['End date']) or
                (period == 'past' and today >= row['End date']) or
                (period == 'future' and today <= row['Start date'])):
            if row['Condition type'] == 'Count':
                if row['Identifier level'] == 0:
                    pass
                elif row['Identifier level'] == 1:
                    relevant_df = my_session_df.loc[((my_session_df['Date'] >= row['Start date']) &
                                                     (my_session_df['Date'] <= row['End date']) &
                                                     (my_session_df['Activity group'] == row['Identifier']))]

                    active_count = relevant_df.shape[0]
                    target = row['Quantity']
                    this_row = dbc.Row(children=[dbc.Col(row['Identifier']),
                                                 dbc.Col(row['Start date'].strftime('%d-%m-%Y')),
                                                 dbc.Col(row['End date'].strftime('%d-%m-%Y')),
                                                 dbc.Col(str(active_count) + ' / ' + str(target))])
                elif row['Identifier level'] == 2:
                    relevant_df = my_session_df.loc[((my_session_df['Date'] >= row['Start date']) &
                                                     (my_session_df['Date'] <= row['End date']) &
                                                     (my_session_df['Activity name'] == row['Identifier']))]

                    active_count = relevant_df.shape[0]
                    target = row['Quantity']
                    this_row = dbc.Row(children=[dbc.Col(row['Identifier']),
                                                 dbc.Col(row['Start date'].strftime('%d-%m-%Y')),
                                                 dbc.Col(row['End date'].strftime('%d-%m-%Y')),
                                                 dbc.Col(str(active_count) + ' / ' + str(target))])
                elif row['Identifier level'] == 3:
                    relevant_df = my_session_df.loc[((my_session_df['Date'] >= row['Start date']) &
                                                     (my_session_df['Date'] <= row['End date']) &
                                                     (my_session_df['Keywords'].apply(lambda x: row['Identifier'] in x if isinstance(x, list) else False)))]

                    active_count = relevant_df.shape[0]
                    target = row['Quantity']
                    this_row = dbc.Row(children=[dbc.Col(row['Identifier']),
                                                 dbc.Col(row['Start date'].strftime('%d-%m-%Y')),
                                                 dbc.Col(row['End date'].strftime('%d-%m-%Y')),
                                                 dbc.Col(str(active_count) + ' / ' + str(target))])
            list_to_return.append(this_row)

    return list_to_return

@app.callback(Output('timeseries-graph', 'figure'),
              Input('Log-col', 'children'), Input('timeseries-selection-dropdown', 'value'))
def update_timeseries_graph(_, selection):
    """
    Callback function to update the logged activity timeseries. This is to indicate how well we are doing in terms of
    reaching highlevel (yearly) goals in terms of number of sessions

    """

    my_sessions_df = pd.read_csv('Session_log.csv', index_col=0)

    my_sessions_df.sort_values('Date', ascending=False, inplace=True)

    date_list = pd.date_range(start='2025-01-01', end=pd.Timestamp.today())

    counter_lists = {}
    figure_to_return = go.Figure()
    # We don't want the colors to change whenever we add or remove a label from the dropdown so we hardcode the
    # desired color codes here
    free_colors = ['#636efa', '#EF553B', '#00cc96', '#ab63fa', '#FFA15A', '#19d3f3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52'] #DEFAULT_PLOTLY_COLORS
    my_color_map = {}

    for selected in selection:
        if selected[-1] == '0':
            counter_lists[selected] = [my_sessions_df.loc[pd.to_datetime(my_sessions_df['Date']) <= date].shape[0] for date in date_list]
        elif selected[-1] == '1':
            counter_lists[selected] = [my_sessions_df.loc[(my_sessions_df['Activity group'] == selected[:-1]) &
                                                          (pd.to_datetime(my_sessions_df['Date']) <= date)].shape[0] for
                                       date in date_list]
        else:
            counter_lists[selected] = [my_sessions_df.loc[(my_sessions_df['Activity name'] == selected[:-1]) &
                                                          (pd.to_datetime(my_sessions_df['Date']) <= date)].shape[0] for
                                       date in date_list]

        my_color_map[selected] = free_colors.pop(0)
        if len(free_colors) == 0:
            free_colors = ['#636efa', '#EF553B', '#00cc96', '#ab63fa', '#FFA15A', '#19d3f3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']

        figure_to_return.add_trace(go.Scatter(y=counter_lists[selected], x=date_list, name=selected[:-1],
                                              line=dict(color=my_color_map[selected])))

    # Want to define this elsewhere in the long term, but a quick way to add yearly goals for number of session
    # We can then plot an indication of how progress should be throughout the year
    climbing_session_goal = 85
    running_session_goal = 60
    strength_session_goal = 60

    goal_date = pd.Timestamp.today()
    full_date_list = pd.date_range(start='2025-01-01', end=goal_date)
    climbing_goal_list = [climbing_session_goal * (i / 365) for i in range(len(full_date_list))]
    running_goal_list = [running_session_goal * (i / 365) for i in range(len(full_date_list))]
    strength_goal_list = [strength_session_goal * (i / 365) for i in range(len(full_date_list))]

    # We only want to plot the progress indicator if the activity has been selected in the dropdown, i.e. if it is
    # in the my_color_map dict. Then we also want to make sure we are plotting it in the same color (but dashed)
    if 'Climbing2' in my_color_map:
        figure_to_return.add_trace(go.Scatter(y=climbing_goal_list, x=full_date_list, mode='lines', showlegend=False,
                                              line={'dash': 'dash', 'color': my_color_map['Climbing2']},
                                              name='Climbing target'))
    if 'Running2' in my_color_map:
        figure_to_return.add_trace(go.Scatter(y=running_goal_list, x=full_date_list, mode='lines', showlegend=False,
                                              line={'dash': 'dash', 'color': my_color_map['Running2']},
                                              name='Running target'))
    if 'Strength2' in my_color_map:
        figure_to_return.add_trace(go.Scatter(y=strength_goal_list, x=full_date_list, mode='lines', showlegend=False,
                                              line={'dash': 'dash', 'color': my_color_map['Strength2']},
                                              name='Strength target'))

    figure_to_return.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),  # Left, Right, Top, Bottom
        xaxis_title="Date",
        yaxis_title="Session count",
        #plot_bgcolor="#343a40",  # Dark background
        paper_bgcolor="#272b30",
        font=dict(color="#f8f9fa"),
        legend=dict(
            x=0.05,  # Horizontal position (0: left, 1: right)
            y=0.95,  # Vertical position (0: bottom, 1: top)
            xanchor='left',  # Align legend box's right side at x
            yanchor='top',  # Align legend box's top side at y
            bgcolor='#343a40',  # Optional: Semi-transparent white background
        )
    )

    return figure_to_return

@app.callback(Output('Log-col', 'children'),
              Input('Temp-log-initiator', 'children'))
def update_log(_):
    """
    Function to update the activity log column upon updating of the dummy col. This should happen at the initial
    opening of the dashboard, reloads and whenever an activity is saved

    """
    # The headers of the column
    to_return = [html.H2('My log',
                         className="d-flex justify-content-center align-items-center"),
                 dbc.Row(children=[dbc.Col('Activity', style={"font-weight": "bold"}),
                                   dbc.Col('Activity group', style={"font-weight": "bold"}),
                                   dbc.Col('Date', style={"font-weight": "bold"})])]

    my_sessions_df = pd.read_csv('Session_log.csv', index_col=0)

    my_sessions_df.sort_values('Date', ascending=False, inplace=True)

    # Gradually build the content from the data file
    for index, row in my_sessions_df.iterrows():
        this_row = dbc.Row(children=[dbc.Col(row['Activity name']),
                                     dbc.Col(row['Activity group']),
                                     dbc.Col(dt.datetime.strptime(row['Date'], '%Y-%m-%d').strftime('%d-%m-%Y'))])

        to_return.append(this_row)

    return to_return

@app.callback(Output('Temp-log-initiator', 'children'),
              Input('Session-save-button', 'n_clicks'),
              State('Session-calendar', 'date'),
              State('Activity-type-select', 'value'),
              State('Subactivity-type-select', 'value'),
              State('Activity-highlights', 'value'),
              State('Session-notes', 'value'),
              prevent_initial_call=True)
def save_session(_, date, activity_type, subactivity_type, highlights, notes):
    """
    Function to save a session to data file. The input is the button, but the callback also needs access to the
    states of a number of input fields. It then updates a dummy col to intiate a callback chain

    """
    session_log_df = pd.read_csv('Session_log.csv', index_col=0)

    # We want to pick the lowest positive id number which is available
    new_session_id = 1

    while new_session_id in session_log_df.index:
        new_session_id += 1

    session_log_df.loc[new_session_id] = {'Date': date,
                                          'Activity group': activity_type,
                                          'Activity name': subactivity_type,
                                          'Keywords': highlights,
                                          'Notes': notes,
                                          'Duration': ''}

    session_log_df.to_csv('Session_log.csv')

    return 'Update'

@app.callback(Output('Subactivity-type-select', 'options'),
              Output('Subactivity-type-select', 'value'),
              Input('Activity-type-select', 'value'))
def set_subactivities(selected_activity):
    """
    Callback function to specify subactivity selection based on the selected activity

    """

    subactivity_dict = {}
    selected_value = None
    # Define the subactivity for each activity group. Remember to specify the desired selected value. Also note that
    # ordering here defines the ordering in the app
    if selected_activity == 'Exercise':
        subactivity_dict['Climbing'] = 'Climbing'
        subactivity_dict['Running'] = 'Running'
        subactivity_dict['Strength'] = 'Strength'
        subactivity_dict['Cross-country skiing'] = 'Cross-country skiing'
        subactivity_dict['Cycling'] = 'Cycling'
        selected_value = 'Climbing'
    elif selected_activity == 'Technical':
        subactivity_dict['Technical skills'] = 'Technical skills'
        selected_value = 'Technical skills'
    elif selected_activity == 'Culture':
        subactivity_dict['Reading'] = 'Reading'
        subactivity_dict['Languages'] = 'Languages'

        selected_value = 'Reading'

    return subactivity_dict, selected_value

@app.callback(Output('Activity-highlights', 'options'),
              Input('Subactivity-type-select', 'value'))
def set_activity_highlights(selected_subactivity):
    """
    Certain (sub-)activities might have desired keywords or highlights. These can be defined here.

    """
    highlights = {}

    if selected_subactivity == 'Climbing':
        highlights['Lead climbing'] = 'Lead climbing'
        highlights['Toprope climbing'] = 'Toprope climbing'
        highlights['Bouldering'] = 'Bouldering'
    elif selected_subactivity == 'Running':
        highlights['Base'] = 'Base'
        highlights['Tempo'] = 'Tempo'
        highlights['Intervals'] = 'Intervals'
    elif selected_subactivity == 'Strength':
        highlights['Bench press'] = 'Bench press'
        highlights['Deadlifts'] = 'Deadlifts'
        highlights['Squats'] = 'Squats'
    elif selected_subactivity == 'Cross-country skiing':
        highlights['Classic'] = 'Classic'
        highlights['Skate'] = 'Skate'
    elif selected_subactivity == 'Cycling':
        pass
    elif selected_subactivity == 'Technical skills':
        highlights['Personal projects'] = 'Personal projects'
        highlights['Technical books'] = 'Technical books'
        highlights['Courses'] = 'Courses'
    elif selected_subactivity == 'Reading':
        highlights['Fiction'] = 'Fiction'
        highlights['Non-fiction'] = 'Non-fiction'
    elif selected_subactivity == 'Languages':
        pass

    return highlights

if __name__ == '__main__':
    app.run(debug=True)