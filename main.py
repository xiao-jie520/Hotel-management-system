from datetime import datetime
from nicegui import ui
import mysql.connector
ROOM_TYPE = ['单人间','大床房', '双人间']
PAGE_SYSTEM = '/page_system'
CUSTOMER_INFO_MANAGE = '/customer_info_manage'
PAGE_ROOM_MANAGE = '/page_room_manage'
PAGE_USER_MANAGE = '/page_user_manage'
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456"
)
cursor = db.cursor()
cursor.execute("USE demo01")
def menu():
    with ui.row().classes('w-full items-center'):
        result = ui.label().classes('mr-auto')
    with ui.button(icon='menu'):
        with ui.menu() as menu:
            ui.menu_item('入住系统', lambda: ui.navigate.to(PAGE_SYSTEM))
            ui.menu_item('住客信息管理系统',lambda: ui.navigate.to(CUSTOMER_INFO_MANAGE))
            ui.menu_item('房间管理系统', lambda: ui.navigate.to(PAGE_ROOM_MANAGE))
            ui.menu_item('用户管理系统',
                         lambda: ui.navigate.to(PAGE_USER_MANAGE), auto_close=False)
            ui.separator()
            ui.menu_item('关闭', menu.close)
@ui.page('/')
def page():
    with ui.column().classes('h-screen w-full items-center justify-center'):
        ui.label('酒店管理系统').classes('h-50 text-5xl')
        with ui.row().classes('w-full justify-center items-center h-10 '):
            username = ui.input(label='账号',value='admin')
            password = ui.input(label='密码', password=True)
        ui.label('').classes('h-3')
        ui.button('登录',on_click=lambda:login(username,password)).classes('w-52') 

def login(username,password):
    cursor.execute("SELECT * FROM users WHERE username = %s", (username.value,))
    user = cursor.fetchone()
    if user and user[1] == password.value:        
        ui.navigate.to('/page_system')
        ui.notify('欢迎回来')
    else:
        ui.notify('账号或密码错误')
def customer_info_get(customer_id):
    cursor.execute("SELECT * FROM customer_info WHERE customer_id = %s", (customer_id,))
    data = cursor.fetchone()
    if data:
        ui.notify(f' 身份证号: {data[0]} \n'
                  f' 姓名: {data[1]} \n'
                  f' 手机号: {data[2]} \n'
                  f' 性别: {data[3]} \n'
                  ,multi_line=True,
    classes='multi-line-notification',close_button="信息无误")
        return None
    else:
        ui.notify('该顾客不存在，请先录入身份')
        return None

def customer_add(customer_id,customer_name,customer_telephone,customer_sex):
    cursor.execute("SELECT 1 FROM customer_info WHERE customer_id = %s", (customer_id,))
    if cursor.fetchone():
        ui.notify('该住客已存在')
        return
    cursor.execute("INSERT INTO customer_info (customer_id, customer_name, customer_telephone, customer_sex) VALUES (%s, %s, %s, %s)",
                   (customer_id, customer_name, customer_telephone, customer_sex))
    db.commit()
    ui.notify('住客新增成功')
    ui.navigate.to(PAGE_SYSTEM)



def reserve_room(customer_id,expected_checkin,expected_checkout,room_id):
    cursor.execute("SELECT 1 FROM room_info WHERE room_id = %s", (room_id,))
    if not cursor.fetchone():
        ui.notify('该房间不存在')
        return
    cursor.execute("SELECT 1 FROM reservations WHERE room_id = %s AND (expected_checkin <= %s AND expected_checkout >= %s)",
                   (room_id, expected_checkout, expected_checkin))
    if cursor.fetchone():
        ui.notify('该房间已被预订')
        return
    cursor.execute("INSERT INTO reservations (customer_id, room_id, expected_checkin, expected_checkout) VALUES (%s, %s, %s, %s)",
                   (customer_id, room_id, expected_checkin, expected_checkout))
    db.commit()
    ui.notify('预订成功')
    ui.navigate.to(PAGE_SYSTEM)

