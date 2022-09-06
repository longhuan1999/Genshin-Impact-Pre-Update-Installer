import stat
import winreg
import os
import json
import zipfile
from tkinter.filedialog import askopenfilename, askdirectory
from progress.bar import IncrementalBar
from py import process


# 删除文件只读属性
def delet_IWRITE(file_path):
    if os.path.isfile(file_path):
        os.chmod(file_path, stat.S_IWRITE)


# 删除文件夹下所有文件和子目录
def delete_dirs(path):
    """删除文件夹下所有的文件和子目录"""
    while True:
        try:
            os.rmdir(path)
            break
        except:
            for root, dirs, files in os.walk(path):
                for name in files:
                    file_path = os.path.join(root, name)
                    if os.path.isfile(file_path):
                        try:
                            delet_IWRITE(file_path)
                            os.remove(file_path)
                        except:
                            pass

                for name in dirs:
                    dir_path = os.path.join(root, name)
                    if os.path.isdir(dir_path):
                        try:
                            os.rmdir(dir_path)
                        except:
                            pass
    

# 保存数据或任务进度到process.json
def process_json_save(process_json):
    with open("process.json","w",encoding="utf-8") as f:
        json.dump(process_json, f, indent=4, ensure_ascii=False)


# 找到处理的文件所在二级列表在一级列表中的索引
def index_filename(filename, keyname):
    # 读取任务进度
    process_json = read_json()
    if process_json is False:
        input("process.json 文件读取出错，程序退出...")
        exit(0)
    n = 0
    for i in process_json[keyname]:
        if filename in i:
            return n
        n += 1


# 通过注册表找到原神启动器所在目录
def find_gi_path():
    """
    读取windows安装的所有应用
    @return:
    """
    gi_path = ""
    # 需要遍历的两个注册表
    sub_key = [r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
               r'SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall']
    for i in sub_key:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, i)
        for j in range(winreg.QueryInfoKey(key)[0]):
            try:
                each_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f'{i}\\{winreg.EnumKey(key, j)}')
                DisplayName = winreg.QueryValueEx(each_key, 'DisplayName')[0]
                InstallPath = winreg.QueryValueEx(each_key, 'InstallPath')[0]
                if DisplayName == "原神":
                    gi_path = InstallPath
                    break
            except WindowsError:
                pass
    return gi_path


# 找到原神游戏安装目录
def find_gig_path():
    # 找到原神启动器所在目录
    gi_path = find_gi_path()
    #print(gi_path)
    # gi_path = "" # 测试手动选择原神启动器所在目录

    # 如果注册表找不到，手动选择原神启动器所在目录
    if gi_path == None or gi_path == "":
        print("未找到原神安装目录，请手动选择！\n")
        gi_path = (askopenfilename(title='选择原神启动器 launcher.exe 所在路径', filetypes=[('EXE', 'launcher.exe')]))[:-13]
        gi_path = gi_path.replace("/", "\\")
    #print(gi_path)

    config_path = os.path.join(gi_path, "config.ini")
    gig_path = ""
    # 如果配置文件config.ini存在，尝试获取 game_install_path
    if os.path.isfile(config_path):
        with open(config_path, 'r', encoding = "utf-8") as f: 
            for i in f.readlines():
                # 尝试获取 game_install_path
                if "game_install_path" in i:
                    gig_path = (i[18:].strip("= \n")).replace("/","\\")
    # 如果配置文件config.ini存在且 game_install_path 存在，判断路径是否正确
    if gig_path != "":
        GenshinImpact = os.path.join(gig_path, "GenshinImpact.exe")
        YuanShen = os.path.join(gig_path, "YuanShen.exe")
        # 判断路径是否正确
        if os.path.isfile(GenshinImpact) is False and os.path.isfile(YuanShen) is False:
            gig_path = ""
    # 如果配置文件config.ini不存在或者 game_install_path 不存在，又或者路径不正确，判断默认路径是否正确
    if gig_path == "":
        gig_path = os.path.join(gi_path, "Genshin Impact Game")
        GenshinImpact = os.path.join(gig_path, "GenshinImpact.exe")
        YuanShen = os.path.join(gig_path, "YuanShen.exe")
        # 判断默认路径是否正确
        if os.path.isfile(GenshinImpact) is False and os.path.isfile(YuanShen) is False:
            print("未找到游戏安装目录，请手动选择！\n")
            gig_path_ = askopenfilename(title='选择原神游戏 GenshinImpact.exe/YuanShen.exe 所在路径', filetypes=[('EXE', 'YuanShen.exe'),('EXE', 'GenshinImpact.exe')])
            gig_path = (gig_path_[:gig_path_.rfind("/")]).replace("/","\\")
    #print(gig_path)
    return gig_path


