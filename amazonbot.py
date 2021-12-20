import threading
import os
import time
from datetime import datetime
from matplotlib import animation
import matplotlib.pyplot as plt
import pandas as pd
import PySimpleGUI as sg
from selenium import webdriver
from csv import DictWriter
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


right_click_menu = ['', ['Copy', 'Paste']]

file_list_column = [
    [
        sg.Text("ASIN NO"),
        sg.Input(size=(20, 1), key="-IN-", right_click_menu=right_click_menu),
        sg.Button(button_text='Search', key= '-SEARCH-'),

    ],
    [   sg.Text('SERVER'),
        sg.Combo(['www.amazon.com','www.amazon.de',],default_value='www.amazon.com',size=(20,1),key='-SERVER-'),
    ],

    [   sg.Text('Check every '),
        sg.Input(default_text='10', size=(5,1),key='-MINUTES-'),
        sg.Text('minute(s)')
    ],
    [
        sg.Listbox(values=[], enable_events=True, size=(40, 25), key="-SEARCHEDLIST-")
    ],
    [
        sg.Button(button_text='Graph', key='-SHOWLINEGRAPH-'),
        sg.Button(button_text='Delete', key='-DELETE-')
    ],    
]
file_viewer_column = [
    [sg.Text("")],
    [sg.Text(size=(1, 1), key="-TOUT-")],
    [sg.Image(key='-IMAGE-')],
]
layout = [
    [
        sg.Column(file_list_column),
    ]
]
window = sg.Window("Amazon Stock", layout).Finalize()
mline:sg.Input = window["-IN-"]
# Important values----------------
alist = []
ASINno = ''
header = ["Time","Stock"]
data={}
plt.style.use('fivethirtyeight')
# show_only_sold = False
# -----------------------------



def animate(i):
    data = pd.read_csv('result'+ASINno+'.csv')
    x = data['Time']
    y = data['Stock']
    x = x[-25:]
    y = y[-25:]
    txt = list(y)[-1]
    
    plt.cla()
    plt.plot(x, y, label=txt)
    plt.title(ASINno)
    
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)

def linegraph(current_asin):
        graph_asin = current_asin
        data = pd.read_csv('result'+graph_asin+'.csv')
        x = data['Time']
        y = data['Stock']
        x = x[-20:]
        y = y[-20:]

        line = plt.plot(x[0], y[0], linestyle='solid')

        plt.title(ASINno, fontsize=16)
        plt.ylabel('Stock', fontsize=10)
        plt.xlabel('Time', fontsize=10)


        plt.ion()   # set interactive mode
        plt.show()
        for i, row in data.iterrows():
            line = plt.plot(x[i], y[i], linestyle='solid')
            plt.gcf().autofmt_xdate()
            plt.gcf().canvas.draw()
            plt.pause(4)
        return line

def csv_Update(data):
    with open ('result'+ASINno+'.csv','a') as csv_file:
        csv_writer = DictWriter(csv_file, fieldnames=header)
        csv_writer.writerow(data)
        csv_file.close()

def get_url(search_term,server):
    template = 'http://'+server+'/s?k='+search_term+'&ref=nb_sb_noss'
    search_term = search_term.replace(' ','+')
    return template.format(search_term)

def search_thread(window):
    while True:
        asn = values["-IN-"]
        server_id = values['-SERVER-']
        try:
            driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.maximize_window()
            url1 = 'http://'+server_id+'/'
            url2 = 'http://'+server_id+'/gp/cart/view.html?ref_=nav_cart'
            driver.get(url1)
            driver.implicitly_wait(5)

            if os.path.isfile('./result'+asn+'.csv')==False:
                with open('result'+asn+'.csv','w') as csv_file:
                    csv_writer = DictWriter(csv_file, fieldnames=header)
                    csv_writer.writeheader()

            url = get_url(asn,server_id)
            driver.get(url)

            xPATH = '//div[@data-asin='+"'"+asn+"']"
            driver.find_element_by_xpath(xPATH).click()
            break
        except:
            print('Could not open find item, Check the ASIN number')
            break


    try:
        driver.find_element_by_id('add-to-cart-button').click()
    except:
        print('Error : First method not worked')
    # For diffrent cart button
    try:
        driver.find_element_by_id('attach-view-cart-button-form').click()        
    except:
        print('Error : Second method not worked')        
    
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(url2)
    driver.switch_to.window(driver.window_handles[0])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    driver.implicitly_wait(3)

    while True:
        try:
            driver.find_element_by_class_name('quantity').click()
            driver.find_element_by_id("quantity_10").click()
            driver.find_element_by_name('quantityBox').send_keys('999')
            driver.find_element_by_id("a-autoid-1").click()
            driver.implicitly_wait(3)
            break
        except:
            print("First Value Error")
            break

    while True:
        ss = driver.find_element_by_name('quantityBox')
        driver.execute_script("arguments[0].value='999';", ss)
        driver.find_element_by_class_name('a-spacing-top-small').submit()
        driver.implicitly_wait(60)
        driver.refresh()
        
        # set first value
        ss = driver.find_element_by_name('quantityBox')
        lastStock = ss.get_attribute('value')
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        data={'Time':current_time,'Stock':lastStock}
        
        with open ('result'+asn+'.csv','a') as csv_file:
            csv_writer = DictWriter(csv_file, fieldnames=header)
            csv_writer.writerow(data)
            csv_file.close()

        stock_check_duration=values['-MINUTES-']
        time.sleep((int(stock_check_duration)*60)-3)
        try:
            b=alist.index(asn)
        except ValueError:
            pass
        else:
            pass

def search():
    threading.Thread(target=search_thread, args=(window,), daemon=True).start()


while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event == "-SEARCHED LIST-":  # A file was chosen from the listbox
        try:
            # filename = os.path.join(values["-IN-"], values["-SEARCHEDLIST-"][0])
            # window["-TOUT-"].update(filename)
            # window["-IMAGE-"].update(filename=filename)
            pass

        except:
            pass

    elif event =='-SEARCH-':
        try:
            a = values["-IN-"]
            if a in alist:
                print(a + '  already exist in list')
            elif a =='':
                print('Try again')    
            else:
                alist.append(a)
                window["-SEARCHEDLIST-"].update(alist)
                time.sleep(1)
                search()

        except:
            pass

    elif event == '-SHOWLINEGRAPH-':
        try:
            ASINno = values["-SEARCHEDLIST-"][0]
            anime_data = animation.FuncAnimation(plt.gcf(), animate, interval= 1000)
            plt.show()

        except:
            
            pass

    elif event == '-DELETE-':
        try:
            selected = values["-SEARCHEDLIST-"][0]
            alist.remove(selected)
            window["-SEARCHEDLIST-"].update(alist)

        except:
            pass

    elif event == 'Copy':
        try:
            text = mline.Widget.selection_get()
            window.TKroot.clipboard_clear()
            window.TKroot.clipboard_append(text)
        except:
            print('Nothing selected')

    elif event == 'Paste':
        mline.Widget.insert(sg.tk.INSERT, window.TKroot.clipboard_get())


window.close()
