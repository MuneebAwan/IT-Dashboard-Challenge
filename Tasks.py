import re
from time import sleep
import configparser
from RPA.Browser.Selenium import Selenium
import time
from RPA.Excel.Files import Files
import os
from RPA.Tables import Column
import shutil
browser_lib = Selenium()
excel_obj = Files()
dashboard = "Welcome to IT Dashboard | IT Dashboard"


def  get_agency_name():
    current_dir = os.getcwd()
    print(current_dir)
    agency_dir= current_dir+"\\Output_Files\\Agency Configuration"
    config = configparser.ConfigParser()
    print(agency_dir+'\\Config.ini')
    if os.path.exists(agency_dir+'\\Config.ini'):
        config.read(agency_dir+'\\Config.ini')
        agency_name = config.get('Agencyname','Agency')
        return agency_name
    else:
        return ''
def create_excel_file(path_to_file): 
    print("start of create_excel_file")
    
    if os.path.exists(path_to_file):
        print("file already exist")
    else:
        wb=excel_obj.create_workbook(path_to_file,'xlsx')
        sb=wb.create_worksheet("Agencies")
        excel_obj.set_worksheet_value(1,1,"Agencies Name")
        excel_obj.set_worksheet_value(1 ,2 ,"Amount")
        excel_obj.save_workbook(path_to_file)
        excel_obj.close_workbook()
    print("end of create_excel_file")   

def  go_to_agency_page(agency,path_to_file):
    print("end of go_to_agency_page")
    print("agency============ : ",agency)
    time.sleep(5)
    browser_lib.scroll_element_into_view('''//a[@href="#read-more-row-2"]''')
    time.sleep(10)
    browser_lib.click_link('''//a[@href="#read-more-row-2"]''')
    time.sleep(20)
    browser_lib.scroll_element_into_view('''//select[@name="investments-table-object_length"]''')
    time.sleep(20)
    browser_lib.select_from_list_by_label('''//select[@name="investments-table-object_length"]''','All')
    time.sleep(5)
    # extract headers
    browser_lib.scroll_element_into_view('''//*[@id="investments-table-object_wrapper"]/div[3]/div[1]/div/table/thead/tr[2]/th[1]''')
    time.sleep(5)
    column = '''//*[@id="investments-table-object_wrapper"]/div[3]/div[1]/div/table/thead/tr[2]/th'''
    row = '''//*[@id="investments-table-object"]/tbody/tr'''
    
    excel_obj.open_workbook(path_to_file)
    excel_obj.create_worksheet(agency)
    excel_obj.save_workbook(path_to_file)
    excel_obj.close_workbook()
    url_list =extract_data_from_table(path_to_file,column,row)
    print("end of go_to_agency_page")
    return url_list
def  extract_data_from_table(path_to_file,column,row):
    print("start of extract_data_from_table")
    excel_obj.open_workbook(path_to_file)
    column_count = browser_lib.get_element_count(column)
    # get the table headers
    for c in range (1,column_count+1):
        column_headers = browser_lib.get_text('''//*[@id="investments-table-object_wrapper"]/div[3]/div[1]/div/table/thead/tr[2]/th[{}]'''.format(c))
        excel_obj.set_cell_value(1,c,column_headers)
        excel_obj.save_workbook(path_to_file)
    
    url_list = []
    
    row_count = browser_lib.get_element_count(row)
    
    browser_lib.scroll_element_into_view('''//*[@id="investments-table-object_wrapper"]/div[3]''')
    
    for j in range (1,column_count+1):
        for i in range (1,row_count+1):
            text = browser_lib.get_text('''//*[@id="investments-table-object"]/tbody/tr[{0}]/td[{1}]'''.format(i,j))
            element_attribute = browser_lib.get_element_attribute('''//*[@id="investments-table-object"]/tbody/tr[{0}]/td[1]/a'''.format(j),"href")
            if type(element_attribute) == str:
                url_list.append(element_attribute) if element_attribute not in url_list else url_list
                url_list.append(element_attribute)

            excel_obj.set_cell_value(i+1,j,text)
            excel_obj.save_workbook(path_to_file)
    
    excel_obj.close_workbook()
    
    print("start of extract_data_from_table")
    return  url_list
