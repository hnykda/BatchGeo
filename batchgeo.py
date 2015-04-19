# encoding: utf-8
'''
batch_process -- shortdesc

batch_process is a description

It defines classes_and_methods

@author:     user_name

@copyright:  2015 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
'''

import sys
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException



from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2015-04-18'
__updated__ = '2015-04-18'

program_name = os.path.basename( sys.argv[0] )
program_version = "v%s" % __version__
program_build_date = str( __updated__ )
program_version_message = '%%(prog)s %s (%s)' % ( program_version, program_build_date )
program_shortdesc = __import__( '__main__' ).__doc__.split( "\n" )[1]
program_license = '''%s

Created by Daniel Hnyk on %s.
Copyright 2015 organization_name. All rights reserved.

Licensed under the Apache License 2.0
http://www.apache.org/licenses/LICENSE-2.0

Distributed on an "AS IS" basis without warranties
or conditions of any kind, either express or implied.

USAGE
!CURRENTLY MUST BE RUN ON FULLSCREEN!
''' % ( program_shortdesc, str( __date__ ) )

# Setup argument parser
parser = ArgumentParser( description = program_license, formatter_class = RawDescriptionHelpFormatter )
parser.add_argument( "-v", "--verbose", dest = "verbose", action = "store_true", help = "Verbose mode." )
parser.add_argument( "-f", "--file", default = "input.html", help = "Input file formated in HTML which should be pasted into Long Description" )
parser.add_argument( "-c", "--codes", required = True, type = str, help = "Codes of geacaches separated by comma. E.g. 'GC3YJME,GC3YJMX'" )
parser.add_argument( '-V', '--version', action = 'version', version = program_version_message )
parser.add_argument( "-m", "--maternal_url", default = "http://www.geocaching.com/geocache/", type = str, help = "Maternal URL of geocaches" )
parser.add_argument( "-l", "--logins", required = True, help = "Login names and passwords in 'user1:passwd1,user2:passwd2'" )
parser.add_argument( '-s', "--submit", action = 'store_true', help = "If changes should be submited." )
parser.add_argument( '-b', "--border", default = "<!--DONTCHANGE-->", help = "Every long description must contain this string exactly TWICE. Everything between these two occurences will be replaced." )
parser.add_argument( '--log', default = "out.log", help = "Name of log file." )

# Process arguments
args = parser.parse_args()

codes = args.codes.split( "," )
users = args.logins.split( "," )

content = ""
with open( args.file, "r", encoding = "utf8" ) as ifile:
    content = ifile.read()
# print( content )

dr = webdriver.Firefox()

def verb( st ):
    if args.verbose:
        print( st )

    with open( args.log, "a", encoding = "utf8" ) as logfile:
        logfile.write( st + "\n" )

class Cache():

    code = ""
    url = ""

    verb( '\n\n--------\n' )

    def __init__( self, code ):
        self.code = code
        self.url = args.maternal_url + code


        verb( "Processing: " + self.code )
        trying = True
        for user in users:
            if trying:
                login_name, password = user.split( ":" )
                verb( "Username: " + login_name + ", Password: " + password )

                dr.get( self.url )
                name_of_cache = dr.find_element_by_xpath( '//*[@id="ctl00_ContentBody_CacheName"]' ).text
                verb( "Name of cache: " + name_of_cache )

                try:
                    # sign in form
                    dr.find_element_by_xpath( '//*[@id="hlSignIn"]' ).click()

                    lgn = dr.find_element_by_xpath( '//*[@id="ctl00_tbUsername"]' )
                    lgn.send_keys( login_name )

                    psw = dr.find_element_by_xpath( '//*[@id="ctl00_tbPassword"]' )
                    psw.send_keys( password )

                    # check box remember me (maybe not necessary)
                    dr.find_element_by_xpath( '//*[@id="ctl00_cbRememberMe"]' ).click()

                    # submit login form
                    dr.find_element_by_xpath( '//*[@id="ctl00_btnSignIn"]' ).click()
                except NoSuchElementException:
                    verb( "You are already login" )

                try:
                    # click on edit link
                    dr.find_element_by_xpath( '//*[@id="ctl00_ContentBody_GeoNav_adminTools"]/li[2]/a' ).click()

                    # inser to text area of long description
                    textarea = dr.find_element_by_xpath( '//*[@id="tbLongDesc"]' )
                    text = textarea.get_attribute( "value" )

                    verb( '------OLD TEXT----' )
                    verb( text )
                    verb( '------END OF OLD TEXT-----\n' )

                    start_pos = text.find( args.border )
                    dont_change = text[:start_pos + len( args.border )] + "\n"
                    start_pos2 = text[start_pos + 1:].find( args.border )
                    dont_change2 = "\n" + text[start_pos2:]

                    textarea.clear()  # clear textarea
                    newtext = dont_change + content + dont_change2
                    textarea.send_keys( newtext )  # insert unchanged text + content
                    verb( '------NEW TEXT----' )
                    verb( newtext )
                    verb( '------END OF NEW TEXT-----\n' )

                    # check boxes about understand and disclaimer
                    dr.find_element_by_xpath( '//*[@id="ctl00_ContentBody_chkUnderstand"]' ).click()
                    dr.find_element_by_xpath( '//*[@id="ctl00_ContentBody_chkDisclaimer"]' ).click()

                    if args.submit:
                        # submit edit
                        dr.find_element_by_xpath( '//*[@id="ctl00_ContentBody_btnSubmit"]' ).click()

                    trying = False
                except NoSuchElementException:
                    verb( "You have no rights to edit this geocache!" )

                    # sign out
                    dr.find_element_by_xpath( '//*[@id="ctl00_divSignedIn"]/ul/li[1]/button' ).click()
                    dr.find_element_by_xpath( '//*[@id="ctl00_hlSignOut"]' ).click()
                    from time import sleep
                    sleep( 2 )
                    # dr.get( self.url )

        body = dr.find_element_by_tag_name( "body" )
        body.send_keys( Keys.CONTROL + 't' )


if __name__ == "__main__":

    for code in codes:
        Cache( code )

    sys.exit()