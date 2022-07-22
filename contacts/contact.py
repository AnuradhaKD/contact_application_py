# import need module from tkinter
from multiprocessing.pool import TERMINATE
from tkinter import Tk, Button, PhotoImage, Label, LabelFrame, W, E, N, S, Entry, END, StringVar, Scrollbar,Toplevel, Widget, font

# provides access to Tk themed Widgets
from tkinter import ttk
#import db
import sqlite3

import sys

class Contacts:

    #--------------------------------------Create database--------------------------------------
    db_filename = 'contacts.db'

    #init
    def __init__(self, root):
        self.root = root
        self.create_gui()
        ttk.style = ttk.Style()
        ttk.style.configure("Treeview", font=('helvetica', 10))
        ttk.style.configure("Treeview.Heading", font=('helvetica', 12, 'bold'))
        
        
    #--------------------------------------execute database--------------------------------------
    def execute_db_query(self, query, parameters=()) :
        with sqlite3.connect(self.db_filename) as conn:
            print(conn)
            print("You have successfully connected to the DataBase . . . ")
            cursor = conn.cursor()
            query_result = cursor.execute(query, parameters)
            conn.commit()
        return query_result

    #--------------------------------------set gui interface--------------------------------------
    def create_gui(self):
        self.create_left_icon()
        self.create_label_frame()
        self.create_msg_area()
        self.create_tree_view()
        self.create_scrollbar()
        self.create_bottom_buttons()
        self.view_contacts()
        self.delete_contacts()

    # --------------------------------------left icon--------------------------------------
    def create_left_icon(self):
        photo = PhotoImage(file="icons/logo_1.gif")
        label = Label(image = photo)
        label.image = photo
        label.grid(row = 0, column = 0)
        
    #--------------------------------------create labels--------------------------------------
    def create_label_frame(self):
        labelframe = LabelFrame(self.root, text='Create New Contact', bg="sky blue", font="helvetica 10")
        Label(labelframe, text='Name', bg="green", fg="white").grid(row=1, column=1, sticky=W, padx=15, pady=2)
        labelframe.grid(row=0, column=1, padx=8, pady=8, sticky='ew')
        Label(labelframe, text='Name', bg="green", fg="white").grid(row=1, column=1, sticky=W, padx=15, pady=2)
        self.namefield = Entry(labelframe)
        self.namefield.grid(row=1, column=2, sticky=W, padx=5, pady=2)
        Label(labelframe, text='E-Mail', bg="brown", fg="white").grid(row=2, column=1, sticky=W, padx=15, pady=2)
        self.emailfield = Entry(labelframe)
        self.emailfield.grid(row=2, column=2, sticky=W, padx=5, pady=2)
        Label(labelframe, text='Number', bg="black", fg="white").grid(row=3, column=1, sticky=W, padx=15, pady=2)
        self.numfield = Entry(labelframe)
        self.numfield.grid(row=3, column=2, sticky=W, padx=5, pady=2)
        Button(labelframe, text="Add Contact", command=self.on_add_contact_button_clicked, bg="blue", fg="white").grid(row=4, column=2, sticky=E, padx=5, pady=5)

    #--------------------------------------msg area--------------------------------------
    def create_msg_area(self):
        self.message = Label(text='', fg='red')
        self.message.grid(row=3, column=1, sticky=W)

    def create_tree_view(self) :
        self.tree = ttk.Treeview(height=10, columns=("email", "number"), style='Treeview')
        self.tree.grid(row=6, column=0, columnspan=3)
        self.tree.heading('#0', text='Name', anchor=W)
        self.tree.heading('email', text='Email Address', anchor=W)
        self.tree.heading('number', text='Contact Number', anchor=W)

    def create_scrollbar(self) :
        self.scrollbar = Scrollbar(orient='vertical', command=self.tree.yview)
        self.scrollbar.grid(row=6, column=3, rowspan=10, sticky='sn')

    #--------------------------------------buttons--------------------------------------
    def create_bottom_buttons(self):
        Button(text='Delete Selected', command=self.on_delete_selected_button_clicked, bg="green", fg="white").grid(row=8, column=0, sticky=W, padx=20, pady=10)
        Button(text='Modify Selected', command=self.on_modify_selected_button_clicked, bg="purple", fg="white").grid(row=8, column=1, sticky=W)
        
    def on_add_contact_button_clicked(self):
        self.add_new_contact()

    def on_delete_selected_button_clicked(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'No Item selected to Delete'
            return
        self.delete_contacts()

    def on_modify_selected_button_clicked(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'No Item selected to Modify'
            return
        
        self.open_modify_window()

    def new_contacts_vallidated(self):
        return len(self.namefield.get()) != 0 and len(self.emailfield.get()) != 0 and len(self.numfield.get()) != 0
    
    #--------------------------------------View--------------------------------------
    def view_contacts(self):
        items = self.tree.get_children()
        for item in items:
            self.tree.delete(item)
        query = 'SELECT * FROM contact_list ORDER by name desc'
        contact_entries = self.execute_db_query(query)
        for row in contact_entries:
            self.tree.insert('', 0, text=row[1], values=(row[2], row[3]))

        #--------------------------------------adding new--------------------------------------
    def add_new_contact(self):
        if self.new_contacts_vallidated():
            query = 'INSERT INTO contact_list VALUES(NULL, ?, ?, ?)'
            parameters = (self.namefield.get(), self.emailfield.get(), self.numfield.get())
            self.execute_db_query(query, parameters)
            self.message['text'] = 'New Contact {} Added. '.format(self.namefield.get())
            self.namefield.delete(0, END)
            self.emailfield.delete(0, END)
            self.numfield.delete(0, END)
            self.view_contacts()

        else:
            self.message['text'] = 'name, email and number cannot be blank'
            self.view_contacts()

    #--------------------------------------delete contact--------------------------------------
    def delete_contacts(self):
        self.message['text'] = ''
        name = self.tree.item(self.tree.selection())['text']
        query = 'DELETE FROM contact_list WHERE name = ?'
        self.execute_db_query(query, (name,))
        self.message['text'] = 'Contacts for {} deleted '.format(name)
        self.view_contacts()

    #--------------------------------------Modify window--------------------------------------
    def open_modify_window(self):
        name = self.tree.item(self.tree.selection())['text']
        old_number = self.tree.item(self.tree.selection())['values'][1]
        self.transient = Toplevel()
        self.transient.title('Update Contact')
        Label(self.transient, text="Name: ").grid(row=0, column=1)
        Entry(self.transient, textvariable=StringVar(self.transient, value=name), state='readonly').grid(row=0, column=2)
        Label(self.transient, text='Old Contact Number: ').grid(row=1, column=1)
        Entry(self.transient, textvariable=StringVar(self.transient, value=old_number), state='readonly').grid(row=1, column=2)

        Label(self.transient, text='New Phone Number: ').grid(row=2, column=1)
        new_phone_number_entry_widget = Entry(self.transient)
        new_phone_number_entry_widget.grid(row=2, column=2)

        Button(self.transient, text='Update Contact', command= lambda: self.update_contacts(new_phone_number_entry_widget.get(), old_number, name)).grid(row=3, column=2, sticky=E)

        self.transient.mainloop()

    def update_contacts(self,newphone, old_phone, name):
        query = 'UPDATE contact_list SET number=? WHERE number=? AND name=?'
        parameters = (newphone, old_phone, name)
        self.execute_db_query(query, parameters)
        self.transient.destroy()
        self.message['text'] = 'Phone number of {} modified'.format(name)
        self.view_contacts()


#--------------------------------------main--------------------------------------
if __name__ == '__main__':
    root = Tk()
    root.title("My Contact List")
    root.geometry("650x450")
    root.resizable(width=False, height=False)
    application = Contacts(root)
    root.mainloop()