def write_agencies_data_to_excel(path_to_file):
    print("start of write_agencies_data_to_excel")
    excel_obj.open_workbook(path_to_file)
    configured_agency_name = get_agency_name()
    if configured_agency_name=='':
        print("No Agency in configured in the  Config.ini file")
    else:
        browser_lib.scroll_element_into_view('''//*[@id="home-dive-in"]/div/div[2]''')
        element_count = browser_lib.get_element_count('''//*[@id="agency-tiles-widget"]/div/div[*]/div[*]''')
        element_count= element_count+1
        
        print("element_count ==== ",element_count)
        rows= int(element_count/3)
        print(rows)
        Column = int(element_count/rows)
        print(Column)  
        for row_index in range (1,rows+1):
            for column_index in range (1,Column+1):
                agency=  browser_lib.get_text('''//*[@id="agency-tiles-widget"]/div/div[{0}]/div[{1}]/div/div/div/div[1]/a/span[1]'''.format(row_index,column_index))
                if str(configured_agency_name)!=str(agency):
                     continue
                     
                else:
                    print(configured_agency_name)
                    browser_lib.click_element('''//*[@id="agency-tiles-widget"]/div/div[{0}]/div[{1}]/div/div/div/div[1]/a/span[1]'''.format(row_index,column_index))
                    url_list =go_to_agency_page(str(agency),path_to_file)
                    break
            break 
        return url_list
def download_wait(file_path):
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < 40:
        time.sleep(1)
        dl_wait = False
        if os.path.exists(file_path):
                dl_wait = True
        seconds += 1
    return seconds
def  download_pdf_file(url_list):
    
    url_list = set(url_list)
    # convert the set to the list
    url_list = (list(url_list))
    print(url_list)
    
    browser_lib.open_available_browser("https://google.com/")
    
    current_dir = os.getcwd()
    output_dir= current_dir+"\\Output_Files"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    download_dir =os.environ['USERPROFILE'] + '\Downloads'
    
    file_source = download_dir
    file_destination = output_dir+"\\"
    for i in url_list:
        pdf_name = i.split("/")
        file_source = download_dir+'\\'+pdf_name[-1]+".pdf"
        browser_lib.go_to(i)
        browser_lib.wait_until_element_is_visible('''//a[@href="#"]''')
        browser_lib.click_link('''//a[@href="#"]''')
        download_wait(file_source)
        print(file_source)
        time.sleep(20)
        if os.path.exists(file_source):
            if not os.path.exists(file_destination+"\\"+pdf_name[-1]+".pdf"):
                shutil.move(file_source , file_destination)
        else:
            print("no file exist")
    browser_lib.close_browser  
def open_the_website(url):
    browser_lib.open_available_browser(url)
def main():
    try:
        agency_title_widget ="agency-tiles-container"
        cur_dir = str(os.getcwd())
        output_dir= cur_dir+"\\Output_Files"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        path_to_file = str(output_dir)+"\\"+"Output File.xlsx"
        if os.path.exists(path_to_file):
            os.remove(path_to_file)
        create_excel_file(path_to_file)
        open_the_website("https://itdashboard.gov/")
        browser_lib.maximize_browser_window()
        browser_lib.click_link('//a[@href="#home-dive-in"]')
        browser_title = browser_lib.get_window_titles()
        print(browser_title)
        browser_lib.scroll_element_into_view('''//*[@id="agency-tiles-container"]''')
        time.sleep(15)
        web_elements = browser_lib.get_text('''//*[@id="agency-tiles-container"]''')
        str_list = web_elements.split("view")
        str_list = [x.strip() for x in str_list if x.strip()]
        excel_obj.open_workbook(path_to_file)
        counter = 2
        for items in str_list:
            text = items.split('\n')
            agency_name = text[0]
            amount = text[2]
            excel_obj.set_worksheet_value(counter,1,agency_name)
            excel_obj.set_worksheet_value(counter ,2 ,amount)
            counter=counter+1
            excel_obj.save_workbook(path_to_file)
        excel_obj.close_workbook()
        url_list = write_agencies_data_to_excel(path_to_file)
        download_pdf_file(url_list)
    except print(0):
        pass
    finally:
        browser_lib.close_all_browsers
   
    
if __name__ == "__main__":
        main()
        