from random import randint, sample, choice
import os

def chunks(lst, n):
  """Yield successive n-sized chunks from lst."""
  for i in range(0, len(lst), n):
    yield lst[i:i + n]

class Disk:
  def __init__(self, fragsize, fragdev):
    self._fragsize = fragsize
    self._fragdev = fragdev
    self._manifest = dict()
    self._memory = list()
    self._staging = list()
    self._idcount = 0

  def add_file(self, path, bits, filler):
    self._staging.append({
      "id": self._idcount,
      "path": path,
      "chunks": list(chunks(bits, self._fragsize)),
      "isFiller": filler
    })
    self._idcount += 1

  def flush(self):
    while all([len(x["chunks"]) > 0 for x in self._staging]):
      file = choice(self._staging)
      start = len(self._memory)

      for _ in range(randint(1, self._fragdev)):
        self._memory.extend(file["chunks"].pop())

      end = len(self._memory)

      if file["id"] not in self._manifest.keys():
        self._manifest[file["id"]] = list()

      self._manifest[file["id"]].append((start, end))
      

def main():
  print("Starting...")
  disk = Disk(1024, 4)
  for file in os.listdir('good_pics'):
    with open('good_pics/' + file, mode='rb') as f:
      print("Adding file " + file)
      disk.add_file(file, f.read(), False)

  print("Added all files, flushing")
  disk.flush()
  print("Flushing done")


if __name__ == "__main__":
  main()