# 找到game和zh-cn增量更新包，并获取版本信息
def find_zipfile(gig_path):
    listdir = os.listdir(gig_path)
    zip_game = ""
    zip_zh_cn = ""
    # 查找游戏增量更新包和游戏中文语音增量更新包
    for i in listdir:
        if "game_" in i and ".zip" in i:
            zip_game = os.path.join(gig_path, i)
        if "zh-cn_" in i and ".zip" in i:
            zip_zh_cn = os.path.join(gig_path, i)
    # 更新包不存在是的处理
    if zip_game == "":
        print("\n！！！当前游戏增量更新包：未找到！！！\n")
        return False
        # input("游戏增量更新包不存在，安装无法进行！")
        # exit()
    else:
        current_v = (zip_game[zip_game.rindex("\\"):].split("_"))[1]
        update_v = (zip_game[zip_game.rindex("\\"):].split("_"))[2]
        print("当前游戏增量更新包：%s\n" % zip_game)
    if zip_zh_cn == "":
        print("\n！！！当前游戏中文语音增量更新包：未找到！！！\n")
        #zip_zh_cn = False
        select = input("游戏中文语音增量更新包不存在，是否继续？\n继续输入1，否则退出：\n")
        if select != "1":
            exit()
        else:
            zip_zh_cn = False
    else:
        print("当前游戏中文语音增量更新包：%s\n" % zip_zh_cn)
    return {"zip_game":zip_game, "zip_zh_cn":zip_zh_cn, "current_v":current_v, "update_v":update_v}


# 读取 process.json 文件
def read_json():
    if os.path.isfile("process.json"):
        with open("process.json","r",encoding="utf-8") as f:
            injson = json.load(f)
            if "old_v" in injson and "new_v" in injson and "gig_path" in injson and "zip_files_staut" in injson and "hdiff_files_staut" in injson and "delete_files_staut" in injson:
                return injson
            else:
                return False
    else:
        return False


# 关闭原神启动器和原神游戏，否则修改文件会报错
def close_exe():
    print("检查原神启动器和游戏是否运行...\n")
    cmd1 = 'tasklist /v /fi "imagename eq launcher.exe"'
    cmd2 = 'tasklist /v /fi "imagename eq GenshinImpact.exe"'
    with os.popen(cmd1, "r") as p:
            r1 = (p.read()).split("\n")
            # print(r1)
    with os.popen(cmd2, "r") as p:
            r2 = (p.read()).split("\n")
    for i in r1:
        if "Genshin Impact" in i:
            #print(repr(i))
            i_list = i.split(" ")
            for h in i_list:
                if h.isdigit() and len(h) >= 3:
                    print("关闭原神启动器...\n")
                    os.popen("taskkill /f /pid %s"%h, "r")
                    break
    for i in r2:
        if "GenshinImpact.exe" in i:
            i_list = i.split(" ")
            for h in i_list:
                if h.isdigit() and len(h) >= 3:
                    print("关闭原神游戏...\n")
                    os.popen("taskkill /f /pid %s"%h, "r")
                    break
    print()


# 检查增量更新工具是否存在
def check_hpatchz():
    # 检查 hpatchz.exe 工具是否存在
    cmd = "hpatchz.exe 2>null"
    # cmd = "sdfsef"
    with os.popen(cmd, "r") as p:
        r = p.read()
    if "HDiffPatch::hpatchz" not in r:
        print("hpatchz.exe工具不存在，安装无法进行！\n")
        print("hpatchz.exe工具用于增量更新，请下载到当前目录：https://github.com/sisong/HDiffPatch/releases\n")
        input("")
        exit()


