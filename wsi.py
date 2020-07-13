#!/usr/bin/env python3

#   selenium and webdriver for Firefox is required to take the screenshots
#   https://pypi.org/project/selenium/
#   https://github.com/mozilla/geckodriver/releases

import os
import datetime
import requests
import re
import logging
import argparse
try:
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options
except:
    print("""selenium and webdriver for Firefox is required to take the screenshots
            https://pypi.org/project/selenium/
            https://github.com/mozilla/geckodriver/releases""")
    exit()
try:
    from bs4 import BeautifulSoup
except:
    print("""Beautiful Soup is required to check links out on the pages.
            pip3 install bs4""")
    exit()

#logging.basicConfig(level=logging.DEBUG)

cwd = os.getcwd()

ap = argparse.ArgumentParser()
ap.add_argument("-c", "--config", required=True, help="We need a config file to work with.  Copy and rename defaultConfig.txt and use this")
args = vars(ap.parse_args())

#   Some text so we can keep it out of functions and clean it up when needed
scriptName = """
                _     
__      __ ___ | |__  
\ \ /\ / // _ \| '_ \ 
 \ V  V /|  __/| |_) |
  \_/\_/ _\___||_.__/ 
 ___ (_)| |_  ___     
/ __|| || __|/ _ \    
\__ \| || |_|  __/    
|___/|_| \_______|    
(_) _ __   / _|  ___  
| || '_ \ | |_  / _ \ 
| || | | ||  _|| (_) |
|_||_| |_||_|   \___/ 
details in csv or html
v.001
@https://github.com/m0nkeyplay
########################################

"""
                      
logStart = 'Test URL,Check Time,Source IP,Final URL,HTTP Status Code,Hop Codes,Title,Server Type,Screenshot,Links on Page\n'

theHTMLstart = """
<html>
<head>
<title>Web Site(s) Report</title>
<style>
body {
  background-color: white;
  font-family: Arial, Helvetica, sans-serif;
}
table {
  border-collapse: collapse;
}
table, th, td {
  border: 1px solid black;
  vertical-align: top;
}
th {
   background-color: #f5f5f5; 
}
tr:hover {
    background-color: #f5f5f5;
    }
</style>
</head>
<body>
<h4>web site info - RESULTS</h4>
<table>
<tr>
<th>Test URL</th><th>Check Time</th><th>Source IP</th>
<th>Final URL</th><th>HTTP Status Code</th>
<th>Hop Codes</th><th>Page Title</th><th>Server Type</th><th>Screenshot</th><th>Links</th>
</tr>
"""

theHTMLend = '</table></body></html>'

#   dictionary of things to look for
dictOfInfo = {
    'wordpress': 'Detected: Wordpress;',
    'drupal': 'Detected: Drupal',
    'zen-cart': 'Detected: Zen Cart',
    'joomla': 'Detected: Joomla',
    'woocommerce': 'Detected: WooCommerce',
    'bigcommerce': 'Detected: BigCommerce',
    'shopify': 'Detected: Shopify',
    'magento': 'Detected: Magento',
    'wix': 'Detected: Wix',
    'bitrix24': 'Detected: Bitrix24',
    'prestashop': 'Detected: Prestashop',
    'zend': 'Detected: zend',
    'symfony': 'Detected: Symphony',
    'aws.amazon.com': 'Detected:  Possibkle AWS usage - check links',
    'cloud.google.com': 'Detected: Possible GCP usage - check links',
    'azure.microsoft.com' : 'Detected: Possible Azure usage - check links'
}

#   Create a folder for all this stuff
def project_dir(projectName):
    timeDone = datetime.datetime.now()
    timeStamp = str(timeDone).split('.')[1]
    cleanName = projectName.lower().replace('.','-').replace(' ','-')+timeStamp
    if not os.path.isdir('./'+cleanName):
        print('Creating folder for data.')
        os.mkdir(cleanName)
        return cleanName
    else:
        answer = input("A folder with this name already exists.  If you continue, files can be overwritten.\nDo you want to continue? Y/N   ")
        if answer.lower() == 'y' or answer.lower() == 'yes':
            return cleanName
        else:
            print("Okay.  Come up with a new project name and rerun.")
            exit()

