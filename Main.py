import sqlite3
import tkinter as tk
import tkinter.messagebox as tm
from tkinter import ttk
import re
from win32api import GetSystemMetrics
from math import ceil

###############
# Sqlite3 logic
###############

#connect sqlite3 to db file
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)

    return conn
conn = create_connection("pythonsqlite.db")


#create tables
sql_create_tasks = """
        CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        task TEXT NOT NULL,
                        name varchar(12) NOT NULL,
                        abandoned BOOLEAN NOT NULL,
                        timeDone DATETIME,
                        timeSet DATETIME DEFAULT CURRENT_TIMESTAMP
                        );"""

sql_create_users = """
        CREATE TABLE IF NOT EXISTS users (
                        userId integer PRIMARY KEY NOT NULL,  
                        name varchar(12) UNIQUE NOT NULL
                        );"""

sql_create_last_user = """
        CREATE TABLE IF NOT EXISTS lastuser ( 
                        name varchar(12) UNIQUE NOT NULL
                        );"""

if conn is not None:
    try:
        c = conn.cursor()
        c.execute(sql_create_tasks)
        c.execute(sql_create_users)
        c.execute(sql_create_last_user)
        conn.commit()
        c.close()
    except sqlite3.Error as e:
        print(e)

else:
    print("Error creating the tables.")
    exit(0)


#custom queries
def insertNewTask(task, username):
    try:
        c = conn.cursor()
        c.execute(f'INSERT INTO tasks (task, abandoned, name) values (?,?,?)', (task, False, username))
        conn.commit()
        c.close()
    except sqlite3.Error as e:
        print(e)

def insertNewUser(username):
    try:
        c = conn.cursor()
        c.execute(f"INSERT INTO users (name) VALUES (?);", (username,))
        conn.commit()
    except sqlite3.Error:
        raise ValueError("The username is already taken, please choose another one")


def deleteLastUserData():
    try:
        c = conn.cursor()
        c.execute("DELETE FROM lastuser;")
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def addLastUser(username):
    try:
        c = conn.cursor()
        c.execute(f"INSERT INTO lastuser (name) VALUES (?);", (username,))
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def checkLastUser():
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM lastuser;")
        rows = c.fetchall()
        return rows
    except sqlite3.Error as e:
        print(e)


def getTasks(username, pageNb, nbTasksToDisp):
    try:
        c = conn.cursor()
        c.execute(f"SELECT * FROM tasks WHERE name = ? ORDER BY timeSet ASC limit ? offset ?;", (username, nbTasksToDisp, nbTasksToDisp*pageNb))
        rows = c.fetchall()
        return rows
    except sqlite3.Error as e:
        print(e)


def getNbTasks(username):
    try:
        c = conn.cursor()
        c.execute(f"SELECT COUNT(*) FROM tasks WHERE name = ?;", (username,))
        rows = c.fetchall()
        return rows
    except sqlite3.Error as e:
        print(e)


def finishTask(idTask):
    try:
        c = conn.cursor()
        c.execute(f"UPDATE tasks SET timeDone = CURRENT_TIMESTAMP, abandoned = False WHERE id = ?;", (idTask,))
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def giveupTask(idTask):
    try:
        c = conn.cursor()
        c.execute(f"UPDATE tasks SET timeDone = CURRENT_TIMESTAMP, abandoned = True WHERE id = ?;", (idTask,))
        conn.commit()
    except sqlite3.Error as e:
        print(e)

###############
# Tkinter logic
###############

LARGE_FONT = ("Verdana", 12)