# 初始化 process.json 文件
def get_change_files(gig_path, zip_game, zip_zh_cn, current_v, update_v):
    hdifffiles = []
    deletefiles = []
    replacefiles = []
    addfiles = []
    with zipfile.ZipFile(zip_game, mode="r") as zf:
        zf_namelist = zf.namelist()
        for filename in zf_namelist:
            if filename == "hdifffiles.txt":
                text = (zf.read(filename).decode(encoding="utf-8")).splitlines()
                for i in text:
                    hdifffiles.append((i[16:-2]).replace("/","\\"))
            elif filename == "deletefiles.txt":
                text = (zf.read(filename).decode(encoding="utf-8")).splitlines()
                for i in text:
                    deletefiles.append(i.replace("/","\\"))
            else:
                if "/" in filename:
                    filename = filename.replace("/", "\\")
                origin_file = os.path.join(gig_path, filename)
                if os.path.isfile(origin_file):
                    delet_IWRITE(os.path.join(gig_path, filename))
                    replacefiles.append(filename)
                else:
                    addfiles.append(filename)
    if zip_zh_cn:
        with zipfile.ZipFile(zip_zh_cn, mode="r") as zf:
            zf_namelist = zf.namelist()
            for filename in zf_namelist:
                if filename == "hdifffiles.txt":
                    text = (zf.read(filename).decode(encoding="utf-8")).splitlines()
                    for i in text:
                        hdifffiles.append((i[16:-2]).replace("/","\\"))
                elif filename == "deletefiles.txt":
                    text = (zf.read(filename).decode(encoding="utf-8")).splitlines()
                    for i in text:
                        deletefiles.append(i.replace("/","\\"))
                else:
                    if "/" in filename:
                        filename = filename.replace("/", "\\")
                    origin_file = os.path.join(gig_path, filename)
                    if os.path.isfile(origin_file):
                        delet_IWRITE(origin_file)
                        replacefiles.append(filename)
                    else:
                        addfiles.append(filename)

    zipfiles = replacefiles + addfiles
    zip_files_staut = []
    hdiff_files_staut = []
    delete_files_staut = []
    for i in zipfiles:
        zip_files_staut.append([i,"wait_for_unzip","wait_for_backup"])
    for i in hdifffiles:
        hdiff_files_staut.append([i, "wait_for_hdiff"])
    for i in deletefiles:
        delete_files_staut.append([i, "wait_for_delete", "wait_for_backup"])
    
    # 选择备份路径
    backup_path = askdirectory(title='更新前请选择备份文件夹"备份%s"保存路径'%current_v)
    backup_path = os.path.join(backup_path.replace("/","\\"),"备份%s"%current_v)
    process_json = {
        "old_v": current_v,
        "new_v": update_v,
        "gig_path": gig_path,
        "backup_path": backup_path,
        "zip_files_staut": zip_files_staut,
        "hdiff_files_staut": hdiff_files_staut,
        "delete_files_staut": delete_files_staut
    }
    process_json_save(process_json)


