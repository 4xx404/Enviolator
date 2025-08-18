#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
sys.dont_write_bytecode = True

class Config:
	def __init__(self):
		self.ThreadPoolExecutorMaxWorkers = 50

		self.Headers = {
			"Accept-Language": "en-US,en;q=0.5",
			"Cache-Control": "no-cache", 
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
		}

		self.EnvFileNames = [
			".env",
			".env.prod",
			".env.production",
			".env.dev",
			".env.development",
			".env.local",
			".env.localhost",
			".env.staging",
			".env.example",
			".env.backup",
			".env.old"
		]

		self.DirectoriesWordlistGithubUrl = "https://raw.githubusercontent.com/3ndG4me/KaliLists/master/dirbuster/directory-list-2.3-small.txt"
		self.DirectoriesWordlistLocalPath = Path("Wordlists") / "directory-list-2.3-small.txt"