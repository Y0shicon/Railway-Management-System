import csv
from tkinter import *
from tkinter import ttk
from ttkwidgets import CheckboxTreeview
from os import listdir
from datetime import date,datetime
import time

root = Tk()
root.geometry('1366x768')
#root.attributes('-fullscreen', True)

#Creating a dictionary of all csv files in the 'Train's info' folder
def find_csv_filenames( path_to_dir, suffix=".csv" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]

#Function returns a list of all csv files
filenames = find_csv_filenames('Trains Info')

#Creating a dictionary for all the csv files
all_train_csv_dict = {}
for files in filenames:
	if files == 'blank.csv':
		continue
	all_train_csv_dict[files.split(' - ')[1][0:5]] = (files.split(' - ')[0], files)
#Dictionary saved in the form of - {'train no.' : ('train name', 'csv file name')}

#Heading for columns and values
heading_raw = []
data = []
df = 'Trains Info/blank.csv'
with open (df, mode = 'r') as file:
	reader = csv.reader(file)
	for row in reader:
		if heading_raw == []:
			heading_raw = row
		else:
			data.append(row)

password_text = ''

global login_status
login_status = False

headings = ['S. No.',
	'Station Code', 
	'Station Name',
	'Route No.',
	'Arrival Time',
	'Departure Time',
	'Halt Time (In Minutes)',
	'Distance',
	'Day']

#headings = ['Reached?'] + up_headings

#Defining the treeview
tree = ttk.Treeview(root, height = 28)

style = ttk.Style(tree)
style.configure('Treeview', rowheight = 22)

#Leaving some space on the left of treeview
for i in range(10):
		Label(root, text = ' ').grid(row = i, column = 0)

#Defining columns

tree['columns'] = tuple(headings)

#Format Columns
tree.column('#0',width=0, stretch=NO)
for i in headings:
	if i == 'Station Code' or 'Staion Name':
		tree.column(i, width = 150)
	else:
		tree.column(i, width = 70)

#Creating headings
tree.heading('#0', text = '')
for i in headings:
	tree.heading(str(i), text = str(i))

#Add data
for i in range(len(data)):
	tree.insert(parent = '',
		 index = 'end',
		 iid = i,
		 text = '',
		 values = data[i])

#Placing the treeview
tree.grid(row = 1, column = 1, columnspan = len(headings), rowspan = len(data))

#Login Button
def remove_txt(textbox):
	if textbox == password_text:
		textbox['show'] = '*'
	textbox.delete(0,  END)
	textbox['fg'] = 'black'

