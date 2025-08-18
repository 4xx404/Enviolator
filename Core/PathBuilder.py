#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os, requests
from tqdm import tqdm
from urllib.parse import urljoin
sys.dont_write_bytecode = True

from Core.Stylesheet.Styling import bc
from Core.Console import Console
from Core.Config import Config
from Core.Commands import Command
from Core.Validity import Validation

class PathBuilder:
    def __init__(self):
        self.Console = Console()
        self.Config = Config()
        self.Cmd = Command()
        self.Validator = Validation()

        self.WordlistUrl = self.Config.DirectoriesWordlistGithubUrl
        self.WordlistPath = self.Config.DirectoriesWordlistLocalPath

        self.BruteForceDirectories = None

    def __BuildRootPaths(self) -> list[str]:
        Files = self.Config.EnvFileNames + [".gitignore"]

        return [f"/{File}" for File in Files]
    
    def __LoadWordlistOnce(self) -> list[str]:
        if (self.BruteForceDirectories is not None):
            return self.BruteForceDirectories

        # Ensure directories exist only once
        os.makedirs(os.path.dirname(self.WordlistPath), exist_ok=True)

        self.BruteForceDirectories = self.__GetCachedWordlist(self.WordlistUrl, self.WordlistPath)

        return self.BruteForceDirectories
    
    def __BuildDirectoryPathsGenerator(self):
        Directories = self.__LoadWordlistOnce()

        if (not self.Validator.NotEmpty(Directories)):
            return

        EnvFiles = self.Config.EnvFileNames

        for Directory in Directories:
            CleanedDirectory = str(Directory).strip()

            for File in EnvFiles:
                yield f"/{CleanedDirectory}/{File}"

    def __GetCachedWordlist(self, Url: str, LocalPath: str) -> list:
        if (not os.path.exists(LocalPath)):
            self.Console.Raw("[*] Downloading wordlist...", True)

            try:
                with requests.get(Url, stream=True, timeout=10) as Response:
                    Response.raise_for_status()

                    TotalSize = int(Response.headers.get("content-length", 0))
                    ChunkSize = 1024

                    with open(LocalPath, "w", encoding="utf-8") as FileWriter:
                        with tqdm.tqdm(total=TotalSize, unit="B", unit_scale=True, desc="Downloading") as ProgressBar:
                            for Chunk in Response.iter_content(chunk_size=ChunkSize):
                                if (Chunk):
                                    DecodedChunk = Chunk.decode("utf-8")
                                    FileWriter.write(DecodedChunk)
                                    ProgressBar.update(len(Chunk))

            except requests.RequestException as e:
                self.Console.Error(f"Failed to download directories wordlist\n{bc.RC} {str(e)}", True)

                return []

        with open(LocalPath, "r", encoding="utf-8") as FileReader:
            Lines = [Line.strip() for Line in FileReader if (Line.strip() and not Line.startswith("#"))]
            FilteredLines = [Line for Line in Lines if self.Validator.Directory(Line)]

            return FilteredLines
        
    def BuildTargets(self, Domain: str, IsDirectoryBuild: bool = False) -> list:
        BaseUrl = Domain.strip().lower()

        if IsDirectoryBuild:
            BuildPaths = self.__BuildDirectoryPathsGenerator()  # generator, lazy evaluation

            # for BuildPath in BuildPaths:
            #     print(BuildPath)

            # quit()
        else:
            BuildPaths = self.__BuildRootPaths()

        TargetsSet = set()  # Use a set to avoid duplicates
        TargetCounter = 1

        PathsList = list(BuildPaths)  # convert generator to list

        # Wrap the iteration with tqdm progress bar
        for BuildPath in tqdm(PathsList, desc=f"{bc.BC} Building targets", ncols=80, bar_format='{desc} ' + bc.GC + '{n}' + bc.BC + '/' + bc.GC + '{total}' + bc.BC + ': ' + bc.GC + '{bar}' + bc.BC + '|' + bc.GC + '{percentage:3.0f}%' + bc.BC):
            FullUrl = urljoin(BaseUrl, BuildPath)

            if (FullUrl not in TargetsSet):
                TargetCounter += 1
                TargetsSet.add(FullUrl)

        print()

        return list(TargetsSet)