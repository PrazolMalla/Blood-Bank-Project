import time
from datetime import date
import matplotlib.pyplot as plt
from hospital import *
#* Preliminary Steps

#* Blood Compatibility Dictionary used for delivering blood that is compatible to blood demand if exact blood grp is not available in blood bank
blood_compatibility = {
    'A+':['A+','A-','O+','O-'],
    'A-':['A-','O-'],
    'B+':['B+','B-','O+','O-'],
    'B-':['B-','O-'],
    'O+':['O+','O-'],
    'O-':['O-'],
    'AB+':['AB+','AB-','A+','A-','B+','B-','O+','O-'],
    'AB-':['AB-','A-','B-','O-'],
}



print("<<< LifeServe Blood Institute >>>")

#* creating empty tuples to store data from text file 
donar_data=()
stock_data=()

#*load database function
def load_db(donor_fname,stock_fname):
    try: 
        file1 = open(donor_fname,'r')
        file2 =open(stock_fname,'r')
        donar_lines = file1.readlines()
        global donar_data
        #* storing data line wise in tuples
        donar_data = [tuple(line.strip().split(',')) for line in donar_lines]
        global stock_data
        stock_lines = file2.readlines()
        stock_data = [tuple(line.strip().split(',')) for line in stock_lines]
    except:
        print("File not found")


#*save database function
def save_db(donate_newdata,stock_newdata):
     with open('data/donors-new.txt', 'w') as f:
        f.write(','.join(donate_newdata)) 
     with open('data/bags-new.txt', 'w') as fp:
        fp.write(','.join(stock_newdata))

time.sleep(3) #* adds delay in output
print('Loading database.....')

#* taking filename from user
df = input('''Enter the database file names without .txt extension
or just press Enter to accept defaults
Donors database (donors): 
''')

sf = input('Stock inventory database (bags): ') 

if(df !=""):
    donar_fname = 'data/'+df+'.txt'
else:
    donar_fname='data/donors.txt'

if(sf !=""):
    stock_fname = 'data/'+sf+'.txt'
else:
    stock_fname='data/bags.txt'


load_db(donar_fname,stock_fname)


#* Function to work  


#*Check inventory function
global expired_blood
expired_blood =[]
today = date.today()
def check_inventory():
   global count
   count = 0
   
   for stock in stock_data:
        # checking bloods that are expired_blood
        some_date = date.fromisoformat(stock[2])
        days_diff = (today - some_date).days  
        if(days_diff>30):
            expired_blood.append(stock[0])
            print(stock[0])
            count +=1

#* check demand Function 
def demand():
  
    
    blood_demand  = check_demand()#* from hospital.py
    # blood_demand  = "O+"
    time.sleep(2)
    if blood_demand!="X":
        print(f'''Currently {blood_demand} blood is required.
Checking the stock inventory...
    ''')
        countblood = 0
        compat = 0
        days_dif = []
        stock_index = []
        for stock in stock_data:
            if stock[1] == blood_demand:  #* blood demand matches blood that is in stock
                countblood =  1
                break
            for bloods in blood_compatibility[blood_demand]: #* blood demand doesn't matches blood that is in stock but compatible blood is available
                if bloods == stock[1]:
                    some_date = date.fromisoformat(stock[2])
                    days_dif.append((today - some_date).days)
                    stock_index.append(stock_data.index(stock)) 
                    compat = 1
            
        if(compat == 1):
           day = max(days_dif)
           i = stock_index.index(days_dif.index(day))
           countblood = 1
                   
        if countblood == 1:
               time.sleep(2)
               print(f'''Following bag should be supplied
ID: {stock_data[i][0]}({stock_data[i][1]})''')
               key = input('Press any key once it is packed for dispatch...')
               print(f'''Inventory records updated.
Updated database files saved to disk.
''')            
               #*deleting the blood that is dispatched 
               if(keys or keys==''):
                expired_blood.append(stock_data[i][0])
                delete_data(stock_fname)
                load_db(donar_fname,stock_fname)
        
        else: # if there is no blood that is compatible to blood demand in stock
            print("We can not meet the requirement. Checking the donor database...")
            print("Following donors match the requirements. Please contact them for new donation.")
            for donar in donar_data:
                if blood_demand == donar[4]:
                    print(f". {donar[1]},{donar[2]},{donar[3]}")
               
            
    else:
        print('''Could not connect to hospital web server.
Please try again after some time.
''')
    return 0 


#* record new donation 
def record():
    donar_id = input("Enter the donor's unique ID: ")
    for donar in donar_data:
        if(donar_id == donar[0]):
            donated_date = date.fromisoformat(donar[-1])
            ddays_diff = (today - donated_date).days  
            if(ddays_diff>=120):
                print("Recording a new donation with following details:")
                print(f'''From :{donar[1]} 
Group:{donar[4]} 
Date :{today}(today) 
Bag Id:{int(stock_data[-1][0])+1}
                      ''')
                opt = input('Please confirm (y/n): ')
                if opt == "Y" or opt =="y" :
                    new_donar = list(donar[0:5]) + [str(today)]  
                    new_stock = [str(int(stock_data[-1][0]) + 1), donar[4], str(today)] 
                    save_db(new_donar,new_stock)
                    print(f'''Done. Donor's last donation date also updated to {today}
Updated database files saved to disk.
''')
                else:
                    print("Cancelled")
            else:
                print("not eligible")
        
#* function to show pie chart
def stock():
    partition = []
    count_blood_g=[]
    new_partition=[]
    for stock in stock_data:
        partition.append(stock[1])
    # so that the blood doesn't repeat
    for bloodg in partition:
        if bloodg not in new_partition:
            new_partition.append(bloodg)


    for bloodg in new_partition:
        #* suppose there is A+ twice in database so count must be 2 but must come only once so we use
        #* newpartition and partition if not partition = [A+,A+,B+] count = [2,2,1]  
        count_blood_g.append(partition.count(bloodg))
    fig1,ax1 = plt.subplots()
    ax1.pie(count_blood_g,labels=new_partition,autopct= lambda p:f'{p*sum(count_blood_g)/100 :.0f}',shadow=True,startangle=90)
    ax1.axis('equal')
    plt.show()
    print('''Pie chart opens in a new window...
Close the chart window to continue
''')

#* function to delete stock
def delete_data(stock_fname):
    file2 =open(stock_fname,'r')
    stock_lines = file2.readlines()
    with open(stock_fname, 'w') as fp:
        for number,line in enumerate(stock_lines):
            count1= 0
            for s in expired_blood:
                if(line[0:4]==s):
                    count1= 1
                    break
            if(count1==0):
               fp.write(line)
    fp.close()

                


#* MENU *

choice = 0 
while (choice!=5):
    print('''----------------
    Main Menu
----------------
    ''')
    print('(1) Check inventory')
    print('(2) Attend to blood demand')
    print('(3) Record new donation')
    print('(4) Stock visual report')
    print('(5) Exit')
    choice = int(input("Enter your choice: "))
    if(choice == 1):
        print('Following bags are out of their use-by date')
        check_inventory()
        if(count >0):
            keys =input('Please dispose them of. Press any key when done...')
            if(keys or keys==''):
                delete_data(stock_fname)
                print("Updated database files saved to disk.")
                load_db(donar_fname,stock_fname)
        else:
            print('There is nothing to dispose')
        
    elif(choice==2):
        demand()

    elif(choice==3):
        record()

    elif(choice==4):
        stock()

    elif(choice==5):
        exit()
    else:
        print("You Enter a wrong choice")

