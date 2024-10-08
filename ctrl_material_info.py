import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
import resources_rc
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QInputDialog
from PyQt5 import QtWidgets
from material_info import Ui_material_info
from ctrl_update_material import update_material_window
from ctrl_total_data import total_data_window
import var
import sqlite3
from openpyxl import Workbook
import time


class material_info_window(QMainWindow, Ui_material_info):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.main_window = self
        self.setWindowIcon(QIcon(":/images/image.ico"))
        self.query_btn.setStyleSheet("background:#FF95CA")
        self.selected_row = -1
        self.selected_row_ll = []
        self.del_material_btn.clicked.disconnect()
        self.query_btn.clicked.disconnect()
        self.update_btn.clicked.disconnect()
        conn = sqlite3.connect("material_management.db")
        conn.text_factory = str
        cur = conn.cursor()
        cur.execute("select * from material")
        res = cur.fetchall()
        cur.close()
        conn.close()
        self.fill_table(res)

        # self.query_btn.clicked.disconnect()
        # self.total_data_btn.clicked.disconnect()  # 删除汇总统计

        self.del_material_btn.clicked.connect(self.on_del_material_btn_clicked)
        # self.del_both_btn.clicked.connect(self.on_del_both_btn_clicked)
        self.update_btn.clicked.connect(self.on_update_btn_clicked)
        self.cancel.clicked.connect(self.on_cancel_btn_clicked)
        self.query_btn.clicked.connect(self.on_query_btn_clicked)
        self.clear_query_info.clicked.connect(self.on_clear_query_btn_clicked)
        self.tableView.clicked.connect(self.on_tableview_select_item)
        self.export_excel.clicked.connect(self.on_export_btn_clicked)
        # self.total_data_btn.clicked.connect(self.on_total_data_btn_clicked)  # 删除汇总统计

        # self.query_btn_lock=False
        # self.query_btn.installEventFilter(self)

    # def eventFilter(self, object, event):
    #     if event.type() == QtCore.QEvent.HoverMove:
    #         self.query_btn_lock = False
    #         return True
    #     return False
    def on_total_data_btn_clicked(self):
        conn = sqlite3.connect("material_management.db")
        conn.text_factory = str
        cur = conn.cursor()
        sql="select count(*) from material"
        cur.execute(sql)
        res=cur.fetchone()
        if res[0]==0:
            QMessageBox.question(self, '汇总统计失败！', '装备表为空！', QMessageBox.Yes)
            return

        window = total_data_window()
        window.show()


    def on_export_btn_clicked(self):
        if self.export_data == []:
            QMessageBox.question(self, '导出失败！', '请确认表中存在装备数据！', QMessageBox.Yes)
            return
        book = Workbook()
        book.iso_dates = True
        sheet = book.active
        sheet.append(('装备编码', '装备名称', '规格型号', '计量单位', '配发单位', '部署位置', '期初数量', '结存数量'))
        for row in self.export_data:
            sheet.append(row)

        tmp_dialog = QtWidgets.QFileDialog(None, "选取装备数据保存路径", "C:/")
        tmp_dialog.setLabelText(QtWidgets.QFileDialog.Accept, '确认')
        tmp_dialog.setLabelText(QtWidgets.QFileDialog.Reject, '取消')
        tmp_dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        if tmp_dialog.exec_():
            ll = tmp_dialog.selectedFiles()
            dir_path = ll[0]
        else:
            return
        time_str = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
        file_name = time_str + "装备数据.xlsx"
        content, conform = QInputDialog.getText(self.main_window, '文件名', '请输入文件名：', text=file_name)
        if conform:
            file_name = content
        else:
            return
        try:
            book.save(dir_path + "/" + file_name)
            QMessageBox.question(self, '导出成功！', '装备数据已导出至Excel！', QMessageBox.Yes)
        except:
            QMessageBox.question(self, '导出失败！', '文件名有误！', QMessageBox.Yes)

    def fill_table(self, datas):  # datas为列表
        self.export_data = datas
        self.model = QStandardItemModel(len(datas), 8)
        self.model.setHorizontalHeaderLabels(['装备编码', '装备名称', '规格型号', '计量单位', '配发单位', '部署位置', '期初数量', '结存数量'])
        if datas != []:
            for i in range(0, len(datas)):
                item = QStandardItem(datas[i][0])
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.model.setItem(i, 0, item)

                item = QStandardItem(datas[i][1])
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.model.setItem(i, 1, item)

                item = QStandardItem(datas[i][2])
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.model.setItem(i, 2, item)

                item = QStandardItem(datas[i][3])
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.model.setItem(i, 3, item)

                item = QStandardItem("{}".format(datas[i][4]))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.model.setItem(i, 4, item)

                item = QStandardItem(str(datas[i][5]))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.model.setItem(i, 5, item)

                item = QStandardItem(format(datas[i][6], '.0f'))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.model.setItem(i, 6, item)

                item = QStandardItem(format(datas[i][7], '.0f'))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.model.setItem(i, 7, item)

        self.tableView.setModel(self.model)
        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()
        self.tableView.horizontalHeader().setStretchLastSection(True)

    def my_query(self):
        conn = sqlite3.connect("material_management.db")
        conn.text_factory = str
        cur = conn.cursor()
        flag1 = self.st_num.text() == ""
        flag2 = self.ed_num.text() == ""


        # if self.st_num.text()=="" or self.ed_num=="" or self.st_per_price=="" or self.ed_per_price=="":
        #     QMessageBox.question(self, '查询失败！', "结存数量和单价范围不可为空！\n这两项不做筛选请点击\"清楚筛选\"恢复默认值！", QMessageBox.Yes)
        #     return

        sql = "select * from material where 1=1"
        # 数量筛选
        if flag1 and not flag2:
            try:
                ed_num = float(self.ed_num.text())
            except:
                return (-2, [])
            sql += " and now_num<=" + str(ed_num)
        if not flag1 and flag2:
            try:
                st_num = float(self.st_num.text())
            except:
                return (-2, [])
            sql += " and now_num>=" + str(st_num)

        if not flag1 and not flag2:
            try:
                st_num = float(self.st_num.text())
                ed_num = float(self.ed_num.text())
                if st_num > ed_num:
                    return (-1, [])
                sql += " and now_num>=" + str(st_num) + " and now_num<=" + str(ed_num)
            except:
                return (-2, [])

        # 单位筛选
        if self.st_per_price.text() != "":
            st_per_price = self.st_per_price.text()
            sql = "select * from material where per_price like '%" + st_per_price + "%'"


        if self.id.text() != "":
            id_ll = self.id.text()
            id_ll = id_ll.strip('%\n\t ')
            id_ll = id_ll.split('%')
            sql += " and ("
            for i in range(len(id_ll)):
                sql += "material_id='" + id_ll[i] + "'"
                if i < len(id_ll) - 1:
                    sql += " or "
            sql += ")"

        if self.name.text() != "":
            name_ll = self.name.text()
            name_ll = name_ll.strip('%\n\t ')
            name_ll = name_ll.split('%')
            name_ll1 = []
            name_ll2 = []
            for tname in name_ll:
                name_ll1.append("%" + tname + "%")
                name_ll2.append("%%" + tname + "%%")
            sql += " and ("
            for i in range(len(name_ll)):
                sql += "material_name like '" + name_ll1[i] + "' or material_name like '" + name_ll2[i] + "'"
                if i < len(name_ll) - 1:
                    sql += " or "
            sql += ")"

        if self.spec_lineEdit.text() != "":
            spec_ll = self.spec_lineEdit.text()
            spec_ll = spec_ll.strip('%\n\t ')
            spec_ll = spec_ll.split('%')
            spec_ll1 = []
            spec_ll2 = []
            for tspec in spec_ll:
                spec_ll1.append("%" + tspec + "%")
                spec_ll2.append("%%" + tspec + "%%")
            sql += " and ("
            for i in range(len(spec_ll)):
                sql += "spec like '" + spec_ll1[i] + "' or spec like '" + spec_ll2[i] + "'"
                if i < len(spec_ll) - 1:
                    sql += " or "
            sql += ")"

        if self.position_lineEdit.text() != "":
            pos_ll = self.position_lineEdit.text()
            pos_ll = pos_ll.strip('%\n\t ')
            pos_ll = pos_ll.split('%')
            pos_ll1 = []
            pos_ll2 = []
            for tpos in pos_ll:
                pos_ll1.append("%" + tpos + "%")
                pos_ll2.append("%%" + tpos + "%%")
            sql += " and ("
            for i in range(len(pos_ll)):
                sql += "pos like '" + pos_ll1[i] + "' or pos like '" + pos_ll2[i] + "'"
                if i < len(pos_ll) - 1:
                    sql += " or "
            sql += ")"

        cur.execute(sql)
        res = cur.fetchall()
        cur.close()
        conn.close()
        if res == []:
            return (1, [])
        return (2, res)

    def on_query_btn_clicked(self):
        # if self.query_btn_lock:
        #     return
        # self.query_btn_lock=True
        (flag, res) = self.my_query()
        if flag == -1:
            QMessageBox.question(self, '查询失败！', "结存数量范围冲突！", QMessageBox.Yes)
            self.fill_table([])
        elif flag == 1:
            QMessageBox.question(self, '查询失败！', '未查询到相关装备！', QMessageBox.Yes)
            self.fill_table([])
        elif flag == -2:
            QMessageBox.question(self, '查询失败！', '结存数量应输入实数！', QMessageBox.Yes)
            self.fill_table([])
        else:
            self.fill_table(res)
            QMessageBox.question(self, '查询成功！', '查询结果位于表格中', QMessageBox.Yes)

    def on_tableview_select_item(self, event):
        self.selected_row = self.tableView.currentIndex().row()
        # self.tableView.selectRow(self.selected_row)

    def on_clear_query_btn_clicked(self):
        self.id.setText("")
        self.name.setText("")
        self.spec_lineEdit.setText("")
        self.position_lineEdit.setText("")
        self.st_num.setText("")
        self.ed_num.setText("")
        self.st_per_price.setText("")
        # self.ed_per_price.setText("")
        (flag, res) = self.my_query()
        self.fill_table(res)

    def on_del_material_btn_clicked(self):
        indexs = self.tableView.selectionModel().selectedIndexes()
        tt = set()
        for t in indexs:
            tt.add(t.row())
        indexs = []
        for t in tt:
            indexs.append(t)
        if indexs == []:
            QMessageBox.question(self, '删除失败！', '请正确选择装备！', QMessageBox.Yes)
            return
        id_ll = []
        for index in indexs:
            row_num = index
            tid = self.model.item(row_num, 0).text()
            id_ll.append(tid)

        conn = sqlite3.connect("material_management.db")
        conn.text_factory = str
        cur = conn.cursor()
        for tid in id_ll:
            sql = "delete from material where material_id='" + tid + "'"
            cur.execute(sql)
            sql = "delete from in_log where material_id='" + tid + "'"
            cur.execute(sql)
            sql = "delete from out_log where material_id='" + tid + "'"
            cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        QMessageBox.question(self, '删除成功！', str(len(indexs)) + '条装备已删除！', QMessageBox.Yes)
        (flag, res) = self.my_query()
        self.fill_table(res)

    def refresh_after_update(self):
        (flag, res) = self.my_query()
        self.fill_table(res)

    def on_update_btn_clicked(self):
        indexs = self.tableView.selectionModel().selectedIndexes()
        tt = set()
        for t in indexs:
            tt.add(t.row())
        indexs = []
        for t in tt:
            indexs.append(t)
        if indexs == []:
            QMessageBox.question(self, '修改失败！', '请正确选择装备！', QMessageBox.Yes)
            return
        if len(indexs) > 1:
            QMessageBox.question(self, '修改失败！', '只能选中一行记录进行修改！', QMessageBox.Yes)
            return
        row_num = indexs[0]
        tid = self.model.item(row_num, 0).text()
        var.tid = tid
        window = update_material_window()
        window.my_Signal.connect(self.refresh_after_update)
        window.show()

    def on_cancel_btn_clicked(self):
        self.close()

    def keyPressEvent(self, event):
        if str(event.key()) == '16777220' or str(event.key()) == '16777221':
            self.on_query_btn_clicked()
