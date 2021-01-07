import tkinter as tk
from tkinter import ttk, scrolledtext, END, INSERT, Menu
import tkinter.messagebox
import tkinter.filedialog

import pymysql
import threading
import os
import json
import base64
import time


def write_log(func):
    def wrapper(self, *args, **kwargs):
        self.update_detail('{}, done'.format(func.__name__))
        return func(self, *args, **kwargs)

    return wrapper


class Application:
    def __init__(self):
        self.child = []
        self.window = tk.Tk()
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        self.tabControl = None
        self.__init_window()
        self.__create_widgets()
        self.__load_saved()
        self.window.update()
        self.__set_win_center(self.window)
        self.window.mainloop()

    def __del__(self):
        try:
            self.cursor.close()
            self.conn.close()
        except AttributeError as e:
            self.update_detail(str(e))

    def __fork(self, func, args=()):
        t = threading.Thread(target=func, args=args)
        t.setDaemon(True)
        t.run()
        self.child.append(t)

    @staticmethod
    def __set_win_center(root, width='', height=''):
        if not width:
            width = root.winfo_width()
        if not height:
            height = root.winfo_height()
        scn_w, scn_h = root.maxsize()
        cen_x = (scn_w - width) / 2
        cen_y = (scn_h - height) / 2
        size_xy = '%dx%d+%d+%d' % (width, height, cen_x, cen_y)
        root.withdraw()
        root.geometry(size_xy)
        root.deiconify()

    def __load_saved(self):
        if not os.path.exists('app.cfg'):
            self.update_detail('No saved login detail')
        else:
            try:
                with open('app.cfg', encoding='utf-8') as config_file:
                    cfg = json.load(config_file)
                    self.login_server_name.set(base64.b64decode(cfg['server']).decode())
                    self.login_user_name.set(base64.b64decode(cfg['user']).decode())
                    self.login_pwd_name.set(base64.b64decode(cfg['pwd']).decode())
                    self.login_db_name.set(base64.b64decode(cfg['db']).decode())
                self.__connect_sql()
            except KeyError as e:
                self.update_detail(str(e))

    def __select_res(self):
        self.restorePath = tkinter.filedialog.askopenfilename()
        self.sel_name.set(os.path.split(self.restorePath)[1])
        self.restore_frame.deiconify()

    def __load_restore(self):
        _user = self.sql_user_name.get()
        _pwd = self.sql_pwd_name.get()
        _db = self.sql_db_name.get()
        os.popen('mysql -u{} -p{} --execute="drop database if exists {};"'.format(_user, _pwd, _db))
        os.popen('mysql -u{} -p{} --execute="create database {};"'.format(_user, _pwd, _db))
        os.popen('mysql -u{} -p{} {} < "{}"'.format(_user, _pwd, _db, self.restorePath))
        self.update_detail('restore {}'.format(self.restorePath))
        tkinter.messagebox.askokcancel(title='加载', message='加载完成')

    def __restore_sql(self):
        self.restore_frame = tk.Toplevel()
        self.restore_frame.title('加载')
        self.sql_user = ttk.Label(self.restore_frame, text='用户')
        self.sql_user.grid(column=0, row=0, sticky='W')
        self.sql_user_name = tk.StringVar()
        self.sql_user_entry = ttk.Entry(self.restore_frame, width=12, textvariable=self.sql_user_name)
        self.sql_user_entry.grid(column=0, row=1, sticky='W')

        self.sql_pwd = ttk.Label(self.restore_frame, text='密码')
        self.sql_pwd.grid(column=0, row=2, sticky='W')
        self.sql_pwd_name = tk.StringVar()
        self.sql_pwd_entry = ttk.Entry(self.restore_frame, width=12, textvariable=self.sql_pwd_name, show='*')
        self.sql_pwd_entry.grid(column=0, row=3, sticky='W')

        self.sql_db = ttk.Label(self.restore_frame, text='数据库名')
        self.sql_db.grid(column=0, row=4, sticky='W')
        self.sql_db_name = tk.StringVar()
        self.sql_db_entry = ttk.Entry(self.restore_frame, width=12, textvariable=self.sql_db_name)
        self.sql_db_entry.grid(column=0, row=5, sticky='W')
        space = ttk.Label(self.restore_frame, text='')
        space.grid(column=0, row=6, sticky='W')

        self.select = ttk.Button(self.restore_frame, text='选择备份', command=self.__select_res)
        self.select.grid(column=1, row=2)
        self.restore = ttk.Button(self.restore_frame, text='加载备份', command=self.__load_restore)
        self.restore.grid(column=1, row=3)
        self.selLabel = ttk.Label(self.restore_frame, text='已选择备份')
        self.selLabel.grid(column=2, row=2, sticky='W')
        self.sel_name = tk.StringVar()
        self.sel_name.set('None')
        self.sel_name_entry = ttk.Label(self.restore_frame, width=12, textvariable=self.sel_name)
        self.sel_name_entry.grid(column=2, row=3, sticky='W')

        self.restore_frame.update()
        self.__set_win_center(self.restore_frame)

    def __backup(self):
        try:
            id(self.cursor)
            backup_path = tkinter.filedialog.asksaveasfile(mode='w', defaultextension=".sql",
                                                           filetypes=[('mysql files', '.sql')])
            if not backup_path:
                return
            backup_path = backup_path.name
            _user = self.login_user_name.get()
            _pwd = self.login_pwd_name.get()
            _db = self.login_db_name.get()
            os.popen('mysqldump -u{} -p{} {} > "{}"'.format(_user, _pwd, _db, backup_path))
            tkinter.messagebox.askokcancel(title='备份', message='备份成功')
            self.update_detail('backup sql')
        except AttributeError as e:
            self.update_detail(str(e))
            tkinter.messagebox.showerror(title='备份失败', message='未连接到数据库')

    def update_detail(self, s):
        self.detail.configure(state=tk.NORMAL)
        self.detail.insert(INSERT, str(time.strftime("%Y-%m-%d %H:%M:%S  ", time.localtime())) + s + '\n\n')
        self.detail.see(END)
        self.detail.configure(state=tk.DISABLED)

    def __connect_sql(self):
        _server = self.login_server_name.get()
        _user = self.login_user_name.get()
        _pwd = self.login_pwd_name.get()
        _db = self.login_db_name.get()
        try:
            self.update_detail('Connecting to Mysql database')
            self.conn = pymysql.connect(_server, user=_user, passwd=_pwd, db=_db)
            self.cursor = self.conn.cursor()
            self.update_detail('Connect to database')
        except Exception as e:
            self.update_detail('Connect failed')
            self.update_detail(str(e))
        finally:
            if self.save_status.get():
                _server = base64.b64encode(_server.encode(encoding='utf-8')).decode()
                _user = base64.b64encode(_user.encode(encoding='utf-8')).decode()
                _pwd = base64.b64encode(_pwd.encode(encoding='utf-8')).decode()
                _db = base64.b64encode(_db.encode(encoding='utf-8')).decode()
                with open('app.cfg', 'w') as f:
                    json.dump({'server': _server, 'user': _user, 'pwd': _pwd, 'db': _db}, f)

    def treeview_sort_column(self, tv, col, reverse):
        try:
            tv_list = [(eval(tv.set(k, col)), k) for k in tv.get_children('')]
        except NameError:
            tv_list = [(tv.set(k, col), k) for k in tv.get_children('')]
        tv_list.sort(reverse=reverse)
        for index, (val, k) in enumerate(tv_list):
            tv.move(k, '', index)
        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))

    @write_log
    def __get_info(self):
        _id = self.io_book_id.get()
        _name = self.io_book_name.get()
        if _id:
            sel_sql = 'select * from book where book_id={};'.format(_id)
        else:
            sel_sql = 'select * from book where book_name=\'{}\';'.format(_name)
        try:
            self.cursor.execute(sel_sql)
            _result = self.cursor.fetchone()
            _message = '书籍名称:{}\n目前数量:{}\n价格:{}'.format(_result[1], _result[2], round(_result[3] / 1000, 3))
            ok = tkinter.messagebox.askokcancel(title='查询结果', message=_message)
        except TypeError as e:
            ok = tkinter.messagebox.showerror(title='查询结果', message='未查找到该书籍')
        except AttributeError as e:
            ok = tkinter.messagebox.showerror(title='查询结果', message='未连接到数据库')
        finally:
            self.conn.commit()

    @write_log
    def __sale(self):
        _id = self.io_book_id.get()
        _name = self.io_book_name.get()
        if _id:
            sel_sql = 'select * from book where book_id={};'.format(_id)
        else:
            sel_sql = 'select * from book where book_name=\'{}\';'.format(_name)
        try:
            self.cursor.execute(sel_sql)
            _result = self.cursor.fetchone()
            if _result[2] == 0:
                raise ValueError
            _message = '售出书籍:{}\n剩余数量:{}'.format(_result[1], _result[2] - 1)
            exe_sql = 'insert into trade(book_id,trade_type,trade_num) value({},\'out\',1);'.format(_result[0])
            self.cursor.execute(exe_sql)
            exe_sql = 'update book set num=num-1 where book_id={};'.format(_result[0])
            self.cursor.execute(exe_sql)
            ok = tkinter.messagebox.askokcancel(title='出售成功', message=_message)
        except TypeError as e:
            ok = tkinter.messagebox.showerror(title='出售失败', message='未查找到该书籍')
        except AttributeError as e:
            ok = tkinter.messagebox.showerror(title='出售失败', message='未连接到数据库')
        except ValueError as e:
            ok = tkinter.messagebox.showerror(title='出售失败', message='书籍已售罄')
        finally:
            self.io_book_id.set('')
            self.io_book_name.set('')
            self.conn.commit()

    @write_log
    def __ret(self):
        _id = self.io_book_id.get()
        _name = self.io_book_name.get()
        if _id:
            sel_sql = 'select * from book where book_id={};'.format(_id)
        else:
            sel_sql = 'select * from book where book_name=\'{}\';'.format(_name)
        try:
            self.cursor.execute(sel_sql)
            _result = self.cursor.fetchone()
            _message = '退还书籍:{}\n剩余数量:{}'.format(_result[1], _result[2] + 1)
            exe_sql = 'insert into trade(book_id,trade_type) value({},\'in\');'.format(_result[0])
            self.cursor.execute(exe_sql)
            exe_sql = 'update book set num=num+1 where book_id={};'.format(_result[0])
            self.cursor.execute(exe_sql)
            ok = tkinter.messagebox.askokcancel(title='退货成功', message=_message)
        except TypeError as e:
            ok = tkinter.messagebox.showerror(title='退货失败', message='未查找到该书籍')
        except AttributeError as e:
            ok = tkinter.messagebox.showerror(title='退货失败', message='未连接到数据库')
        finally:
            self.io_book_id.set('')
            self.io_book_name.set('')
            self.conn.commit()

    @write_log
    def __buy_one(self):
        try:
            _id = self.io_book_id.get()
            sel_sql = 'select * from book where book_id={};'.format(_id)
            self.cursor.execute(sel_sql)
            _result = self.cursor.fetchone()
            self.__buy_book(_id, _result[3], 1)
        except pymysql.err.ProgrammingError as e:
            tkinter.messagebox.showerror(title='进货失败', message='未查找到该书籍')
        except AttributeError as e:
            ok = tkinter.messagebox.showerror(title='进货失败', message='未连接到数据库')

    @write_log
    def __buy_book(self, bid, price, num):
        sel_sql = 'select * from supplier where sup_book_id={}'.format(bid)
        self.cursor.execute(sel_sql)
        _result = self.cursor.fetchall()
        _result = sorted(list(_result), key=lambda x: x[2])
        ok = True
        if _result[0][2] > price:
            ok = tkinter.messagebox.askokcancel(title='进货警告', message='最低进货价高于书籍销售价，是否继续进货')
        if ok:
            exe_sql = 'update book set num=num+{} where book_id={};'.format(num, bid)
            self.cursor.execute(exe_sql)
            exe_sql = 'insert into trade(book_id,trade_type,trade_num) value({},\'buy\',{});'.format(bid, num)
            self.cursor.execute(exe_sql)

    @write_log
    def __buy(self):
        sel_sql = 'select * from trade'
        try:
            self.cursor.execute(sel_sql)
            _result = self.cursor.fetchall()
            total = dict()
            for _, bid, _type, __ in _result:
                if bid not in total:
                    total.update({bid: 1})
                if _type == 'out':
                    total[bid] += 1
                else:
                    total[bid] -= 1
            t_num, t_price = 0, 0
            for bid in total:
                sel_sql = 'select * from book where book_id={};'.format(bid)
                self.cursor.execute(sel_sql)
                _result = self.cursor.fetchone()
                sub = total[bid] - _result[2] + 1
                if sub > 0:
                    self.__buy_book(bid, _result[3], sub)
                    t_num += sub
                    t_price += sub * _result[3]
            ok = tkinter.messagebox.askokcancel(title='进货成功',
                                                message='本次进货{}本书籍，花费{}元'.format(t_num, round(t_price / 1000, 3)))
        except AttributeError as e:
            ok = tkinter.messagebox.showerror(title='进货失败', message='未连接到数据库')
        finally:
            self.conn.commit()

    @write_log
    def __check_all(self):
        sel_sql = 'select * from book'
        try:
            self.cursor.execute(sel_sql)
            _result = self.cursor.fetchall()
            total = dict()
            new_frame = tk.Toplevel()
            new_frame.title('库存')
            tree = ttk.Treeview(new_frame, show='headings')
            tree['columns'] = ('书籍id', '书籍名称', '存量', '单价')
            for c in tree['columns']:
                tree.column(c, width=150, anchor='center')
                tree.heading(c, text=c)
            i = 0
            for bid, name, num, price in _result:
                tree.insert('', i, values=(bid, name, num, round(price / 1000, 3)))
                i += 1
            tree.pack()
            new_frame.update()
            self.__set_win_center(new_frame)
        except AttributeError as e:
            ok = tkinter.messagebox.showerror(title='查询失败', message='未连接到数据库')

    @staticmethod
    def __trans(x):
        x = list(x)
        if x[2] == 'in':
            x[2] = '退货'
        if x[2] == 'out':
            x[2] = '出售'
        if x[2] == 'buy':
            x[2] = '进货'
        return tuple(x[1:])

    @write_log
    def __latest_k_trade(self, k):
        sel_sql = 'select * from trade'
        try:
            self.cursor.execute(sel_sql)
            _result = list(self.cursor.fetchall())
            _result = _result[-min(k, len(_result)):]
            _result = list(map(self.__trans, _result))
            new_frame = tk.Toplevel()
            new_frame.title('交易记录')
            tree = ttk.Treeview(new_frame, show='headings')
            tree['columns'] = ('交易类型', '书籍名称', '交易数量')
            for c in tree['columns']:
                tree.column(c, width=150, anchor='center')
                tree.heading(c, text=c)
            i = 0
            cache = dict()
            for _id, _type, num in _result:
                if _id not in cache:
                    sel_sql = 'select * from book where book_id={};'.format(_id)
                    self.cursor.execute(sel_sql)
                    _result = self.cursor.fetchone()
                    cache.update({_id: _result[1]})
                name = cache[_id]
                tree.insert('', i, values=(_type, name, num))
                i += 1
            tree.pack()
            new_frame.update()
            self.__set_win_center(new_frame)
        except AttributeError as e:
            ok = tkinter.messagebox.showerror(title='查询失败', message='未连接到数据库')

    @write_log
    def __statistic(self):
        sel_sql = 'select * from trade'
        try:
            self.cursor.execute(sel_sql)
            _result = self.cursor.fetchall()
            total = dict()
            for _, bid, _type, __ in _result:
                if bid not in total:
                    total.update({bid: [0]})
                if _type == 'out':
                    total[bid][0] += 1
                elif _type == 'in':
                    total[bid][0] -= 1
            for bid in total:
                sel_sql = 'select * from book where book_id={};'.format(bid)
                self.cursor.execute(sel_sql)
                _result = self.cursor.fetchone()
                total[bid].append(total[bid][0] * _result[3])
                total[bid].append(_result[1])

            new_frame = tk.Toplevel()
            new_frame.title('报表')
            tree = ttk.Treeview(new_frame, show='headings')
            tree['columns'] = ('书籍id', '书籍名称', '销售总量', '销售总额')
            for c in tree['columns']:
                tree.column(c, width=150, anchor='center')
                tree.heading(c, text=c)
            i = 0
            for _, v in total.items():
                tree.insert('', i, values=(_, v[2], v[0], round(v[1] / 1000, 3)))
                i += 1
            for col in tree['columns']:
                tree.heading(col, text=col, command=lambda _col=col: self.treeview_sort_column(tree, _col, False))
            tree.pack()
            new_frame.update()
            self.__set_win_center(new_frame)
        except AttributeError as e:
            ok = tkinter.messagebox.showerror(title='统计失败', message='未连接到数据库')

    @write_log
    def __get_supplier(self):
        sel_sql = 'select * from supplier'
        try:
            self.cursor.execute(sel_sql)
            _result = self.cursor.fetchall()
            new_frame = tk.Toplevel()
            new_frame.title('供应商')
            tree = ttk.Treeview(new_frame, show='headings')
            tree['columns'] = ('供应商id', '书籍名称', '供应价格')
            for c in tree['columns']:
                tree.column(c, width=150, anchor='center')
                tree.heading(c, text=c)
            i = 0
            cache = dict()
            for _id, _bid, price in _result:
                if _bid not in cache:
                    sel_sql = 'select * from book where book_id={};'.format(_bid)
                    self.cursor.execute(sel_sql)
                    _result = self.cursor.fetchone()
                    cache.update({_bid: _result[1]})
                name = cache[_bid]
                tree.insert('', i, values=(_id, name, round(price / 1000, 3)))
                i += 1
            tree.pack()
            new_frame.update()
            self.__set_win_center(new_frame)
        except AttributeError as e:
            ok = tkinter.messagebox.showerror(title='查询失败', message='未连接到数据库')

    def __init_window(self):
        self.window.title('Shop')
        self.tabControl = ttk.Notebook(self.window)

    def __create_widgets(self):

        self.tab1 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab1, text='功能')
        self.tab2 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab2, text='登录')
        self.tab3 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab3, text='日志')
        self.tabControl.pack(expand=1, fill='both')

        self.io_mighty = ttk.LabelFrame(self.tab1, text='')
        self.io_mighty.grid(column=0, row=0, padx=8, pady=4)

        self.io_input_label = ttk.Label(self.io_mighty, text='输入书籍id')
        self.io_input_label.grid(column=0, row=1, sticky='W')

        self.io_book_id = tk.StringVar()
        self.io_id_entry = ttk.Entry(self.io_mighty, width=12, textvariable=self.io_book_id)
        self.io_id_entry.grid(column=0, row=2, sticky='W')

        self.io_input_name_label = ttk.Label(self.io_mighty, text='输入书籍名称')
        self.io_input_name_label.grid(column=0, row=3, sticky='W')

        self.io_book_name = tk.StringVar()
        self.io_name_entry = ttk.Entry(self.io_mighty, width=12, textvariable=self.io_book_name)
        self.io_name_entry.grid(column=0, row=4, sticky='W')

        self.io_check = ttk.Button(self.io_mighty, text='查询', command=self.__get_info)
        self.io_check.grid(column=3, row=1)
        self.io_ret = ttk.Button(self.io_mighty, text='退货', command=self.__ret)
        self.io_ret.grid(column=3, row=2)
        self.io_out = ttk.Button(self.io_mighty, text='出售', command=self.__sale)
        self.io_out.grid(column=3, row=3)
        self.io_in = ttk.Button(self.io_mighty, text='进货', command=self.__buy_one)
        self.io_in.grid(column=3, row=4)

        self.func_mighty = ttk.LabelFrame(self.tab1, text='')
        self.func_mighty.grid(column=0, row=4, padx=8, pady=4)
        self.io_store = ttk.Button(self.func_mighty, text='库存', command=self.__check_all)
        self.io_store.grid(column=0, row=5)
        self.io_cal = ttk.Button(self.func_mighty, text='统计', command=self.__statistic)
        self.io_cal.grid(column=1, row=5)
        self.io_other = ttk.Button(self.func_mighty, text='查询最近交易', command=lambda :self.__latest_k_trade(30))
        self.io_other.grid(column=2, row=5)
        self.io_in = ttk.Button(self.func_mighty, text='一键进货', command=self.__buy)
        self.io_in.grid(column=3, row=5)
        self.io_sup = ttk.Button(self.func_mighty, text='供应商列表', command=self.__get_supplier)
        self.io_sup.grid(column=0, row=6)

        self.other_mighty = ttk.LabelFrame(self.tab2, text='')
        self.other_mighty.grid(column=0, row=0, padx=8, pady=4)

        self.login_server = ttk.Label(self.other_mighty, text='服务器')
        self.login_server.grid(column=0, row=1, sticky='W')
        self.login_server_name = tk.StringVar()
        self.login_server_entry = ttk.Entry(self.other_mighty, width=12, textvariable=self.login_server_name)
        self.login_server_entry.grid(column=1, row=1, sticky='W')

        space = ttk.Label(self.other_mighty, text='')
        space.grid(column=0, row=2, sticky='W')

        self.login_user = ttk.Label(self.other_mighty, text='用户')
        self.login_user.grid(column=0, row=3, sticky='W')
        self.login_user_name = tk.StringVar()
        self.login_user_entry = ttk.Entry(self.other_mighty, width=12, textvariable=self.login_user_name)
        self.login_user_entry.grid(column=1, row=3, sticky='W')

        self.login_pwd = ttk.Label(self.other_mighty, text='密码')
        self.login_pwd.grid(column=0, row=4, sticky='W')
        self.login_pwd_name = tk.StringVar()
        self.login_pwd_entry = ttk.Entry(self.other_mighty, width=12, textvariable=self.login_pwd_name, show='*')
        self.login_pwd_entry.grid(column=1, row=4, sticky='W')

        self.login_db = ttk.Label(self.other_mighty, text='数据库')
        self.login_db.grid(column=0, row=5, sticky='W')
        self.login_db_name = tk.StringVar()
        self.login_db_entry = ttk.Entry(self.other_mighty, width=12, textvariable=self.login_db_name)
        self.login_db_entry.grid(column=1, row=5, sticky='W')

        self.login = ttk.Button(self.other_mighty, text='登录', command=self.__connect_sql)
        self.login.grid(column=2, row=4)

        self.save_status = tk.IntVar()
        self.save_check = tk.Checkbutton(self.other_mighty, text='记住密码', variable=self.save_status)
        self.save_check.select()
        self.save_check.grid(column=2, row=5, sticky=tk.W)

        self.log_mighty = ttk.LabelFrame(self.tab3, text='')
        self.log_mighty.grid(column=0, row=0, padx=8, pady=4)
        self.detail = scrolledtext.ScrolledText(self.log_mighty, width=45, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.detail.grid(column=0, row=1, sticky='W')

        self.menu_bar = Menu(self.window)
        self.window.config(menu=self.menu_bar)

        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Restore", command=self.__restore_sql)
        self.file_menu.add_command(label="Backup", command=self.__backup)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)


if __name__ == '__main__':
    app = Application()