def verify_psswd(username, password):
	login_details = []
	with open('admin_psswd.csv', 'r') as login_handle:
		login_reader = csv.reader(login_handle)
		for i in login_reader:
			login_details.append(i)
		login_details.pop(0)
		#print(login_details)
	count = 0
	for details in login_details:
		if username == details[1] and password == details[2]:
			confirm_label = Label(login_win, text = 'Access Granted')
			confirm_label.grid(row = 4, column = 1)
			login_status = True

			#Changing the text on the login buttons
			login_but['text'] = 'Log Out'
			login_win_but['text'] = 'Log Out'
 
			#Displaying the buttons
			delay_but.grid(row = 0, column = len(headings)//2+1, sticky = 'w')
			advance_but.grid(row = 0, column = len(headings)//2-1, sticky = 'e')
			time_lag_txt.grid(row = 0, column = len(headings)//2)
			logs_but.grid(row = len(data) + 2, column = 5, ipadx = 10, ipady = 10)
			break

		elif count == len(login_details)-1:
			confirm_label = Label(login_win, text = 'Wrong Username or password')
			confirm_label.grid(row = 4, column = 1)

			login_status = False

			delay_but.grid_forget()
			advance_but.grid_forget()
			time_lag_txt.grid_forget()
			logs_but.grid_forget()

			#Changing text on the logout buttons
			login_but['text'] = 'Log In'
			login_win_but['text'] = 'Log In'

		count += 1

def login():
	global login_win
	global password_text
	global login_win_but

	login_win = Toplevel()
	login_win.geometry('200x130')
	login_win.title('Login to get admin privileges')

	#Creating space on the left
	for i in range(10):
		Label(login_win, text = ' ').grid(row = i, column = 0)

	#Definging the textboxes
	username = StringVar()
	password = StringVar()
	username_text = Entry(login_win, width = 30, textvariable = username, font=("Arial",8), fg = 'grey')
	username_text.grid(row = 1,  column = 1)
	password_text = Entry(login_win, width = 30, textvariable = password, font=("Arial",8), fg = 'grey')
	password_text.grid(row = 2,  column = 1)

	#Setting Default values for the textboxes
	username_text.insert(0, 'Enter username')
	password_text.insert(0, 'Enter Password')
	username_text.bind('<Button-1>', lambda event : remove_txt(textbox = username_text))
	password_text.bind('<Button-1>', lambda event : remove_txt(textbox = password_text))
	username_text.bind('<Return>', lambda event : verify_psswd(username.get(), password.get()))
	password_text.bind('<Return>', lambda event : verify_psswd(username.get(), password.get()))

	#Create a new account


	#Button to login
	login_win_but = Button(login_win, text = 'Log In', command = lambda : verify_psswd(username.get(), password.get()))
	login_win_but.grid(row =3, column = 1, sticky = 'w')

	login_win.mainloop()

#Login Button on main window
login_but = Button(root, text = 'Log In', command = login)
login_but.grid(row = 0, column = len(headings), sticky = 'e', padx = 10, pady = 5, ipadx = 15)

#######################Main logic of delay or advancement of train timmings#####################
#Defining main functions
def min_to_hour(minutes):
	hour = minutes // 60
	minute = str(minutes%60)
	if len(minute) == 1:
		minute = '0' + minute
	return str(hour)+':'+minute

def hour_to_min(time):
	#time in 24-hour format - eg. 21:54 ---> 9:54 PM
	hour = int(time.split(':')[0])
	minute = int(time.split(':')[1])
	minutes = (hour * 60) + minute 
	return minutes

def time_editor(minutes):
	selected = tree.focus()
	temp = tree.item(selected, 'values')
	for i in range(int(selected), len(data)):
		temp = tree.item(i, 'values')
		new_day = temp[8]
		#changing arrival and departure times and days
		try:
			new_arrival = min_to_hour(hour_to_min(temp[4]) + minutes)
			#In case, time goes above 24:00
			if hour_to_min(new_arrival) > 1440:
				new_arrival = min_to_hour((hour_to_min(new_arrival)-1440))
			#In case, time goes below 00:00
			elif hour_to_min(new_arrival) < 0:
				new_arrival = min_to_hour((1440 + hour_to_min(new_arrival)))

		except ValueError:
			new_arrival = temp[4]
		
		try:
			new_departure = min_to_hour(hour_to_min(temp[5]) + minutes)
			#In case, time goes above 24:00
			if hour_to_min(new_departure) > 1440:
				new_departure = min_to_hour((hour_to_min(new_departure)-1440))
				#Defining new day as when deprature time goes after 12 midnight
				new_day = str(int(temp[8]) + 1)
			#In case, time goes below 00:00
			elif hour_to_min(new_departure) < 0:
				new_departure = min_to_hour((1440 + hour_to_min(new_departure)))
				new_day = str(int(temp[8]) -1)

		except ValueError:
			new_departure = temp[5]
			new_day = temp[8]

		tree.item(i, values = (temp[0], temp[1], temp[2], temp[3], new_arrival, new_departure, temp[6], temp[7], new_day))


#Textbox
time_lag = IntVar()
time_lag_txt = Entry(root, width = 30, textvariable = time_lag, font=("Arial",8), fg = 'grey')
time_lag_txt.insert(1, 'Enter the time lag(in min)')
time_lag_txt.bind('<Button-1>', lambda event : remove_txt(textbox = time_lag_txt))

#Buttons
delay_but = Button(root, text = 'Delay (+)', command = lambda : time_editor(time_lag.get()))
advance_but = Button(root, text = 'Advance (-)', command = lambda : time_editor(-time_lag.get()))

###########Searching for csv files##########
#Search function
def open_csv(df, title):
	global data
	root.title(title)
	tree.delete(*tree.get_children())
	
	#Displaying the name of Train on the top-left

	global train_name_label
	
	try:
		train_name_label.destroy()
		print('Destroyed')
	except NameError:
	 	print('Error')

	train_name_label = Label(root,
					 text = title,
					 fg = "light green",
					 bg = "dark green",
					 font = "Helvetica 16 bold italic")
	train_name_label.grid(row = 0, column = 0, columnspan = 3)

	#Heading for columns and values
	heading_raw = []
	data = []
	path = 'Trains Info/' + df
	with open (path, mode = 'r') as file:
		reader = csv.reader(file)
		for row in reader:
			if heading_raw == []:
				heading_raw = row
			else:
				data.append(row)

	#Editing the treeview
	if len(data) < 28:
		tree['height'] = len(data)
	else:
		tree['height'] = 28

	#Adding Data
	for i in range(len(data)):
		tree.insert(parent = '',
			 index = 'end',
			 iid = i,
			 text = '',
			 values = data[i])

	#Placing the treeview
	tree.grid(row = 1, column = 1, columnspan = len(headings), rowspan = len(data))
	
	search_label.grid(row = len(data) + 2, column = 2, sticky = 'e')
	search_txt.grid(row = len(data) + 2, column = 3)
	show_all_train_but.grid(row = len(data) + 2, column = 4, ipadx = 10)
	help_but.grid(row = len(data)+2, column = 7, ipady = 10, ipadx = 10)
	if login_status == True:
		logs_but.grid(row = len(data) + 1, column = 5, ipadx = 10, ipady = 10)

def search(key):
	global df
	global title
	title = ''
	for train_no in all_train_csv_dict:
		if key == train_no:
			df = all_train_csv_dict[train_no][1]
			title = all_train_csv_dict[train_no][0]
			open_csv(df, title)
	remove_txt(textbox = search_txt)

#Textbox
search_tag = StringVar()
search_txt = Entry(root, width = 30, textvariable = search_tag, font=("Arial",11), fg = 'grey')
search_txt.insert(1, 'Enter the train number')
search_txt.bind('<Button-1>', lambda event : remove_txt(textbox = search_txt))
search_txt.bind('<Return>', lambda event : search(key = search_tag.get()))

search_label = Label(root, text = 'Search for the schedule via train no.')

search_label.grid(row = len(data) + 2, column = 2, sticky = 'e')
search_txt.grid(row = len(data) + 2, column = 3, ipady = 10)


#####Show a list of all trains and their numbers#######
#Functions
def display_list():
	display_trains = Toplevel()
	display_trains.title('Table of Trains')
	
	class Table:

		def __init__(self, display_trains):

			for i in range(total_rows):
				for j in range(total_columns):

					self.e = Entry(display_trains)
					self.e.grid(row = i, column = j)
					self.e.insert(END, lst[i][j]) 
	  
	# take the data
	lst = [('S No.','Train Name', 'Train No.')]

	count = 1
	for i in all_train_csv_dict:
		lst.append((count, all_train_csv_dict[i][0], i))
		count += 1

	total_rows = len(lst)
	total_columns = len(lst[0])
	   
	t = Table(display_trains)

#Button to show a list of all trains and their schedules available
show_all_train_but = Button(root, text = 'Show a list of all trains and their no. available', command = display_list)
show_all_train_but.grid(row = len(data) + 2, column = 4, ipadx = 10, ipady = 10)

############Saving Logs##############
#Defing functions
def save_csv():
    with open('Logs/['+ today+ '] - ' +df, "w", newline='') as myfile:
        csvwriter = csv.writer(myfile)
        
        for row_id in tree.get_children():
            row = tree.item(row_id)['values']
            print('save row:', row)
            csvwriter.writerow(row)
#Button
logs_but = Button(root, text = 'Save Logs', command = save_csv)

today = date.today()
today = today.strftime("%b-%d-%Y")
#print("Logs/["+today+' : '+ now + ']'+df)

############## Need Help #############
def help():
	help_win = Toplevel()
	help_win.title('Help')
	with open('Read Me.txt', 'r') as fh:
		readme = fh.read()

	Label(help_win, text = readme).pack()

help_but = Button(root, text = 'Need Help?', command = help)
help_but.grid(row = len(data)+2, column = 7, ipady = 10, ipadx = 10)


root.mainloop()