import pandas as pd
import time


def prepare_candidate_profile_per_date(accepted_candidates_dtf, months):
    # criteres to keep and their corresponding names
    elig_criterions = ["critère_n1_bénéficiaire_du_rsa",
                       "critère_n1_detld_plus_de_24_mois",
                       "critère_n2_deld_12_à_24_mois",
                       "critère_n2_jeune_moins_de_26_ans",
                       "critère_n2_résident_qpv"]
    elig_criterions_names = ["RSA",
                             "DETLD",
                             "DELD",
                             "Jeune",
                             "QPV"]

    # keep only needed cols
    cols = elig_criterions + ["id_anonymisé", "date_diagnostic"]
    dtf = accepted_candidates_dtf[cols].copy()
    # add monthly date col
    dtf["date_diagnostic_mensuelle"] = dtf.apply(lambda row: str(row.date_diagnostic.month)+"-"+str(row.date_diagnostic.year) if row.date_diagnostic else None, axis=1)

    # groupy diagnostic date
    dtf = dtf.groupby("date_diagnostic_mensuelle")[elig_criterions].sum()
    dtf["sum"] = dtf.apply(lambda row: sum(row), axis=1)
    cols = elig_criterions+["sum"]

    dtf[cols] = dtf[cols].apply(lambda x: round(x/x["sum"] * 100), axis=1)
    dtf = dtf[elig_criterions]

    table_cols = [{"id": c, "name": n} for c,n in zip(elig_criterions, elig_criterions_names)]
    return dtf, table_cols


# data load
def load_candidatures_echelle_locale(path):
    """

    """
    df = pd.read_csv(path, sep="\t")
    df["date_candidature"] = pd.to_datetime(df["date_candidature"])
    df["date_candidature_mensuelle"] = df.apply(lambda row: str(row.date_candidature.month)+"-"+str(row.date_candidature.year) if row.date_candidature is not None else None, axis=1)
    return df

def load_candidats(path):
    candidats = pd.read_csv(path)
    candidats["date_inscription"] = pd.to_datetime(candidats["date_inscription"])
    candidats["date_diagnostic"] = pd.to_datetime(candidats["date_diagnostic"])
    return candidats

# prepare data
def groupby_count(dtf, grouby_cols, count_col):
    counts_df = dtf.groupby(grouby_cols)[count_col].nunique().reset_index(name='count')
    return counts_df


# filters
def get_n_prev_months(N):
    now = time.localtime()
    n_months = [time.localtime(time.mktime((now.tm_year, now.tm_mon - n, 1, 0, 0, 0, 0, 0, 0)))[:2] for n in range(N)]
    n_months.sort()
    return n_months
