from random import randint, sample, choice
from uuid import uuid4
import os
import sys
import json

REPEAT_FILES = 20

class Disk:
  def __init__(self, fragsize, fragdev):
    self._fragsize = fragsize
    self._fragdev = fragdev
    self.manifest = list()
    self.memory = list()
    self._staging = list()
    self._idcount = 0

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

  def delete_file(self, path):
    for id, entry in self.manifest.items():
      entry["deleted"] = entry["path"] == path

  def reformat(self, fragsize, fragdev):
    self._fragsize = fragsize
    self._fragdev = fragdev

  def get_file(self, path):
    fileentry = None
    for id, entry in self.manifest.items():
      if entry["path"] == path:
        fileentry = entry
        break

    buffer = bytearray()
    for start, end in fileentry["chunks"]:
      buffer.extend(self._memory[start:end])

    return buffer


def main():
  print("Starting...")
  disk = Disk(2**10, 8)

  for file in os.listdir('good_pics'):
    with open('good_pics/' + file, mode='rb') as f:
      print("Adding file " + file)
      disk.add_file(file, bytearray(f.read()), False)

  print("Added all files, flushing")
  for progress in disk.flush():
    print("Flush progress {:.2f}%".format(progress), end='\r')
  print("\nFlushing done")


if __name__ == "__main__":
  main()