# 备份旧版本文件
def backup_files(gig_path, fun_selected):
    # 读取任务进度
    process_json = read_json()
    if process_json is False:
        input("process.json 文件或备份路径读取出错，程序退出...")
        exit(0)
    if "backup_path" not in process_json: 
        # 选择备份路径
        backup_path = askdirectory(title='未找到备份文件夹路径，请手动选择备份文件夹"备份%s"保存路径'%process_json["old_v"])
        backup_path = os.path.join(backup_path.replace("/","\\"),"备份%s"%process_json["old_v"])
        process_json["backup_path"] = backup_path
        process_json_save(process_json)
    backup_path = process_json["backup_path"]
    if os.path.isdir(backup_path) is False:
        os.mkdir(backup_path)
    

    already_backup_files = []
    if fun_selected == "continue_update":
        for i in process_json["zip_files_staut"]:
            if i[2] == "already_backed_up" or i[2] == "no_need_back_up":
                already_backup_files.append(i[0])
        for i in process_json["delete_files_staut"]:
            if i[2] == "already_backed_up" or i[2] == "no_need_back_up":
                already_backup_files.append(i[0])
     
    bar1 = IncrementalBar('备份文件中：\t\t', max = len(process_json["zip_files_staut"])+len(process_json["delete_files_staut"])-len(already_backup_files))
    
    # 备份解压缩覆盖的文件
    n = 0
    for i in process_json["zip_files_staut"]:
        filename = i[0]
        if filename in already_backup_files:
            n += 1
            continue
        ishdiff = False
        if filename[-6:] == ".hdiff":
            filename = filename[:-6]
            ishdiff = True
        origin_file_path = os.path.join(gig_path, filename)
        if os.path.isfile(origin_file_path):
            backup_file_path = os.path.join(backup_path, filename)
            if "\\" in filename:
                file_dir_path = os.path.join(backup_path, filename[:filename.rindex("\\")])
                if os.path.isdir(file_dir_path) is False:
                    os.makedirs(file_dir_path)
            result = os.system("copy /y \"%s\" \"%s\" >null"%(origin_file_path, backup_file_path))
            if ishdiff and result == 0:
                os.remove(origin_file_path)
            elif result != 0:
                input("\n！！！复制文件\n%s\n到\n%s\n时出错！！！\n程序退出"%(origin_file_path, backup_file_path))
                exit()
            process_json["zip_files_staut"][n][2] = "already_backed_up"
            process_json_save(process_json)
        else:
            process_json["zip_files_staut"][n][2] = "no_need_back_up"
            process_json_save(process_json)
        n += 1
        bar1.next()
        
    
    # 备份更新时会删除的文件
    n = 0
    for i in process_json["delete_files_staut"]:
        filename = i[0]
        if filename in already_backup_files:
            n += 1
            continue
        origin_file_path = os.path.join(gig_path, filename)
        backup_file_path = os.path.join(backup_path, filename)
        file_dir_path = os.path.join(backup_path, filename[:filename.rindex("\\")])
        if os.path.isdir(file_dir_path) is False:
            os.makedirs(file_dir_path)
        result = os.system("copy /y \"%s\" \"%s\" >null"%(origin_file_path, backup_file_path))
        if result == 0:
            process_json["delete_files_staut"][n][2] = "already_backed_up"
            process_json_save(process_json)
        else:
            input("\n！！！复制文件\n%s\n到\n%s\n时出错！！！\n程序退出"%(origin_file_path, backup_file_path))
            exit()
        n += 1
        bar1.next()
    
    bar1.finish()
    print()


# 解压game和zh-cn增量更新包
def unzip(gig_path, zip_game, zip_zh_cn, fun_selected):
    # 读取任务进度
    process_json = read_json()
    if process_json is False:
        input("process.json 文件读取出错，程序退出...")
        exit(0)

    already_unzip_files = []
    if fun_selected == "continue_update":
        for i in process_json["zip_files_staut"]:
            if i[1] == "already_unzip":
                already_unzip_files.append(i[0])
    
    bar1 = IncrementalBar('解压游戏增量更新包中：\t', max = len(process_json["zip_files_staut"])-len(already_unzip_files))
    # 解压游戏增量更新包，并处理增量更新文件和过期文件
    with zipfile.ZipFile(zip_game, mode="r") as zf:
        zf_namelist = zf.namelist()
        for filename in zf_namelist:
            if filename == "hdifffiles.txt" or filename == "deletefiles.txt":
                continue
            else:
                if "/" in filename:
                    filename = filename.replace("/", "\\")
                origin_file = os.path.join(gig_path, filename)
                if os.path.isfile(origin_file):
                    delet_IWRITE(origin_file)
                if filename not in already_unzip_files:
                    zf.extract(filename.replace("\\","/"), gig_path)
                    process_json["zip_files_staut"][index_filename(filename, "zip_files_staut")][1] = "already_unzip"
                    process_json_save(process_json)                     
                    # sleep(0.01)
                    bar1.next()
    if zip_zh_cn:
        with zipfile.ZipFile(zip_zh_cn, mode="r") as zf:
            zf_namelist = zf.namelist()
            for filename in zf_namelist:
                if filename == "hdifffiles.txt" or filename == "deletefiles.txt":
                    continue
                else:
                    if "/" in filename:
                        filename = filename.replace("/", "\\")
                    origin_file = os.path.join(gig_path, filename)
                    if os.path.isfile(origin_file):
                        delet_IWRITE(origin_file)
                    if filename not in already_unzip_files:
                        zf.extract(filename.replace("\\","/"), gig_path)
                        process_json["zip_files_staut"][index_filename(filename, "zip_files_staut")][1] = "already_unzip"
                        process_json_save(process_json)                     
                        # sleep(0.01)
                        bar1.next()
    bar1.finish()
    print()


