from urllib2 import urlopen
import smtplib
import bs4
import re
import time

printer_list = ['10.0.0.221/menuhome.htm', '10.0.0.224', '10.0.2.52', '10.2.0.20', '10.2.0.21', '10.2.0.22', '10.2.16.54', '10.3.0.20', '10.3.0.21', '10.3.0.22', '10.3.0.23', '10.3.0.24',]
#printer_list = [insert your printer IP's here in list above]
statuslist = []
error_list = []

def getprinterdata(printer_list, flag):
    for printer in printer_list:
        print(printer)
        try:
            page = urlopen(url='http://'+printer, timeout=5)
        except IOError:
            tmp = 'Printer page could not be opened. HTTP Request: '+printer
            if not flag:
                error_list.append(printer)
            continue
        
        soup = bs4.BeautifulSoup(page, 'html.parser')
    
        printer_name = None
        
        headertitle = soup.find(id='headertitle')
        if headertitle is not None:
            printer_name = headertitle.text
            
        if not printer_name:
            page_title = soup.title.string
            page_title = re.sub("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", '', page_title)
            page_title = re.sub("\ \-\ ", '', page_title)
            page_title = re.sub("Home", '', page_title)
            printer_name = page_title.strip() ##gets printer name from HTML title and regex
            
        statbox = soup.find(id='statboxtbl') #gets printer status message
        if statbox is not None:
            message =  statbox.text.strip()
    
        lcdpanel = soup.find(attrs={'class':'lcdpnl'}) #for printers without statboxtbl, gets printer status message
        if lcdpanel is not None:
            message = lcdpanel.text.strip()
        
        stdleft = soup.findAll('td', class_='stdleftfrm_2') #for printers without pstatus2, gets printer status
        if stdleft is not None:
            if stdleft:
                statusleft = str(stdleft).lower()
                if 'warning' in statusleft:
                    status = 'warning'
                if 'ready' in statusleft:
                    status = 'ready'
                if 'error' in statusleft:
                    status = 'error'
                if 'busy' in statusleft:
                    status = 'busy'
        
        framestata = soup.find(attrs={'href':'framestat.htm'}) #for printers who don't like pstatus2 or stdleftfrm_2
        if framestata is not None:
            status = framestata.parent.next_sibling.string
        
        statuslist.append([printer, status.capitalize(), message, printer_name])
        
        if flag:
            error_list.pop(printer) #if previously unconnectable printer can connect, remove it from the error_list

getprinterdata(printer_list, flag=None)

n=0
while error_list is not None:
    print('Trying Offline Printers.. ({0})'.format(n))
    getprinterdata(error_list, flag=1)
    n += 1
    if n == 5:
        break
    
#email config below

sender = 'printers@domain.com'
receivers = ['cc@domain.com','gba@domain.com','kobon@domain.com']
subject = 'Printer Status'




body = """From:  Printers <printers@domain.com>
Subject: Xerox Printer Status
This is a summary of the Phaser printers at DSSD. If you have any questions, contact kobon@domain.com. \n
This email was sent to: """+', '.join(receivers)+"""  \n\n"""

for entry in statuslist:
    add = 'Printer Name: '+entry[3].strip()+'\n'+'Printer Address: '+entry[0]+'\n'+'Status: '+entry[1]+'\n'+'Message: '+entry[2]+'\n\n'
    body += add

print body

try:
    smtp = smtplib.SMTP('10.0.0.178')
    smtp.sendmail(sender, receivers, body)
    print "Successfully sent email"
except smtplib.SMTPException:
    print 'Error: unable to send email'

#email.end