def reserve_cancel(customer_id):
    cursor.execute("SELECT 1 FROM reservations WHERE customer_id = %s", (customer_id,))
    if not cursor.fetchone():
        ui.notify('该顾客不存在预订记录')
        return
    cursor.execute("DELETE FROM reservations WHERE customer_id = %s", (customer_id,))
    db.commit()
    ui.notify('预订取消成功')
    ui.navigate.to(PAGE_SYSTEM)

def reserve_update(customer_id,expected_checkin,expected_checkout,room_id):
    cursor.execute("SELECT 1 FROM reservations WHERE customer_id = %s AND room_id = %s",
                   (customer_id, room_id))
    if not cursor.fetchone():
        ui.notify('该顾客不存在该房间的预订记录')
        return
    cursor.execute("UPDATE reservations SET expected_checkin = %s, expected_checkout = %s WHERE customer_id = %s AND room_id = %s",
                   (expected_checkin, expected_checkout, customer_id, room_id))
    db.commit()
    ui.notify('预订更新成功')
    ui.navigate.to(PAGE_SYSTEM)

def customer_checkin(customer_id,room_id,checkin_time,checkout_time):
    cursor.execute("SELECT 1 FROM room_info WHERE room_id = %s AND room_status = '空闲'", (room_id,))
    if not cursor.fetchone():
        ui.notify('该房间不存在或已被预订')
        return
    cursor.execute("INSERT INTO checkins (customer_id, room_id, checkin_time, checkout_time) VALUES (%s, %s, %s, %s)",
                   (customer_id, room_id, checkin_time, checkout_time))
    db.commit()
    ui.notify('入住成功')
    ui.navigate.to(PAGE_SYSTEM)

def fast_checkin(customer_id):
    
    cursor.execute("SELECT room_id, expected_checkin, expected_checkout FROM reservations WHERE customer_id = %s", (customer_id,))
    data = cursor.fetchone()
    if data:
        room_id, checkin_time, checkout_time = data
        reserve_cancel(customer_id)
    else:
        ui.notify('该顾客已入住或未预定')
        return
    cursor.execute("INSERT INTO checkins (customer_id, room_id, checkin_time, checkout_time) VALUES (%s, %s, %s, %s)",
                   (customer_id, room_id, checkin_time, checkout_time))
    db.commit()
    ui.notify('快速入住成功',close_button="确认")
    ui.navigate.to(PAGE_SYSTEM)
    
def checkin_update(customer_id,room_id,checkin_time,checkout_time):
    cursor.execute("SELECT 1 FROM checkins WHERE customer_id = %s", (customer_id,))
    if not cursor.fetchone():
        ui.notify('该顾客不存在该房间的入住记录')
        return
    cursor.execute("UPDATE checkin_record SET checkin_time = %s, checkout_time = %s WHERE customer_id = %s AND room_id = %s",
                   (checkin_time, checkout_time, customer_id, room_id))
    db.commit()
    ui.notify('入住更新成功')
    ui.navigate.to(PAGE_SYSTEM)

def customer_checkout(customer_id,room_id,checkout_time):
    cursor.execute("SELECT * FROM checkins WHERE customer_id = %s AND room_id = %s", (customer_id, room_id))
    data = cursor.fetchone()
    if data:
        checkin_time = data[2]
    else:
        ui.notify('该顾客不存在该房间的入住记录')
        return
    cursor.execute("UPDATE checkins SET checkout_time = %s WHERE customer_id = %s AND room_id = %s",
                   (checkout_time, customer_id, room_id))
    db.commit()
    cursor.execute("SELECT price FROM room_info WHERE room_id = %s", (room_id,))
    price = cursor.fetchone()[0]
    fmt = "%Y-%m-%d"
    checkin_dt = datetime.strptime(str(checkin_time), fmt)
    checkout_dt = datetime.strptime(str(checkout_time), fmt)
    ui.notify(f"该顾客的入住时间为{checkin_time}，退房时间为{checkout_time}，房间价格为{price * (checkout_dt - checkin_dt).days}元",close_button="确认")
    cursor.execute("DELETE FROM checkins WHERE customer_id = %s AND room_id = %s", (customer_id, room_id))
    db.commit()
    ui.timer(5.0,lambda:ui.navigate.to(PAGE_SYSTEM),once=True)
    