#   Send a clean error message from requests if we get one
def search_error(errorMessage):
    searchFor = "(\[Errno\s\d+\])(.*)'"
    match = re.search(searchFor,errorMessage)
    if match:
        return match.group(2).replace(',','-')
    else:
        return ''

#   Grab the title of the web page
def search_title(webPage):
    searchFor = "<title>(.*)</title>"
    match = re.search(searchFor,webPage)
    if match:
        return match.group(1)[0:30].strip() 
    else:
        return ''

#   Grab the codes it took to get to the final page
def search_history(theText):  
    for code in theText:
        httpCode = re.search('\d{3}',str(code))
    return httpCode[0]

#   uniform text from a URL for file names etc
def name_clean(someText):
    cleaned = someText.replace('http://','').replace('https://','').replace('.','-').replace('/','').strip()
    return cleaned

#   check on some common server techs
def server_stuff(field,searchFor,say):
    if field.find(str(searchFor)) > 0:
        print("  "+say.strip(';'))
        return say      
    else:
        return ''

#   Get links on the page
#   Write it to a file
def get_links(pageText,fName,folder):
    fileName = name_clean(fName)+'-links.txt'
    saveName = folder+'/links/'+fileName
    saveLinks = open(saveName,'w')
    saveLinks.write(fName+'\n')
    soup = BeautifulSoup(pageText, 'html.parser')
    monkey_link_list_items = soup.find_all('a')
    for monkey in monkey_link_list_items:
        href = monkey.get('href')
        if href and href is not "None":
            if href[0] is not '#':
                writeMe = str(href+'\n')
                saveLinks.write(writeMe)    
    saveLinks.close()
    return fileName

# Take a screenshot
def take_screenshot(url,finalUrl,aProxy,folder):
    options = Options()
    options.headless = True
    selenuimProxy = aProxy
    fileName = name_clean(url)
    fileName = fileName+'.png'
    saveFile = folder+'/screenshots/'+fileName

    if selenuimProxy is not "":
        webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
            "httpProxy": selenuimProxy,
            "ftpProxy": selenuimProxy,
            "sslProxy": selenuimProxy,
            "proxyType": "MANUAL"
        }
    with webdriver.Firefox(options=options) as driver:
        try:
            driver.get(finalUrl)
            driver.save_screenshot(saveFile)
            toReturn = fileName
        except:
            print("unable to get screenshot")
            toReturn = 'Unable to get screenshot'
        driver.quit()
    return toReturn

