import csv
import pandas as pd
import  tag_finder as tf

def read_csv(file_name):
    users = []
    with open(file_name, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip() for h in reader.fieldnames]

        for row in reader:
            name = row.get("Name")
            repo_url = row.get("Repository's Location")

            if not name or not repo_url:
                print("Skipping invalid row:", row)
                continue

            users.append((name, repo_url))

    return users

if __name__ == "__main__":
    users = read_csv("data/name_repo.csv")
    df = pd.read_csv("data/student_progress.csv", dtype=str)
    token_file = "tokens/github_token.txt"
    with open(token_file, "r") as f:
        token = f.read()
    headers = df.columns.tolist()

    for i in range(len(users)):
        tags = tf.get_all_tags_from_url(users[i][1][:-4], token)

        for tag in tags:
            if tag in headers:
                df.loc[df["Full Name"] == users[i][0], tag] = '1'

    df.to_csv("data/student_progress.csv", index=False)
    print(users)