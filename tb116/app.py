from pathlib import Path

from dash import Dash, html, dcc, Input, Output
from data_mgmt import *
from viz_mgmt import *

from config import DATA_PATH

app = Dash(__name__)

# how many months to keep
n_months = 12
# calculate n previous months
prev_months = get_n_prev_months(12)
# convert datetime to string for filtering candidatures_12_prev_months
prev_months_filter = [str(y)+"-"+str(x) for (x, y) in prev_months]

# init dataframe with all data

candidatures_echelle_locale_csv_path = DATA_PATH / "candidatures_echelle_locale_light.csv"
candidats_csv_path = DATA_PATH / "candidats_light.csv"

candidatures_df = load_candidatures_echelle_locale(candidatures_echelle_locale_csv_path)
candidats_df = load_candidats(candidats_csv_path)

# prepare candidate profile table
candidate_profile, table_cols = prepare_candidate_profile_per_date(candidats_df, prev_months_filter)


# filter only 12 previous months
candidatures_12_prev_months = candidatures_df[candidatures_df["date_candidature_mensuelle"].isin(prev_months_filter)]
accepted_df = candidatures_df[candidatures_df.état == "Candidature acceptée"]
declined_df = candidatures_df[candidatures_df.état == "Candidature déclinée"]
notaccepted = candidatures_df[candidatures_df["état"] != "Candidature acceptée"]

# calculate groupby for candidatures
accepted_by_employer = groupby_count(candidatures_df, ['type_structure', 'date_candidature_mensuelle'], "id_anonymisé")
accepted_by_employer = accepted_by_employer[accepted_by_employer["date_candidature_mensuelle"].isin(prev_months_filter)]
accepted_by_employer = accepted_by_employer[accepted_by_employer["type_structure"].isin(["ACI", "AI", "EI", "EITI", "ETTI"])]
accepted_by_employer.sort_values(by="date_candidature_mensuelle")


accepted_by_orienteur = groupby_count(candidatures_df, ['origine', 'date_candidature_mensuelle'], "id_anonymisé")
accepted_by_orienteur = accepted_by_orienteur[accepted_by_orienteur["date_candidature_mensuelle"].isin(prev_months_filter)]
accepted_by_orienteur.sort_values(by="date_candidature_mensuelle")


counts_df_état = groupby_count(candidatures_12_prev_months,
                          ['état', 'date_candidature_mensuelle'],
                          "id_anonymisé")
counts_df_état.sort_values(by="date_candidature_mensuelle")


counts_df_origine = groupby_count(candidatures_12_prev_months,
                          ['origine', 'date_candidature_mensuelle'],
                          "id_anonymisé")
counts_df_origine.sort_values(by="date_candidature_mensuelle")

refus_labels = list(set(notaccepted.motif_de_refus))
refus_counts = [len(notaccepted[notaccepted["motif_de_refus"] == l]) for l in refus_labels]
counts_pct_motif_refus = [round(c/sum(refus_counts)*100) for c in refus_counts]
total_refus = len(notaccepted)

# add all to init filter
depts = list(set(candidatures_df.nom_département_structure.dropna()))+["all"]
depts.sort()

employer = list(set(candidatures_df.type_structure.dropna()))+["all"]
employer.sort()

fig_counts_état = multiple_bar_plot(counts_df_état,
                        "date_candidature_mensuelle",
                        "count",
                        "état",
                        prev_months_filter)

fig_counts_origine = multiple_bar_plot(counts_df_origine,
                        "date_candidature_mensuelle",
                        "count",
                        "origine",
                        prev_months_filter)

fig_counts_employer = multiple_bar_plot(accepted_by_employer,
                        "date_candidature_mensuelle",
                        "count",
                        "type_structure",
                        prev_months_filter)

fig_counts_orienteur = multiple_bar_plot(accepted_by_orienteur,
                        "date_candidature_mensuelle",
                        "count",
                        "origine",
                        prev_months_filter)

fig_pie = pie_plot(refus_labels,
                    counts_pct_motif_refus,
                    total_refus,
                    "Motifs de refus des candidatures provenant des orienteurs et prescripteurs")

