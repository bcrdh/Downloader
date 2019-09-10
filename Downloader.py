import datetime
import os
import time
from tkinter import *
from tkinter import messagebox
from tkinter import ttk

import urllib3.util.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from tkcalendar import DateEntry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
usernameStr = ""
passwordStr = ""

def signIn(browser, usernameStr, passwordStr):
    #usernameStr = 'Sharon Hanna'
    #passwordStr = '0re02oo2'  
    browser.get('https://doh.arcabc.ca/user/login')
    # fill in username and hit the next button
    username = browser.find_element_by_id('edit-name')
    username.send_keys(usernameStr)
    password = browser.find_element_by_id('edit-pass')
    password.send_keys(passwordStr)
    signInButton = browser.find_element_by_id('edit-submit')
    signInButton.click()

#disable XACML (remove restrictions on object management and access)
# def disableXACML(browser, repo, colln):
#     url = "https://doh.arcabc.ca/islandora/object/" + repo + "%3A" + colln + "#overlay=islandora/object/" + repo + "%253A" + colln + "/manage/xacml"
#     browser.get(url)
#     #Deselect checkbox only when it is selected 
#     result = browser.find_element_by_id("edit-access-enabled").is_selected();
#     if result:
#         togglePerm = True  
#         browser.find_element_by_id("edit-access-enabled").click()
#         browser.find_element_by_id("edit-submit").click()
#         print('Checkbox deselected')
#         #select = Select(browser.find_element_by_id("edit-update-options"))
#         #select.select_by_value('all_children')
#         select = Select(browser.find_element_by_id('edit-update-options'))
#         selected_option = select.first_selected_option
#         print(selected_option.text)
#         #print(storeSelectedId( selectLocator, variableName))
#         print("all children selected")
#         setPerm = browser.find_element_by_id('edit-submit')
#         setPerm.click()
#         print('permissions set')    
#         print('XACML has been disabled for ' + colln)
#     else:
#         print('Checkbox already deselected')
#         select = Select(browser.find_element_by_id('edit-update-options'))
#         selected_option = select.first_selected_option
#         print(selected_option.text)
#         #print(storeSelectedId( selectLocator, variableName))
#         print("all children selected")
#         setPerm = browser.find_element_by_id('edit-submit')
#         setPerm.click()
#         print('permissions set')    
#         print('XACML has been disabled for ' + colln)
#         #select.select_by_value('all_children')
#        
# def selectMult(browser,selecList):
#     for item in selecList:
#         ActionChains(browser).key_down(Keys.CONTROL).click(item).key_up(Keys.CONTROL).perform()
#
#enable XACML (enforce restrictions on object management and access) 
# def enableXACML(browser, repo, colln):
#     url = "https://doh.arcabc.ca/islandora/object/" + repo + "%3A" + colln + "/manage/xacml?render=overlay"
#     browser.get(url)
#     
#     #Tick box
#     print(browser.find_element_by_id("edit-access-enabled").is_selected())
#     #print(result)
#     if browser.find_element_by_id("edit-access-enabled").is_selected():
#         print('Checkbox already selected')
#         return
#     else:
#         browser.find_element_by_id("edit-access-enabled").click();
#         print('Checkbox selected')
#     
#         usrs = []
#         usrs.append(browser.find_element_by_xpath("//select[@name='access[users][]']/option[text()='brandonw']"))
#         usrs.append(browser.find_element_by_xpath("//select[@name='access[users][]']/option[text()='Chris Hives']"))
#         usrs.append(browser.find_element_by_xpath("//select[@name='access[users][]']/option[text()='dgiadmin']"))
#         usrs.append(browser.find_element_by_xpath("//select[@name='access[users][]']/option[text()='dimnamkhao']"))
#         usrs.append(browser.find_element_by_xpath("//select[@name='access[users][]']/option[text()='eamonrs']"))
#         usrs.append(browser.find_element_by_xpath("//select[@name='access[users][]']/option[text()='ehomolka']"))
#         usrs.append(browser.find_element_by_xpath("//select[@name='access[users][]']/option[text()='paigeh']"))
#         usrs.append(browser.find_element_by_xpath("//select[@name='access[users][]']/option[text()='Sharon Hanna']"))
#         usrs.append(browser.find_element_by_xpath("//select[@name='access[users][]']/option[text()='sunnin']"))
#         usrs.append(browser.find_element_by_xpath("//select[@name='access[users][]']/option[text()='KaylaHilstob']"))
#         usrs.append(browser.find_element_by_xpath("//select[@name='access[users][]']/option[text()='Kayla Hilstob']"))
#         usrs.append(browser.find_element_by_xpath("//select[@name='access[users][]']/option[text()='Sharon Hanna']"))
#         
#         selectMult(usrs)
#         
#         roles = [] 
#         roles.append(browser.find_element_by_xpath("//select[@name='access[roles][]']/option[text()='administrator']"))
#         roles.append(browser.find_element_by_xpath("//select[@name='access[roles][]']/option[text()='IR staff']"))
#         roles.append(browser.find_element_by_xpath("//select[@name='access[roles][]']/option[text()='Local administrator']"))
#         roles.append(browser.find_element_by_xpath("//select[@name='access[roles][]']/option[text()='repositories']"))
#         
#         selectMult(roles)
#         
#         select = Select(browser.find_element_by_xpath("//select[@name='update_options']"))
#         select.select_by_value('all_children')
#         print("all children selected")
#          
#         setPerm = browser.find_element_by_id('edit-submit')
#         setPerm.click()
#         print('permissions set')
#         togglePerm = False
#         print('XACML has been enabled')

