'''

browser:
 
part of the wordfish python package: extracting relationships of terms from corpus
this set of functions is for parsing content in a web browser

Copyright (c) 2015-2018 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to 
do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included 
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def get_browser():
    return webdriver.Firefox()

def get_page(browser,url):
    browser.get(url)

# Run javascript and get output
def run_javascript(browser,code):
    return browser.execute_script(code)

# Blogger Functions
# A function to click to the next page
def next_page(browser,page_number):
    browser.execute_script('''
        var page_number = parseInt(arguments[0])
        document.getElementsByClassName("gsc-cursor-page")[page_number].click()
        ''',page_number)

# A function to get blog urls on a page
def get_blogs(browser):
    return browser.execute_script('''
        var results = document.getElementsByClassName('gsc-url-top')
        var urls = [];
        for (i = 0; i < results.length-2; i++) { 
            urls.push(results[i].children[0].textContent)
        }
        return urls''')