def update_checkin(customer_id,room_id,checkin_time,checkout_time):
    cursor.execute("SELECT 1 FROM checkins WHERE customer_id = %s", (customer_id,))
    if not cursor.fetchone():
        ui.notify('该顾客不存在该房间的入住记录')
        return
    cursor.execute("UPDATE checkin_record SET checkin_time = %s, checkout_time = %s WHERE customer_id = %s AND room_id = %s",
                   (checkin_time, checkout_time, customer_id, room_id))
    db.commit()
    ui.notify('入住更新成功')
    ui.navigate.to(PAGE_SYSTEM)



@ui.page(PAGE_SYSTEM)
def page_system():
    with ui.row():
        menu()
        ui.label('酒店入住系统').classes('text-xl mb-4')
    with ui.row():
        with ui.column().classes('w-100'):
            cursor.execute("SELECT * FROM room_info")
            data = [{'room_id': row[0], 'room_capacity': row[1], 'room_type': row[2],'price':row[3],'room_status':row[4]} for row in cursor.fetchall()]
            ui.table(columns=[
                {'name': 'room_id','label':'房间号', 'field': 'room_id'},
                {'name': 'room_capacity','label':'房间容量', 'field': 'room_capacity'},
                {'name': 'room_type','label':'房间类型', 'field': 'room_type'},
                {'name': 'price','label':'价格', 'field': 'price'},
                {'name': 'room_status','label':'房间状态', 'field': 'room_status'}
            ], rows=data,title='房间状态',row_key='room_id').classes('w-100 h-66')

            cursor.execute("SELECT * FROM reservations")
            data = [{'customer_id': row[0], 'room_id': row[1], 'expected_checkin': row[2], 'expected_checkout': row[3]} for row in cursor.fetchall()]
            ui.table(columns=[
                {'name': 'customer_id','label':'身份证号', 'field': 'customer_id'},
                {'name': 'room_id','label':'房间号', 'field': 'room_id'},
                {'name': 'expected_checkin','label':'预计入住时间', 'field': 'expected_checkin'},
                {'name': 'expected_checkout','label':'预计退房时间', 'field': 'expected_checkout'}
            ], rows=data,title='房间预订状态',row_key='room_id').classes('w-100 h-66')

            cursor.execute("SELECT * FROM checkins")
            data = [{'customer_id': row[0], 'room_id': row[1], 'checkin_time': row[2], 'checkout_time': row[3]} for row in cursor.fetchall()]
            ui.table(columns=[
                {'name': 'customer_id','label':'身份证号', 'field': 'customer_id'},
                {'name': 'room_id','label':'房间号', 'field': 'room_id'},
                {'name': 'checkin_time','label':'入住时间', 'field': 'checkin_time'},
                {'name': 'checkout_time','label':'退房时间', 'field': 'checkout_time'}
            ], rows=data,title='住客入住状态',row_key='room_id').classes('w-100 h-66')
        with ui.column():
            with ui.card().classes('w-96'):
                ui.label('顾客信息登记').classes('text-lg')
                customer_name1 = ui.input(label='姓名')
                customer_phone1 = ui.input(label='电话')
                customer_identity1 = ui.input(label='身份证号')
                customer_sex1 = ui.select(label='性别', options=['男', '女']).classes('w-30')
                ui.button('登记', on_click=lambda: customer_add(customer_identity1.value,customer_name1.value,customer_phone1.value,customer_sex1.value))
            with ui.card().classes('w-96'):
                ui.label('预定管理').classes('text-lg')
                customer_identity2 = ui.input(label='身份证号')
                expected_checkin2 = ui.date_input('预计入住时间')
                expected_checkout2 = ui.date_input('预计退房时间')
                room_id2 = ui.input(label='房间号')
                with ui.row():
                    ui.button('预订',on_click=lambda : reserve_room(customer_identity2.value,expected_checkin2.value,expected_checkout2.value,room_id2.value))
                    ui.button('修改预订',on_click=lambda : reserve_update(customer_identity2.value,expected_checkin2.value,expected_checkout2.value,room_id2.value))
                    ui.button('取消预订',on_click=lambda : reserve_cancel(customer_identity2.value))
        with ui.column():
            with ui.card().classes('w-96'):
                ui.label('顾客入住登记').classes('text-lg mb-4')
                with ui.row():
                    customer_identity3 = ui.input(label='身份证号',value=customer_identity1.value)
                    ui.button('查询', on_click=lambda: customer_info_get(customer_identity3.value))
                customer_checkin_time3 = ui.date_input('入住时间')
                customer_checkout_time3 = ui.date_input('退房时间')
                customer_room_type3 = ui.select(label='房间类型', options=ROOM_TYPE).classes('w-30')
                customer_room_id3 = ui.input(label='房间号')
                ui.button('入住', on_click=lambda: customer_checkin(customer_identity3.value,customer_room_id3.value,customer_checkin_time3.value,customer_checkout_time3.value))
            
            with ui.card().classes('w-96'):
                ui.label('已预定快捷入住')
                customer_identity4 = ui.input(label='身份证号')
                
                ui.button('快捷入住', on_click=lambda: fast_checkin(customer_identity4.value))
        with ui.card().classes('w-96'):
            ui.label('顾客退房登记').classes('text-lg mb-4')
            with ui.row():
                customer_identity5 = ui.input(label='身份证号',value=customer_identity1.value)
                ui.button('查询', on_click=lambda: customer_info_get(customer_identity5.value))
            customer_checkout_time5 = ui.date_input('退房时间')
            customer_room_id5 = ui.input(label='房间号')
            ui.button('退房', on_click=lambda: customer_checkout(customer_identity5.value,customer_room_id5.value,customer_checkout_time5.value))

