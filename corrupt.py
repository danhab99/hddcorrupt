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
    self.manifest = dict()
    self._memory = list()
    self._staging = list()
    self._idcount = 0

  def add_file(self, path, bits, filler):
    c = list(chunks(bits, self._fragsize))
    c.reverse()
    self._staging.append({
      "id": self._idcount,
      "path": path,
      "chunks": c,
      "isFiller": filler
    })
    self._idcount += 1
    
  def _getStagedChunks(self):
    return sum([len(x["chunks"]) for x in self._staging])

  def flush(self):
    initialChunkCount = float(self._getStagedChunks())
    while all([len(x["chunks"]) > 0 for x in self._staging]):
      file = choice(self._staging)
      start = len(self._memory)

      for _ in range(min(len(file["chunks"]), randint(1, self._fragdev))):
        self._memory.extend(file["chunks"].pop())

      end = len(self._memory)

      if file["id"] not in self.manifest.keys():
        self.manifest[file["id"]] = {
          "chunks": list(),
          "deleted": False,
          "path": file["path"]
        }

      self.manifest[file["id"]]["chunks"].append((start, end))
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