# 增量更新文件
def hdiff_files(gig_path, fun_selected):
    # 读取任务进度
    process_json = read_json()
    if process_json is False:
        input("process.json 文件读取出错，程序退出...")
        exit(0)
    backup_path = process_json["backup_path"]
    
    already_hdiff_files = []
    if fun_selected == "continue_update":
        for i in process_json["hdiff_files_staut"]:
            if i[1] == "already_hdiff":
                already_hdiff_files.append(i[0])

    bar1 = IncrementalBar('增量更新文件处理中：\t', max = len(process_json["hdiff_files_staut"])-len(already_hdiff_files))
    select_skip = "0"
    for i in process_json["hdiff_files_staut"]:
        filename = i[0]
        if filename in already_hdiff_files:
            continue
        o_pck = os.path.join(backup_path, filename)
        pck_hdiff = os.path.join(gig_path, filename + ".hdiff")
        t_pck = os.path.join(gig_path, filename)
        cmd = 'hpatchz.exe "%s" "%s" "%s"'%(o_pck, pck_hdiff, t_pck)
        with os.popen(cmd, "r") as p:
            r = p.read()
        if "patch ok!" in r:
            os.remove(pck_hdiff)
            process_json["hdiff_files_staut"][index_filename(filename, "hdiff_files_staut")][1] = "already_hdiff"
            process_json_save(process_json)
            bar1.next()
        else:
            if select_skip == "2":
                print("!!!增量更新失败!!!：\n%s\n"%r)
            else:
                select_skip = input("!!!增量更新失败!!!：\n%s\n跳过本文件输入1，忽略错误输入2，回车退出："%r)
                if select_skip != "1" and select_skip != "2":
                    exit()
            
    bar1.finish()
    print()


# 删除过期文件
def delete_files(gig_path, fun_selected):
    # 读取任务进度
    process_json = read_json()
    if process_json is False:
        input("process.json 文件读取出错，程序退出...")
        exit(0)
    
    already_delete_files = []
    if fun_selected == "continue_update":
        for i in process_json["delete_files_staut"]:
            if i[1] == "already_deleted":
                already_delete_files.append(i[0])

    bar1 = IncrementalBar('删除过期文件中：\t\t', max = len(process_json["delete_files_staut"])-len(already_delete_files))
    for i in process_json["delete_files_staut"]:
        filename = i[0]
        if filename in already_delete_files:
            continue
        deletefile = os.path.join(gig_path, filename)
        if os.path.isfile(deletefile):
            delet_IWRITE(os.path.join(gig_path, deletefile))
            os.remove(deletefile)
            process_json["delete_files_staut"][index_filename(filename, "delete_files_staut")][1] = "already_deleted"
        bar1.next()
    bar1.finish()
    print()

# 修补metadata
def patch_metadata(gig_path):
    # 读取任务进度
    process_json = read_json()
    if process_json is False:
        input("process.json 文件读取出错，程序退出...")
        exit(0)
    update_v = process_json["new_v"]
    patched_path = r"%s_patch\patched\GenshinImpact_Data" % update_v
    target_path = os.path.join(gig_path, "GenshinImpact_Data")
    if os.path.isdir(r"%s_patch\patched\GenshinImpact_Data" % update_v):
        result = os.system("xcopy /s /e /y \"%s\" \"%s\" >null"%(patched_path, target_path))
        if result != 0:
            input("\n！！！复制文件夹\n%s\n到\n%s\n时出错！！！\n程序退出"%(patched_path, target_path))
            exit()
        process_json["patch_metadata"] = True
        process_json_save(process_json)
        print("\n！！！已修补metadata！！！\n")


# 恢复metadata
def restore_metadata(gig_path):
    # 读取任务进度
    process_json = read_json()
    if process_json is False:
        input("process.json 文件读取出错，程序退出...")
        exit(0)
    update_v = process_json["new_v"]
    origin_path = r"%s_patch\origin\GenshinImpact_Data" % update_v
    target_path = os.path.join(gig_path, "GenshinImpact_Data")
    if os.path.isdir(r"%s_patch\origin\GenshinImpact_Data" % update_v):
        result = os.system("xcopy /s /e /y \"%s\" \"%s\" >null"%(origin_path, target_path))
        if result != 0:
            input("\n！！！复制文件夹\n%s\n到\n%s\n时出错！！！\n程序退出"%(origin_path, target_path))
            exit()
        del process_json["patch_metadata"]
        process_json_save(process_json)
        print("\n！！！已还原metadata！！！\n")


