import errno
import os
import io
import time
import pty
import select
import subprocess
from random import randrange

def tty_capture(cmd, args, read_size=2048, sleep_count=1,
                sleep_interval=0.5, arg_interval=0.1):
  """Capture the output of cmd with args to stdin,
  with stdin, stdout and stderr as TTYs.

  Based on Andy Hayden's gist:
  https://gist.github.com/hayd/4f46a68fc697ba8888a7b517a414583e
  """
  mo, so = pty.openpty()  # provide tty to enable line-buffering
  me, se = pty.openpty()  
  mi, si = pty.openpty()  

  p = subprocess.Popen(cmd, bufsize=1, stdin=si, stdout=so,
                       stderr=se, close_fds=True)
  
  for fd in [so, se, si]:
    os.close(fd)

  for bts in args:
    if type(bts) is not bytes:
      bts = bts.encode('utf8')
    os.write(mi, bts)
    time.sleep(arg_interval)

  select_timeout = 0.04  # seconds
  readable = [mo, me]
  result = {mo: b'', me: b''}
  count = 0
  try:
    while readable:
      ready, _, _ = select.select(readable, [], [], select_timeout)
      for fd in ready:
        try:
          data = os.read(fd, read_size)
        except OSError as e:
          if e.errno != errno.EIO:
            raise
          # EIO means EOF on some systems
          readable.remove(fd)
        else:
          if not data: # EOF
            readable.remove(fd)
          result[fd] += data
      if not ready:
        count += 1
        time.sleep(sleep_interval)
        if count > sleep_count :
          os.write(mi, b'q')
          break

  finally:
    for fd in [mo, me, mi]:
      os.close(fd)
    if p.poll() is None:
      p.terminate()
    p.wait()

  return result[mo].decode("utf-8"), result[me]
