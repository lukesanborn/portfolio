import datetime
import os
from typing import List

import pandas as pd
import psycopg2
import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource
from googleapiclient.discovery import build
from todoist.api import TodoistAPI


def connect():
    DATABASE_URL = os.environ.get("DATABASE_URL")
    con = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = con.cursor()
    return con, cur


def close(con, cur):
    con.commit()
    cur.close()
    con.close()


def timezone(utc):
    local_tz = pytz.timezone('US/Eastern')
    try:
        due_time = utc['dueTime']
        date = utc['dueDate']
    except KeyError:
        return
    try:

        due_date = datetime.datetime(date['year'], date['month'], date['day'], due_time['hours'],
                                     due_time['minutes'])
    except KeyError:
        due_date = datetime.datetime(date['year'], date['month'], date['day'], due_time['hours'])
    local_dt = due_date.replace(tzinfo=pytz.utc).astimezone(local_tz)
    local_dt = local_tz.normalize(local_dt)
    return local_dt.strftime('%m/%d/%Y %H:%M')


def entry_check(name, due):
    """"Checks to see if identical task in database. Returns false if there is an identical assignment"""
    con, cur = connect()
    cur.execute(f"select name,due,id,work_id from work where name ='{name}'")
    task = cur.fetchall()
    close(con, cur)
    try:
        if task[0][0] == name and task[0][1] == due:
            # Same name same due date - identical task
            return True, False, None
        elif name == task[0][0] and due != task[0][1]:
            #  Same name different due date - update due date
            return False, True, task[0][2]
    except IndexError:
        return False, False, None


class todoist:
    """Connects to todoist."""

    def __init__(self):
        super().__init__()
        token = os.environ.get("TODOIST_TOKEN")
        self.api = TodoistAPI(token)
        self.project = 2219911906

    def add_section(self, name: str):
        self.api.sync()
        section = self.api.sections.add(name, project_id=self.project)
        self.api.commit()
        return section.__getitem__("id")

    def add_task(self, section_id: int, task: str, description: str, date: str):
        """"Adds an item to todoist if the item does not already exist"""
        self.api.sync()
        task = self.api.items.add(content=task, description=description, project_id=self.project, section_id=section_id,
                                  date_string=date)
        self.api.commit()
        return task.__getitem__("id")

    def get_task_due(self, task_id: int):
        """Fetches due date for a given todoist task"""
        self.api.sync()
        item = self.api.items.get_by_id(task_id)
        item_due = item.__getitem__('due')['date']
        return item_due

    def update_task(self, task_id: int, new_date: str):
        """"Changes the due date of a task to the specified"""
        self.api.sync()
        item = self.api.items.get_by_id(task_id)
        item.update(date_string=new_date)
        self.api.commit()

    def delete_task(self, task_id: int):
        """"Deletes a task"""
        self.api.sync()
        item = self.api.items.get_by_id(task_id)
        item.delete()
        self.api.commit()

    def complete_task(self, task_id: int):
        self.api.sync()
        item = self.api.items.get_by_id(task_id)
        item.complete()
        self.api.commit()


def authorize() -> Resource:
    """Google OAuth2. Returns Service Object
    :rtype: object
    """

    SCOPES = [
        'https://www.googleapis.com/auth/classroom.courses.readonly',
        'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
        # 'https://www.googleapis.com/auth/classroom.coursework.students.readonly',
        # "https://www.googleapis.com/auth/classroom.coursework.me.readonly"
    ]

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'google-credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('classroom', 'v1', credentials=creds)