# 添加任务完成的键和值
def complete_task():
    # 读取任务进度
    process_json = read_json()
    if process_json is False:
        input("process.json 文件读取出错，程序退出...")
        exit(0)
    AllDone = True
    for i in process_json["zip_files_staut"]:
        if i[1] == "wait_for_unzip" or i[2] == "wait_for_backup":
            AllDone = False
    for i in process_json["hdiff_files_staut"]:
        if i[1] == "wait_for_hdiff":
            AllDone = False
    for i in process_json["delete_files_staut"]:
        if i[1] == "wait_for_delete" or i[2] == "wait_for_backup":
            AllDone = False
    if AllDone == True:
        process_json["AllDone"] = True
        process_json_save(process_json)
        print("\n***安装完成！***\n")
        input("！！！请勿删除程序当前路径下的 process.json 文件，否则无法恢复备份和后续操作！！！")
    else:
        print("\n***安装未完全！***\n")
        input("！！！请勿删除程序当前路径下的 process.json 文件，否则无法恢复备份和后续操作！！！")


# 恢复备份
def restore_backup():
    # 读取 process.json 文件
    process_json = read_json()
    if process_json is False:
        input("process.json 文件读取出错，程序退出...")
        exit(0)
    if "restore_backup" in process_json:
        print("\n！！！备份已恢复，无需恢复！！！\n")
        return "\n！！！备份已恢复，无需恢复！！！\n"
    backup_path = process_json["backup_path"]
    gig_path = process_json["gig_path"]
    updatefiles = []
    deletefiles = []
    backupfiles = []
    for i in process_json["zip_files_staut"]:
        if i[0][-6:] == ".hdiff":
            updatefiles.append(i[0][:-6])
        if i[2] == "already_backed_up":
            backupfiles.append(i[0])
        updatefiles.append(i[0])
    for i in process_json["delete_files_staut"]:
        deletefiles.append(i[0])
        backupfiles.append(i[0])
    
    backupfiles_hiatus = []
    for i in backupfiles:
        if os.path.isfile(os.path.join(backup_path, i)) is False:
            backupfiles_hiatus.append(i)
    if len(backupfiles_hiatus) > 0:
        # print("\n！！！ ！！！\n")
        print("\n！！！备份文件不完整，建议重新安装游戏！！！\n")
        select = input("继续恢复备份请输入1，回车退出")
        if select != "1":
            exit()
        else:
            for i in backupfiles_hiatus:
                print("！！！备份文件\"%s\"不存在，恢复失败！！！"%i)
    
    for i in updatefiles:
        if os.path.isfile(os.path.join(gig_path, i)):
            os.remove(os.path.join(gig_path, i))
    
    result = os.system("xcopy /s /e /y \"%s\" \"%s\" >null"%(backup_path, gig_path))
    if result != 0:
            input("\n！！！复制文件夹\n%s\n到\n%s\n时出错！！！\n程序退出"%(backup_path, gig_path))
            exit()
    n = 0
    for i in process_json["zip_files_staut"]:
        process_json["zip_files_staut"][n][1] = "wait_for_unzip"
        if i in backupfiles_hiatus:
            process_json["zip_files_staut"][n][2] = "wait_for_backup"
        n += 1
    n = 0
    for i in process_json["delete_files_staut"]:
        process_json["delete_files_staut"][n][1] = "wait_for_delete"
        if i in backupfiles_hiatus:
            process_json["delete_files_staut"][n][2] = "wait_for_backup"
        n += 1
    del process_json["AllDone"]
    process_json["restore_backup"] = True
    process_json_save(process_json)
    print("\n！！！备份已恢复！！！\n")


# 删除备份
def delete_backup():
    # 读取 process.json 文件
    process_json = read_json()
    if process_json is False:
        input("process.json 文件读取出错，程序退出...")
        exit(0)  
    if "delete_backup" in process_json:
        print("\n！！！备份已删除，无需删除！！！\n")
        return "\n！！！备份已删除，无需删除！！！\n"
    backup_path = process_json["backup_path"]
    print("\n！！！请确保游戏可以整除游玩后再删除备份！！！\n")
    select = input("继续删除备份输入1，回车取消：")
    if select == "1":
        delete_dirs(backup_path)
        process_json["delete_backup"] = True
        process_json_save(process_json)
        print("\n！！！备份已删除！！！\n")
    



