with open('C:/Users/jvris/Downloads/pod-siksha/static/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('<header class="master-header">')
end = text.find('</header>', start) + len('</header>')
print(text[start:end])