def get_em(url,logFile,dhtml,proxies,outTime,ip,folder):
    timeDone = datetime.datetime.now()
    timeStamp = str(timeDone).split('.')[0]
    screenShotProxy = proxies['http']
    serverFind = []
    serverCSV = ''
    serverHTML = ''

    try:
        print("Checking %s..."%url)
        r = requests.get(url,stream=True,allow_redirects=True,timeout=outTime,proxies=proxies)
        finalURL = str(r.url)
        print("  Landed on %s"%finalURL)
        status = str(r.status_code)
        print("  Status: %s"%status)
        hops = ''
        if r.history:
            hops = str(search_history(r.history))
        try:
            rServer = str(r.headers["Server"]).replace(',',' ')
            serverFind.append('Server: '+rServer+';')
            print("  Server Type: %s"%rServer)
        except:
            rServer = ''
        try:
            rPoweredBy = str(r.headers["X-Powered-By"]).replace(',',' ')
            serverFind.append('X-Powered By: '+rPoweredBy+';')
            print("  X-Powered By: %s"%rPoweredBy)
        except:
            rServer = ''
        for k,v in dictOfInfo.items():
            moreInfo = server_stuff(r.text,k,v)
            if moreInfo:
                serverFind.append(moreInfo)
        try:
            titleText = search_title(r.text).replace(',', ' ')
            print("  Page Title: %s"%titleText)
        except:
            titleText = ''
        try:
            linkInfo = get_links(r.text,url,folder)
            print("  Links on page collected.")
        except:
            linkInfo = ''
        try:
            pic = take_screenshot(url,finalURL,screenShotProxy,folder)
            print("  Screenshot captured.")
        except:
            pic = ''

        for x in serverFind:
            serverCSV += x+' '
            serverHTML+= x.replace(';','<br />')


        writeToLog = url+','+timeStamp+','+str(ip)+','
        writeToLog += finalURL+','+status+','+hops+','
        writeToLog += titleText+','+serverCSV+','+pic+','+linkInfo+'\n'

        writeHTML = '''<tr>
        <td valign="top">%s</td>
        <td valign="top">%s</td>
        <td valign="top">%s</td>
        <td valign="top">%s</td>
        <td valign="top">%s</td>
        <td valign="top">%s</td>
        <td valign="top">%s</td>
        <td valign="top">%s</td>
        <td valign="top"><a href="screenshots/%s">%s</a></td>
        <td valign="top"><a href="links/%s">%s</a></td>
        </tr>
        '''%(url,timeStamp,str(ip),finalURL,status,hops,titleText,serverHTML,pic,pic,linkInfo,linkInfo)            
        logFile.write(writeToLog)
        dhtml.write(writeHTML)

    except requests.exceptions.RequestException as err:
        requestsErrorMsg = '''
        <tr>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td></td>
            <td>%s</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>
        '''%(url,timeStamp,str(ip),search_error(str(err)))
        logFile.write(url+","+timeStamp+","+str(ip)+",,"+search_error(str(err))+",,\n")
        dhtml.write(requestsErrorMsg)
        print("  Did not connect: %s" %search_error(str(err)))

#   Do the work once things are gathered
#   Read the domains to search, open the logs and for each domain 
#   Check them for as much info as possible
def check_em(urls,log,htmlFile,proxies,outTime,ip,folder):
    domains = open(urls,'r')
    dlog = open(log,'w')
    dlog.write(logStart)
    dhtml = open(htmlFile,'w')
    dhtml.write(theHTMLstart)
    for domain in domains:
        get_em(domain.strip(),dlog,dhtml,proxies,float(outTime),str(ip),folder)
    domains.close()
    dlog.close()
    dhtml.write(theHTMLend)
    dhtml.close()

if __name__ == '__main__':
    print(scriptName)
    if not os.path.isfile(args["config"]):
        print("We can't find the config file you supplied.")
        exit()
    else:
        ourSettings = open(args["config"],'r')
        for line in ourSettings:
            if line[0] is not "#":
                setup = line.split(',')
                urlFile = setup[0].strip()
                if not os.path.isfile(urlFile):
                    print("We can't find the list of URLs. Please update the config file and try again.")
                    exit()
                projectDirectory = project_dir(setup[1].strip())
                os.mkdir(projectDirectory+'/screenshots')
                os.mkdir(projectDirectory+'/links')
                outputcsv = projectDirectory+'/'+'results.csv'
                outputHTML = projectDirectory+'/'+'results.html'
                timeoutTime = str(setup[4].strip())
                proxies = {}
                proxies['http'] = setup[2].strip()
                proxies['https'] = setup[3].strip()
                ip = requests.get('https://checkip.amazonaws.com',proxies=proxies,timeout=10).text.strip()
                check_em(urlFile,outputcsv,outputHTML,proxies,timeoutTime,str(ip),projectDirectory)
        ourSettings.close()
        print("\n\n*************************")
        print("""Done. Data has been written to the folder %s/\nScreenshots and links are all in there.
        \tCSV: %s
        \tHTML: %s"""%(projectDirectory,outputcsv,outputHTML))