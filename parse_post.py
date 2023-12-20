import json
import time

import vk
import pprint
import re
import sqlite3
import os

API_KEY = 'TOKEN'
v = "5.131"
sesion = vk.API(access_token=API_KEY)

own_id = -28905875
pst_id = 32634653


# conc = f"{own_id}_{pst_id}"
#
# wl2 = sesion.wall.getComments(v=v, owner_id=own_id, post_id=pst_id, extend=1, count=1, thread_items_count=5)
# wl = sesion.wall.getById(v=v, posts=conc)
#
# lk = sesion.likes.getList(v=v, owner_id=own_id, item_id=pst_id, type='post', count=1, extended=1)
# pprint.pp(wl)
# pprint.pp(wl2)
# pprint.pp(lk)
# print(len(lk['items']))

def OnlyBigSize(pht):
    pht['photo']['sizes'] = [sorted(pht['photo']['sizes'], key=lambda x: x['height'])[-1]]
    return pht


def parsePost(own_id, pst_id):
    print(f"Parse {own_id}_{pst_id} ", end=' ')
    str_pst = f"{own_id}_{pst_id}"
    pst_get = sesion.wall.getById(v=v, posts=str_pst)[0]
    mn = {}
    mn['attachments'] = [OnlyBigSize(el) if el.get('type', '') == 'photo' else el for el in pst_get['attachments']]
    mn['date'] = pst_get['date']
    mn['from_id'] = pst_get['from_id']
    mn['owner_id'] = own_id
    mn['text'] = pst_get['text']
    mn['views'] = pst_get['views']
    mn['id'] = pst_get['id']
    mn['reposts'] = pst_get['reposts']
    mn['likes'] = []
    mn['comments'] = []

    get_coms = sesion.wall.getComments(v=v, owner_id=own_id, post_id=pst_id, extended=1, count=1000, thread_items_count=10, sort='asc', fields='city,bdate')
    # print(get_coms)
    profs = {el['id']: el for el in get_coms["profiles"]}
    trs = []
    for el in get_coms['items']:
        a = {'id': el['id'],
             'date': el['date'],
             'text': el.get('text', ''),
             'user': profs.get(el['from_id'], {}),
             'from_id': el['from_id']}
        trs.extend(el['thread']['items'])
        mn['comments'].append(a)

    for el in trs:
        a = {'id': el['id'],
             'date': el['date'],
             'text': el.get('text', ''),
             'user': profs.get(el['from_id'], {}),
             'from_id': el['from_id']}
        mn['comments'].append(a)
    # print(len(mn['comments']))
    # pprint.pp(mn)
    count_lim = 1000
    l_c = 0
    while len(mn['likes']) < count_lim:
        #print('л', end=' ')
        get_likes = sesion.likes.getList(v=v, owner_id=own_id, item_id=pst_id, type='post', count=1000, offset=l_c * 1000)
        time.sleep(0.05)
        # print(get_likes['count'])
        count_lim = get_likes['count']
        uuser=sesion.users.get(v=v,user_ids=get_likes['items'],fields="bdate,city")
        mn['likes'].extend(uuser)
        l_c += 1
    # print(len(mn['likes']))
    # print(get_likes)

    # pprint.pp(mn)
    folder_path = f"vake/{own_id}"

    # Проверяем, существует ли папка, и создаем её, если она не существует
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Создаем JSON файл в папке
    file_path = f"{folder_path}/{pst_id}.json"
    with open(file_path, 'w') as file:
        # Здесь вы можете записать данные в файл
        file.write(json.dumps(mn))
    print("Ended!")


# print(sesion.users.get(v=v))
[parsePost(own_id, el['id']) for el in sesion.wall.get(v=v, owner_id=own_id, count=100,offset=0)['items']]
# parsePost(own_id,pst_id)
