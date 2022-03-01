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
  Description = RepoObj["description"]
  if Description is None or Description == "None" or Description == "":
    Description = "W.I.P."

  Description = Description.replace('"', '\\"')

  FileContent = """---
title: "{}"
excerpt: "{}"
category: "{}"
link: {}
---

{}
""".format(RepoObj["name"], Description, RepoObj["language"], RepoObj["html_url"], Description)
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


def IsWIPRepo(RepoObj):
  return (RepoObj["description"] is None or RepoObj["description"] == "None" or RepoObj["description"] == "")


if __name__ == "__main__":
  Data = GetRepos()
  Settings = ReadSettings()

  def _GetFolder(RepoObj):
    RtnValues = []
    for Key in Settings.keys():
      if not Key in ["ProcessedRepos", "LanguagesAliases"]:
        if RepoObj["name"] in Settings[Key]["Items"]:
          RtnValues.append(Settings[Key]["FolderName"])
    return set(RtnValues)

  PrintInfo = False
  for Repo in Data:
    if (not Repo["name"] in Settings["ProcessedRepos"]) and (not Repo["name"] in Settings["IgnoredRepos"]["Items"]):
      Folders = _GetFolder(Repo)

      if len(Folders) == 0 or IsWIPRepo(Repo):
        print("No category or WIP repo: {}".format(Repo["name"]))
        PrintInfo = True
      else:
        Settings["ProcessedRepos"].append(Repo["name"])
        if Repo["language"] in Settings["LanguagesAliases"].keys():
          Repo["language"] = Settings["LanguagesAliases"][Repo["language"]]
        for Folder in Folders:
          CreateMDFile(Repo, Folder)

  if PrintInfo:
    print("===\nCategorize those repos in the Settings.json file, then rerun this program")
  WriteSettings(Settings)
