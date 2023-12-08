import time
import requests
from requests.auth import HTTPBasicAuth
from prometheus_client import start_http_server, Gauge

# Configuration
JIRA_DOMAIN = "================="
JIRA_USERNAME = "====="
JIRA_TOKEN = "====="  # Use environment variables or a secure method to store this!
JIRA_PROJECT = "test-jira-dashboard"
PROMETHEUS_PORT = 8000

# Prometheus Metrics
issues_by_status_gauge = Gauge('jira_issues_by_status', 'Number of issues by status', ['status'])

# Start Prometheus HTTP server
start_http_server(PROMETHEUS_PORT)

# Function to fetch data from Jira and update Prometheus metrics
def update_metrics():
    search_url = f"https://{JIRA_DOMAIN}/rest/api/3/search"
    auth = HTTPBasicAuth(JIRA_USERNAME, JIRA_TOKEN)

    # Define the statuses you are interested in
    statuses = ['To Do', 'In Progress', 'Done']

    for status in statuses:
        # Reset metric for the status
        issues_by_status_gauge.labels(status=status).set(0)

        # Formulate JQL Query
        jql = f'project = "{JIRA_PROJECT}" AND status = "{status}"'

        # Fetch data from JIRA
        response = requests.get(
            search_url,
            auth=auth,
            headers={"Content-Type": "application/json"},
            params={"jql": jql}
        )

        if response.status_code == 200:
            issues = response.json().get('issues', [])
            
            # Set Prometheus metric
            issues_by_status_gauge.labels(status=status).set(len(issues))

            # Print details for each issue
            for issue in issues:
                fields = issue.get('fields', {})
                issue_key = issue.get('key')
                summary = fields.get('summary')
                issue_type = fields.get('issuetype', {}).get('name')
                assignee_info = fields.get('assignee')
                reporter_info = fields.get('reporter')

                # Check if assignee or reporter is not None before getting displayName
                assignee = assignee_info.get('displayName', 'Unassigned') if assignee_info else 'Unassigned'
                reporter = reporter_info.get('displayName', 'Unreported') if reporter_info else 'Unreported'

                print(f"Issue Key: {issue_key}, Summary: {summary}, Issue Type: {issue_type}, "
                      f"Assignee: {assignee}, Reporter: {reporter}")
        else:
            print(f"Failed to fetch JIRA issues for status '{status}': {response.status_code}, {response.text}")

# Expose metrics and print issue details
def expose_metrics():
    while True:
        update_metrics()
        time.sleep(60)  # Update every 1 minutes

# Main execution
if __name__ == '__main__':
    expose_metrics()
