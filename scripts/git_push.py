import ctypes, ctypes.wintypes, subprocess, sys

class CREDENTIAL(ctypes.Structure):
    _fields_ = [
        ('Flags', ctypes.wintypes.DWORD), ('Type', ctypes.wintypes.DWORD),
        ('TargetName', ctypes.wintypes.LPWSTR), ('Comment', ctypes.wintypes.LPWSTR),
        ('LastWritten', ctypes.wintypes.FILETIME), ('CredentialBlobSize', ctypes.wintypes.DWORD),
        ('CredentialBlob', ctypes.POINTER(ctypes.c_byte)), ('Persist', ctypes.wintypes.DWORD),
        ('AttributeCount', ctypes.wintypes.DWORD), ('Attributes', ctypes.c_void_p),
        ('TargetAlias', ctypes.wintypes.LPWSTR), ('UserName', ctypes.wintypes.LPWSTR)
    ]

pcred = ctypes.POINTER(CREDENTIAL)()
res = ctypes.windll.advapi32.CredReadW('git:https://github.com', 1, 0, ctypes.byref(pcred))
if not res:
    print('Failed to read git credentials')
    sys.exit(1)

user = pcred.contents.UserName
blob = ctypes.string_at(pcred.contents.CredentialBlob, pcred.contents.CredentialBlobSize)
token = blob.decode('utf-16' if b'\x00' in blob else 'utf-8').strip()
ctypes.windll.advapi32.CredFree(pcred)

msg = sys.argv[1] if len(sys.argv) > 1 else 'chore: update'
subprocess.run(['git', 'add', '-A'], cwd=r'C:\Users\jvris\Downloads\pod-siksha')
subprocess.run(['git', 'commit', '-m', msg], cwd=r'C:\Users\jvris\Downloads\pod-siksha')
cmd = ['git', 'push', f'https://{user}:{token}@github.com/Rishitha1806/pod-siksha.git', 'HEAD:refs/heads/main']
p = subprocess.run(cmd, cwd=r'C:\Users\jvris\Downloads\pod-siksha', capture_output=True, text=True)
print('Push result:', p.stdout, p.stderr)

cmd_fetch = ['git', 'fetch', f'https://{user}:{token}@github.com/Rishitha1806/pod-siksha.git', 'main:refs/remotes/origin/main']
subprocess.run(cmd_fetch, cwd=r'C:\Users\jvris\Downloads\pod-siksha', capture_output=True, text=True)