app.layout = html.Div(children=[
    html.H1(children='''TB116 - Suivi et analyse des candidatures (Recrutement)'''),

    dcc.Dropdown(options=depts,
                 value="all",
                 id="deptsfilter"),

 dcc.Dropdown(options=employer,
              value="all",
              id="employerfilter"),

    html.Div(id="deptsoutput"),

    html.H2(children=
        '''🚀 Nouveauté '''
        ),
    html.Div([
        html.P('''Il est désormais possible de filtrer les résultats à l'échelle locale des EPCI et bassin d'emploi'''),
        html.P('''[enfin, l'implémentation des filtres arrive soon sur cette version Dash 💃🏽 ]''')
        ]),

    html.H2(children=
    '''
     ☝️ Rappels
    '''),

    html.Div([
        html.P('''lorsqu'aucune précision temporelle est apportée, les chiffres présentés correspondent aux données agrégées par la plateforme de l'inclusion depuis sa création (début 2020). Afin de retrouver, par exemple, l'état des candidatures par métier sur les 12 derniers mois, il vous suffit de filtrer sur les 12 derniers mois à l'aide du filtre "intervalle de dates"'''),
        html.P('''une candidature est l'acte de candidature à un poste proposé par un employeur, par un candidat, directement ou avec l’aide d’un orienteur ou d’un prescripteur​'''),
        html.P('''un candidat est une personne qui postule, directement ou avec l’aide d’un orienteur ou d’un prescripteur, à un poste auprès d’un employeur''')
    ]),

    html.H2(children=
    '''
     Indicateurs clés
    ''', style={"align": "center"}),

    html.Div([
        html.P('''Ci dessous vous retrouvez des chiffres clés associés à ce tableau de bord, calculés à l'aide des données obtenues depuis la création de la plateforme de l'inclusion. Afin d'affiner votre recherche sur une période spécifique des filtres (filtre temporel et par intervalles de dates) sont à votre disposition''')
    ]),

    html.Table(
        [
            html.Tr([
                html.Th(id="nb_total_candidatures",
                        style={"font-size":"160%"}),
                html.Th(id="pct_accepted",
                        style={"font-size":"160%"}),
                html.Th(id="pct_delined",
                        style={"font-size":"160%"})
            ]),
            html.Tr([
                html.Td('''de candidatures émises''',
                        style={"textAlign":"center"}),
                html.Td('''de candidatures acceptées''',
                        style={"textAlign":"center"}),
                html.Td('''de candidatures déclinées''',
                        style={"textAlign":"center"})
            ])
        ]
        ,
        style={"align": "center",
               "width": "100%"}
    ),

    html.H2(children='''
        1. Comment évoluent les candidatures reçues sur les 12 derniers mois ?
    '''),
    html.Div([
        html.P('''- par état'''),
        html.P('''- par origine''')
    ]),
    html.H3(children='''Evolution des candidatures sur les 12 derniers mois, par état'''),
    dcc.Graph(
        id='fig_counts_état',
        figure=fig_counts_état
    ),
    html.H3(children='''Evolution des candidatures sur les 12 derniers mois, par origine'''),
    dcc.Graph(
        id='fig_counts_origine',
        figure=fig_counts_origine
    ),

    html.H2(children='''
        2. Comment se répartissent les candidatures acceptées sur les 12 derniers mois ?
    '''),
    html.Div([
        html.P('''- par type d'employeur'''),
        html.P('''- par type d'orienteur''')
    ]),
    html.H3(children='''Evolution des candidatures acceptées sur les 12 derniers mois, par type d'employeur'''),
    dcc.Graph(
        id='fig_counts_employer',
        figure=fig_counts_employer
    ),
    html.H3(children='''Evolution des candidatures acceptées sur les 12 derniers mois, par type d'orienteur'''),
    dcc.Graph(
        id='fig_counts_orienteur',
        figure=fig_counts_orienteur
    ),

    html.H2(children='''
        3. Quel est le profil des candidats acceptés sur les 12 derniers mois ?
    '''),
    generate_table(candidate_profile, table_cols),

    html.H2(children='''
        4. Quelle est la part de candidatures acceptées et refusées ?
    '''),
    html.Div([
        html.P('''- par métier'''),
        html.P('''- par domaine professionnel''')
    ]),

    html.H2(children='''
        5. Quel est le taux de candidature accepté selon le prescripteur ?
    '''),

    html.H2(children='''
        6. Quels sont les motifs de refus des candidatures provenant des prescripteurs et des orienteurs ?
    '''),
    dcc.Graph(
        id='fig_pie',
        figure=fig_pie
    ),
    html.H2(children='''
        7. Quel est le taux de refus par type de structure ?
    ''')

])

