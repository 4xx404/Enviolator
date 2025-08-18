#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, re, time
from urllib.parse import urljoin
from pathlib import Path
from threading import Lock
from collections import deque
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.dont_write_bytecode = True

from Core.Stylesheet.Styling import bc
from Core.Console import Console
from Core.Config import Config
from Core.Commands import Command
from Core.Input import Input
from Core.Validity import Validation

from Core.PathBuilder import PathBuilder
from Core.EnvFile import EnvFile

class Enviolator:
    def __init__(self):
        self.Console = Console()
        self.Config = Config()
        self.Cmd = Command()
        self.Input = Input()
        self.Validator = Validation()

        self.PathBuilder = PathBuilder()
        self.EnvFile = EnvFile()

        self.WordlistUrl = self.Config.DirectoriesWordlistGithubUrl
        self.WordlistPath = self.Config.DirectoriesWordlistLocalPath

        self.TotalTargets = 0
        self.CompletedTargets = 0
        self._counter_lock = Lock()
        
        self.FoundEnvs = []
        
    def DisplayResults(self, EnvVars: dict, SourceUrl: str):
        self.Console.Raw(f"Environment Variables from {bc.GC}{SourceUrl}", True)

        for Key, Value in EnvVars.items():
            self.Console.Raw(f"{bc.BC}{Key}: {bc.GC}{Value}", False)

        print("\n")

    def SaveResults(self, EnvVars: dict, Url: str):
        Path("Results").mkdir(exist_ok=True)

        SafeFilename = re.sub(r'[^\w\-_.]', '_', Url.replace("https://", "").replace("http://", ""))
        FilePath = Path("Results") / f"{SafeFilename}.env"

        with open(FilePath, "w") as f:
            for k, v in EnvVars.items():
                f.write(f"{k}={v}\n")

    def Start(self) -> None:
        Host = self.Input.SetHostUrl()
        StartTime = time.time()

        # Phase 1: Scan root-level env paths
        RootTargets = self.PathBuilder.BuildTargets(Host, False)

        self.Console.Raw(f"Scanning root paths on {bc.GC}{len(RootTargets)}{bc.BC} targets.")
        self.ScanTargets(RootTargets)

        # Phase 2: Brute-force directories only if nothing was found
        ShouldBruteForceDirectories = self.Input.ShouldBruteForceDirectories()

        if (ShouldBruteForceDirectories):
            if (not self.Validator.NotEmpty(self.FoundEnvs)):
                BruteTargets = self.PathBuilder.BuildTargets(Host, IsDirectoryBuild=True)
                self.Console.Raw(f"Brute-forcing directories on {bc.GC}{len(BruteTargets)}{bc.BC} targets.\n")

                self.ScanTargets(BruteTargets)
            elif (ShouldBruteForceDirectories):
                self.Console.Raw(f"Skipping brute-force because {bc.GC}.env{bc.BC} file was already found in root paths", True)

        ElapsedTime = time.time() - StartTime

        self.Cmd.Clear(f"{bc.BC}Scan complete.")
        self.Console.Raw(f"Total Targets: {bc.GC}{self.TotalTargets}", False)

        FoundCount = len(self.FoundEnvs)
        Plural = "file" if FoundCount == 1 else "files"
        self.Console.Raw(f"Found .env {Plural}: {bc.GC}{FoundCount}", False)

        if self.Validator.NotEmpty(self.FoundEnvs):
            self.Console.Raw(f"{bc.BC}Files Discovered:", True)

            for Url in self.FoundEnvs:
                self.Console.Raw(f"{bc.GC}{Url}", False, False)

            print()

        self.Console.Raw(f"Elapsed Time: {bc.GC}{ElapsedTime:.2f}s", True)

    def ScanTargets(self, Targets: list[str]):
        self.TotalTargets = len(Targets)
        self.CompletedTargets = 0

        BufferedResults = []  # Store tuples of (env_vars_dict, url)

        with ThreadPoolExecutor(max_workers=self.Config.ThreadPoolExecutorMaxWorkers) as Executor:
            FutureToUrl = {Executor.submit(self.EnvFile.Fetch, Url): Url for Url in Targets}

            with tqdm(total=self.TotalTargets, desc="Scanning", ncols=80, bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}") as Progress:
                for Future in as_completed(FutureToUrl):
                    try:
                        Url, Content = Future.result()

                        if (not self.Validator.NotEmpty(Content)):
                            Progress.update(1)
                            continue

                        # Special handling for .gitignore expansion
                        if (Url.endswith(".gitignore")):
                            GitIgnorePaths = self.EnvFile.ExtractGitignorePaths(Content)

                            if (self.Validator.NotEmpty(GitIgnorePaths)):
                                Expanded = [urljoin(Url, Path) for Path in GitIgnorePaths]
                                self.Console.Raw(f"Expanding .gitignore with {bc.GC}{len(Expanded)}{bc.BC} new paths", False)

                                self.ScanTargets(Expanded) # Recursively scan the new paths

                        # Regular .env parsing
                        EnvVars = self.EnvFile.Parse(Content)

                        if (self.Validator.NotEmpty(EnvVars)):
                            with self._counter_lock:
                                self.FoundEnvs.append(Url)

                            BufferedResults.append((EnvVars, Url))

                        with (self._counter_lock):
                            self.CompletedTargets += 1
                            self.Console.Raw(f"[{bc.GC}{self.CompletedTargets}{bc.BC}/{bc.GC}{self.TotalTargets}{bc.BC}] Processed: {bc.GC}{Url}", False)

                        Progress.update(1)

                    except Exception as e:
                        self.Console.Error(f"Unhandled error while scanning: {str(e)}", False)

                        Progress.update(1)

        print()

        # Final save after all scans
        for EnvVars, Url in BufferedResults:
            self.DisplayResults(EnvVars, Url)
            self.SaveResults(EnvVars, Url)

if (__name__ == "__main__"):
    def Initiate():
        try:
            Enviolator().Start()
        except KeyboardInterrupt:
            quit()

    Command().Clear()
    Initiate()
