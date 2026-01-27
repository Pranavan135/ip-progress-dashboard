# iP Progress Dashboard Generator

A tool that:
1. Tracks student progress through manual CSV updates
2. Generates progress table in MarkBind-compatible markdown
3. Deploys to a website using MarkBind and GitHub Pages

## How It Works

1. Update `data/student_progress.csv` daily:
   - Mark completed tasks with `1`
   - Mark incomplete tasks with `0`

2. Run the generator:
   ```bash
   python3 scripts/generate_progress_table.py
   ```

3. Push to master branch:
   - GitHub Actions will automatically build and deploy
   - Dashboard updates at: [https://nus-cs2103de-ay2526s2.github.io/ip-progress-dashboard/]
   (https://nus-cs2103de-ay2526s2.github.io/ip-progress-dashboard/)
   - Current timestamp will be shown on the website

## Data Files

### task_definitions.csv
Contains task metadata:
- Task Name: Identifier for the task
- Task Type: Weekly/Increment/Admin
- Is Optional: true/false
- Due Date: YYYY-MM-DD HH:MM format
- Week Number: Week the task belongs to

### student_progress.csv
Tracks student completion:
- Full Name: Student's name
- Student ID: Anonymized ID
- Task columns: One column per task (1=completed, 0=not completed)

## Progress Display

The script automatically generates badges with 5 different statuses:

| Badge Color | Meaning |
|------------|---------|
| Green | Completed required task |
| Light Blue | Completed optional task (well done!) |
| Red | Overdue task, not completed |
| Dark | Task due soon (within 5 days), not completed |
| Gray | Optional task due soon, not completed |

Tasks are only shown if they are:
- Due in past weeks
- Due in current week
- Due within next 5 days 