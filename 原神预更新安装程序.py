from __future__ import print_function
import os
import ctypes, sys
from progress.bar import IncrementalBar
from tkinter.filedialog import askopenfilename, askdirectory
from methods import *
#from methods import find_gig_path, hdiff_files, delete_files, delet_IWRITE, delete_dirs, backup_file, read_json, find_zipfile
from time import sleep


""" 
old_v = process_json["old_v"]
new_v = process_json["new_v"]
gig_path = process_json["gig_path"]
zip_files_staut = process_json["zip_files_staut"]
hdiff_files_staut = process_json["hdiff_files_staut"]
delete_files_staut = process_json["delete_files_staut"] 
"""
def main():
    print("="*100 + "\n！！！请仔细阅读程序的提示，并正确操作！！！\n！！！请仔细阅读程序的提示，并正确操作！！！\n！！！请仔细阅读程序的提示，并正确操作！！！\n")
    print("\n！！！关闭原神启动器和游戏以及修改只读文件需要管理员权限！！！\n")
    print("="*100 + "\n")
    # 找到原神游戏安装目录
    gig_path = find_gig_path()
    # gig_path = r"E:\Genshin Impact\Genshin Impact Game"
    print("当前原神游戏安装目录：%s\n" % gig_path)
    select = input("如果你想修改当前原神游戏安装目录请输入1，否则回车继续：")
    print()
    if select == "1":
        gig_path_ = askopenfilename(title='选择原神游戏 GenshinImpact.exe/YuanShen.exe 所在路径', filetypes=[('EXE', 'YuanShen.exe'),('EXE', 'GenshinImpact.exe')])
        gig_path = (gig_path_[:gig_path_.rfind("/")]).replace("/","\\")
    

    
    # 
    while True:
        # 查找更新包位置和版本信息
        return_dict = find_zipfile(gig_path)
        if return_dict:
            zip_game = return_dict["zip_game"]
            zip_zh_cn = return_dict["zip_zh_cn"]
            current_v = return_dict["current_v"]
            update_v = return_dict["update_v"]
        else:
            process_json = read_json()
            if process_json:
                if "AllDone" not in process_json:
                    print("\n！！！未找到game和zh-cn增量更新包，且上次任务未完成！！！\n")
                    print("\n！！！建议将game和zh-cn增量更新包放在游戏安装目录再试，或尝试恢复备份！！！\n")
                    select = input("尝试恢复备份请输入1，回车退出：")
                    if select == "1":
                        restore_backup()
                else:
                    zip_game = False
                    zip_zh_cn = False
                    current_v = process_json["old_v"]
                    update_v = process_json["new_v"]
            else:
                input("\n！！！未找到game和zh-cn增量更新包，且未找到任务进度文件，建议将game和zh-cn增量更新包放在游戏安装目录再试！！！\n")
                exit()

        # 尝试读取任务进度并设计主菜单
        process_json = read_json()
        fun_str = "\n%s\n"%("="*100)
        if process_json:
            if process_json["old_v"] == current_v and process_json["gig_path"] == gig_path and "AllDone" not in process_json:
                fun_str += "1.继续上次未完成的任务\n2.md5检查\n3.退出\n"
                fun_list = ["continue_update","md5_check","exit"]
            elif "AllDone" in process_json and os.path.isdir(r"%s_patch\patched\GenshinImpact_Data" % update_v):
                fun_str += "1.管理备份\n2.md5检查\n3.修改/还原metadata\n4.退出\n"
                fun_list = ["backup_manage","md5_check","metadata_patch","exit"]
            elif "AllDone" in process_json and "backup_path" in process_json:
                fun_str += "1.管理备份\n2.md5检查\n3.退出\n"
                fun_list = ["backup_manage","md5_check","exit"]
            else:
                fun_str += "1.开始新的更新\n2.退出\n"
                fun_list = ["new_update","exit"]
        else:
            fun_str += "1.开始新的更新\n2.退出\n"
            fun_list = ["new_update","exit"]
        
        print(fun_str)
        select_fun = input("请输入功能编号：")
        fun_selected = ""
        for i in range(len(fun_list)):
            if str(i+1) == select_fun:
                fun_selected = fun_list[i]
        if fun_selected == "":
            print("\n！！！输入有误，请重新输入！！！\n")
            continue
        if fun_selected == "new_update":
            print("\n%s\n"%("="*100))
            select = input("继续更新前，请确定是从%s更新到%s，否则会出错！\n回车继续，输入1返回主菜单："%(current_v, update_v))
            print()
            if select == "1":
                continue
            close_exe()
            check_hpatchz()
            print("总共4个步骤，请耐心等待！\n")

            # 初始化process.json文件
            get_change_files(gig_path, zip_game, zip_zh_cn, current_v, update_v)
            
            backup_files(gig_path, fun_selected)
            unzip(gig_path, zip_game, zip_zh_cn, fun_selected)
            hdiff_files(gig_path, fun_selected)
            delete_files(gig_path, fun_selected)
            if os.path.isdir(r"%s_patch\patched\GenshinImpact_Data" % update_v):
                select = input("连接私服可能需要修补metadata\n修补请输入1，回车跳过：")
                print()
                if select == "1":
                    patch_metadata(gig_path)
            complete_task()
            break
        elif fun_selected == "continue_update":
            print("\n%s\n"%("="*100))
            select = input("继续更新前，请确定是从%s更新到%s，否则会出错！\n回车继续，输入1返回主菜单："%(current_v, update_v))
            print()
            if select == "1":
                continue
            close_exe()
            check_hpatchz()
            print("总共4个步骤，请耐心等待！\n")
            backup_files(gig_path, fun_selected)
            unzip(gig_path, zip_game, zip_zh_cn, fun_selected)
            hdiff_files(gig_path, fun_selected)
            delete_files(gig_path, fun_selected)
            if os.path.isdir(r"%s_patch\patched\GenshinImpact_Data" % update_v) and "patch_metadata" not in process_json:
                select = input("连接私服可能需要修补metadata\n修补请输入1，回车跳过：")
                print()
                if select == "1":
                    patch_metadata(gig_path)
            complete_task()
            break
        elif fun_selected == "backup_manage":
            while True:
                process_json = read_json()
                if "delete_backup" in process_json:
                    input("\n！！！备份已删除，无可用操作！！！\n")
                    break
                elif "restore_backup" in process_json:
                    print("\n%s\nX.备份已还原\n2.删除备份\n3.返回上一级\n"%("="*100))
                    select = input("请输入操作序号：")
                    if select == "1":
                        select == False
                else:
                    print("\n%s\n1.还原备份\n2.删除备份\n3.返回上一级\n"%("="*100))
                    select = input("请输入操作序号：")
                if select == "1":
                    restore_backup()
                    break
                elif select == "2":
                    delete_backup()
                    break
                elif select == "3":
                    break
                else:
                    print("\n！！！输入有误，请重新输入！！！\n")
        elif fun_selected == "metadata_patch":
            while True:
                process_json = read_json()
                if os.path.isdir(r"%s_patch\patched\GenshinImpact_Data" % update_v) and "patch_metadata" not in process_json:
                    print("\n%s\n1.修补metadata\nX.未修补\n3.返回上一级\n"%("="*100))
                    select = input("请输入操作序号：")
                    if select == "2":
                        select == False
                    patch_metadata(gig_path)
                elif os.path.isdir(r"%s_patch\patched\GenshinImpact_Data" % update_v) and "patch_metadata" in process_json:
                    print("\n%s\nX.已修补\nX.还原metadata\n3.返回上一级\n"%("="*100))
                    select = input("请输入操作序号：")
                    if select == "1":
                        select == False
                if select == "1":
                    patch_metadata()
                    break
                elif select == "2":
                    restore_metadata()
                    break
                elif select == "3":
                    break
                else:
                    print("\n！！！输入有误，请重新输入！！！\n")
        elif fun_selected == "md5_check":
            print("\n%s\n"%("="*100))
            md5_check()
            sleep(1)
            print("\n%s\n"%("="*100))
        elif fun_selected == "exit":
            exit()


#main()
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
if is_admin():
    main()
else:
    if sys.version_info[0] == 3:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    else:#in python2.x
        ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(__file__), None, 1)