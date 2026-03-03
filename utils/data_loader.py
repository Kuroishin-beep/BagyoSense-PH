import pandas as pd
import os


def load_data() -> pd.DataFrame:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base, "dataset", "philippines_typhoon_monthly_2014_2024.csv")
    df = pd.read_csv(csv_path)

    month_short = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                   7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    month_full  = {1:"January",2:"February",3:"March",4:"April",
                   5:"May",6:"June",7:"July",8:"August",
                   9:"September",10:"October",11:"November",12:"December"}

    df["Month_Name"] = df["Month"].map(month_short)
    df["Month_Full"] = df["Month"].map(month_full)
    df["Date"]       = pd.to_datetime(df[["Year","Month"]].assign(DAY=1))
    df["Season"]     = df["Month"].apply(
        lambda m: "Peak (Jun-Nov)" if 6 <= m <= 11 else "Off-Season (Dec-May)"
    )
    df["ENSO_Phase"] = df["ONI"].apply(
        lambda x: "El Nino" if x >= 0.5 else ("La Nina" if x <= -0.5 else "Neutral")
    )
    df["Typhoon_Category"] = df["Number_of_Typhoons"].apply(
        lambda x: "None"         if x == 0
             else "Low (1-2)"    if x <= 2
             else "Moderate (3-4)" if x <= 4
             else "High (5+)"
    )
    return df