@ui.page('/page_submit_success')
def page_submit_success():
    menu()
    with ui.card().classes('w-1/4 mt-8 left-1/2 justify-start'):
        ui.label('提交成功')
        ui.label('顾客房间号为')
        ui.button('返回',on_click=lambda:ui.navigate.to('/page_system')).classes('w-52')


def submit(customer_name,customer_phone,customer_id):
    customer_room_number = customer_id[:4]
    return customer_room_number


'''用户管理系统'''

def user_add(username,password):
    cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        ui.notify('用户名已存在')
        ui.navigate.to(PAGE_USER_MANAGE)
        return -1  # 用户名已存在
        
    else:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        ui.notify('添加成功')
        ui.navigate.to(PAGE_USER_MANAGE)
        return 1


def user_delete(username):
    if username == 'admin':
        ui.notify('不能删除管理员账号')
        return -1  # 不能删除管理员账号
    cursor.execute("DELETE FROM users WHERE username = %s", (username,))
    db.commit()
    ui.notify('删除成功')
    ui.navigate.to(PAGE_USER_MANAGE)


def user_password(username,password):
    cursor.execute("UPDATE users SET password = %s WHERE username = %s", (password, username))
    db.commit()
    ui.notify('修改成功')
    ui.navigate.to(PAGE_USER_MANAGE)


@ui.page('/page_user_manage')
def page_user_manage():
    with ui.row():
        menu()
        ui.label('用户管理系统').classes('text-xl mb-4')
    with ui.row().classes('w-full justify-center'):
        
        cursor.execute("SELECT * FROM users")
        data = [{'username': row[0], 'password': row[1]} for row in cursor.fetchall()]
        ui.table(columns=[
            {'name': 'username', 'label': '账号', 'field': 'username'},
            {'name': 'password', 'label': '密码', 'field': 'password'},
        ], rows = data , row_key='username',title='用户列表').classes('w-96')
        ui.label('').classes('w-40')
        with ui.column().classes('w-96'):
            with ui.card().classes('w-96'):
                ui.label('添加用户').classes('text-xl mb-4')
                username1 = ui.input(label='账号')
                password1 = ui.input(label='密码',password = True)
                ui.button('添加', on_click=lambda: user_add(username1.value,password1.value))
            with ui.card().classes('w-96'):
                ui.label('删除用户').classes('text-xl mb-4')
                username2 = ui.input(label='账号')
                ui.button('删除', on_click=lambda: user_delete(username2.value))    
            with ui.card().classes('w-96'):
                ui.label('修改密码').classes('text-xl mb-4')
                username3 = ui.input(label='账号')
                password3 = ui.input(label='新密码',password = True)
                ui.button('修改', on_click=lambda: user_password(username3.value,password3.value))

