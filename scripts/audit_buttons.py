import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

buttons = re.findall(r'<button([^>]*)>(.*?)</button>', html, re.DOTALL)
print(f"Total buttons: {len(buttons)}")
for idx, (attrs, content) in enumerate(buttons):
    id_m = re.search(r'id=["\']([^"\']+)["\']', attrs)
    click_m = re.search(r'onclick=["\']([^"\']+)["\']', attrs)
    cls_m = re.search(r'class=["\']([^"\']+)["\']', attrs)
    btn_id = id_m.group(1) if id_m else 'NO_ID'
    btn_onclick = click_m.group(1) if click_m else 'NO_ONCLICK'
    btn_cls = cls_m.group(1) if cls_m else 'NO_CLASS'
    content_text = ' '.join(re.sub(r'<[^>]+>', '', content).split())[:35]
    out_str = f"{idx+1:2d}: id={btn_id:25} | onclick={btn_onclick:35} | text='{content_text}'"
    print(out_str.encode('ascii', 'replace').decode('ascii'))