def grabDate(browser, repo, objNum, fromDate, toDate):    
    revDate = "000000"
    modsVersions = 'https://doh.arcabc.ca/islandora/object/' + repo + '%3A' + objNum + '/datastream/MODS/version#overlay-context=islandora/object/'
    modsVersions += repo + '%253A' + objNum + '3%3Fsolr_nav%255Bid%255D%3Db14ff4ceba3e979a9556%26solr_nav%255Bpage%255D%3D0%26solr_nav%255Boffset%255D%3D0'
    mngData = 'https://doh.arcabc.ca/islandora/object/' + repo + '%3A' + objNum + '?solr_nav%5Bid%5D=b14ff4ceba3e979a9556&solr_nav%5Bpage%5D=0&solr_nav%5Boffset%5D=0#overlay=islandora/object/'
    mngData += repo + '%253A' + objNum + '/manage/datastreams'
    browser.get(modsVersions)
    try:
        dt = browser.find_element_by_css_selector('td.datastream-date')
        v0Arr = dt.get_attribute('innerHTML').split()
        dtStr = v0Arr[2]
        revDate = datetime.datetime.strptime(dtStr,'%d-%b-%y').strftime('%Y%m%d') #convert date to yymmdd string format
    except NoSuchElementException as e:
        print("Broke at " + modsVersions)
        print(e)
    return (int(revDate) <= toDate and int(revDate) >= fromDate) #if date on or after fromDate and on or after toDate, return T, else return F   

def download(browser, savePath, collName, fromDate, toDate):
    repolist = ['arms:armsmin', 'arms:cheerio', 'arms:photographs', 'arms:spallmin', 'arms:spallroll','boundary:oralhistory','enderby:inland', 'enderby:photographs','hedley:photographs', 'kdgs:reports']
    repolist += ['lake:goulding','lake:photographs','lumby:photographs', 'naramata:irrigation', 'naramata:photographs', 'naramata:robinson','okeefe:lantern','okeefe:photographs','osoyoos:ofb']
    repolist += ['osoyoos:photographs', 'peach:assessment','peach:buildings', 'peach:photographs','sicamous:photographs','ssm:keremeos','summer:photographs','summer:postcards','summer:womens','westbank:bridge']
    
    if collName != "All DOH MODS":
        coll = collName.split(" -- ")[1].strip()
        print(coll)
        repolist = [coll]
    def my_filter(tag):
            return(tag.name=="a" and
                   tag.parent.name=="dt" and
                   "islandora-object-thumb" in tag.parent["class"])

    def getObjNums():
            for a in bs.find_all(my_filter):
                objURLlist.append(str(a))
 
    for i in range(len(repolist), 0, -1):
        count = 0
        rep = repolist[i-1]
        objURLlist = []
        objNums = []
        dirName = ""
        collNm = ""
        repNm = ""
        repNm = rep.split(":")[0]
        collNm = rep.split(":")[1]
        print(repNm)
        print(collNm)
        
        dirName = repNm + "_" + collNm
        baseURL = r"https://doh.arcabc.ca/islandora/object" + '/' + repNm + "%3A" + collNm
        savePath += dirName
       
        if not os.path.exists(savePath):    #if folder does not exist
            os.makedirs(savePath)           #create it
        browser.get(baseURL)
        source = browser.page_source
        bs = BeautifulSoup(source, "html.parser") 
        lstPgLnk = bs.find('li',class_="pager-last last")
        
        if lstPgLnk is None:    #if collection has only 1 page
            last = 0
        else:
            lstPgStr = str(lstPgLnk)
            beg = lstPgStr.find("page=") + 5
            end = lstPgStr.find("title=") - 2
            lastP = lstPgStr[beg:end]
            last = int(lastP)
            
        for i in range(0, last + 1):
            if i == 0:          #if on first page of collection
                getObjNums()
            else:
                currURL = baseURL + "?page=" + str(i)
                browser.get(currURL)
                source = browser.page_source
                bs = BeautifulSoup(source, "html.parser") 
                getObjNums()    
        begStr = '<a href="/islandora/object/' +  repNm + r'%3A'
        beg = len(begStr)
   
        for u in objURLlist:
            end = int(u.find("title=") - 2) 
            num = u[beg:end]
            objNums.append(num)

        for num in objNums:
            try:
                if (grabDate(browser, repNm, num, fromDate, toDate)):  
                    objU = r"https://doh.arcabc.ca/islandora/object" + "/" + repNm + "%3A" + num + "/" + r"datastream/MODS/view#overlay-context=islandora/object" + "/" + repNm + "%253A" + num
                    auth = usernameStr + ":" + passwordStr
                    headers = urllib3.util.request.make_headers(disable_cache=True, basic_auth=auth)
                    http = urllib3.PoolManager()
                    r = http.request('get', objU, headers=headers)
                    filename = repNm + '_' + num + '.xml'
                    completeNm = savePath + r'/' + filename
                    with open(completeNm, 'wb') as file:
                        file.write(r.data)
                        count += 1
            except NoSuchElementException:
                print("Broke at " + repNm + ":" + num)
                continue    
        rep = rep.replace(":","_")

        if count==0:
            msg = "Sorry, no XML records matching your date criteria were found for the collection '" + rep + "'."
            messagebox.showinfo(title = 'No records were downloaded.', message = msg)
                
        elif count==1:
            msg = "1 XML record has been written to the " + rep + " folder on your Desktop."
            messagebox.showinfo(title = 'One record was downloaded.', message = msg)
        else:
            msg =  str(count) + " XML records have been written to the " + rep + " folder on your Desktop."
            messagebox.showinfo(title = 'Success!', message = msg)
        