class classroom:
    def __init__(self):
        self.service = authorize()
        self.t = todoist()

    def get_classes(self) -> List[dict]:
        """Gets class info. Returns list of class and ids"""
        courses = []
        class_list = self.service.courses().list(courseStates=["ACTIVE"], fields='courses/id,courses/name').execute()
        courses.extend(class_list.get('courses', []))
        return [dict(id=int(class_dict["id"]), name=class_dict["name"]) for class_dict in class_list['courses']]

    def _get_assignment_info(self, class_id: int, task_id: int):
        """Gets coursework info for given assignment. Returns list of name and assignment id"""
        response = self.service.courses().courseWork().get(courseId=class_id, id=task_id,
                                                           fields='id,title,dueDate,dueTime,description',
                                                           ).execute()
        response['description'] = response.get('description', "").replace('\n', '').strip()
        return response

    def _get_assignments(self, class_id: int):
        """Gets assignments with state not turned in"""
        state = self.service.courses().courseWork().studentSubmissions().list(courseId=class_id,
                                                                              courseWorkId='-',
                                                                              states=['CREATED', 'NEW'],
                                                                              fields='studentSubmissions(courseWorkId,state)'
                                                                              ).execute()
        if state.get('studentSubmissions'):
            assignment_ids = [item.get('courseWorkId') for item in state.get('studentSubmissions')]
        else:
            assignment_ids = list()
        return assignment_ids

    def create_classes(self, class_list):
        """Add classes to db and todoist with input from classroom"""
        con, cur = connect()
        for item in class_list:
            cur.execute(f"select 1 from classes where name='{item['name']}'")
            row = cur.fetchall()
            if not row:
                section_id = self.t.add_section(item['name'])
                cur.execute("insert into classes (classroom_id, name,todoist_id) values (%s, %s,%s)",
                            (int(item['id']), item['name'], section_id))
        close(con, cur)

    @staticmethod
    def _get_project(class_id):
        con, cur = connect()
        cur = con.cursor()
        cur.execute(f"select classroom_id,todoist_id from classes where classroom_id ='{class_id}'")
        project_id = cur.fetchall()[0][1]
        close(con, cur)
        return project_id

    @staticmethod
    def _get_class(class_id):
        con, cur = connect()
        cur = con.cursor()
        cur.execute(f"select classroom_id,id from classes where classroom_id ='{class_id}'")
        fkey = cur.fetchall()[0][1]
        close(con, cur)
        return fkey

    def create_assignments(self, class_id: int):
        assignment_ids = self._get_assignments(class_id)
        for item in assignment_ids:
            response = self._get_assignment_info(class_id, item)
            work_id = response['id']
            title = response['title']
            desc = response['description']
            due = timezone(response)
            con, cur = connect()
            cur.execute(f"select name,due,id,work_id from work where work_id = '{work_id}'")
            task = cur.fetchall()
            # If an item in the database exists with the same title
            if not task:
                # If no item exists with the same title - insert new item
                print(
                    f'Inserting {title} into database with id {work_id} and due date {due} in class {class_id}')
                task_id = self.t.add_task(self._get_project(class_id), title, desc, due)
                cur.execute(
                    "insert into work (work_id, name, due,completed, class_id,todoist_task_id) values (%s, %s, %s, %s, %s, %s)",
                    (work_id, title, due, True, self._get_class(class_id), task_id))
            elif due != task[0][1]:
                # If an item in the database already exists with the same title but different due date - update due date
                cur.execute(f"select todoist_task_id from work where work_id={work_id}")
                todoist_task_id = cur.fetchall()[0][0]
                print(title, work_id,todoist_task_id)
                print(f"{due=}")
                if self.t.get_task_due(todoist_task_id) != due:
                    print(f'Changing date for task {title}')
                    self.t.update_task(todoist_task_id, due)
                    cur.execute(f"update work set due ='{due}' where id={task[0][2]}")

            close(con, cur)

    # def complete_assignments(self, class_id):
    #     assignment_ids = self._get_assignments(class_id)
    #     work_ids = []
    #     todoist_ids = {}
    #     for item in work:
    #         response = classwork(service, class_id, item)
    #         work_ids.append(int(response['id']))
    #     con, cur = connect()
    #     cur.execute(
    #         f"select work.completed, work.work_id, work.todoist_task_id from work inner join classes on work.class_id = classes.id where classes.classroom_id={class_id}")
    #     rows = cur.fetchall()
    #     for row in rows:
    #         in_todoist = row[0]
    #         classroom_id = row[1]
    #         todoist_task_id = row[2]
    #         if in_todoist:
    #             work_ids.append(classroom_id)
    #             todoist_ids.append[rows.index(row)] = todoist_task_id
    #
    #     completed = [x for x, y in collections.Counter(work_ids).items() if y == 1]
    #     # completed is list of tasks for that class that have been turned and is_todoist is true
    #     if completed:
    #         for item_id in completed:
    #             t = todoist()
    #             t.complete(todoist_ids[item_id])
    #             cur.execute(f"update work set completed=False where work_id={item_id}")
    #     close(con, cur)


def driver():
    con, cur = connect()
    table = pd.read_sql_query('select classroom_id from classes', con)
    class_ids = table["classroom_id"].to_list()
    close(con, cur)
    gc = classroom()
    enrolled_classes = gc.get_classes()
    classes_to_add = [item for item in enrolled_classes if item["id"] not in class_ids]
    if classes_to_add:
        gc.create_classes(classes_to_add)
    list(map(gc.create_assignments, class_ids))
    # threads = []
    # for item in class_ids:
    #     t = threading.Thread(target=gc.create_assignments, args=(item[0],))
    #     threads.append(t)
    #     # if completions:
    #     #     y = threading.Thread(target=complete_assignments, args=(item[0],))
    #     #     threads.append(y)
    # for item in threads:
    #     item.start()
    # for item in threads:
    #     item.join()
    # print(f"--- {(time.time() - start_time)} seconds for {class_ids[threads.index(item)][1]} ---")


if __name__ == "__main__":
    driver()