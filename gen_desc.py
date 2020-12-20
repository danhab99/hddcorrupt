from json import load

# https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix='B'):
  for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
    if abs(num) < 1024.0:
      return "%3.1f%s%s" % (num, unit, suffix)
    num /= 1024.0
  return "%.1f%s%s" % (num, 'Yi', suffix)

with open('selections.list', 'r') as lst:
  for uid in lst:
    uid = uid.strip()
    with open('corrupt_pics/' + uid + '.json', 'r') as js:
      desc = load(js)
    
    with open('corrupt_pics/' + uid + '.txt', 'w+') as out:
      out.write('Item ')
      out.write(uid)
      out.write(' from ')
      out.write(desc['original'])
      out.write('\n')

      out.write('Image was broken into chunks of ')
      out.write(sizeof_fmt(desc['chunk size']))
      out.write(' and corrupted at a rate of ')
      out.write('{:.2f}'.format(desc['corruption rate']))
      out.write('\n')

      out.write('Harddrive skipped ')
      out.write(str(desc['skip rate']))
      out.write(' times while writing\n')

      out.write('Files that overwrote this image include: ')
      out.write(', '.join(desc['injected files']))
      out.write('\n')