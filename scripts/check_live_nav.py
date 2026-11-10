import urllib.request

url = 'https://fairly-private-supported-killing.trycloudflare.com/'
with urllib.request.urlopen(url) as resp:
    html = resp.read().decode('utf-8')
print("mainScreenSwitcher in public HTML:", 'mainScreenSwitcher' in html)
print("Hidden style present:", 'style="display:none !important;"' in html)