'''房间管理系统'''
def room_add(room_id,room_capacity,room_type,price):
    cursor.execute("SELECT 1 FROM room_info WHERE room_id = %s", (room_id,))
    if cursor.fetchone():
        ui.notify('房间号已存在')
        return
    cursor.execute("INSERT INTO room_info (room_id, room_capacity, room_type, price) VALUES (%s, %s, %s, %s)",
                   (room_id, room_capacity, room_type, price))
    db.commit()
    ui.navigate.to(PAGE_ROOM_MANAGE)
    ui.notify('新增房间成功')

def room_delete(room_id):
    cursor.execute("SELECT 1 FROM room_info WHERE room_id = %s", (room_id,))
    if not cursor.fetchone():
        ui.notify('房间号不存在')
        return
    cursor.execute("DELETE FROM room_info WHERE room_id = %s", (room_id,))
    db.commit()
    ui.navigate.to(PAGE_ROOM_MANAGE)
    ui.notify('删除房间成功')

def room_update(room_id,room_capacity,room_type,price):
    cursor.execute("SELECT 1 FROM room_info WHERE room_id = %s", (room_id,))
    if not cursor.fetchone():
        ui.notify('房间号不存在')
        return
    cursor.execute("UPDATE room_info SET room_capacity = %s, room_type = %s, price = %s WHERE room_id = %s",
                   (room_capacity, room_type, price, room_id))
    db.commit()
    ui.navigate.to(PAGE_ROOM_MANAGE)
    ui.notify('修改房间成功')

@ui.page('/page_room_manage')
def page_room_manage():
    with ui.row():
        menu()
        ui.label('房间管理系统').classes('text-xl mb-4')
    with ui.row().classes('w-full justify-center'):
        
        cursor.execute("SELECT * FROM room_info")

        data = [{'room_id': row[0], 'room_capacity': row[1], 'room_type': row[2], 'price': row[3]} for row in cursor.fetchall()]
        ui.table(columns=[
            {'name': 'room_id', 'label': '房间号', 'field': 'room_id'},
            {'name': 'room_capacity', 'label': '房间容量', 'field': 'room_capacity'},
            {'name': 'room_type', 'label': '房间类型', 'field': 'room_type'},
            {'name': 'price', 'label': '房间价格', 'field': 'price'},
        ], rows = data , row_key='room_id',title='现存房间列表').classes('w-96')

        with ui.column():
            with ui.card().classes('w-96'):
                ui.label('新增房间').classes('text-lg mb-4')
                room_id1 = ui.input(label='房间号')
                room_capacity1 = ui.input(label='房间容量')
                room_type1 = ui.select(label='房间类型', options=ROOM_TYPE, value=ROOM_TYPE[0]).classes('w-full')
                price1 = ui.input(label='房间价格')
                ui.button('新增房间',on_click=lambda: room_add(room_id1.value,room_capacity1.value,room_type1.value,price1.value))

            with ui.card().classes('w-96'):
                ui.label('删除房间').classes('text-lg mb-4')
                room_id2 = ui.input(label='房间号')
                ui.button('删除房间',on_click=lambda: room_delete(room_id2.value))
        with ui.card().classes('w-96'):
            ui.label('修改房间信息').classes('text-lg mb-4')
            room_id3 = ui.input(label='房间号')
            room_capacity3 = ui.input(label='房间容量')
            room_type3 = ui.select(label='房间类型', options=ROOM_TYPE, value=ROOM_TYPE[0]).classes('w-full')
            price3 = ui.input(label='房间价格')
            ui.button('修改房间信息',on_click=lambda: room_update(room_id3.value,room_capacity3.value,room_type3.value,price3.value))

