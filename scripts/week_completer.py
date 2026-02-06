import pandas as pd
import sys

def find_week_tasks(week_number: str, tasks = "data/task_definitions.csv"):
    df_tasks = pd.read_csv(tasks, dtype=str)
    df_tasks = df_tasks.drop(df.index[:5]) # Remove all the week rows

    filtered_df = df_tasks[
        (df_tasks["Week Number"] == week_number) &
        (df_tasks["Is Optional"] == "FALSE")
        ]

    return filtered_df.iloc[:, 0].tolist()

# pass week number as a command line argument
if __name__ == "__main__":
    week_no = sys.argv[1]
    df = pd.read_csv("data/student_progress.csv", dtype=str)

    week_tasks = find_week_tasks(week_no)
    print(week_tasks)

    df["Week" + week_no] = (
        df[week_tasks]
        .eq("1")
        .all(axis=1)
        .map({True: "1", False: "0"})
    )

    df.to_csv("data/student_progress.csv", index=False)

