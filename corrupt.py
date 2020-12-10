from random import randint, sample, choice
from uuid import uuid4
import os
import sys
import json

REPEAT_FILES = 10

class Disk:
  def __init__(self, fragsize, fragdev):
    self._fragsize = fragsize
    self._fragdev = fragdev
    self.manifest = list()
    self.memory = list()
    self._staging = list()
    self._idcount = 0
    self._fresh = True
    self._freshnessPoint = 0

  def add_file(self, path, filler):
    filesize = os.path.getsize(path)
    chunks = [ i * self._fragsize for i in range(filesize // self._fragsize) ]
    chunks = [ (s, e - 1) for s, e in zip(chunks, chunks[1:]) ]
    chunks = list(chunks)
    chunks.reverse()
    
    self._staging.append({
      "id": self._idcount,
      "path": path,
      "chunks": chunks,
      "isFiller": filler
    })

    self._idcount += 1
    
  def _getStagedChunks(self):
    return sum([len(x["chunks"]) for x in self._staging])

  def flush(self):
    initialChunkCount = float(self._getStagedChunks())

    while self._getStagedChunks() > 0:
      file = choice(self._staging)

      if len(file["chunks"]) > 0:
        if not self._fresh:
          i = self._freshnessPoint
          fdev = randint(1, self._fragdev)
          deletedFiles = list(filter(lambda x : x["deleted"], self.manifest))
          deletedFileIDs = list(map(lambda x : x["id"], deletedFiles))

          while i < len(self.memory) and self.memory[i]["id"] not in deletedFileIDs:
            i += 1

          if i >= len(self.memory):
            self._fresh = True
            continue

          while fdev >= 0 and self.memory[i]["id"] in deletedFileIDs and len(file["chunks"]) > 0:
            self.memory[i] = {
              "id": file["id"],
              "chunk": file["chunks"].pop()
            }
            fdev -= 1
            i += 1

          self._freshnessPoint = i
        else:
          for _ in range(min(len(file["chunks"]), randint(1, self._fragdev))):
            self.memory.append({
              "id": file["id"],
              "chunk": file["chunks"].pop()
            })
      else:
        self.manifest.append({
          "id": file["id"],
          "path": file["path"],
          "isFiller": file["isFiller"],
          "deleted": False
        })
        self._staging.remove(file)
      
      yield (initialChunkCount - self._getStagedChunks()) / initialChunkCount

    self._staging = list()
    self._fresh = False

  def deleteFile(self, id):
    for item in self.manifest:
      if (item["id"] == id):
        item["deleted"] = True
        return

  def getFile(self, path):



def main():
  print("Starting...")
  disk = Disk(2**11, 8)

  def AddFiles(dir, repeat, filler):
    for file in os.listdir(dir):
      print("Adding file " + file)

      for i in range(repeat):
        disk.add_file(dir + '/' + file, filler)
        print("Progress {:.2f}%".format(i / REPEAT_FILES), end='\r')

  AddFiles('good_pics', 3, False)
  AddFiles('filler_data', 7, True)

  def Flush():
    print("Flushing")
    for progress in disk.flush():
      print("Flush progress {:.3f}%".format(progress), end='\r')
    print("\nFlushing done")

  Flush()

  print("Deleting files at random")
  for deleteFile in sample(disk.manifest, int(len(os.listdir('good_pics')) + len(os.listdir('filler_data')) * 0.7) ):
    disk.deleteFile(deleteFile["id"])
  print("Done")
  
  AddFiles('filler_data', 10, True)
  Flush()


if __name__ == "__main__":
  main()