class main(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        #tools
        def exitFullscreen():
            app.attributes('-fullscreen', False)
            app.geometry(f"{int(GetSystemMetrics(0)/2)}x{int(GetSystemMetrics(1)/2)}")

        def enterFullscreen():
            app.attributes('-fullscreen', True)
            app.geometry(f"{GetSystemMetrics(0)}x{GetSystemMetrics(1)}")

        #title
        tk.Tk.wm_title(self, "TodoKing")

        #icon
        iconImage = tk.PhotoImage(file = 'todoking.png')
        self.iconphoto(False, iconImage)

        #container configuration
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        style = ttk.Style()
        style.theme_use('clam')

        menu_bar = tk.Menu(container)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        screen_menu = tk.Menu(menu_bar, tearoff=0)


        file_menu.add_command(label="Say Hello", command=lambda: tm.showinfo("Message", "Hello There!"))
        file_menu.add_separator()
        screen_menu.add_command(label="Exit fullscreen", command=lambda: exitFullscreen())
        screen_menu.add_command(label="Go fullscreen", command=lambda: enterFullscreen())

        menu_bar.add_cascade(label="Screen", menu=screen_menu)
        menu_bar.add_cascade(label="Actions", menu=file_menu)

        tk.Tk.config(self, menu=menu_bar)

        self.frames = {}

        for F in (LoginPage, MainPage):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        # Automatically login user if he selected to stay signed it
        if self.isSignedIn() is True:
            self.show_frame(MainPage)
        else:
            self.show_frame(LoginPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

    def isSignedIn(self):
        lastuser = checkLastUser()
        if lastuser:
            global user
            user = lastuser[0][0]
            print(user)
            tm.showinfo("Login Information", "You're logged in as " + user)
            return True



class LoginPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        frame = tk.Frame(self)
        frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)

        label = tk.Label(self, text="Login", font=LARGE_FONT, background="aquamarine2")
        label.grid(row=0, column=0, sticky=tk.W)

        bg_image = tk.PhotoImage(file="bg2.png")
        bg_label = tk.Label(self, image=bg_image)
        bg_label.image = bg_image
        bg_label.place(relwidth=1, relheight=1)

        self.btnLog = tk.Button(self, text="Login", command=lambda: self.login(controller), background='pink')
        self.btnLog.config(height=2, width=15, font=("Courier", 19))
        self.btnLog.place(relx=0.2, rely=0.4)

        self.btnReg = tk.Button(self, text="Register", command=lambda: self.register(controller), background='HotPink1')
        self.btnReg.config(height=2, width=15, font=("Courier", 19))
        self.btnReg.place(relx=0.2, rely=0.5)

        self.btnStaySignedInVar = tk.IntVar()
        self.btnStaySignedIn = tk.Checkbutton(self, text="Stay signed in?", background='light coral', variable=self.btnStaySignedInVar)
        self.btnStaySignedIn.config(height=1, width=15, font=("Courier", 15))
        self.btnStaySignedIn.place(relx=0.4, rely=0.3)

        self.label_username = tk.Label(self, text="Username", background='light pink')
        self.label_username.config(font=("Courier", 30))

        self.entry_username = ttk.Entry(self)
        self.entry_username.config(font=("Courier", 30))

        self.label_username.place(relx=0.2, rely=0.2)
        self.entry_username.place(relx=0.4, rely=0.2)

    def login(self, cont):
        user = self.entry_username.get()
        try:
            c = conn.cursor()
            c.execute(f"SELECT * FROM users WHERE name = ?;", (user,))
            rows = c.fetchall()
            if rows:
                if self.btnStaySignedInVar.get() == 0:
                    deleteLastUserData()
                else:
                    deleteLastUserData()
                    addLastUser(user)
                self.entry_username.delete(0, 'end')
                return cont.show_frame(MainPage)
            else:
                tm.showinfo("Message", "Username doesn't exist.")
                self.entry_username.delete(0, 'end')
                pass
        except sqlite3.Error as e:
            tm.showinfo("Error", str(e))

            self.entry_username.delete(0, 'end')

    def register(self, cont):
        user = self.entry_username.get()
        try:
            choice = tm.askquestion("Yes/No",
                                    f"Are you want {self.entry_username.get()} to be your username, this is unique and it will be necessary to access your account, keep it safe!",
                                    icon="warning")
            if choice == "yes":
                insertNewUser(user)
                tm.showinfo("Registration complete", "Congratulations, you have successfully created your account")
                if self.btnStaySignedInVar.get() == 0:
                    deleteLastUserData()
                else:
                    deleteLastUserData()
                    addLastUser(user)
                self.entry_username.delete(0, 'end')
                return cont.show_frame(MainPage)
            else:
                pass
        except (sqlite3.Error, ValueError) as e:
            tm.showerror("Error", "This username already exists")
            self.entry_username.delete(0, 'end')


class MainPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        frame = tk.Frame(self)
        frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)

        label = tk.Label(self, text="Login", font=LARGE_FONT, background="aquamarine2")
        label.grid(row=0, column=0, sticky=tk.W)

        bg_image = tk.PhotoImage(file="bg2.png")
        bg_label = tk.Label(self, image=bg_image)
        bg_label.image = bg_image
        bg_label.place(relwidth=1, relheight=1)

        self.label_task = tk.Label(self, text="Task", background='pale violet red')
        self.label_task.config(font=("Courier", 30))

        self.entry_task = ttk.Entry(self)
        self.entry_task.config(font=("Courier", 30), width=40)

        self.label_task.place(relx=0.2, rely=0.1)
        self.entry_task.place(relx=0.3, rely=0.1)

        self.btnLog = tk.Button(self, text="Back", command=lambda: self.back(controller), background='DeepPink2')
        self.btnLog.config(height=2, width=10, font=("Courier", 10))
        self.btnLog.place(relx=0.1, rely=0.95)

        self.load = tk.Button(self, text="Load", command=lambda: self.loadContent(), background='DeepPink2')
        self.load.config(height=2, width=10, font=("Courier", 10))
        self.load.place(relx=0.1, rely=0.05)

        self.load = tk.Button(self, text="Exit", command=lambda: exit(0), background='Red')
        self.load.config(height=2, width=10, font=("Courier", 10))
        self.load.place(relx=0.92, rely=0.01)

        self.load = tk.Button(self, text="Create", command=lambda: self.createTask(user, controller), background='DeepPink2')
        self.load.config(height=2, width=10, font=("Courier", 10))
        self.load.place(relx=0.85, rely=0.05)

        self.nextPage = tk.Button(self, text="Next Page", command=lambda: self.nextPageCommand(controller), background='Orange')
        self.nextPage.config(height=2, width=10, font=("Courier", 10))
        self.nextPage.place(relx=0.9, rely=0.88)

        self.previousPage = tk.Button(self, text="Previous Page", command=lambda: self.previousPageCommand(controller), background='Orange')
        self.previousPage.config(height=2, width=14, font=("Courier", 10))
        self.previousPage.place(relx=0.1, rely=0.88)

        self.pageText = tk.Label(self, text="1")
        self.pageText.config(height=2, width=5, font=("Courier", 10))
        self.pageText.place(relx=0.5, rely=0.88)

        self.nbTasksToDisp = 13
        self.page = 0

        self.tasks = []
        self.tasksButtons = []   

        self.uselessVariable = False

    def createTask(self, username, cont):
        newTaskText = self.entry_task.get()
        if newTaskText:
            print(newTaskText, username)
            insertNewTask(newTaskText, username)
            self.entry_task.delete(0, 'end')
            self.loadContent()
        else:
            tm.showinfo("For your information", "You need to input a new task, nothing isn't valid")

    def nextPageCommand(self, cont):
        nbTasks = getNbTasks(user)[0][0]
        if (nbTasks % self.nbTasksToDisp) != 0:
            nbTasks += self.nbTasksToDisp - (nbTasks % self.nbTasksToDisp)

        if ((self.page + 2) * self.nbTasksToDisp)<=nbTasks:
            self.page += 1
        
        self.loadContent()

    def previousPageCommand(self, cont):
        if self.page-1 >= 0:
            self.page -= 1
        self.loadContent()

    def loadContent(self):
        nbTasks = getNbTasks(user)[0][0]

        for taskButt in self.tasksButtons:
            taskButt.destroy()
        self.tasksButtons.clear()

        # This little if else helps me load the newest tasks first instead of the oldest
        if self.uselessVariable is False:
            self.pageText.config(text=str(ceil(nbTasks/self.nbTasksToDisp))+"/"+str(ceil(nbTasks/self.nbTasksToDisp)))
            self.page = ceil(nbTasks/self.nbTasksToDisp)-1
            self.tasks = getTasks(user, ceil(nbTasks/self.nbTasksToDisp)-1, self.nbTasksToDisp)
            self.uselessVariable = True
        else:
            self.pageText.config(text=str(self.page+1)+"/"+str(ceil(nbTasks/self.nbTasksToDisp)))
            self.tasks = getTasks(user, self.page, self.nbTasksToDisp)

        for i, task in enumerate(self.tasks):
            if task[4] is None:
                self.tasksButtons.append(tk.Button(self, text=self.tasks[i][5] + " : " + self.tasks[i][1], anchor=tk.W, command=lambda i=i: self.taskOption(self.tasks[i])))
            elif task[3] is 1:
                self.tasksButtons.append(tk.Button(self, text=self.tasks[i][5] + " : [" + self.tasks[i][1] + "], ABANDONED ON: "+self.tasks[i][4], anchor=tk.W, command=lambda i=i: self.taskOption(self.tasks[i]), bg="firebrick1"))
            else:
                self.tasksButtons.append(tk.Button(self, text=self.tasks[i][5] + " : [" + self.tasks[i][1] + "], COMPLETED ON: "+self.tasks[i][4], anchor=tk.W, command=lambda i=i: self.taskOption(self.tasks[i]), bg="chartreuse2"))

        for x, but in enumerate(self.tasksButtons):
            but.config(height=2, width=len(but["text"]), font=("Courier", 10))
            but.place(relx=0.1, rely=0.20+0.05*x)

    def back(self, cont):
        user = None
        deleteLastUserData()
        return cont.show_frame(LoginPage)


    def taskOption(self, task):

        def completeTask(idTask):
            finishTask(idTask)
            windo.destroy()
            self.loadContent()

        def abandonTask(idTask):
            giveupTask(idTask)
            windo.destroy()
            self.loadContent()

        windo = tk.Toplevel(self)
        windo.geometry("300x150")

        windo.configure(background="white")
        checkbtnimg = tk.PhotoImage(file="checkbtn.png")
        checkbtn = tk.Button(windo, image=checkbtnimg, command=lambda: completeTask(task[0]), borderwidth=0, highlightthickness = 0, bd = 0)
        checkbtn.image = checkbtnimg
        checkbtn.place(relx=0.6, rely=0.3)

        crossbtnimg = tk.PhotoImage(file="crossbtn.png")
        crossbtn = tk.Button(windo, image=crossbtnimg, command=lambda: abandonTask(task[0]), borderwidth=0, highlightthickness = 0, bd = 0)
        crossbtn.image = crossbtnimg
        crossbtn.place(relx=0.2, rely=0.3)

        button = tk.Button(windo, text="Back", background="MistyRose4",
                            command=lambda: windo.destroy())
        button.config(height=1, width=10, font=("Courier", 10))
        button.place(relx=0.05, rely=0.8)



# user = None
# To get session username, type <current_users[-1]>
app = main()
#app.geometry(f"{GetSystemMetrics(0)}x{GetSystemMetrics(1)}")
# app.geometry("800x500")
# app.wm_attributes('-transparentcolor','black')
app.attributes('-fullscreen', True)
app.mainloop()