class Downloader:     
    def __init__(self, master):
        master.title('MODS XML Downloader')
        #master.resizable(False, False)
        master.configure(background = '#ffffff')
        master.config(height = 900, width = 600)      
        self.style = ttk.Style()
        self.style.configure('TFrame', background = '#ffffff')
        self.style.configure('TButton', background = 'blue')
        self.style.configure('TLabel', font = ('Arial', 11),background='#ffffff', foreground = '#000000')#, background = '#e1d8b9', font = ('Arial', 11))
        self.style.configure('Header.TLabel', font = ('Arial', 16, 'bold'), foreground="#2223ED")      
        
        self.folder=''
        self.frame_header = ttk.Frame(master, relief="sunken")
        self.frame_header.pack(fill=BOTH, expand=1)
        self.frame_header.config(width=600,height=900) 
        self.logo = PhotoImage(file = 'data_files/DOH.gif').subsample(5, 5)
        ttk.Label(self.frame_header, image = self.logo).grid(row = 0, column = 0,pady=(5,5), padx=(40,0),sticky='se')
        ttk.Label(self.frame_header, text = "DOH MODS XML Downloader", style='Header.TLabel').grid(row = 0, column = 1,pady=(0,10), padx=(40,0),sticky='se')
        self.frame_content = ttk.Frame(master, relief="sunken")
        self.frame_content.pack(fill=BOTH, expand=1)
        ttk.Label(self.frame_content, text='Arca Username:').grid(row = 2, column = 0, padx = (65,0), pady=(10,5), sticky = 'sw')
        self.uName = ttk.Entry(self.frame_content, width = 30)
        self.uName.grid(row = 3, column = 0, padx = (65,0), pady=(0,5), sticky = 'sw')
        ttk.Label(self.frame_content, text='Arca password:').grid(row = 2, column = 0, padx = (300,10), pady=(10,5), sticky = 'sw')
        self.pw = ttk.Entry(self.frame_content, width = 30)
        self.pw.grid(row = 3, column = 0, padx = (300,10), pady=(0,5), sticky = 'sw')
        self.pw.config(show = '*')
            
        self.savePath = os.path.expanduser('~') + '\\Desktop\\'        
        ttk.Label(self.frame_content, text = "This program will use your web browser in automated mode. After a collection's XML\nhas been downloaded, you will get a popup notice. Click 'OK' on the popup to continue.").grid(row = 6, column = 0, padx = (65,65), pady=(30,10), sticky = 'sw')
        self.colln = StringVar()
        vals = ('All DOH MODS','Armstrong Cheerio Club -- arms:cheerio','Armstrong City Minutes -- arms:armsmin')
        vals += ('Armstrong High School -- arms:school','Armstrong Photograph Collection -- arms:photographs', "B.C.'s Inland Empire (Enderby) -- enderby:inland","Boundary Oral Histories -- boundary:oralhistory","Enderby Photographs -- enderby:photographs")
        vals += ('Goulding Collection (Lake Country) -- lake:goulding','Hedley Photographs -- hedley:photographs','KDGS Reports -- kdgs:reports','Lumby Photographs -- lumby:photographs', 'Municipality of Spallumcheen Land Rolls (Armstrong) -- arms:spallroll', "O'Keefe Lantern Glass Slides -- okeefe:lantern", "O'Keefe Ranch Photograph Collections -- okeefe:photographs")
        vals += ('Osoyoos Fire Brigade fonds -- osoyoos:ofb','Peachland Student Photographs -- peach:studentphotos','Spallumcheen Township Minutes (Armstrong) -- arms:spallmin','Stokes Fonds (Lake Country) -- lake:photographs','Westbank Bridge -- westbank:bridge')
        self.comboLabel = ttk.Label(self.frame_content, text="Please choose a single collection or 'All DOH MODS':")
        self.comboLabel.grid(row=7,column=0,sticky='sw',padx = 65, pady=(20,0))
        self.combobox = ttk.Combobox(self.frame_content, values=vals, width = 60, height = 300,state="readonly")
        self.combobox.bind("<<>ComboboxSelected>")
        self.combobox.grid(row=8, column=0,sticky='sw', padx=65)#,pady=(0,40)) # columnspan = 5, rowspan = 5,
        self.combobox.configure(height=100)   
        self.combobox.config(values = vals)
       
        def getCurrDate():
            now = str(datetime.datetime.now())[:10]
            return now
        self.currdate=getCurrDate()
        msg = 'Limit records by date (between 2017-05-01 and ' + self.currdate + "):"
        ttk.Label(self.frame_content, text = msg).grid(row = 9, column = 0, padx = (65,15), pady = (40,5),sticky = 'sw')
        ttk.Label(self.frame_content, text='From (yyyy-mm-dd):').grid(row=10, column=0, padx=(65,0), sticky='sw')
        self.cal = DateEntry(self.frame_content, width=12, background='darkblue',
                    foreground='white', borderwidth=2)
        self.cal.grid(row=12, column=0, padx=(109,0), sticky='sw')

        ttk.Label(self.frame_content, text='To (yyyy-mm-dd):').grid(row=10, column=0, padx=(45,15), sticky='s')
        self.cal2 = DateEntry(self.frame_content, width=12, padding = 5, background='darkblue',
                    foreground='white', borderwidth=2)
        self.cal2.grid(row=12, column=0, padx=(58,0), sticky='s')
        
        ttk.Button(self.frame_content, text = 'Submit',
                   command = self.submit).grid(row = 14, column = 0, padx=65, pady = (40,40), sticky = 'sw')

    def dateOK(self, intCurrDate, intToDt, intFrmDt):
        return (intToDt > 20170501 and intToDt <= intCurrDate and intFrmDt > 20170501 and intFrmDt <= intCurrDate and intFrmDt <= intToDt)
    
    def collPicked(self):
        return(len(self.combobox.get())>5)
    def getUserName(self):
        return(self.uName.get())
    def uNameEntered(self):
        return len.getUserName()>0 
    def getPassword(self):
        return(self.pw.get())
    def pWEntered(self):
        return len.self.getPassword()>0 
    def submit(self):
        fromdtstr = self.cal.get()
        todtstr = self.cal2.get()
        self.fromDate=todtstr[2:].replace("-","")
        fromdt2=fromdtstr.replace('-', '')
        
        intFrmDt = int(fromdt2)
        self.toDate=todtstr[2:].replace("-","")
        todt2=todtstr.replace('-', '')
        intToDt=int(todt2)
        intCurrDate = int(self.currdate.replace('-',''))
        if self.uName.get().strip() == "":
            messagebox.showinfo("**Please enter username.              ")
        if self.pw.get().strip() == "":
            messagebox.showinfo("**Please enter password.              ")
        if self.combobox.get().strip() =="":
            messagebox.showinfo("**Please pick a collection or 'All DOH MODS'.            ")
        if not self.dateOK(intCurrDate, intToDt, intFrmDt):
            messagebox.showinfo("**Dates must be between 2017-05-01 and today.\n", "**'To Date' must fall on or after 'From Date'.")         
        if len(str(self.combobox.get()).strip()) > 5 and self.dateOK(intCurrDate, intToDt, intFrmDt) and self.uName.get().strip()!="" and self.pw.get().strip()!="":
            browser = webdriver.Chrome()
            usernameStr = self.uName.get().strip()
            passwordStr = self.pw.get().strip()
            signIn(browser, usernameStr, passwordStr)
            download(browser, self.savePath, self.combobox.get(), intFrmDt, intToDt)
            time.sleep(5)# Gives time to complete the task before closing the browser. You may increase the seconds to 10 or 15,basically the amount of time required for download otherwise it goes to the next step immediately.
            browser.quit()
         
def main():            
    root = Tk()
    downloader = Downloader(root)
    root.mainloop()
    
if __name__ == "__main__": main()