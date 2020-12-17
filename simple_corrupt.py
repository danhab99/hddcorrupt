import os

from random import randint, choice, random
from uuid import uuid4
from json import dump
from imghdr import what
from math import sqrt

try:
  os.mkdir("corrupt_pics")
except:
  pass

def corrupt(tid):
  def log(msg):
    print("Thread %s: %s" % (tid, msg))

  for picture_path in os.listdir('good_pics'):
    log("Corrupting " + picture_path)
    file_size = os.path.getsize('good_pics/' + picture_path)

    with open('good_pics/' + picture_path, 'rb') as picture:
      uid = str(uuid4())
      ext = os.path.splitext(picture_path)[1]
      chunk_size = randint(5, 30)
      corruption_rate = random()
      skip_rate = randint(0, 50)
      description = {
        "original": picture_path,
        "chunk size": file_size // chunk_size,
        "corruption rate": corruption_rate,
        "injected files": [],
        "skip rate": skip_rate
      }

      log("Established parameters")
      corrupt_path = 'corrupt_pics/' + uid + ext
      with open(corrupt_path, 'wb+') as out:
        bytes_written = 0
        while bytes_written < file_size:
          leng = int((random() * file_size) // chunk_size)
          bytes_written += leng
          skip_avaliable = (picture.tell() // leng)

          if random() > corruption_rate ** (skip_rate / 10) and skip_avaliable > 0:
            skip_dir = 1 if random() > 0.5 else -1
            skip_times = randint(1, skip_avaliable)

            for _ in range(skip_times):
              try:
                picture.seek(picture.tell() + (leng * skip_dir))

              except Exception as e:
                print("ERROR " + str(e))

          if random() > corruption_rate:
            out.write(picture.read(leng))
            log("Wrote {} good bytes, {:.2f}% done".format(leng, bytes_written / file_size))
          else:
            new_file_path = choice(os.listdir('filler_data'))
            description["injected files"].append(new_file_path)
            with open('filler_data/' + new_file_path, 'rb') as filler:
              out.write(filler.read(leng))
              log("Wrote {} bad bytes, {:.2f}% done".format(leng, bytes_written / file_size))

    if what('corrupt_pics/' + uid + ext):
      log("Valid picture")
      with open('corrupt_pics/' + uid + '.json', 'w+') as f:
        dump(description, f)
    else:
      log("Invalid pic")
      os.remove(corrupt_path)

if __name__ == '__main__':
    for i in range(50):
      corrupt(i)
