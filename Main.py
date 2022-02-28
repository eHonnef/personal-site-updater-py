import json
import os
import requests

GITHUB_USER = "eHonnef"


def GetRepos():
  Address = "https://api.github.com/users/{}/repos".format(GITHUB_USER)
  ApiRequest = requests.get(url=Address)
  return ApiRequest.json()


def ReadSettings():
  return json.load(open("./Settings.json", "r", encoding="utf8"))

def WriteSettings(Settings):
  json.dump(Settings, open("./Settings.json", "w+", encoding="utf8"))

def MDFileContent(RepoObj):
  FileContent = """---
title: "{}"
excerpt: "{}"
category: "{}"
link: {}
---

{}
""".format(RepoObj["name"], RepoObj["description"], RepoObj["language"], RepoObj["html_url"], RepoObj["description"])
  return FileContent


def CreateMDFile(RepoObj, DestFolder):
  FolderPath = "./{}".format(DestFolder)
  FilePath = "{}/{}.md".format(FolderPath, RepoObj["name"])

  if not os.path.exists(FolderPath):
    os.makedirs(FolderPath)

  if os.path.exists(FilePath):
    return False

  File = open(FilePath, "w+", encoding="utf8")
  File.write(MDFileContent(RepoObj))
  File.close()
  return True


if __name__ == "__main__":
  Data = GetRepos()
  Settings = ReadSettings()

  def _GetFolder(RepoObj):
    RtnValues = []
    for Key in Settings.keys():
      if Key != "ProcessedRepos":
        if RepoObj["name"] in Settings[Key]["Items"]:
          RtnValues.append(Settings[Key]["FolderName"])
    return set(RtnValues)

  PrintInfo = False
  for Repo in Data:
    if (not Repo["name"] in Settings["ProcessedRepos"]) and (not Repo["name"] in Settings["IgnoredRepos"]["Items"]):
      Folders = _GetFolder(Repo)

      if len(Folders) == 0:
        print("Set category for repository: {}".format(Repo["name"]))
        PrintInfo = True
      else:
        Settings["ProcessedRepos"].append(Repo["name"])
        for Folder in Folders:
          CreateMDFile(Repo, Folder)

  if PrintInfo:
    print("Categorize those repos in the Settings.json file, then rerun this program")
  WriteSettings(Settings)
