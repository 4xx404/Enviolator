#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, requests, re, codecs
sys.dont_write_bytecode = True

from Core.Stylesheet.Styling import bc
from Core.Console import Console
from Core.Config import Config
from Core.Commands import Command
from Core.Validity import Validation

class EnvFile:
    def __init__(self):
        self.Console = Console()
        self.Config = Config()
        self.Cmd = Command()
        self.Validator = Validation()

        self.Session = requests.Session()

    def Fetch(self, FullUrl: str) -> tuple[str, str | None]:
        try:
            Response = self.Session.get(FullUrl, headers=self.Config.Headers, timeout=3)

            if (Response.status_code == 200 and self.Validator.NotEmpty(Response.text)):
                EnvVars = self.Parse(Response.text)

                if self.Validator.NotEmpty(EnvVars):
                    self.Console.Success(f"Found .env at {bc.GC}{FullUrl}", False)

                    return (FullUrl, Response.text)

            self.Console.Raw(f"No .env found at {bc.RC}{FullUrl}{bc.BC} [Status: {bc.RC}{Response.status_code}{bc.BC}]", False)
        except requests.ConnectionError:
            # Fallback to HTTP if HTTPS fails to connect
            if (FullUrl.startswith("https://")):
                FallbackUrl = FullUrl.replace("https://", "http://", 1)
                self.Console.Raw(f"{bc.BC}Retrying over HTTP: {bc.GC}{FallbackUrl}", False)

                try:
                    FallbackResponse = requests.get(FallbackUrl, headers=self.Config.Headers, timeout=3)

                    if (FallbackResponse.status_code == 200 and self.Validator.NotEmpty(FallbackResponse.text)):
                        EnvVars = self.Parse(FallbackResponse.text)

                        if self.Validator.NotEmpty(EnvVars):
                            self.Console.Success(f"Found .env at {bc.GC}{FallbackUrl}", False)

                            return (FallbackUrl, FallbackResponse.text)

                    self.Console.Raw(f"No .env found at {bc.RC}{FallbackUrl}{bc.BC} [Status: {bc.RC}{FallbackResponse.status_code}{bc.BC}]", False)

                except requests.RequestException as e:
                    self.Console.Error(f"Fallback HTTP request failed at {bc.RC}{FallbackUrl}\n {bc.RC}{str(e)}", False)

        except requests.RequestException as e:
            self.Console.Error(f"Request error at {bc.RC}{FullUrl}\n {bc.RC}{str(e)}", False)

        return (FullUrl, None)

    def ExtractGitignorePaths(self, content: str) -> list[str]:
        Extracted = []

        for Line in content.splitlines():
            Line = Line.strip()

            if (not self.Validator.NotEmpty(Line) or Line.startswith("#")):
                continue

            Cleaned = Line.lstrip("/") # Normalize the entry

            if ("*" not in Cleaned and self.Validator.NotEmpty(Cleaned)):
                Extracted.append(Cleaned)

        return Extracted
    
    def Parse(self, EnvContent: str) -> dict:
        EnvVars = {}

        for Line in EnvContent.splitlines():
            Line = Line.strip()

            if (not self.Validator.NotEmpty(Line) or Line.startswith("#")):
                continue

            Match = re.match(r'''
                ^                               # Start of line
                ([A-Za-z_][A-Za-z0-9_\.]*)      # Key: starts with letter or _, includes . and digits
                \s*=\s*                         # Equal sign with optional surrounding whitespace
                (?:                             # Start non-capturing group for value
                    "([^"\\]*(?:\\.[^"\\]*)*)"  # Double-quoted value, with escaped quotes
                    |                           # OR
                    '([^'\\]*(?:\\.[^'\\]*)*)'  # Single-quoted value, with escaped quotes
                    |                           # OR
                    ([^\n#]+?)                  # Unquoted value up to newline or #
                )?                              # Value is optional
                \s*(?:\#.*)?$                   # Optional comment after value
            ''', Line, re.VERBOSE)

            if (Match):
                Key = Match.group(1)
                Value = Match.group(2) or Match.group(3) or Match.group(4) or ""
                Value = Value.strip()

                if (Match.group(2) or Match.group(3)):  # Quoted
                    try:
                        Value = codecs.decode(Value, 'unicode_escape')
                    except Exception:
                        pass  # Fallback in case of decoding errors

                EnvVars[Key] = Value

        return EnvVars