def customer_add(customer_id,customer_name,customer_telephone,customer_sex):
    cursor.execute("SELECT 1 FROM customer_info WHERE customer_id = %s", (customer_id,))
    if cursor.fetchone():
        ui.notify('该住客已存在')
        return
    cursor.execute("INSERT INTO customer_info (customer_id, customer_name, customer_telephone, customer_sex) VALUES (%s, %s, %s, %s)",
                   (customer_id, customer_name, customer_telephone, customer_sex))
    db.commit()
    ui.notify('住客新增成功')
    ui.navigate.to(CUSTOMER_INFO_MANAGE)   

def customer_delete(customer_id):
    cursor.execute("SELECT 1 FROM customer_info WHERE customer_id = %s", (customer_id,))
    if not cursor.fetchone():
        ui.notify('该住客不存在')
        return
    cursor.execute("DELETE FROM customer_info WHERE customer_id = %s", (customer_id,))
    db.commit()
    ui.notify('住客删除成功')
    ui.navigate.to(CUSTOMER_INFO_MANAGE)   

def customer_update(customer_id,customer_name,customer_telephone,customer_sex):
    cursor.execute("SELECT 1 FROM customer_info WHERE customer_id = %s", (customer_id,))
    if not cursor.fetchone():
        ui.notify('该住客不存在')
        return
    cursor.execute("UPDATE customer_info SET customer_name = %s, customer_telephone = %s, customer_sex = %s WHERE customer_id = %s",
                   (customer_name, customer_telephone, customer_sex, customer_id))
    db.commit()
    ui.notify('住客信息更新成功')
    ui.navigate.to(CUSTOMER_INFO_MANAGE)

@ui.page('/customer_info_manage')
def customer_info_manage():
    with ui.row():
        menu()
        ui.label('住客信息管理系统').classes('text-xl mb-4')
        ui.label('').classes('h-12')
    with ui.row().classes('w-full justify-center'):
        cursor.execute("SELECT * FROM customer_info")
        # columns = ['身份证号','姓名','手机号','性别']
        data = [{'customer_id': row[0], 'customer_name': row[1], 'customer_telephone': row[2], 'customer_sex': row[3]} for row in cursor.fetchall()]
        ui.table(columns=[
            {'name': 'customer_id', 'label': '身份证号', 'field': 'customer_id'},
            {'name': 'customer_name', 'label': '姓名', 'field': 'customer_name'},
            {'name': 'customer_telephone', 'label': '手机号', 'field': 'customer_telephone'},
            {'name': 'customer_sex', 'label': '性别', 'field': 'customer_sex'},
        ], rows=data).classes('w-120')
        ui.label('').classes('w-12')
        with ui.column():
            with ui.card().classes('w-96'):
                ui.label('新增住客').classes('text-xl mb-4')
                customer_id1 = ui.input('身份证号').classes('w-94')
                customer_name1 = ui.input('姓名').classes('w-20')
                customer_telephone1 = ui.input('手机号').classes('w-60')
                customer_sex1 = ui.select(label='性别',options=['男', '女','其他'], value='男').classes('w-20')
                ui.button('新增住客', on_click=lambda: customer_add(customer_id1.value,customer_name1.value,customer_telephone1.value,customer_sex1.value)).classes('w-30')
            with ui.card().classes('w-96'):
                ui.label('删除住客').classes('text-xl mb-4')
                customer_id2 = ui.input('身份证号').classes('w-94')
                ui.button('删除住客', on_click=lambda: customer_delete(customer_id2.value)).classes('w-30')
        with ui.card().classes('w-96'):
            ui.label('修改住客信息').classes('text-xl mb-4')
            customer_id3 = ui.input('身份证号').classes('w-94')
            customer_name3 = ui.input('姓名').classes('w-20')
            customer_telephone3 = ui.input('手机号').classes('w-60')
            customer_sex3 = ui.select(label='性别',options=['男', '女','其他'], value='男').classes('w-20')
            ui.button('修改住客信息', on_click=lambda: customer_update(customer_id3.value,customer_name3.value,customer_telephone3.value,customer_sex3.value)).classes('w-30')
ui.run(title='酒店管理系统')