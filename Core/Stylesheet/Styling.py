#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
sys.dont_write_bytecode = True

class bc:
	GC = "\033[1;39m"
	BC = "\033[1;34m"
	RC = "\033[1;31m"
	
class sd:
	iBan = f"{bc.BC}[{bc.GC}?{bc.BC}]" # Info banner
	sBan = f"{bc.BC}[{bc.GC}" + u'\u2713' + f"{bc.BC}]" # Success banner
	eBan = f"{bc.BC}[{bc.RC}" + u'\u2717' + f"{bc.BC}]" # Error banner
	
class Banner:
	Author = f"{bc.BC}\n Author:{bc.GC} 4xx404 \n"
	Version = f"{bc.BC} Version:{bc.GC} 1.0 \n"
	Github = f"{bc.BC} Github: {bc.GC}https://github.com/4xx404 \n"

	Logo = rf"""{bc.RC}
{bc.GC}  _____           _       _       _              
{bc.BC} |  ___|         (_)     | |     | |             
{bc.RC} | |__ _ ____   ___  ___ | | __ _| |_ ___  _ __  
{bc.GC} |  __| '_ \ \ / / |/ _ \| |/ _` | __/ _ \| '__| 
{bc.BC} | |__| | | \ V /| | (_) | | (_| | || (_) | |    
{bc.RC} \____/_| |_|\_/ |_|\___/|_|\__,_|\__\___/|_|    
 {Author}{Version}{Github}"""

class Menu:
	Helper = f"{sd.iBan} Include {bc.GC}http://{bc.BC} | {bc.GC}https://{bc.BC} in URL"