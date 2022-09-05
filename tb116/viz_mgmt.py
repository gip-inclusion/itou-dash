import plotly.express as px
from dash import dash_table
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def pie_plot(labels, counts, center, title):
    # Create subplots: use 'domain' type for Pie subplot
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
    fig.add_trace(go.Pie(labels=labels, values=counts, name=title),
                  1, 1)

    # Use `hole` to create a donut-like pie chart
    fig.update_traces(hole=.6, hoverinfo="label+percent+name")

    fig.update_layout(
        title_text="Motifs de refus des candidatures provenant des orienteurs et prescripteurs",
        # Add annotations in the center of the donut pies.
        annotations=[dict(text=str(center), x=0.13, y=0.5, font_size=10, showarrow=False)])
    #fig.show()

    return fig

def multiple_bar_plot(groupby_df, x_col, y_col, color_col, filter):
    # création fig pyplot
    fig = px.bar(groupby_df, x=x_col, y=y_col, color=color_col)

    fig.update_xaxes(categoryorder='array', categoryarray= filter)
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)

    return fig


def generate_table(df, table_cols):
    """
        doc : https://dash.plotly.com/datatable/style
    """
    df = df.reset_index()
    return dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=table_cols,#[{'id': c, 'name': c} for c in df.columns],

                    style_data={
                        'color': 'black',
                        'backgroundColor': 'white'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(220, 220, 220)',
                        }
                    ],
                    style_header={
                        'backgroundColor': 'rgb(210, 210, 210)',
                        'color': 'black',
                        'fontWeight': 'bold'
                    },
                    id='tbl_candidate_profile'
                )
