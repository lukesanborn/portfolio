# classroom-todoist-integration

### Todoist tasks created for assignments in Google Classroom

* You need to download a credentials.json file in the Google developer portal
* Enable the necessary permissions to access your account
* Todoist api token stored as an environment variable - _Note Todoist Premium not needed_
* You also need to specify the project id to add the assignments

### Behavior

Automatically checks every 2 minutes for assignments in Google Classroom.
New assignments get added to Todoist in a section with the Classroom name. The description is transferred into Todoist.
