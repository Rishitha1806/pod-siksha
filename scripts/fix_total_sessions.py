with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\r\n', '\n')

old_str = '''        total_projects = conn.execute("SELECT COUNT(*) FROM video_projects WHERE user_id = ?", (uid,)).fetchone()[0]
        total_doubts = conn.execute("SELECT COUNT(*) FROM doubts WHERE user_id = ?", (uid,)).fetchone()[0]'''

new_str = '''        total_projects = conn.execute("SELECT COUNT(*) FROM video_projects WHERE user_id = ?", (uid,)).fetchone()[0]
        total_sessions = total_projects
        total_doubts = conn.execute("SELECT COUNT(*) FROM doubts WHERE user_id = ?", (uid,)).fetchone()[0]'''

assert old_str in text, 'old_str not found'
text = text.replace(old_str, new_str, 1)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Fixed total_sessions in server.py!')