# CALLBACKS

# nbcandidatures / deptfilter
@app.callback(
    Output(component_id='nb_total_candidatures', component_property='children'),
    Input(component_id='deptsfilter', component_property='value')
)
def update_nb_candidatures(input_value):
    candidatures_12_prev_months = candidatures_df
    if input_value != "all":
        # récup colonnes d'intérêt
        candidatures_12_prev_months = candidatures_12_prev_months[candidatures_12_prev_months.nom_département_structure == input_value]
    nbtotalcandidatures = len(candidatures_12_prev_months)
    return nbtotalcandidatures

# pct_accepted / deptfilter
@app.callback(
    Output(component_id='pct_accepted', component_property='children'),
    Input(component_id='deptsfilter', component_property='value')
)
def update_pct_delined(input_value):
    candidatures_12_prev_months = accepted_df
    if input_value != "all":
        # récup colonnes d'intérêt
        candidatures_12_prev_months = candidatures_12_prev_months[candidatures_12_prev_months.nom_département_structure == input_value]
    nbtotalcandidatures = round(len(candidatures_12_prev_months)/len(candidatures_df)*100)
    return str(nbtotalcandidatures)+" %"

# pct_accepted / deptfilter
@app.callback(
    Output(component_id='pct_delined', component_property='children'),
    Input(component_id='deptsfilter', component_property='value')
)
def update_pct_accepted(input_value):
    candidatures_12_prev_months = declined_df
    if input_value != "all":
        # récup colonnes d'intérêt
        candidatures_12_prev_months = candidatures_12_prev_months[candidatures_12_prev_months.nom_département_structure == input_value]
    nbtotalcandidatures = round(len(candidatures_12_prev_months)/len(candidatures_df)*100)
    return str(nbtotalcandidatures)+" %"

# tb116-barplot / deptfilter
@app.callback(
    Output(component_id='fig_counts_état', component_property='figure'),
    Input(component_id='deptsfilter', component_property='value'),
    Input(component_id='employerfilter', component_property='value')
)
def update_output_div(deptsfilter, employerfilter):
    newdf = candidatures_12_prev_months
    if deptsfilter != "all":
        # récup colonnes d'intérêt
        newdf = newdf[newdf.nom_département_structure == deptsfilter]
    if employerfilter != "all":
        # récup colonnes d'intérêt
        newdf = newdf[newdf.type_structure == employerfilter]
    counts_df_état = groupby_count(newdf,
                              ['état', 'date_candidature_mensuelle'],
                              "id_anonymisé")

    fig = multiple_bar_plot(counts_df_état,
                            "date_candidature_mensuelle",
                            "count",
                            "état",
                            prev_months_filter)
    return fig

# tb116-barplot / deptfilter
@app.callback(
    Output(component_id='fig_counts_origine', component_property='figure'),
    Input(component_id='deptsfilter', component_property='value'),
    Input(component_id='employerfilter', component_property='value')
)
def update_output_div(deptsfilter, employerfilter):
    newdf = candidatures_12_prev_months
    if deptsfilter != "all":
        # récup colonnes d'intérêt
        newdf = newdf[newdf.nom_département_structure == deptsfilter]

    if employerfilter != "all":
        newdf = newdf[newdf.type_structure == employerfilter]

    counts_df_état = groupby_count(newdf,
                              ['origine', 'date_candidature_mensuelle'],
                              "id_anonymisé")

    fig = multiple_bar_plot(counts_df_état,
                            "date_candidature_mensuelle",
                            "count",
                            "origine",
                            prev_months_filter)
    return fig

# @app.callback(
#     Output(component_id='tbl_candidate_profile', component_property='data'),
#     Input(component_id='deptsfilter', component_property='value')
# )
# def update_candidates_table_profile(deptsfilter):
#     newdf = candidats_df
#     if deptsfilter != "all":
#         # récup colonnes d'intérêt
#         newdf = newdf[newdf.nom_département == deptsfilter]
#     dtf, cols = prepare_candidate_profile_per_date(newdf, prev_months_filter)
#     #table = generate_table(dtf, cols)
#     return dtf

app.run_server(debug=True)
